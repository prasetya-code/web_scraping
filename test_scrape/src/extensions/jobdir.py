import logging
import shutil

from pathlib import Path

from scrapy.crawler import Crawler
from scrapy import signals


logger = logging.getLogger(__name__)


class BaseJobdirExtension:
    """
    Class ini menyediakan operasi umum seperti membaca konfigurasi,
    memeriksa keberadaan JOBDIR, memeriksa isi JOBDIR, dan menghapus JOBDIR.
    """

    def __init__(self, crawler: Crawler) -> None:
        """
        Inisialisasi object dasar JOBDIR.
        """
        try:
            # Menyimpan object crawler.
            self.crawler = crawler

            # Menyimpan settings Scrapy.
            self.settings = crawler.settings

            # Mengambil lokasi JOBDIR dari settings.
            jobdir = self.settings.get("JOBDIR")

            # Konversi menjadi object Path apabila tersedia.
            self.jobdir = (
                Path(jobdir)
                if jobdir
                else None
            )

            print(f"\n{'=' * 45}")
            logger.debug(f"Initialized {self.__class__.__name__}.")
            print(f"{'=' * 45}\n")

        except Exception:
            logger.exception("Gagal menginisialisasi BaseJobdirExtension.")
            raise

    @property
    def is_configured(self) -> bool:
        """
        Memeriksa apakah JOBDIR dikonfigurasi.
        """
        return self.jobdir is not None

    @property
    def exists(self) -> bool:
        """
        Memeriksa apakah direktori JOBDIR tersedia.
        """
        return (
            self.jobdir is not None
            and self.jobdir.exists()
        )

    @property
    def is_empty(self) -> bool:
        """
        Memeriksa apakah JOBDIR kosong.
        """
        if not self.exists:
            return True

        return not any(
            self.jobdir.iterdir()
        )

    @property
    def has_files(self) -> bool:
        """
        Memeriksa apakah JOBDIR memiliki isi.
        """
        return not self.is_empty

    @property
    def file_count(self) -> int:
        """
        Menghitung jumlah file yang terdapat di dalam JOBDIR.
        """
        if not self.exists:
            return 0

        return sum(
            1
            for file in self.jobdir.rglob("*")
            if file.is_file()
        )

    def remove(self) -> None:
        """
        Menghapus seluruh isi JOBDIR.
        """
        try:
            # JOBDIR belum dikonfigurasi.
            if not self.is_configured:
                print(f"\n{'=' * 45}")
                logger.debug("JOBDIR tidak dikonfigurasi.")
                print(f"{'=' * 45}\n")

                return

            # Direktori JOBDIR tidak ditemukan.
            if not self.exists:

                print(f"\n{'=' * 45}")
                logger.debug(f"JOBDIR tidak ditemukan: {self.jobdir}")
                print(f"{'=' * 45}\n")
                
                return

            # Menghapus seluruh isi JOBDIR secara rekursif.
            shutil.rmtree(self.jobdir)

            print(f"\n{'=' * 45}")
            logger.info(f"JOBDIR berhasil dihapus: {self.jobdir}")
            print(f"{'=' * 45}\n")

        except Exception:
            logger.exception("Terjadi kesalahan saat menghapus JOBDIR.")
            raise


class JobdirState(BaseJobdirExtension):
    """
    Mendeteksi kondisi JOBDIR sebelum spider mulai berjalan.
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "JobdirState":
        """
        Factory method yang dipanggil otomatis oleh Scrapy ketika Extension diinisialisasi.
        """
        try:
            # Membuat object JobdirState.
            extension = cls(crawler)

            # Dipanggil ketika spider mulai dijalankan.
            crawler.signals.connect(
                extension.spider_opened,
                signal=signals.spider_opened,
            )

            return extension

        except Exception:
            logger.exception("Gagal menginisialisasi JobdirState.")
            raise

    def spider_opened(self, spider) -> None:
        """
        Dipanggil ketika spider mulai berjalan.
        """
        try:
            stats = self.crawler.stats

            # Nilai default.
            spider.resume_crawl = False
            spider.jobdir_state = "disabled"

            stats.set_value(
                "jobdir/enabled",
                self.is_configured,
            )

            # JOBDIR belum dikonfigurasi.
            if not self.is_configured:

                print(f"\n{'=' * 45}")
                logger.info("JOBDIR tidak dikonfigurasi.")
                print(f"{'=' * 45}\n")

                return

            print(f"\n{'=' * 45}")
            logger.info(f"JOBDIR : {self.jobdir}")
            print(f"{'=' * 45}\n")


            stats.set_value(
                "jobdir/path",
                str(self.jobdir),
            )

            #
            # JOBDIR belum ada.
            #
            if not self.exists:

                spider.jobdir_state = "new"

                stats.set_value(
                    "jobdir/state",
                    "new",
                )

                print(f"\n{'=' * 45}")
                logger.info("Mode : New Crawl")
                print(f"{'=' * 45}\n")

                return

            #
            # JOBDIR kosong.
            #
            if self.is_empty:

                spider.jobdir_state = "new"

                stats.set_value(
                    "jobdir/state",
                    "new",
                )

                print(f"\n{'=' * 45}")
                logger.info("Mode : New Crawl (JOBDIR kosong)")
                print(f"{'=' * 45}\n")

                return

            # JOBDIR memiliki data.
            spider.resume_crawl = True
            spider.jobdir_state = "resume"

            stats.set_value(
                "jobdir/state",
                "resume",
            )

            stats.set_value(
                "jobdir/file_count",
                self.file_count,
            )

            print(f"\n{'=' * 45}")
            logger.info("Mode : Resume Crawl")
            print(f"{'=' * 45}\n")

            print(f"\n{'=' * 45}")
            logger.info(f"Jumlah file JOBDIR : {self.file_count}")
            print(f"{'=' * 45}\n")

        except Exception:
            logger.exception("Terjadi kesalahan saat mendeteksi status JOBDIR.")
            raise


class JobdirCleaner(BaseJobdirExtension):
    """
    - JOBDIR hanya dihapus apabila spider selesai normal (reason == "finished").
    - Jika spider dihentikan atau gagal, JOBDIR dipertahankan agar crawl dapat di-resume.
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "JobdirCleaner":
        """
        Factory method yang dipanggil otomatis oleh Scrapy ketika Extension diinisialisasi.
        """
        try:
            # Membuat object JobdirCleaner.
            extension = cls(crawler)

            # Dipanggil ketika spider selesai.
            crawler.signals.connect(
                extension.spider_closed,
                signal=signals.spider_closed,
            )

            # Dipanggil ketika seluruh engine Scrapy benar-benar telah berhenti.
            crawler.signals.connect(
                extension.engine_stopped,
                signal=signals.engine_stopped,
            )

            return extension

        except Exception:
            logger.exception("Gagal menginisialisasi JobdirCleaner.")
            raise

    def __init__(self, crawler: Crawler) -> None:
        """
        Inisialisasi object JobdirCleaner.
        """
        try:
            super().__init__(crawler)

            # Menyimpan alasan spider berhenti.
            self.finish_reason: str | None = None

        except Exception:
            logger.exception("Gagal menginisialisasi JobdirCleaner.")
            raise

    def spider_closed(self, spider, reason: str) -> None:
        """
        Method ini hanya menyimpan alasan spider berhenti.
        """
        try:
            self.finish_reason = reason

            self.crawler.stats.set_value(
                "jobdir/finish_reason",
                reason,
            )

            print(f"\n{'=' * 45}")
            logger.debug(f"Spider selesai dengan reason: {reason}")
            print(f"{'=' * 45}\n")

        except Exception:
            logger.exception("Terjadi kesalahan pada spider_closed().")
            raise

    def engine_stopped(self) -> None:
        """
        Dipanggil ketika seluruh engine Scrapy telah berhenti.
        """
        try:
            stats = self.crawler.stats

            print(f"\n{'=' * 45}")
            logger.debug("Memeriksa apakah JOBDIR perlu dibersihkan.")
            print(f"{'=' * 45}\n")

            # JOBDIR tidak dikonfigurasi.
            if not self.is_configured:

                stats.set_value(
                    "jobdir/remove_status",
                    "disabled",
                )

                print(f"\n{'=' * 45}")
                logger.debug("JOBDIR tidak dikonfigurasi.")
                print(f"{'=' * 45}\n")

                return

            # Crawl tidak selesai normal.
            if self.finish_reason != "finished":

                stats.set_value(
                    "jobdir/remove_status",
                    "skipped",
                )

                print(f"\n{'=' * 45}")
                logger.debug(
                    "JOBDIR dipertahankan karena "
                    f"crawl berakhir dengan reason: "
                    f"{self.finish_reason}"
                )
                print(f"{'=' * 45}\n")

                return

            # JOBDIR tidak ditemukan.
            if not self.exists:

                stats.set_value(
                    "jobdir/remove_status",
                    "not_found",
                )

                print(f"\n{'=' * 45}")
                logger.debug(
                    f"JOBDIR tidak ditemukan: "
                    f"{self.jobdir}"
                )
                print(f"{'=' * 45}\n")

                return

            # Menghapus JOBDIR.
            self.remove()

            stats.set_value(
                "jobdir/remove_status",
                "removed",
            )

            stats.inc_value(
                "jobdir/remove_count",
            )

            print(f"\n{'=' * 45}")
            logger.info("JOBDIR berhasil dibersihkan.")
            print(f"{'=' * 45}\n")

        except Exception:

            self.crawler.stats.set_value(
                "jobdir/remove_status",
                "failed",
            )

            logger.exception("Terjadi kesalahan saat menghapus JOBDIR.")
            raise