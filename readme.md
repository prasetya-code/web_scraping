# Rekomendasi Set Base(CONCURRENT_REQUESTS_PER_DOMAIN & TARGET_CONCURRENCY) di Scrapy Settings

| Jenis Website        | CONCURRENT_REQUESTS_PER_DOMAIN | TARGET_CONCURRENCY |
| -------------------- | -----------------------------: | -----------------: |
| Website publik       |                            1–2 |                1.0 |
| Website cukup cepat  |                            2–4 |            1.5–2.0 |
| API publik           |                            4–8 |            2.0–4.0 |
| Server milik sendiri |                           8–16 |            4.0–8.0 |


# Format JSON exporters masih bermasalah

# Notes
1. feeder
- csv bisa menggunakan metode bacthing (baik id maupun timestamp) pada saat process feed




2. pipeline tree
```bash
pipelines/
│
├── preprocessing.py
│     ├── ValidationPipeline
│     ├── CleaningPipeline
│     ├── DataTypePipeline
│     ├── NormalizationPipeline
│     └── QualityCheckPipeline
│
├── detection.py
│     ├── DuplicatePipeline
│     ├── IncrementalPipeline
│     ├── ChangeDetectionPipeline
│     └── AnomalyDetectionPipeline
│
├── assets.py
│     ├── BookImagesPipeline
│     └── BookFilesPipeline
│
├── transform.py
│
└── database.py
```

> Urutan implementasi pipeline

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


3. Selector versioning
```bash
Halaman List
      │
      ▼
SelectorManager
      │
      ▼
BooksSelectorV2
      │
      ▼
extract_book()
      │
      ▼
Request Detail
      │
      ▼
Halaman Detail
      │
      ▼
SelectorManager
      │
      ▼
BooksSelectorV1
      │
      ▼
extract_detail()
```

Keuntungannya adalah setiap Response selalu dideteksi berdasarkan HTML yang diterima. Jika suatu saat hanya halaman katalog yang berubah ke V2 sementara halaman detail masih menggunakan struktur V1 (atau sebaliknya), spider tetap akan memilih selector yang tepat tanpa perlu logika tambahan atau meneruskan objek selector antar callback. Ini membuat arsitektur versioning lebih fleksibel dan tahan terhadap perubahan parsial pada website.

4. Metadata
      - Crawl Metadata: menggunakan `stats collector` 
      - Request Metadata: menggunakan `items` -> disatukan dengan items data utama namun beda class
      - Spider Metadata: menggunakan `items` -> disatukan dengan items data utama namun beda class

# Terminal Note
```bash
2026-07-30 11:09:57 [scrapy.middleware] INFO: Enabled downloader middlewares:
['scrapy.downloadermiddlewares.offsite.OffsiteMiddleware',
 'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware',
 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware',
 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware',
 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware',
 'scrapy.downloadermiddlewares.retry.RetryMiddleware',
 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware',
 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware',
 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware',
 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware',
 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware',
 'scrapy.downloadermiddlewares.stats.DownloaderStats',
 'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware']

2026-07-30 11:09:57 [scrapy.middleware] INFO: Enabled spider middlewares:
['scrapy.spidermiddlewares.start.StartSpiderMiddleware',
 'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware',
 'scrapy.spidermiddlewares.referer.RefererMiddleware',
 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware',
 'scrapy.spidermiddlewares.depth.DepthMiddleware']
 
2026-07-30 11:09:57 [scrapy.middleware] INFO: Enabled item pipelines:
[]
```