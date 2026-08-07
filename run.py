from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from test_scrape.src.spiders.books import BooksSpider
# from testing.src.spiders.books import BooksSpider

process = CrawlerProcess(get_project_settings())

process.crawl(BooksSpider)
process.start()