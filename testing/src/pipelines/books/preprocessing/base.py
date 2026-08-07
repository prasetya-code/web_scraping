import re

class BasePipe:
    """
    Tujuan class ini adalah mengurangi duplikasi kode (Don't Repeat Yourself / DRY).
    """

    # ------------------------------------------------------------------
    # Regex yang digunakan bersama oleh beberapa pipeline.
    # ------------------------------------------------------------------
    NUMBER_PATTERN = re.compile(
        r"[^\d.]"
    )

    INTEGER_PATTERN = re.compile(
        r"\d+"
    )

    def open_spider(self, spider):
        """
        Digunakan apabila nanti ingin melakukan inisialisasi resource seperti membuka koneksi database, file, dsb.
        """

        spider.logger.info(f"{self.__class__.__name__} started.")

    def close_spider(self, spider):
        """
        Digunakan untuk cleanup resource apabila diperlukan.
        """

        spider.logger.info(f"{self.__class__.__name__} finished.")

    def log_success(self, spider, item):
        """
        Helper untuk mencatat bahwa item berhasil diproses.
        """

        spider.logger.info(
            f"{self.__class__.__name__} passed: "
            f"{getattr(item, 'title', '<unknown>')}"
        )

    def log_exception(self, spider):
        """
        Helper untuk mencetak stack trace lengkap.
        """

        spider.logger.exception(f"Unexpected error in {self.__class__.__name__}")

    # ==============================================================
    # Helper Methods
    # ==============================================================

    def get_value(self, item, field):
        """
        Helper untuk mengambil nilai field item.
        """

        return getattr(
            item,
            field,
            None,
        )

    def set_value(self, item, field, value):
        """
        Helper untuk mengubah nilai field item.
        """

        setattr(
            item,
            field,
            value,
        )