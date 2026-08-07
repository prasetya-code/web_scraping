from .base import BasePipe

class NormalizationPipe(BasePipe):
    """
    Bertugas menyeragamkan nilai (business value normalization),
    sehingga seluruh item memiliki representasi data yang konsisten.
    """

    # ------------------------------------------------------------------
    # Mapping rating website menjadi integer.
    # ------------------------------------------------------------------
    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def process_item(self, item, spider):

        try:

            # ----------------------------------------------------------
            # Normalisasi seluruh atribut item.
            # ----------------------------------------------------------
            self._normalize_rating(item)
            self._normalize_category(item)


            self.log_success(spider, item)

            return item

        except Exception:

            self.log_exception(spider)
            raise

    # ==============================================================
    # Helper Methods
    # ==============================================================

    def _normalize_rating(self, item):
        """
        Mengubah rating website menjadi integer.
        """

        rating = self.get_value(item, "rating")

        if rating is None:
            return

        # --------------------------------------------------------------
        # Apabila rating sudah berupa integer maka tidak perlu diproses.
        # --------------------------------------------------------------
        if isinstance(rating, int):
            return

        self.set_value(item, "rating",
            self.RATING_MAP.get(
                rating,
                0,
            ),
        )

    def _normalize_category(self, item):
        """
        Menyeragamkan penulisan kategori.
        """

        category = self.get_value(item, "category")

        if not isinstance(category, str):
            return

        self.set_value(item, "category", category.title())