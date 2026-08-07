# ======================
# Concurrency
# ======================

# Jumlah maksimum request yang diproses secara bersamaan oleh seluruh crawler.
# Maksimal X request aktif dalam satu waktu (batas global).
CONCURRENT_REQUESTS = 16

# Batas request paralel ke SATU domain agar tidak membebani server target.
# Hanya X request aktif (batas per website), jika terlalu banyak maka lebih beresiko rate limit dan mudah diblokir.
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Jeda minimum (detik) sebelum mengirim request berikutnya ke domain yang sama.
# Membantu mengurangi beban server dan menghindari rate limit.
DOWNLOAD_DELAY = 1

# ======================
# Retry
# ======================

# Mengaktifkan mekanisme retry otomatis jika request gagal.
RETRY_ENABLED = True

# Jumlah maksimum percobaan ulang.
RETRY_TIMES = 3

# Daftar HTTP status yang akan dicoba kembali.
RETRY_HTTP_CODES = [
    500,
    502,
    503,
    504,
    522,
    524,
    408,
    429,
]

# ======================
# AutoThrottle
# ======================

# Mengaktifkan pengaturan kecepatan crawl secara otomatis berdasarkan respons server.
AUTOTHROTTLE_ENABLED = True

# Delay awal saat spider mulai berjalan.
# Crawl dimulai dengan jeda X detik.
AUTOTHROTTLE_START_DELAY = 5

# Delay maksimum yang boleh diterapkan AutoThrottle.
# Jika server lambat, delay dapat naik hingga X detik.
AUTOTHROTTLE_MAX_DELAY = 60

# Target rata-rata request aktif per server (float).
# ==========================================
# Semakin kecil -> semakin ramah server.
# Semakin besar -> crawling lebih cepat.
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Menampilkan log penyesuaian delay AutoThrottle.
AUTOTHROTTLE_DEBUG = False





DEPTH_LIMIT = 0

DEPTH_PRIORITY = 0

DEPTH_STATS_VERBOSE = False

REFERRER_POLICY = (
    "scrapy.spidermiddlewares.referer.DefaultReferrerPolicy"
)

HTTPERROR_ALLOW_ALL = False

HTTPERROR_ALLOWED_CODES = []