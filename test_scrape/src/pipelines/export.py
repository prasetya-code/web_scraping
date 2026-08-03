from itemadapter import ItemAdapter

from ..exporters.factory import ExporterFactory


class ExportPipe:
    """
    Pipeline ini merupakan penghubung antara Scrapy dan seluruh
    exporter (CSV, JSON, XML, dll).
    """

    def __init__(self, export_dir, export_format):
        """
        export_dir
            Direktori penyimpanan hasil export.

        export_format
            Format export yang dipilih pada custom_settings spider.
        """

        # Membuat exporter sesuai format yang dipilih.
        self.exporter = ExporterFactory.create(
            export_format,
            export_dir,
        )

    @classmethod
    def from_crawler(cls, crawler):
        """
        Seluruh konfigurasi export diambil dari custom_settings
        spider sehingga pipeline tidak perlu menggunakan nilai yang di-hardcode.
        """

        return cls(

            export_dir=crawler.settings.get(
                "EXPORT_DIR",
            ),

            export_format=crawler.settings.get(
                "EXPORT_FORMAT",
            ),
        )

    def open_spider(self, spider):
        """
        Pipeline hanya meneruskan proses pembukaan resource kepada exporter yang sedang digunakan.
        """

        self.exporter.open(spider)

    def process_item(self, item, spider,):
        """
        ExportPipe bertugas mengubah seluruh jenis item Scrapy menjadi dictionary standar menggunakan ItemAdapter.
        """

        # Mengubah item Scrapy menjadi adapter.
        adapter = ItemAdapter(item)

        # Mengubah adapter menjadi dictionary biasa agar seluruh exporter menerima tipe data yang sama.
        self.exporter.export_item(
            adapter.asdict()
        )

        # Mengembalikan item agar pipeline berikutnya masih dapat memproses item tersebut.
        return item

    def close_spider(self, spider):
        """
        Pipeline hanya meneruskan proses penutupan resource kepada
        exporter sehingga setiap exporter dapat melakukan proses
        akhir sesuai kebutuhannya, misalnya:

            - Menutup file CSV.
            - Menulis file JSON.
            - Commit transaksi database.
            - Menutup koneksi database.
        """

        self.exporter.close()