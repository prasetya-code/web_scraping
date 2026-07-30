import hashlib
import logging
import re

from pathlib import Path
from urllib.parse import urlparse

from itemadapter import ItemAdapter

from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes


logger = logging.getLogger(__name__)


# Pastikan sudah install lib pillow
class BookImagesPipe(ImagesPipeline):

    @classmethod
    def from_crawler(cls, crawler):

        # Inisialisasi pipeline bawaan ImagesPipeline
        pipeline = super().from_crawler(crawler)

        # Simpan Stats Collector agar dapat digunakan di seluruh method pipeline
        pipeline.stats = crawler.stats

        return pipeline

    def get_media_requests(self, item, info):

        try:

            # Adapter agar kompatibel dengan dataclass, scrapy.Item maupun dictionary.
            adapter = ItemAdapter(item)

            # Ambil data dari items/books_item.py
            image_url = adapter.get("image")

            # Jika URL tidak tersedia maka download dilewati
            if not image_url:
                # 
                self.stats.inc_value("images/missing_url")

                logger.warning(f"Field 'image' kosong. Download gambar dilewati.")

                return

            self.stats.inc_value("images/requested")

            print(f"\n{'=' * 30}")
            logger.info(f"Download image : {image_url}")
            print(f"{'=' * 30}\n")

            # Kirim request download gambar
            yield Request(url=image_url)

        except Exception:

            self.stats.inc_value("images/errors/get_media_requests")

            logger.exception(f"Error pada get_media_requests()")

    def file_path(self, request, response=None, info=None, *, item=None):

        try:

            # Adapter agar kompatibel dengan dataclass, scrapy.Item maupun dictionary.
            adapter = ItemAdapter(item)

            # Ambil data dari items/books_item.py
            title = adapter.get("title", "untitled")

            # Hapus karakter yang tidak valid untuk nama file
            title = re.sub(r'[\\/*?:"<>|]', "", title).strip()

            # Rapikan spasi
            title = "_".join(title.split())

            # Jika title kosong setelah dibersihkan, gunakan nama default
            if not title:
                title = "untitled"

            # Hash berdasarkan URL gambar agar nama file tetap unik walaupun terdapat title yang sama
            image_hash = hashlib.sha1(to_bytes(request.url)).hexdigest()[:8]

            # Ambil ekstensi file dari URL gambar
            extension = Path(urlparse(request.url).path).suffix

            # Jika URL tidak memiliki ekstensi, gunakan jpg sebagai default
            if not extension:
                extension = ".jpg"

            self.stats.inc_value("images/file_path/generated")

            # Bentuk nama file akhir
            return (
                f"{title}_{image_hash}"
                f"{extension.lower()}"
            )

        except Exception:

            self.stats.inc_value("images/errors/file_path")

            logger.exception(f"Error pada file_path()")

            # Fallback ke implementasi bawaan Scrapy
            return super().file_path(
                request,
                response=response,
                info=info,
                item=item
            )

    def item_completed(self, results, item, info):

        try:

            # Adapter agar kompatibel dengan dataclass, scrapy.Item maupun dictionary.
            adapter = ItemAdapter(item)

            # Ambil hanya hasil download yang berhasil
            successful = [
                result
                for ok, result in results
                if ok
            ]

            self.stats.inc_value("images/download_total", len(results))

            self.stats.inc_value("images/download_success", len(successful))

            self.stats.inc_value("images/download_failed", len(results) - len(successful))

            if not successful:

                self.stats.inc_value("images/items_without_image")

                logger.warning(f"Download gambar gagal atau tidak ada gambar yang berhasil diunduh.")

                return item

            # Simpan path file lokal
            adapter["image"] = successful[0]["path"]

            self.stats.inc_value("images/items_saved")

            logger.info(f"Image berhasil disimpan: {adapter["image"]}")

            return item

        except Exception:

            self.stats.inc_value("images/errors/item_completed")

            logger.exception(f"Error pada item_completed()")

            return item