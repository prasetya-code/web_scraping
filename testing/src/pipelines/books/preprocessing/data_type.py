from .base import BasePipe

class DataTypePipe(BasePipe):
    """
    - Bertugas mengubah tipe data hasil scraping menjadi tipe Python yang sesuai.
    - Pipeline ini TIDAK melakukan normalisasi nilai.
    """

    # ------------------------------------------------------------------
    # Daftar field yang harus dikonversi menjadi float.
    # ------------------------------------------------------------------
    FLOAT_FIELDS = (
        "price_euro",
        "excl_tax_euro",
        "incl_tax_euro",
        "tax",
    )

    # ------------------------------------------------------------------
    # Daftar field yang harus dikonversi menjadi integer.
    # ------------------------------------------------------------------
    INT_FIELDS = (
        "stock",
        "reviews",
    )

    def process_item(self, item, spider):

        try:

            # ----------------------------------------------------------
            # Konversi seluruh field float.
            # ----------------------------------------------------------
            for field in self.FLOAT_FIELDS:

                self._convert_float(item, field)

            # ----------------------------------------------------------
            # Konversi seluruh field integer.
            # ----------------------------------------------------------
            for field in self.INT_FIELDS:

                self._convert_integer(item, field,)

            self.log_success(spider, item)

            return item

        except Exception:

            self.log_exception(spider)
            raise

    # ==============================================================
    # Helper Methods
    # ==============================================================

    def _convert_float(self, item, field,):
        """
        Mengubah string menjadi float.
        Apabila field tidak ada maka akan dilewati.
        """

        value = self.get_value(item, field)

        if value is None:
            return

        # --------------------------------------------------------------
        # Apabila sebelumnya pipeline lain sudah mengubah menjadi float,
        # maka tidak perlu diproses lagi.
        # --------------------------------------------------------------
        if isinstance(value, float):
            return

        # --------------------------------------------------------------
        # Integer juga dapat langsung diubah menjadi float.
        # --------------------------------------------------------------
        if isinstance(value, int):

            self.set_value(item, field, float(value))
            return

        # --------------------------------------------------------------
        # Hanya mengambil pattern numeric saja.
        # --------------------------------------------------------------
        cleaned = self.NUMBER_PATTERN.sub(
            "",
            str(value),
        )

        # --------------------------------------------------------------
        # Hindari ValueError apabila string kosong.
        # --------------------------------------------------------------
        if not cleaned:
            return

        self.set_value(item, field, float(cleaned))

    def _convert_integer(self, item, field):
        """
        Mengubah string menjadi integer.
        Apabila field tidak ada maka akan dilewati.
        """

        value = self.get_value(item, field)

        if value is None:
            return

        # --------------------------------------------------------------
        # Apabila sebelumnya pipeline lain sudah mengubah menjadi integer,
        # maka tidak perlu diproses lagi.
        # --------------------------------------------------------------
        if isinstance(value, int):
            return

        # --------------------------------------------------------------
        # Float juga dapat langsung diubah menjadi integer.
        # --------------------------------------------------------------
        if isinstance(value, float):

            self.set_value(item, field, int(value))
            return

        # --------------------------------------------------------------
        # Mengambil satu atau lebih angka dari string yang ada.
        # --------------------------------------------------------------
        match = self.INTEGER_PATTERN.search(
            str(value),
        )

        # --------------------------------------------------------------
        # Hindari ValueError apabila string kosong.
        # --------------------------------------------------------------
        if not match:
            return

        self.set_value(item, field, int(match.group()))