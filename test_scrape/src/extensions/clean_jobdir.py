import logging
import shutil

from pathlib import Path

from scrapy import signals
from scrapy.crawler import Crawler


logger = logging.getLogger(__name__)


class JobdirCleaner:
    """
    Remove the Scrapy JOBDIR after the engine has completely stopped.

    The JOBDIR is removed only when the spider finishes successfully
    (reason == "finished"). If the spider is interrupted or fails,
    the JOBDIR is preserved so the crawl can be resumed.
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "JobdirCleaner":
        """
        Factory method yang dipanggil otomatis oleh Scrapy ketika Extension diinisialisasi.
        """
        # Membuat object JobdirCleaner
        extension = cls(crawler)

        # Dipanggil ketika spider selesai. Digunakan hanya untuk menyimpan finish reason.
        crawler.signals.connect(
            extension.spider_closed,
            signal=signals.spider_closed,
        )

        # Dipanggil ketika seluruh engine Scrapy benar-benar selesai. Baru pada tahap ini JOBDIR aman dihapus.
        crawler.signals.connect(
            extension.engine_stopped,
            signal=signals.engine_stopped,
        )

        return extension

    def __init__(self, crawler: Crawler) -> None:
        """
        Inisialisasi object JobdirCleaner.
        """
        try:
            # Menyimpan Settings Scrapy agar dapat digunakan pada engine_stopped().
            self.settings = crawler.settings

            # Menyimpan alasan spider berhenti. Nilainya akan diisi pada spider_closed().
            self.finish_reason: str | None = None

            logger.debug(f"Initialized {self.__class__.__name__}.")

        except Exception:
            logger.exception(f"Failed to initialize {self.__class__.__name__}.")
            raise

    def spider_closed(self, spider, reason: str) -> None:
        """
        Dipanggil ketika spider selesai. Method ini TIDAK menghapus JOBDIR.
        Nilai tersebut akan diperiksa nanti ketika engine_stopped() dipanggil.
        """
        try:
            self.finish_reason = reason

            logger.debug(f"Spider closed with reason: {reason}")

        except Exception:
            logger.exception(f"Failed while processing spider_closed signal.")
            raise

    def engine_stopped(self) -> None:
        """
        Dipanggil setelah seluruh engine Scrapy berhenti.
        """
        try:
            logger.debug(
                "Checking whether JOBDIR cleanup is required."
            )

            # Hanya hapus JOBDIR apabila crawl selesai normal.
            # Jika crawl gagal atau dihentikan, JOBDIR dipertahankan agar dapat di-resume.
            if self.finish_reason != "finished":
                logger.debug("Skipping JOBDIR cleanup because spider "
                    f"finished with reason: {self.finish_reason}")
                return

            # Mengambil lokasi JOBDIR dari settings.
            jobdir = self.settings.get("JOBDIR")

            if not jobdir:
                logger.debug(f"JOBDIR is not configured.")
                return

            jobdir_path = Path(jobdir)

            if not jobdir_path.exists():
                logger.debug(f"JOBDIR does not exist: {jobdir_path}")
                return

            # Menghapus seluruh isi JOBDIR secara rekursif.
            shutil.rmtree(jobdir_path)

            logger.info(f"JOBDIR removed successfully: {jobdir_path}")

        except Exception:
            logger.exception(f"Failed to remove JOBDIR.")
            raise