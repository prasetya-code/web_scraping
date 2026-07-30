from test_scrape.src.items.books_item import BookItem
from src.utils.fingerprint import sha256


class BaseBooksSelector:
    """
    Kelas dasar (base class) untuk seluruh versi selector.

    Seluruh selector (V1, V2, V3, dst.) harus mewarisi class ini agar
    memiliki struktur method yang sama.
    """

    # Nomor versi selector.
    # Akan dioverride pada masing-masing versi selector.
    VERSION = 0

    def match(self, response):
        """
        Mengecek apakah struktur halaman cocok dengan selector ini.
        """
        raise NotImplementedError

    def books(self, response):
        """
        Mengambil seluruh daftar buku pada halaman katalog.
        """
        raise NotImplementedError

    def next_page(self, response):
        """
        Mengambil URL halaman berikutnya (pagination).
        """
        raise NotImplementedError

    def extract_book(self, response, book):
        """
        Mengambil data display dari setiap buku pada halaman katalog.
        """
        raise NotImplementedError

    def extract_detail(self, response, item):
        """
        Melengkapi data buku dari halaman detail.
        """
        raise NotImplementedError


class BooksSelectorV1(BaseBooksSelector):
    """
    Selector untuk struktur website BooksToScrape versi 1.
    """

    VERSION = 1

    def match(self, response):
        """
        Mengecek apakah halaman masih menggunakan struktur V1.

        Jika XPath berikut ditemukan,
        berarti selector V1 dapat digunakan.
        """
        return bool(
            response.xpath('//article[@class="product_pod"]')
        )

    def books(self, response):
        """
        Mengambil seluruh elemen buku pada halaman katalog.
        """
        return response.xpath(
            '//article[@class="product_pod"]'
        )

    def next_page(self, response):
        """
        Mengambil URL halaman berikutnya.
        """
        return response.xpath(
            '//li[@class="next"]/a/@href'
        ).get()

    def extract_book(self, response, book_display):
        """
        Mengambil informasi singkat setiap buku.
        """

        # Mengubah URL relatif menjadi URL absolut.
        link_detail = response.urljoin(
            book_display.xpath(".//h3/a/@href").get()
        )

        return BookItem(

            # Fingerprint digunakan sebagai identitas unik buku.
            fingerprint=sha256(link_detail),

            # Judul buku.
            title=book_display.xpath(
                ".//h3/a/@title"
            ).get(),

            # Harga buku.
            price_euro=book_display.xpath(
                "normalize-space(.//p[@class='price_color'])"
            ).get(),

            # Rating buku (One, Two, Three, Four, Five).
            rating=book_display.xpath(
                "substring-after(.//p[contains(@class,'star-rating')]/@class,'star-rating ')"
            ).get(),

            # URL detail buku.
            link=link_detail,

            # URL gambar buku.
            image=response.urljoin(
                book_display.xpath(".//img/@src").get()
            ),
        )

    def extract_detail(self, response, book_detail):
        """
        Melengkapi informasi buku dari halaman detail.
        """

        book_detail.upc = response.xpath(
            'normalize-space(//table//tr[th="UPC"]/td)'
        ).get()

        book_detail.category = response.xpath(
            'normalize-space(//ul[contains(@class,"breadcrumb")]/li[3]/a)'
        ).get()

        book_detail.product_type = response.xpath(
            'normalize-space(//table//tr[th="Product Type"]/td)'
        ).get()

        book_detail.price_excl_tax = response.xpath(
            'normalize-space(//table//tr[th="Price (excl. tax)"]/td)'
        ).get()

        book_detail.price_incl_tax = response.xpath(
            'normalize-space(//table//tr[th="Price (incl. tax)"]/td)'
        ).get()

        book_detail.tax = response.xpath(
            'normalize-space(//table//tr[th="Tax"]/td)'
        ).get()

        book_detail.stock = response.xpath(
            'normalize-space(//table//tr[th="Availability"]/td)'
        ).get()

        book_detail.reviews = response.xpath(
            'normalize-space(//table//tr[th="Number of reviews"]/td)'
        ).get()

        book_detail.description = response.xpath(
            'normalize-space(//div[@id="product_description"]/following-sibling::p[1])'
        ).get()

        return book_detail


class BooksSelectorV2(BaseBooksSelector):
    """
    Selector untuk struktur website versi 2.

    Class ini masih berupa placeholder dan akan diisi ketika
    struktur website berubah.
    """

    VERSION = 2

    def match(self, response):
        """
        Mengecek apakah halaman menggunakan struktur V2.

        Untuk sementara selalu False karena selector belum dibuat.
        """
        return False

    def books(self, response):
        raise NotImplementedError

    def next_page(self, response):
        raise NotImplementedError

    def extract_book(self, response, book):
        raise NotImplementedError

    def extract_detail(self, response, item):
        raise NotImplementedError