import scrapy
import datetime

from pathlib import Path

from src.selectors.manager import SelectorManager


# Scrapy Workspace
BASE_DIR = Path(__file__).resolve().parents[2]


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = "books.toscrape.com"
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

    # Inisialisasi Selector Manager.
    # Manager akan menentukan selector yang sesuai berdasarkan struktur halaman.
    selector_manager = SelectorManager()

    #
    print(f"\n{'=' * 30}")
    print("Scrapy status")
    print(f"{'=' * 30}\n")

    async def start(self):
        # Inisialisasi waktu mulai scraping
        self.start_time = datetime.datetime.now()

        # Collector - Start
        stats = self.crawler.stats
        stats.set_value("crawl/start_time", self.start_time.isoformat())
        stats.inc_value("crawl/start_requests")

        try:
            #
            print(f"\n{'=' * 30}")
            self.logger.info("Spider started")
            self.logger.info(f"Start Time : {self.start_time}")
            print(f"{'=' * 30}\n")

            yield scrapy.Request(
                url=self.target_url,
                callback=self.parse,
            )

        except Exception as e:

            self.logger.error(f"Error saat memulai spider: {e}")

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

            # Iterasi setiap buku
            for book in books:

                # Mengambil data singkat buku
                item = selector.extract_book(
                    response=response,
                    book=book,
                )

                # Masuk ke halaman detail
                yield response.follow(
                    url=item["link"],
                    callback=self.detail_parse,
                    cb_kwargs={
                        "item": item,
                    },
                )

            # Pagination
            next_page = selector.next_page(response)

            if next_page:
                yield response.follow(
                    url=next_page,
                    callback=self.parse,
                )

        except Exception as e:
            #
            stats.inc_value("page/error")

            self.logger.error(f"Error saat parsing: {e}")

    # Books Detail
    def detail_parse(self, response, item):
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

            # Mengambil data detail buku
            item = selector.extract_detail(
                response=response,
                item=item,
            )

            yield item

        except Exception as e:
            #
            stats.inc_value("detail/error")

            self.logger.error(f"Error saat parsing detail: {e}")

    def closed(): 
        pass