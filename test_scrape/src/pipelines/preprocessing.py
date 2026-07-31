import re

from dataclasses import fields

from scrapy.exceptions import DropItem


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


class CleaningPipe(BasePipe):
    """
    - Bertugas membersihkan seluruh field string agar tidak memiliki whitespace di awal maupun akhir.
    - Cleaning dilakukan terlebih dahulu karena pipeline setelahnya mengasumsikan data sudah bersih.
    """

    def process_item(self, item, spider):

        try:

            # Menggunakan dataclasses.fields() membuat pipeline ini otomatis bekerja walaupun nanti jumlah field bertambah.
            for field in fields(item):

                value = self.get_value(item, field.name,)

                # Hanya string yang perlu dibersihkan.
                if not isinstance(value, str):
                    continue

                self.set_value(item, field.name, value.strip())

            self.log_success(spider, item)

            return item

        except Exception:

            self.log_exception(spider)
            raise


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