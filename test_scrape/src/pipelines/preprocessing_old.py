import re

from dataclasses import fields

from scrapy.exceptions import DropItem


class BasePipe:
    """
    Tujuan class ini adalah mengurangi duplikasi kode (Don't Repeat Yourself / DRY).
    """

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

        spider.logger.exception(
            f"Unexpected error in {self.__class__.__name__}"
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

                value = getattr(
                    item,
                    field.name,
                    None,
                )

                # Hanya string yang perlu dibersihkan.
                if isinstance(value, str):

                    setattr(
                        item,
                        field.name,
                        value.strip(),
                    )

            self.log_success(spider, item)

            return item

        except Exception:

            self.log_exception(spider,)
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

    def process_item(self, item, spider):

        try:

            # ----------------------------------------------------------
            # Validasi seluruh field wajib
            # ----------------------------------------------------------
            for field in self.REQUIRED_FIELDS:

                value = getattr(
                    item,
                    field,
                    None,
                )

                self._validate_required(field, value)

            # ----------------------------------------------------------
            # Validasi numerik (TypeConversionPipeline)
            # ----------------------------------------------------------
            self._validate_numeric(item)

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

    def _validate_required(self, field, value):
        """
        Kondisi yang dianggap tidak valid:
        ==================================
        1. Field tidak ada.
        2. Nilai None.
        3. String kosong.
        """

        if value is None:
            raise DropItem(f"Field '{field}' is required.")

        if isinstance(value, str) and not value:
            raise DropItem(f"Field '{field}' is empty.")


    def _validate_numeric(self, item):
        """
        - Memastikan field hanya numeric (sama dengan data numeric items).
        - Parsing dilakukan pada TypeConversionPipeline.
        """

        # price_euro param
        # =================
        price_euro = getattr(
            item,
            "price_euro",
            None,
        )

        if price_euro is None:
            raise DropItem("price_euro is required.")

        if isinstance(price_euro, str):
            # Membersihkan semua karakter selain angka (0-9) dan titik (cocok jika tidak ada spasi)
            cleaned_price_euro = re.sub(
                r"[^\d.]",
                "",
                price_euro,
            )

            if not cleaned_price_euro:
                raise DropItem("price_euro contains no numeric value.")


        # excl_tax_euro param
        # =================
        excl_tax_euro = getattr(
            item,
            "excl_tax_euro",
            None,
        )

        if excl_tax_euro is None:
            raise DropItem("excl_tax_euro is required.")

        if isinstance(excl_tax_euro, str):
            # Membersihkan semua karakter selain angka (0-9) dan titik (cocok jika tidak ada spasi)
            cleaned_excl_tax_euro = re.sub(
                r"[^\d.]",
                "",
                excl_tax_euro,
            )

            if not cleaned_excl_tax_euro:
                raise DropItem("excl_tax_euro contains no numeric value.")


        # incl_tax_euro param
        # =================
        incl_tax_euro = getattr(
            item,
            "incl_tax_euro",
            None,
        )

        if incl_tax_euro is None:
            raise DropItem("incl_tax_euro is required.")

        if isinstance(incl_tax_euro, str):
            # Membersihkan semua karakter selain angka (0-9) dan titik (cocok jika tidak ada spasi)
            cleaned_incl_tax_euro = re.sub(
                r"[^\d.]",
                "",
                incl_tax_euro,
            )

            if not cleaned_incl_tax_euro:
                raise DropItem("incl_tax_euro contains no numeric value.")


        # tax param
        # =================
        tax = getattr(
            item,
            "tax",
            None,
        )

        if tax is None:
            raise DropItem("tax is required.")

        if isinstance(tax, str):
            # Membersihkan semua karakter selain angka (0-9) dan titik (cocok jika tidak ada spasi)
            cleaned_tax = re.sub(
                r"[^\d.]",
                "",
                tax,
            )

            if not cleaned_tax:
                raise DropItem("tax contains no numeric value.")


        # stock param
        # =================
        stock = getattr(
            item,
            "stock",
            None,
        )

        if stock is None:
            raise DropItem(
                "stock is required."
            )

        if isinstance(stock, str):
            # Mengambil satu atau lebih angka dari string yang ada
            match = re.search(
                r"\d+",
                stock,
            )

            if not match:
                raise DropItem(
                    "stock contains no numeric value."
                )

            stock = int(
                match.group()
            )

            setattr(
                item,
                "stock",
                stock,
            )


        # reviews param
        # =================
        reviews = getattr(
            item,
            "reviews",
            None,
        )

        if reviews is None:
            raise DropItem("reviews is required.")

        if isinstance(reviews, str):
            # Membersihkan semua karakter selain angka (0-9) dan titik (cocok jika tidak ada spasi)
            cleaned_reviews = re.sub(
                r"[^\d.]",
                "",
                reviews,
            )

            if not cleaned_reviews:
                raise DropItem("reviews contains no numeric value.")        


    def _validate_change(self, item):
        """
        Validation ini sengaja dipisahkan untuk 
        merubah value str -> num         
        """

        # rating param
        # =================
        rating = getattr(
            item,
            "rating",
            None,
        )

        if rating is None:
            raise DropItem("Rating is required.")


class DataTypePipe(BasePipe):
    """
    - Bertugas mengubah tipe data hasil scraping menjadi tipe Python yang sesuai.
    - Pipeline ini TIDAK melakukan normalisasi nilai.
    """

    # ------------------------------------------------------------------
    # Regex dikompilasi satu kali ketika class dibuat.
    # ------------------------------------------------------------------
    NUMBER_PATTERN = re.compile(
        r"[^\d.]"
    )

    # ------------------------------------------------------------------
    # Daftar field yang harus dikonversi menjadi float.
    # ------------------------------------------------------------------
    FLOAT_FIELDS = (
        "price_euro",
        "excl_tax_euro",
        "incl_tax_euro",
        "tax",
    )

    def process_item(self, item, spider):

        try:

            # ----------------------------------------------------------
            # Konversi seluruh field float.
            # ----------------------------------------------------------
            for field in self.FLOAT_FIELDS:
                self._convert_float(item, field)

            self.log_success(spider, item)

            return item

        except Exception:
            self.log_exception(spider)
            raise

    # ==============================================================
    # Helper Methods
    # ==============================================================

    def _convert_float(self, item, field,
    ):
        """
        Mengubah string menjadi float. Apabila field tidak ada maka akan dilewati.
        """

        value = getattr(
            item,
            field,
            None,
        )

        if value is None:
            return

        # --------------------------------------------------------------
        # Apabila sebelumnya pipeline lain sudah mengubah menjadi float, maka tidak perlu diproses lagi.
        # --------------------------------------------------------------
        if isinstance(value, float):
            return

        # --------------------------------------------------------------
        # Integer juga dapat langsung diubah menjadi float.
        # --------------------------------------------------------------
        if isinstance(value, int):

            setattr(
                item,
                field,
                float(value),
            )

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

        setattr(
            item,
            field,
            float(cleaned),
        )


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

    def _normalize_rating(
        self,
        item,
    ):
        """
        Mengubah rating website menjadi integer.
        """

        rating = getattr(
            item,
            "rating",
            None,
        )

        if rating is None:

            return

        setattr(
            item,
            "rating",
            self.RATING_MAP.get(
                rating,
                0,
            ),
        )


    def _normalize_category(
        self,
        item,
    ):
        """
        Menyeragamkan penulisan kategori.
        """

        category = getattr(
            item,
            "category",
            None,
        )

        if not isinstance(
            category,
            str,
        ):

            return

        setattr(
            item,
            "category",
            category.title(),
        )


class QualityCheckPipe(BasePipe):
    """
    Bertugas melakukan pengecekan kualitas data (business rule validation).
    """

    MIN_RATING = 1
    MAX_RATING = 5

    def process_item(self, item, spider):

        try:

            # rating param
            # =================
            rating = getattr(
                item,
                "rating",
                None,
            )

            if (rating is not None and not (self.MIN_RATING <= rating <= self.MAX_RATING)):
                raise DropItem("Invalid rating.")


            # price_euro param
            # =================
            price_euro = getattr(
                item,
                "price_euro",
                None,
            )

            if (price_euro is not None and price_euro < 0):
                raise DropItem("Negative price_euro.")


            # stock param
            # =================
            stock = getattr(
                item,
                "stock",
                None,
            )

            if (stock is not None and stock < 0):
                raise DropItem("Negative stock.")


            # reviews param
            # =================
            reviews = getattr(
                item,
                "reviews",
                None,
            )

            if (reviews is not None and reviews < 0):
                raise DropItem("Negative reviews.")

            self.log_success(spider, item,)

            return item

        except DropItem as e:

            spider.logger.warning(f"{self.__class__.__name__}: {e}")
            raise

        except Exception:

            self.log_exception(spider)
            raise