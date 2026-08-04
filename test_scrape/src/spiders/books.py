import datetime
import platform
import socket
import uuid

from pathlib import Path

import scrapy

from src.selectors.manager import SelectorManager


# ==========================================================
# Scrapy Workspace
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]


class BooksSpider(scrapy.Spider):
    """
    Spider untuk melakukan crawling website Books to Scrape.
    """

    name = "books"

    allowed_domains = [
        "books.toscrape.com",
    ]

    target_url = (
        "https://books.toscrape.com/"
    )

    custom_settings = {

        # ==================================================
        # Scheduler
        # ==================================================

        # Menggunakan priority queue bawaan Scrapy.
        "SCHEDULER_PRIORITY_QUEUE":
            "scrapy.pqueues.ScrapyPriorityQueue",

        # ==================================================
        # Resume Crawl
        # ==================================================

        "JOBDIR": str(BASE_DIR / "storage" / "job" / "books"),

        # ==================================================
        # Asset Storage
        # ==================================================

        "IMAGES_STORE": str(BASE_DIR / "storage" / "images" / "books"),

        "FILES_STORE": str(BASE_DIR / "storage" / "images" / "books"),

        # ==================================================
        # HTTP Cache
        # ==================================================

        "HTTPCACHE_DIR": str(BASE_DIR / "storage" / "httpcache" / "books"),

        # ==================================================
        # Export
        # ==================================================

        "EXPORT_DIR": str(BASE_DIR / "storage" / "data"),
        "EXPORT_FORMAT": "json",
    }

    # Manager akan menentukan selector yang digunakan berdasarkan struktur halaman.
    selector_manager = SelectorManager()

    async def start(self):
        """
        Membuat request pertama spider.
        """

        try:

            # Informasi crawl.
            self.start_time = (datetime.datetime.now())
            self.crawl_id = (str(uuid.uuid4()))

            # Statistics Collector
            stats = self.crawler.stats

            stats.set_value(
                "crawl/id",
                self.crawl_id,
            )

            stats.set_value(
                "crawl/spider",
                self.name,
            )

            stats.set_value(
                "crawl/start_time",
                self.start_time.isoformat(),
            )

            stats.inc_value(
                "crawl/start_requests",
            )

            # Logging
            self.logger.info("=" * 40)
            self.logger.info("Spider Started")
            self.logger.info(
                "Spider      : %s",
                self.name,
            )

            self.logger.info(
                "Crawl ID    : %s",
                self.crawl_id,
            )

            self.logger.info(
                "Start Time  : %s",
                self.start_time,
            )

            self.logger.info("=" * 40)

            # Request pertama.
            yield scrapy.Request(
                url=self.target_url,
                callback=self.parse,
            )

        except Exception:

            self.logger.exception(
                "Terjadi kesalahan saat memulai spider."
            )
            raise


    # ==========================================================
    # Metadata
    # ==========================================================

    def fill_metadata(self, item, response: scrapy.http.Response,):
        """
        Mengisi metadata spider dan request.
        """

        try:

            #
            # ==================================================
            # Metadata Spider
            # ==================================================
            #
            item.spider.spider_name = self.name

            item.spider.scrapy_version = (
                scrapy.__version__
            )

            item.spider.python_version = (
                platform.python_version()
            )

            item.spider.hostname = (
                socket.gethostname()
            )

            #
            # ==================================================
            # Metadata Request
            # ==================================================
            #
            item.request.crawl_id = (
                self.crawl_id
            )

            item.request.url = (
                response.url
            )

            item.request.referer = (
                response.request.headers
                .get(
                    b"Referer",
                    b"",
                )
                .decode()
            )

            item.request.status_code = (
                response.status
            )

            item.request.response_time = (
                response.meta.get(
                    "download_latency",
                )
            )

            item.request.depth = (
                response.meta.get(
                    "depth",
                    0,
                )
            )

            return item

        except Exception:

            self.logger.exception(
                "Terjadi kesalahan saat mengisi metadata item."
            )

            raise


    # ==========================================================
    # Parsing Halaman Daftar Buku
    # ==========================================================

    def parse(
        self,
        response: scrapy.http.Response,
    ):
        """
        Melakukan parsing halaman daftar buku.
        """

        stats = self.crawler.stats

        # Statistics Collector
        stats.inc_value(
            "page/parsed",
        )

        stats.inc_value(
            f"http/status/{response.status}",
        )

        stats.max_value(
            "response/max_latency",
            response.meta.get(
                "download_latency",
                0,
            ),
        )

        try:

            self.logger.info(
                "Parsing halaman: %s",
                response.url,
            )

            # Mengambil selector yang sesuai berdasarkan struktur halaman.
            selector = (
                self.selector_manager.get(
                    response,
                )
            )

            # Mengambil seluruh buku pada halaman display.
            books = selector.books(
                response,
            )

            #
            # ==============================================
            # Parsing setiap buku.
            # ==============================================
            #
            for book in books:

                #
                # Mengambil informasi dasar buku.
                #
                item = selector.extract_book(
                    response=response,
                    book_display=book,
                )

                #
                # Menambahkan metadata.
                #
                item = self.fill_metadata(
                    item=item,
                    response=response,
                )

                #
                # Membuka halaman detail buku.
                #
                yield response.follow(
                    url=item.link,
                    callback=self.detail_parse,
                    cb_kwargs={
                        "book_detail": item,
                    },
                )

            #
            # ==============================================
            # Pagination
            # ==============================================
            #
            next_page = selector.next_page(
                response,
            )

            if next_page:

                yield response.follow(
                    url=next_page,
                    callback=self.parse,
                )

        except Exception:

            stats.inc_value(
                "page/error",
            )

            self.logger.exception(
                "Terjadi kesalahan saat parsing halaman."
            )

            raise


    # ==========================================================
    # Parsing Halaman Detail Buku
    # ==========================================================

    def detail_parse(
        self,
        response: scrapy.http.Response,
        book_detail,
    ):
        """
        Melakukan parsing halaman detail buku.
        """

        stats = self.crawler.stats

        #
        # Statistics Collector
        #
        stats.inc_value(
            "detail/parsed",
        )

        try:

            self.logger.info(
                "Parsing detail buku: %s",
                response.url,
            )

            #
            # Mengambil selector yang sesuai.
            #
            selector = self.selector_manager.get(
                response,
            )

            #
            # Memperbarui metadata berdasarkan
            # response halaman detail.
            #
            book_detail = self.fill_metadata(
                item=book_detail,
                response=response,
            )

            #
            # Mengambil informasi detail buku.
            #
            book_detail = selector.extract_detail(
                response=response,
                book_detail=book_detail,
            )

            yield book_detail

        except Exception:

            stats.inc_value(
                "detail/error",
            )

            self.logger.exception(
                "Terjadi kesalahan saat parsing detail buku."
            )

            raise


    # ==========================================================
    # Spider Selesai
    # ==========================================================

    def closed(
        self,
        reason: str,
    ) -> None:
        """
        Dipanggil otomatis ketika Spider selesai.

        Method ini hanya bertanggung jawab mencatat
        informasi akhir proses crawling.

        Pembersihan JOBDIR, HTTP Cache, maupun
        pelaporan statistik dilakukan oleh
        Scrapy Extension.
        """

        try:

            end_time = (
                datetime.datetime.now()
            )

            duration = (
                end_time
                - self.start_time
            )

            stats = self.crawler.stats

            #
            # ==========================================
            # Crawl Statistics
            # ==========================================
            #
            stats.set_value(
                "crawl/end_time",
                end_time.isoformat(),
            )

            stats.set_value(
                "crawl/duration",
                str(duration),
            )

            stats.set_value(
                "crawl/reason",
                reason,
            )

            stats.set_value(
                "crawl/items_scraped",
                stats.get_value(
                    "item_scraped_count",
                    0,
                ),
            )

            stats.set_value(
                "crawl/errors",
                stats.get_value(
                    "log_count/ERROR",
                    0,
                ),
            )

            #
            # ==========================================
            # Logging
            # ==========================================
            #
            self.logger.info("=" * 40)

            self.logger.info(
                "Spider Finished"
            )

            self.logger.info(
                "Spider      : %s",
                self.name,
            )

            self.logger.info(
                "Crawl ID    : %s",
                self.crawl_id,
            )

            self.logger.info(
                "Reason      : %s",
                reason,
            )

            self.logger.info(
                "Start Time  : %s",
                self.start_time,
            )

            self.logger.info(
                "End Time    : %s",
                end_time,
            )

            self.logger.info(
                "Duration    : %s",
                duration,
            )

            self.logger.info("=" * 40)

        except Exception:

            self.logger.exception(
                "Terjadi kesalahan saat menutup Spider."
            )

            raise