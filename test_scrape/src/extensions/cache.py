import logging

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections.abc import Iterator

from scrapy.settings import Settings


logger = logging.getLogger(__name__)

# must set in settings/extension.py
@dataclass(frozen=True, slots=True)
class CacheEntry:
    """
    Class ini hanya menyimpan informasi mengenai satu file cache.
    """

    path: Path

    def exists(self) -> bool:
        """
        Memeriksa apakah file cache masih tersedia.
        """
        try:
            return self.path.exists()

        except Exception:
            logger.exception(
                "Gagal memeriksa keberadaan file cache: %s",
                self.path,
            )
            raise

    @property
    def modified_time(self) -> datetime:
        """
        Mengambil waktu terakhir file dimodifikasi.
        """
        try:
            timestamp = self.path.stat().st_mtime

            return datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            )

        except Exception:
            logger.exception(
                "Gagal mengambil waktu modifikasi file cache: %s",
                self.path,
            )
            raise

    @property
    def age(self) -> timedelta:
        """
        Menghitung umur file cache.
        """
        try:
            return (
                datetime.now(timezone.utc)
                - self.modified_time
            )

        except Exception:
            logger.exception(
                "Gagal menghitung umur file cache: %s",
                self.path,
            )
            raise

    def is_expired(
        self,
        max_age: timedelta,
    ) -> bool:
        """
        Memeriksa apakah file cache telah melewati
        batas umur yang ditentukan.
        """
        try:
            return self.age > max_age

        except Exception:
            logger.exception(
                "Gagal memeriksa status kedaluwarsa cache: %s",
                self.path,
            )
            raise

    @property
    def size(self) -> int:
        """
        Mengambil ukuran file cache dalam satuan byte.
        """
        try:
            return self.path.stat().st_size

        except Exception:
            logger.exception(
                "Gagal mengambil ukuran file cache: %s",
                self.path,
            )
            raise


class CacheManager:
    """
    Class ini bertanggung jawab terhadap:

    - Membaca konfigurasi cache dari Scrapy.
    - Mengelola direktori cache.
    - Menyediakan iterator file cache.
    - Menyediakan operasi dasar filesystem.
    """

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        """
        Inisialisasi object CacheManager.
        """
        try:
            self.settings = settings

            cache_dir = settings.get(
                "HTTPCACHE_DIR"
            )

            if not cache_dir:

                raise ValueError(
                    "HTTPCACHE_DIR belum dikonfigurasi."
                )

            self._cache_dir = Path(
                cache_dir
            )

            self._max_age = timedelta(
                seconds=settings.getint(
                    "HTTPCACHE_EXPIRATION_SECS"
                )
            )

            print(f"\n{'=' * 45}")

            logger.debug(
                "Initialized %s",
                self.__class__.__name__,
            )

            logger.debug(
                "Cache directory : %s",
                self.cache_dir,
            )

            logger.debug(
                "Cache expiration : %s",
                self.max_age,
            )

            print(f"{'=' * 45}\n")

        except Exception:
            logger.exception(
                "Gagal menginisialisasi CacheManager."
            )
            raise

    @property
    def cache_dir(self) -> Path:
        """
        Mengambil lokasi direktori HTTP Cache.
        """
        return self._cache_dir

    @property
    def max_age(self) -> timedelta:
        """
        Mengambil batas umur file cache.
        """
        return self._max_age

    def exists(self) -> bool:
        """
        Memeriksa apakah direktori cache tersedia.
        """
        try:
            return self.cache_dir.exists()

        except Exception:
            logger.exception(
                "Gagal memeriksa direktori cache."
            )
            raise

    def is_empty(self) -> bool:
        """
        Memeriksa apakah direktori cache kosong.
        """
        try:
            if not self.exists():
                return True

            return not any(
                self.cache_dir.iterdir()
            )

        except Exception:
            logger.exception(
                "Gagal memeriksa isi direktori cache."
            )
            raise

    def file_count(self) -> int:
        """
        Menghitung jumlah file cache.
        """
        try:
            return sum(
                1
                for _
                in self.iter_files()
            )

        except Exception:
            logger.exception(
                "Gagal menghitung jumlah file cache."
            )
            raise

    def iter_files(self) -> Iterator[CacheEntry]:
        """
        Melakukan iterasi seluruh file cache.

        Method ini menghasilkan object CacheEntry.
        """
        try:
            if not self.exists():
                return

            for path in self.cache_dir.rglob("*"):

                if not path.is_file():
                    continue

                yield CacheEntry(path)

        except Exception:
            logger.exception(
                "Gagal melakukan iterasi file cache."
            )
            raise

    def iter_directories(self) -> Iterator[Path]:
        """
        Melakukan iterasi seluruh direktori cache.
        """
        try:
            if not self.exists():
                return

            directories = sorted(
                (
                    path
                    for path
                    in self.cache_dir.rglob("*")
                    if path.is_dir()
                ),
                reverse=True,
            )

            yield from directories

        except Exception:
            logger.exception(
                "Gagal melakukan iterasi direktori cache."
            )
            raise

    def expired_files(self) -> Iterator[CacheEntry]:
        """
        Melakukan iterasi seluruh file cache
        yang telah melewati batas umur penyimpanan.
        """
        try:
            for entry in self.iter_files():

                if entry.is_expired(
                    self.max_age,
                ):

                    yield entry

        except Exception:
            logger.exception(
                "Gagal mendapatkan daftar cache yang kedaluwarsa."
            )
            raise

    def remove_file(
        self,
        entry: CacheEntry,
    ) -> bool:
        """
        Menghapus satu file cache.
        """
        try:
            if not entry.exists():

                logger.debug(
                    "File cache tidak ditemukan: %s",
                    entry.path,
                )

                return False

            entry.path.unlink()

            logger.debug(
                "File cache berhasil dihapus: %s",
                entry.path,
            )

            return True

        except Exception:
            logger.exception(
                "Gagal menghapus file cache: %s",
                entry.path,
            )

            return False

    def remove_empty_directories(self) -> int:
        """
        Menghapus seluruh direktori cache yang kosong.
        """
        removed = 0

        try:
            for directory in self.iter_directories():

                try:
                    directory.rmdir()

                    removed += 1

                    logger.debug(
                        "Direktori kosong berhasil dihapus: %s",
                        directory,
                    )

                except OSError:
                    #
                    # Direktori masih memiliki isi.
                    #
                    continue

                except Exception:
                    logger.exception(
                        "Gagal menghapus direktori: %s",
                        directory,
                    )

            return removed

        except Exception:
            logger.exception(
                "Gagal membersihkan direktori cache."
            )
            raise

    def clear(self) -> int:
        """
        Method ini berguna apabila suatu saat ingin
        menambahkan fitur "Clear Cache".
        """
        deleted = 0

        try:
            for entry in self.iter_files():

                if self.remove_file(entry):

                    deleted += 1

            removed = self.remove_empty_directories()

            print(f"\n{'=' * 45}")

            logger.info(
                "Seluruh cache berhasil dibersihkan."
            )

            logger.info(
                "File cache dihapus      : %s",
                deleted,
            )

            logger.info(
                "Direktori kosong dihapus: %s",
                removed,
            )

            print(f"{'=' * 45}\n")

            return deleted

        except Exception:
            logger.exception(
                "Gagal menghapus seluruh cache."
            )
            raise


class CacheCleaner(CacheManager):
    """
    Class ini bertanggung jawab terhadap:

    - Membersihkan file HTTP Cache yang telah melewati
      batas waktu penyimpanan.
    """

    def clean(self) -> int:
        """
        Menghapus seluruh file cache yang telah kedaluwarsa.
        """
        deleted = 0

        try:
            print(f"\n{'=' * 45}")

            logger.info(
                "Memulai pembersihan HTTP Cache."
            )

            print(f"{'=' * 45}\n")

            #
            # Direktori cache belum tersedia.
            #
            if not self.exists():

                logger.warning(
                    "Direktori HTTP Cache tidak ditemukan: %s",
                    self.cache_dir,
                )

                return deleted

            #
            # Direktori cache kosong.
            #
            if self.is_empty():

                print(f"\n{'=' * 45}")

                logger.info(
                    "Direktori HTTP Cache kosong."
                )

                print(f"{'=' * 45}\n")

                return deleted

            #
            # Menghitung jumlah file sebelum pembersihan.
            #
            total_files = self.file_count()

            logger.info(
                "Jumlah file cache : %s",
                total_files,
            )

            #
            # Menghapus seluruh cache yang telah kedaluwarsa.
            #
            for entry in self.expired_files():

                if self.remove_file(entry):

                    deleted += 1

            #
            # Menghapus direktori yang sudah kosong.
            #
            removed = self.remove_empty_directories()

            #
            # Menghitung jumlah file yang masih tersisa.
            #
            remaining = self.file_count()

            print(f"\n{'=' * 45}")

            logger.info(
                "Pembersihan HTTP Cache selesai."
            )

            logger.info(
                "File cache sebelum dibersihkan : %s",
                total_files,
            )

            logger.info(
                "File cache dihapus             : %s",
                deleted,
            )

            logger.info(
                "File cache tersisa             : %s",
                remaining,
            )

            logger.info(
                "Direktori kosong dihapus       : %s",
                removed,
            )

            print(f"{'=' * 45}\n")

            return deleted

        except Exception:

            logger.exception(
                "Terjadi kesalahan saat membersihkan HTTP Cache."
            )

            raise


from scrapy import signals
from scrapy.crawler import Crawler


class CacheExtension:
    """
    Class ini bertanggung jawab terhadap:

    - Menghubungkan CacheCleaner dengan lifecycle Scrapy.
    - Menjalankan pembersihan HTTP Cache setelah spider selesai.
    - Menyimpan statistik pembersihan cache.
    """

    @classmethod
    def from_crawler(
        cls,
        crawler: Crawler,
    ) -> "CacheExtension":
        """
        Factory method yang dipanggil otomatis oleh Scrapy
        ketika Extension diinisialisasi.
        """
        try:
            extension = cls(crawler)

            #
            # Dipanggil ketika seluruh engine Scrapy benar-benar
            # telah berhenti.
            #
            crawler.signals.connect(
                extension.engine_stopped,
                signal=signals.engine_stopped,
            )

            return extension

        except Exception:
            logger.exception(
                "Gagal menginisialisasi CacheExtension."
            )
            raise

    def __init__(
        self,
        crawler: Crawler,
    ) -> None:
        """
        Inisialisasi object CacheExtension.
        """
        try:
            self.crawler = crawler

            self.settings = crawler.settings

            self.stats = crawler.stats

            logger.debug(
                "Initialized %s.",
                self.__class__.__name__,
            )

        except Exception:
            logger.exception(
                "Gagal menginisialisasi CacheExtension."
            )
            raise

    @property
    def cleaner(self) -> CacheCleaner:
        """
        Membuat object CacheCleaner berdasarkan
        konfigurasi Scrapy saat ini.
        """
        try:
            return CacheCleaner(
                settings=self.settings,
            )

        except Exception:
            logger.exception(
                "Gagal membuat CacheCleaner."
            )
            raise

    def engine_stopped(self) -> None:
        """
        Dipanggil setelah seluruh engine Scrapy berhenti.

        Pada tahap ini seluruh proses crawling telah selesai,
        sehingga aman untuk melakukan pembersihan HTTP Cache.
        """
        try:
            print(f"\n{'=' * 45}")

            logger.info(
                "Checking expired HTTP Cache..."
            )

            print(f"{'=' * 45}\n")

            deleted = self.cleaner.clean()

            #
            # Menyimpan statistik pembersihan cache.
            #
            self.stats.set_value(
                "cache/deleted",
                deleted,
            )

            logger.info(
                "HTTP Cache cleanup completed."
            )

        except Exception:
            logger.exception(
                "Terjadi kesalahan saat menjalankan CacheExtension."
            )
            raise