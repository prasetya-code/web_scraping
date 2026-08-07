import scrapy
import datetime
import uuid
import socket

from pathlib import Path
from ..utils.feeder import build_feed

from src.selectors.manager import SelectorManager

# ==========================================================
# Scrapy Workspace
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    target_url = "https://books.toscrape.com/"

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
    
        "JOBDIR": str(BASE_DIR / "storage" / "job" / "testing"),
    
        # ==================================================
        # Asset Storage
        # ==================================================
    
        "IMAGES_STORE": str(BASE_DIR / "storage" / "images" / "testing"),
    
        "FILES_STORE": str(BASE_DIR / "storage" / "images" / "testing"),
    
        # ==================================================
        # HTTP Cache
        # ==================================================
    
        "HTTPCACHE_DIR": str(BASE_DIR / "storage" / "httpcache" / "testing"),
    
        # ==================================================
        # Feed Param
        # ==================================================
    
        "FEEDER_DIR": str(BASE_DIR / "storage" / "data"/ "testing"),
        "FEEDER_FORMAT": "csv",
        "FEEDER_BATCH_SIZE": 500,

        # ==================================================
        # Database Param
        # ==================================================
        "EXPORT_DATA": "sqlite",
    }

    # Auto Feed (Jika diterapkan maka akan membuat otomatis file)
    custom_settings["FEEDS"] = build_feed(
        export_dir = custom_settings["FEEDER_DIR"],
        spider_name = name,
        export_format = custom_settings["FEEDER_FORMAT"],
        batch_size = custom_settings["FEEDER_BATCH_SIZE"],
    )

    # Seleksi auto selector
    selector_manager = SelectorManager()


    # ==========================================================
    # Start Spider
    # ==========================================================
    async def start(self):

        try:
            # Statistics Collector
            stats = self.crawler.stats

            self.crawl_id = (str(uuid.uuid4()))
            self.start_time = (datetime.datetime.now())
    
            stats.set_value("crawl/id", self.crawl_id)
            stats.set_value("crawl/spider", self.name)
            stats.set_value("crawl/start_time", self.start_time.isoformat())
            stats.inc_value("crawl/start_requests")
    
            # 
            print(f"\n{'=' * 45}")
            self.logger.info("Spider Started")
            print(f"{'=' * 45}\n")
            self.logger.info(f"Spider \t: {self.name}")
            self.logger.info(f"Crawl ID \t: {self.crawl_id}")
            self.logger.info(f"Start Time \t: {self.start_time}")
            print("\n")
    
            # 
            yield scrapy.Request(url=self.target_url, callback=self.parse)
    
        except Exception:
            self.logger.exception("Terjadi kesalahan saat memulai spider.")
            raise


    # ==========================================================
    # Metadata
    # ==========================================================

    def metadata(self, meta_data, response_meta):

        try:

            # Spider Data
            # ==================
            meta_data.spider.spider_name = self.name
            meta_data.spider.scrapy_version = (scrapy.__version__)
            meta_data.spider.hostname = (socket.gethostname())

            # Request Data
            # ==================
            meta_data.request.crawl_id = (self.crawl_id)
            meta_data.request.url = (response_meta.url)
            meta_data.request.referer = (response_meta.request.headers.get(b"Referer", b"",).decode())
            meta_data.request.status_code = (response_meta.status)
            meta_data.request.response_time = (response_meta.meta.get("download_latency"))
            meta_data.request.depth = (response_meta.meta.get("depth", 0))    # Seberapa jauh sebuah halaman dari halaman awal (start request)

            return meta_data

        except Exception:
            self.logger.exception("Terjadi kesalahan saat mengisi metadata.")
            raise


    # ==========================================================
    # Display Data
    # ==========================================================

    def parse(self, response_display):
        
        try:

            # Statistics Collector
            stats = self.crawler.stats
            
            stats.inc_value("page/parsed")
            stats.inc_value(f"http/status/{response_display.status}")
            stats.max_value("response/max_latency", response_display.meta.get("download_latency", 0))

            # 
            self.logger.info("Parsing halaman: {response.url}")
        
            # Selector berdasarkan versi (versi untuk display)
            selector = (self.selector_manager.get(response_display))
        
            books = selector.books(response_display)
        
            # looping scraping
            for book in books:

                # Mengambil informasi dasar buku.
                item = selector.extract_display(response = response_display, book_display = book)
        
                # Menambahkan metadata.
                item = self.metadata(meta_data = item, response_meta = response_display)
        
                # Membuka halaman detail buku.
                yield response_display.follow(
                    url = item.link,
                    callback = self.parse_detail,
                    cb_kwargs = {
                        "book_detail": item,
                    },
                )
        
            #
            # ==============================================
            # Pagination
            # ==============================================
            #
            next_page = selector.next_page(
                response_display,
            )
        
            if next_page:
        
                yield response_display.follow(url = next_page, callback = self.parse,)
        
        except Exception:
            stats.inc_value("page/error",)
        
            self.logger.exception("Terjadi kesalahan saat parsing halaman.")
            raise


    # ==========================================================
    # Detail Data
    # ==========================================================

    def parse_detail(self, response): 
        
        try:

            # 
            stats = self.crawler.stats
            
            stats.inc_value("detail/parsed")

            # 
            self.logger.info(f"Parsing detail buku: {response.url}")
        
            # Selector berdasarkan versi (versi untuk detail)
            selector = self.selector_manager.get(response = response)
        
            #
            # Memperbarui metadata berdasarkan
            # response halaman detail.
            #
            book_detail = self.metadata(
                meta_data=book_detail,
                response_meta=response,
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
    # Closed Spider
    # ==========================================================
    
    def closed(self, reason: str):
    
            try:

                # 
                end_time = (datetime.datetime.now())
                duration = (end_time - self.start_time)
    
                # 
                stats = self.crawler.stats

                stats.set_value("crawl/end_time", end_time.isoformat())
                stats.set_value("crawl/duration", str(duration))
                stats.set_value("crawl/reason", reason,)
                stats.set_value("crawl/items_scraped", stats.get_value("item_scraped_count", 0))
                stats.set_value("crawl/errors", stats.get_value("log_count/ERROR", 0))
    
                #
                print(f"\n{'=' * 45}")
                self.logger.info("Spider Finished")
                print(f"{'=' * 45}\n")
                self.logger.info(f"Spider \t: {self.name}")
                self.logger.info(f"Crawl ID \t: {self.crawl_id}")
                self.logger.info(f"Reason \t: {reason}")
                self.logger.info(f"Start Time \t: {self.start_time}")
                self.logger.info(f"End Time \t: {end_time}")
                self.logger.info(f"Duration \t: {duration}")
                print(f"{'=' * 45}\n")
    
            except Exception:
                self.logger.exception("Terjadi kesalahan saat menutup Spider.")
                raise