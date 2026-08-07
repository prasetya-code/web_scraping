from .base import BasePipe

from scrapy.exceptions import DropItem

class QualityCheckPipe(BasePipe):
    """
    Bertugas melakukan pengecekan kualitas data (business rule validation).
    """

    # ------------------------------------------------------------------
    # Batas nilai yang dianggap valid.
    # ------------------------------------------------------------------
    MIN_RATING = 1
    MAX_RATING = 5

    # ------------------------------------------------------------------
    # Field yang tidak boleh bernilai negatif.
    # ------------------------------------------------------------------
    NON_NEGATIVE_FIELDS = (
        "price_euro",
        "excl_tax_euro",
        "incl_tax_euro",
        "tax",
        "stock",
        "reviews",
    )

    def process_item(self, item, spider):

        try:

            # ----------------------------------------------------------
            # Validasi rating.
            # ----------------------------------------------------------
            self._check_rating(item)

            # ----------------------------------------------------------
            # Validasi seluruh field yang tidak boleh bernilai negatif.
            # ----------------------------------------------------------
            for field in self.NON_NEGATIVE_FIELDS:

                self._check_non_negative(item, field)

            self.log_success(spider, item)

            return item

        except DropItem as e:

            spider.logger.warning(f"{self.__class__.__name__}: {e}")
            raise

        except Exception:

            self.log_exception(spider)
            raise

    # ==============================================================
    # Helper Methods
    # ==============================================================

    def _check_rating(self, item):
        """
        Memastikan rating berada pada rentang yang valid.
        """

        rating = self.get_value(item, "rating")

        if rating is None:
            return

        if not (self.MIN_RATING <= rating <= self.MAX_RATING):
            raise DropItem(f"Invalid rating.")

    def _check_non_negative(self, item, field):
        """
        Memastikan field tidak bernilai negatif.
        """

        value = self.get_value(item, field)

        if value is None:
            return

        if value < 0:
            raise DropItem(f"Negative {field}.")