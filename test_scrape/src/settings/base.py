# =========================
# Workspace
# =========================
BOT_NAME = "test scrape"

SPIDER_MODULES = [
    "src.spiders",
]

NEWSPIDER_MODULE = "src.spiders"

ROBOTSTXT_OBEY = False

# =========================
# HTTP Cache
# =========================
HTTPCACHE_ENABLED = True

HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24 * 1

HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503,]

# =========================
# Feed
# =========================

FEED_EXPORT_ENCODING = "utf-8"

FEED_STORE_EMPTY = False        # Generate empty file

FEED_EXPORT_INDENT = 4          # Hanya berpengaruh untuk JSON/XML

FEED_URI_PARAMS = None          # Menggunakan default Scrapy