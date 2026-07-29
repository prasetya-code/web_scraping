import scrapy
import datetime
import traceback

from pathlib import Path

# Scrapy Workspace
BASE_DIR = Path(__file__).resolve().parents[2]

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    target_urls = ["https://books.toscrape.com/"]

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

    async def start(self):
        # Inisialisasi waktu mulai scraping
        self.start_time = datetime.now()

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

            yield scrapy.Request(url=self.target_url, callback=self.parse,)

        except Exception as e:

            self.logger.error(f"Error saat memulai spider: {e}")
            self.logger.error(traceback.format_exc())
            
    # Main View Data
    def parse(self, response):
        # Collector - Parse
        stats = self.crawler.stats
        stats.inc_value("page/parsed")
        stats.inc_value(f"http/status/{response.status}")
        stats.max_value("response/max_latency", response.meta.get("download_latency", 0))

        try:
            # 
            print(f"\n{'=' * 30}")
            self.logger.info(f"Start parsing: {response.url}")
            print(f"{'=' * 30}\n")

            # Selector

        except Exception as e:
            # 
            stats.inc_value("page/error")

            self.logger.error(e)
            self.logger.error(traceback.format_exc())

    # Detail View Data
    def detail_parse(self, response):
        # Collector - Detail
        stats = self.crawler.stats
        stats.inc_value("detail/parsed")

        try:
            # 
            print(f"\n{'=' * 30}")
            self.logger.info(f"Detailed parsing: {response.url}")
            print(f"{'=' * 30}\n")

            # Selector

        except Exception as e:
            # 
            stats.inc_value("detail/error")

            self.logger.error(e)
            self.logger.error(traceback.format_exc())
        