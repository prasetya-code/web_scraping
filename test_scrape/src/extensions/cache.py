import logging

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scrapy.settings import Settings
from collections.abc import Iterator


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """
    Class ini hanya menyimpan informasi mengenai file cache.
    """

    path: Path

    def exists(self) -> bool:
        """
        Memeriksa apakah file cache masih tersedia.
        """
        try:
            return self.path.exists()

        except Exception:
            logger.exception("Gagal memeriksa keberadaan file cache: %s", self.path)
            raise

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
            logger.exception("Gagal mengambil waktu modifikasi file cache: %s", self.path)
            raise

    def age(self) -> timedelta:
        """
        Menghitung umur file cache.
        """
        try:
            return (
                datetime.now(timezone.utc)
                - self.modified_time()
            )

        except Exception:
            logger.exception("Gagal menghitung umur file cache: %s", self.path)
            raise

    def is_expired(self, max_age: timedelta) -> bool:
        """
        Memeriksa apakah file cache telah melewati batas umur yang ditentukan.
        """
        try:
            return self.age() > max_age

        except Exception:
            logger.exception("Gagal memeriksa status kedaluwarsa cache: %s", self.path)
            raise

    def size(self) -> int:
        """
        Mengambil ukuran file cache dalam satuan byte.
        """
        try:
            return self.path.stat().st_size

        except Exception:
            logger.exception("Gagal mengambil ukuran file cache: %s", self.path)
            raise


class BaseCache:
    """
    Class ini bertanggung jawab terhadap:
    - Membaca konfigurasi cache dari Scrapy.
    - Mengelola direktori cache.
    - Menyediakan iterator file cache.
    - Menyediakan operasi dasar filesystem.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Inisialisasi object BaseCache.
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

            self.cache_dir = Path(cache_dir)

            self.max_age = timedelta(
                seconds=settings.getint(
                    "HTTPCACHE_EXPIRATION_SECS"
                )
            )

            print(f"\n{'=' * 45}")
            logger.debug(f"Initialized {self.__class__.__name__}")
            logger.debug(f"Cache directory : {self.cache_dir}")
            logger.debug(f"Cache expiration : {self.max_age}")
            print(f"{'=' * 45}\n")

        except Exception:
            logger.exception("Gagal menginisialisasi BaseCache.")
            raise

    def exists(self) -> bool:
        """
        Memeriksa apakah direktori cache tersedia.
        """
        try:
            return self.cache_dir.exists()

        except Exception:
            logger.exception("Gagal memeriksa direktori cache.")
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
            logger.exception("Gagal memeriksa isi direktori cache.")
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
            logger.exception("Gagal menghitung jumlah file cache.")
            raise

    def iter_files(self):
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
            logger.exception("Gagal melakukan iterasi file cache.")
            raise

    def iter_directories(self):
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
            logger.exception("Gagal melakukan iterasi direktori cache.")
            raise

    def expired_files(self) -> Iterator[CacheEntry]:
        """
        Melakukan iterasi seluruh file cache yang telah melewati batas umur penyimpanan.
        """
        try:
            for entry in self.iter_files():

                if entry.is_expired(self.max_age):

                    yield entry

        except Exception:
            logger.exception("Gagal mendapatkan daftar cache yang kedaluwarsa.")
            raise

    def remove_file(self, entry: CacheEntry) -> bool:
        """
        Menghapus satu file cache.
        """
        try:
            if not entry.exists():

                logger.debug(f"File cache tidak ditemukan: {entry.path}")

                return False

            entry.path.unlink()

            logger.debug(f"File cache berhasil dihapus: {entry.path}")

            return True

        except Exception:
            logger.exception("Gagal menghapus file cache: %s", entry.path)
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

                    logger.debug(f"Direktori kosong berhasil dihapus: {directory}")

                except OSError:
                    #
                    # Direktori masih memiliki isi.
                    #
                    continue

                except Exception:
                    logger.exception("Gagal menghapus direktori: %s", directory)

            return removed

        except Exception:
            logger.exception("Gagal membersihkan direktori cache.")
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

            self.remove_empty_directories()

            print(f"\n{'=' * 45}")
            logger.info(
                f"Seluruh cache berhasil dibersihkan. "
                f"{deleted} file dihapus."
            )
            print(f"{'=' * 45}\n")

            return deleted

        except Exception:
            logger.exception(
                "Gagal menghapus seluruh cache."
            )
            raise

class CacheCleaner(BaseCache):
    """
    Membersihkan file HTTP Cache yang telah melewati
    batas waktu penyimpanan.
    """

    def clean(self) -> int:
        """
        Menghapus seluruh file cache yang telah kedaluwarsa.
        """
        deleted = 0

        try:
            print(f"\n{'=' * 45}")
            logger.info("Memulai pembersihan HTTP Cache.")
            print(f"{'=' * 45}\n")

            #
            # Direktori cache belum tersedia.
            #
            if not self.exists():

                logger.warning("Direktori HTTP Cache tidak ditemukan: %s", self.cache_dir)

                return deleted

            #
            # Direktori cache kosong.
            #
            if self.is_empty():

                print(f"\n{'=' * 45}")
                logger.info("Direktori HTTP Cache kosong.")
                print(f"{'=' * 45}\n")

                return deleted

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

            print(f"\n{'=' * 45}")
            logger.info("Pembersihan HTTP Cache selesai.")
            logger.info(f"File cache dihapus      : {deleted}")
            logger.info(f"Direktori kosong dihapus: {removed}")
            print(f"{'=' * 45}\n")

            return deleted

        except Exception:
            logger.exception("Terjadi kesalahan saat membersihkan HTTP Cache.")
            raise