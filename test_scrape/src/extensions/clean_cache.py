import logging

from datetime import datetime, timedelta
from pathlib import Path

from scrapy.settings import Settings

logger = logging.getLogger(__name__)


class CacheCleaner:
    """
    Remove expired HTTP cache files based on Scrapy settings.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the cache cleaner using Scrapy settings.
        """
        try:
            self.cache_dir = Path(
                # from custom settings spider
                settings["HTTPCACHE_DIR"]
            )

            self.max_age = timedelta(
                # from settings/base.py
                seconds=settings.getint("HTTPCACHE_EXPIRATION_SECS")
            )

            print(f"\n{'=' * 30}")
            logger.debug(f"Initialized {self.__class__.__name__}.")
            logger.debug(f"Cache directory : {self.cache_dir}")
            logger.debug(f"Cache expiration: {self.max_age}")
            print(f"{'=' * 30}\n")


        except Exception:
            logger.exception(f"Failed to initialize {self.__class__.__name__}.")
            raise

    def clean(self) -> int:
        """
        Delete expired HTTP cache files.
        """
        deleted = 0

        try:
            logger.debug("Starting HTTP cache cleanup.")

            if not self.cache_dir.exists():
                logger.warning(f"HTTP cache directory does not exist: {self.cache_dir}")
                return deleted

            now = datetime.now()

            # rglob: Cari semua file dan folder secara rekursif
            for file in self.cache_dir.rglob("*"):

                if not file.is_file():
                    continue

                try:
                    modified = datetime.fromtimestamp(
                        file.stat().st_mtime    # Last Modified Time
                    )

                    age = now - modified

                    if age <= self.max_age:
                        continue

                    file.unlink()

                    deleted += 1

                    print(f"\n{'=' * 30}")
                    logger.debug(f"Deleted expired cache: {file}")
                    print(f"{'=' * 30}\n")

                except Exception:
                    logger.exception(f"Failed to delete cache file: {file}")

            # 
            self._remove_empty_dirs()

            print(f"\n{'=' * 30}")
            logger.info("HTTP cache cleanup completed. "
                f"{deleted} expired file(s) removed.")
            print(f"{'=' * 30}\n")

            return deleted

        except Exception:
            logger.exception("HTTP cache cleanup failed.")
            raise

    def _remove_empty_dirs(self) -> None:
        """
        Remove empty directories inside the cache directory.
        """
        try:
            # sorting: reverse sort
            for directory in sorted(
                # rglob: Cari semua file dan folder secara rekursif
                self.cache_dir.rglob("*"),
                reverse=True,
            ):

                if not directory.is_dir():
                    continue

                try:
                    # remove directory
                    directory.rmdir()

                    print(f"\n{'=' * 30}")
                    logger.debug(f"Removed empty directory: {directory}")
                    print(f"{'=' * 30}\n")

                except OSError:
                    # Directory is not empty.
                    continue

                except Exception:
                    logger.exception(f"Failed to remove directory: {directory}")

        except Exception:
            logger.exception("Failed while removing empty cache directories.")
            raise