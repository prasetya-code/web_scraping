import uuid
import socket
import scrapy
import datetime
import platform

from pathlib import Path

from src.selectors.manager import SelectorManager
from src.extensions.clean_cache import CacheCleaner


# Scrapy Workspace
BASE_DIR = Path(__file__).resolve().parents[2]


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    target_url = "https://books.toscrape.com/"

    custom_settings = {
        # Menggunakan priority queue bawaan Scrapy
        "SCHEDULER_PRIORITY_QUEUE": "scrapy.pqueues.ScrapyPriorityQueue",

        # Resume crawl
        "JOBDIR": str(BASE_DIR / "storage" / "job" / "books"),

        # Asset storage
        "IMAGES_STORE": str(BASE_DIR / "storage" / "images" / "books"),
        "FILES_STORE": str(BASE_DIR / "storage" / "files" / "books"),

        # HTTP Cache
        "HTTPCACHE_DIR": str(BASE_DIR / "storage" / "httpcache" / "books"),
    }

    # Manager akan menentukan selector yang sesuai berdasarkan struktur halaman.
    selector_manager = SelectorManager()

    #
    print(f"\n{'=' * 30}")
    print("Scrapy status")
    print(f"{'=' * 30}\n")

    async def start(self):
        # Inisialisasi informasi crawl.
        self.start_time = datetime.datetime.now()
        self.crawl_id = str(uuid.uuid4())

        # Collector - Start
        stats = self.crawler.stats

        stats.set_value("crawl/id", self.crawl_id)
        stats.set_value("crawl/spider", self.name)
        stats.set_value("crawl/start_time", self.start_time.isoformat())

        stats.inc_value("crawl/start_requests")

        try:
            #
            print(f"\n{'=' * 30}")
            self.logger.info("Spider started")
            self.logger.info(f"Crawl ID   : {self.crawl_id}")
            self.logger.info(f"Start Time : {self.start_time}")
            print(f"{'=' * 30}\n")


            self.logger.info("Create first request")

            request = scrapy.Request(
                url=self.target_url,
                callback=self.parse,
            )

            self.logger.info(request)

            yield request

            self.logger.info("Request yielded")


        except Exception:

            self.logger.exception(f"Error saat memulai spider.")

    # METADATA
    def fill_metadata(self, item, response):
        """
        Mengisi metadata spider dan request.

        Selector hanya bertugas mengambil data HTML.
        Metadata diisi oleh spider karena berasal dari proses crawling.
        """

        # ==========================
        # Spider Metadata
        # ==========================

        item.spider.spider_name = self.name

        item.spider.scrapy_version = scrapy.__version__

        item.spider.python_version = (
            platform.python_version()
        )

        item.spider.hostname = (
            socket.gethostname()
        )

        # ==========================
        # Request Metadata
        # ==========================

        item.request.crawl_id = (
            self.crawl_id
        )

        item.request.url = (
            response.url
        )

        item.request.referer = (
            response.request.headers
            .get(b"Referer", b"")
            .decode()
        )

        item.request.status_code = (
            response.status
        )

        item.request.response_time = (
            response.meta.get(
                "download_latency"
            )
        )

        item.request.depth = (
            response.meta.get(
                "depth",
                0,
            )
        )

        return item


    # Books Display
    def parse(self, response):
        # Collector - Parse
        stats = self.crawler.stats

        stats.inc_value("page/parsed")
        stats.inc_value(f"http/status/{response.status}")

        stats.max_value(
            "response/max_latency",
            response.meta.get("download_latency", 0),
        )

        try:
            #
            print(f"\n{'=' * 30}")
            self.logger.info(f"Start parsing: {response.url}")
            print(f"{'=' * 30}\n")

            # Selector
            selector = self.selector_manager.get(response)

            # Mengambil seluruh daftar buku
            books = selector.books(response)

            # ======================================
            # Iterasi setiap buku
            # ======================================
            for book in books:

                # Mengambil data singkat buku
                item = selector.extract_book(
                    response=response,
                    book_display=book,
                )

                # Mengisi metadata item
                item = self.fill_metadata(
                    item=item,
                    response=response,
                )

                # Masuk ke halaman detail
                yield response.follow(
                    url=item.link,
                    callback=self.detail_parse,
                    cb_kwargs={
                        "book_detail": item,
                    },
                )

            # ======================================
            # Pagination
            # ======================================
            next_page = selector.next_page(response)

            if next_page:
                yield response.follow(
                    url=next_page,
                    callback=self.parse,
                )

        except Exception:

            #
            stats.inc_value("page/error")

            self.logger.exception(
                "Error saat parsing halaman."
            )


    # Books Detail
    def detail_parse(self, response, book_detail):
        # Collector - Detail
        stats = self.crawler.stats

        stats.inc_value("detail/parsed")

        try:
            #
            print(f"\n{'=' * 30}")
            self.logger.info(f"Detailed parsing: {response.url}")
            print(f"{'=' * 30}\n")

            # Selector
            selector = self.selector_manager.get(response)

            # Memperbarui metadata berdasarkan response halaman detail
            book_detail = self.fill_metadata(
                item=book_detail,
                response=response,
            )

            # Mengambil data detail buku
            book_detail = selector.extract_detail(
                response=response,
                book_detail=book_detail,
            )

            yield book_detail

        except Exception:

            #
            stats.inc_value("detail/error")

            self.logger.exception(
                "Error saat parsing detail."
            )


    def closed(self, reason):
        """
        Dipanggil otomatis saat spider selesai.
        """

        end_time = datetime.datetime.now()

        duration = end_time - self.start_time

        #
        stats = self.crawler.stats

        # Collector - Crawl
        stats.set_value("crawl/end_time", end_time.isoformat())
        stats.set_value("crawl/duration", str(duration))
        stats.set_value("crawl/reason", reason)

        stats.set_value(
            "crawl/items_scraped",
            stats.get_value("item_scraped_count", 0),
        )

        stats.set_value(
            "crawl/errors",
            stats.get_value("log_count/ERROR", 0),
        )

        #
        self.logger.info(f"{'=' * 30}")
        self.logger.info("Spider Finished")
        self.logger.info(f"Crawl ID   : {self.crawl_id}")
        self.logger.info(f"Reason     : {reason}")
        self.logger.info(f"Start Time : {self.start_time}")
        self.logger.info(f"End Time   : {end_time}")
        self.logger.info(f"Duration   : {duration}")
        self.logger.info(f"{'=' * 30}\n")

        try:

            self.logger.info(
                "Checking expired HTTP cache..."
            )

            cleaner = CacheCleaner(
                settings=self.settings,
            )

            deleted = cleaner.clean()

            self.logger.info(
                "HTTP cache cleanup finished. "
                f"Deleted {deleted} expired file(s)."
            )

            #
            stats.set_value(
                "cache/deleted",
                deleted,
            )

            #
            self.logger.info(f"{'=' * 30}")
            self.logger.info("Scrapy Statistics")
            self.logger.info(f"{'=' * 30}")

            for key, value in sorted(stats.get_stats().items()):

                self.logger.info(
                    f"{key:<35}: {value}"
                )

            self.logger.info(f"{'=' * 30}\n")

        except Exception:

            self.logger.exception(
                "Error while cleaning HTTP cache."
            )