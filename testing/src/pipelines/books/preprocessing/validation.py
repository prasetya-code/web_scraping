from .base import BasePipe

from scrapy.exceptions import DropItem

class ValidationPipe(BasePipe):
    """
    - Bertugas memastikan bahwa item memenuhi syarat minimum sebelum diproses oleh pipeline berikutnya.
    - Apabila ditemukan data yang tidak valid maka item akan dihentikan menggunakan DropItem dan stop ke pipeline berikutnya.
    """

    # ------------------------------------------------------------------
    # > Apabila salah satu field tidak ada atau bernilai kosong, maka item akan dianggap tidak valid.
    # > fields harus sama dengan data items
    # ------------------------------------------------------------------
    REQUIRED_FIELDS = (
        "title",
        "price_euro",
        "rating",
        "link",
    )

    # ------------------------------------------------------------------
    # Field yang harus mengandung nilai numerik.
    # Parsing dilakukan pada DataTypePipe.
    # ------------------------------------------------------------------
    FLOAT_FIELDS = (
        "price_euro",
        "excl_tax_euro",
        "incl_tax_euro",
        "tax",
        "reviews",
    )

    INT_FIELDS = (
        "stock",
    )

    def process_item(self, item, spider):

        try:

            # ----------------------------------------------------------
            # Validasi seluruh field wajib
            # ----------------------------------------------------------
            for field in self.REQUIRED_FIELDS:

                self._validate_required(field, self.get_value(
                        item,
                        field,
                    ),
                )

            # ----------------------------------------------------------
            # Validasi numerik (DataTypePipe)
            # ----------------------------------------------------------
            self._validate_numeric(item,)


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

    def _validate_required(self, field, value,):
        """
        Kondisi yang dianggap tidak valid:
        ==================================
        1. Field tidak ada.
        2. Nilai None.
        3. String kosong.
        """

        if value is None:
            raise DropItem(f"Field '{field}' is required.")

        if (isinstance(value, str) and not value):
            raise DropItem(f"Field '{field}' is empty.")

    def _validate_numeric(self, item):
        """
        - Memastikan field hanya numeric (sama dengan data numeric items).
        - Parsing dilakukan pada DataTypePipe.
        """

        for field in self.FLOAT_FIELDS:

            self._validate_float(item, field)

        for field in self.INT_FIELDS:

            self._validate_integer(item, field)

    def _validate_float(self, item, field):
        """
        Memastikan field mengandung nilai numerik
        tanpa mengubah tipe datanya.
        """

        value = self.get_value(item, field)

        if value is None:
            raise DropItem(f"{field} is required.")

        if not isinstance(value, str):
            return

        # Membersihkan semua karakter selain angka (0-9) dan titik (cocok jika tidak ada spasi)
        cleaned = self.NUMBER_PATTERN.sub(
            "",
            value,
        )

        if not cleaned:
            raise DropItem(f"{field} contains no numeric value.")

    def _validate_integer(self, item, field):
        """
        Memastikan field mengandung bilangan bulat
        tanpa mengubah tipe datanya.
        """

        value = self.get_value(item, field)

        if value is None:
            raise DropItem(f"{field} is required.")

        if not isinstance(value, str):
            return

        # Mengambil satu atau lebih angka dari string yang ada
        match = self.INTEGER_PATTERN.search(value)

        if not match:
            raise DropItem(f"{field} contains no numeric value.")