# Scrapy Start Project

gunakan step berikut pada scrapy:
```bash
# membuat workspace scraping
scrapy startproject src "folder name"

# hasil workspace generate
web_scrap/              <- folder project
├── scrapy.cfg
└── src/
    ├── __init__.py
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    └── spiders/
```

* Stepnya **membuat dir kategori di root baru buat workspace**, misal: **news-scraper -> `scrapy startproject src "nama_folder"`**
* Untuk membuat spiders yakni: **`scrapy genspider "nama_spider" "target_url"`**


## Prinsip yang saya gunakan

Saya biasanya mengelompokkan scraper berdasarkan tiga pertanyaan:

- Apakah kagtegori datanya sama?
- Apakah pipeline dan proses penyimpanannya sama?
- Apakah settings, middleware, dan logika scraping sebagian besar bisa digunakan bersama?

```txt
Kalau jawaban untuk ketiganya "ya", maka saya akan menaruhnya dalam satu repository.

Kalau jawabannya "tidak", saya akan membuat repository terpisah.
```


## Rekomendasi penyimpanan hasil scrapping

| Peran                | Penyimpanan                 |
| -------------------- | --------------------------- |
| Belajar Web Scraping | Print → CSV                 |
| Data Analyst         | CSV                         |
| Data Scientist       | CSV → Parquet               |
| Backend Developer    | PostgreSQL / MySQL          |
| Fullstack Developer  | PostgreSQL + JSON API       |
| Data Engineer        | PostgreSQL → Data Warehouse |
| Scraping skala kecil | SQLite                      |
| Scraping skala besar | PostgreSQL/MySQL            |


# Project Structure

berikut project structure penggunaan scrapy:
```bash
bookscraper/

├── spiders/
│
├── extensions/
│   ├── monitoring.py
│   ├── alert.py

│
├── items/
│   ├── name_crawl.py
│   ├── name_item.py
│   └── name_request.py
│
├── selectors/
│   ├── manager.py
│   └── name_ver.py
│
├── pipelines/
│   ├── preprocessing.py
│   │   ├── ValidationPipeline
│   │   ├── CleaningPipeline
│   │   └── NormalizationPipeline
│   │
│   ├── detection.py
│   │   ├── FingerprintPipeline
│   │   ├── DuplicatePipeline
│   │   ├── IncrementalPipeline
│   │   └── ChangeDetectionPipeline
│   │
│   ├── assets.py
│   │   ├── BookImagesPipeline
│   │   └── BookFilesPipeline
│   │
│   ├── transform.py
│   │
│   └── database.py
│
├── middleware/
│   ├── downloader.py
│   ├── spider.py
│   ├── proxy.py
│   ├── retry.py
│   ├── headers.py
│   ├── cookies.py
│   ├── rate_limit.py
│   └── user_agent.py
│
├── utils/
│   ├── clean_cache.py
│   ├── clean_jobdir.py
│   ├── csv_delimit.py
│   └── fingerprint.py
│
├── settings/
│   ├── __init__.py
│   ├── base.py
│   ├── extension.py
│   ├── feed.py
│   ├── middleware.py
│   ├── pipeline.py
│   └── spider.py
│
└── scrapy.cfg
```

berikut flow penggunaan scrapy:
```bash
                        SETTINGS
                            │
                            ▼
                    Scrapy Engine
                            │
                            │
                  Start Request (Spider)
                            │
                            ▼
                Downloader Middleware
       ┌────────────────────────────────────┐
       │ Headers                            │
       │ User-Agent                         │
       │ Cookies                            │
       │ Proxy                              │
       │ Downloader (Logging)               │
       │ Retry (bawaan Scrapy)              │
       └────────────────────────────────────┘
                            │
                            ▼
                     Downloader
                            │
                            ▼
                    Internet / Website
                            │
                            ▼
                        Response
                            │
                            ▼
                Downloader Middleware
                   (arah kembali)
                            │
                            ▼
                  Spider Middleware
                  (biasanya kosong)
                            │
                            ▼
                        Spider
              parse() / parse_detail()
                            │
                            ▼
                        Loader
                (Cleaning awal)
                            │
                            ▼
                         Item
                    (@dataclass)
                            │
                            ▼
                    Item Pipeline
       ┌────────────────────────────────────┐
       │ CleaningPipeline                   │
       │ NormalizationPipeline              │
       │ ValidationPipeline (Pydantic)      │
       │ DuplicatePipeline                  │
       │ DatabasePipeline                   │
       │ ExportPipeline                     │
       └────────────────────────────────────┘
                            │
                            ▼
                    Database / JSON / CSV
```

Scrapy akan menjalankan berdasarkan lifecycle dan konfigurasi di settings.py: 
- terdapat konfigurasi dasar (basic) 
- terdapat konfigurasi priority (no urut running task pada parameter tertentu, semakin kecil akan di run terlebih dahulu)

## Monitoring
Monitoring bisa dengan `stats collectors` dimana biasanya berada pada:
- spider
```py
self.crawler.stats
```

- pipeline
```py
spider.crawler.stats
```

- Extension
```py
crawler.stats
```

- Middleware
```py
spider.crawler.stats
```


### Scrapy Stats Collector Value
Berikut `Core Value dari Stats Collector`:
```py
set_value(key, value)

""" menetapkan (overwrite) suatu nilai statistik, biasanya untuk informasi yang hanya memiliki satu nilai:
1. waktu mulai crawl
2. nama spider
3. versi scraper
4. hostname
5. crawl id
6. job id
7. target website """
```


```py
inc_value(key, count=1, start=0) 

""" menambah suatu counter, biasanya untuk melakukan scraping agar mengetahui scraping sudah melakukan berapa banyak """
```


```py
max_value(key, value) 

""" menyimpan nilai terbesar yang pernah ditemukan, biasanya untuk:
1. waktu response
2. ukuran file / image
3. Jumlah item terbesar """
```


```py
get_stats()

""" mengembalikan seluruh statistik dalam bentuk dictionary """
```


## Spider

Berikut cara membuat spider:
```bash
scrapy genspider "nama spider" "target url tanpa http/https dan www"
```

Saya sarankan membiasakan pola ini:
- Satu spider = satu website/domain.
- Satu callback = satu jenis halaman.


## Items 

Items pada scrapy digunakan sebagai entry poin parameter apa saja yang akan diambil dari suatu website. Berikut contoh penerapan items:
```py
from dataclasses import dataclass
from typing import Optional

@dataclass(
    # Memaksa semua field diisi menggunakan keyword argument
    # agar kode lebih jelas dan mengurangi kesalahan urutan parameter.
    kw_only=True,

    # Menghemat penggunaan memori dan meningkatkan performa
    # dengan membatasi atribut hanya pada field yang didefinisikan.
    slots=True
)
class TestingItem:
    fingerprint: Optional[str] = None
    
    isi_item: Optional[str] = None
```

### Pipeline

```bash
pipelines/
│
├── preprocessing.py
│     ├── ValidationPipeline
│     ├── CleaningPipeline
│     └── NormalizationPipeline
│
├── detection.py
│     ├── FingerprintPipeline
│     ├── DuplicatePipeline
│     ├── IncrementalPipeline
│     └── ChangeDetectionPipeline
│
├── assets.py
│     ├── BookImagesPipeline
│     └── BookFilesPipeline
│
├── transform.py
│
└── database.py
```


### Extensions

```bash
Extensions
    ├── monitoring.py
    └── alerting.py
```

## Midleware (Not final)

Middleware memproses hanya:
- HTTP Request
- HTTP Response

```bash
middlewares/

    __init__.py

    downloader.py

    headers.py

    proxy.py

    cookies.py

    session.py

    playwright.py

    response_validation.py
```

## Utils

Utils pada scrapy hanya bertugas sebagai pelengkap, biasanya untuk cleaning dan format yang dibutuhkan oleh scrapy
```bash
utils/
├── clean_cache.py
├── clean_jobdir.py
├── csv_delimit.py
└── fingerprint.py
```

## Basic Settings

```bash
settings/
│
├── __init__.py
├── base.py          # Setting inti Scrapy
├── spider.py        # Semua konfigurasi crawling
├── middleware.py    # Registrasi & konfigurasi middleware
└── pipeline.py      # Registrasi & konfigurasi pipeline
```

### base.py
```py
BOT_NAME = "x"

SPIDER_MODULES = [
    "src.spiders",
]

NEWSPIDER_MODULE = "src.spiders"

ADDONS = {}

FEED_EXPORT_ENCODING = "utf-8"
```

### spiders.py
```py
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16

CONCURRENT_REQUESTS_PER_DOMAIN = 1

DOWNLOAD_DELAY = 1

AUTOTHROTTLE_ENABLED = True

AUTOTHROTTLE_START_DELAY = 5

AUTOTHROTTLE_MAX_DELAY = 60

AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

AUTOTHROTTLE_DEBUG = False
```

### middleware.py
```py
DOWNLOADER_MIDDLEWARES = {

    # Logging Request/Response
    "test_scrap.middleware.downloader.DownloaderMiddleware":100,

    # Header
    "test_scrap.middleware.headers.HeadersMiddleware":200,

    # User Agent
    "test_scrap.middleware.user_agent.UserAgentMiddleware":300,

    # Cookies
    "test_scrap.middleware.cookies.CookiesMiddleware":400,

    # Proxy
    "test_scrap.middleware.proxy.ProxyMiddleware":500,

}
```

### pipelines.py
```py
ITEM_PIPELINES = {

    # Bersihkan data
    "test_scrap.pipelines.cleaning.CleaningPipeline": 100,

    # Normalisasi
    "test_scrap.pipelines.normalization.NormalizationPipeline": 200,

    # Validasi
    "test_scrap.pipelines.validation.ValidationPipeline": 300,

    # Cek duplikasi
    "test_scrap.pipelines.duplicate.DuplicatePipeline": 400,

    # Download gambar
    "scrapy.pipelines.images.ImagesPipeline": 500,

    # Simpan Database
    "test_scrap.pipelines.database.DatabasePipeline": 600,

    # Export
    "test_scrap.pipelines.export.ExportPipeline": 700,
}
```

# Urutan implementasi pipeline

| Tahap | Fitur                                  | Prioritas         |
| ----- | -------------------------------------- | ----------------- |
| 1     | Data Validation                        | ⭐⭐⭐⭐⭐     |
| 2     | Data Cleaning                          | ⭐⭐⭐⭐⭐     |
| 3     | Anti-Duplicate                         | ⭐⭐⭐⭐⭐     |
| 4     | Change Detection                       | ⭐⭐⭐⭐⭐     |
| 5     | Incremental Scraping                   | ⭐⭐⭐⭐⭐     |
| 6     | Session Management                     | ⭐⭐⭐⭐☆      |
| 7     | Monitoring (Stats Collector)           | ⭐⭐⭐⭐☆      |
| 8     | Alerting                               | ⭐⭐⭐⭐☆      |
| 9     | Metadata Collection                    | ⭐⭐⭐⭐☆      |
| 10    | Selector Versioning                    | ⭐⭐⭐⭐☆      |
| 11    | Crawl Discovery                        | ⭐⭐⭐☆☆       |
| 12    | Prioritization Queue                   | ⭐⭐⭐☆☆       |
| 13    | Headless Browser (`scrapy-playwright`) | ⭐⭐⭐☆☆       |
| 14    | Asset Download                         | ⭐⭐☆☆☆        |
| 15    | ETL Pipeline lengkap                   | ⭐⭐⭐⭐☆      |
| 16    | Distributed Crawling (`scrapy-redis`)  | ⭐⭐☆☆☆        |
