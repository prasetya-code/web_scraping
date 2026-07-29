import logging

from scrapy.exporters import CsvItemExporter

logger = logging.getLogger(__name__)


class CsvSemicolon(CsvItemExporter):
    """
    CSV exporter that uses a semicolon (;) as the field delimiter.
    """

    def __init__(self, 
                 *args,     # get all arguments from CsvItemExporter
                 **kwargs   # get key value from CsvItemExporter
                 ) -> None:
        try:
            kwargs.setdefault("delimiter", ";")

            super().__init__(*args, **kwargs)   # meneruskan perubahan ke parent class

            print(f"\n{'=' * 30}")
            logger.debug(f"Initialized {self.__class__.__name__} with delimiter '{kwargs["delimiter"]}'.")
            print(f"{'=' * 30}\n")

        except Exception:
            logger.exception(f"Failed to initialize {self.__class__.__name__}.")
            raise