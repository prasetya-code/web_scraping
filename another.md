sebagai scraper harus bisa melakukan hal berikut:
- Change Detection              : Simpan hash atau data lama lalu bandingkan `(menggunakan JSON atau db)`
- Event-driven Scraping         : Trigger dari webhook, cron, message queue `(menggunakan JSON atau db)`
- Incremental Scraping          : Simpan URL/ID terakhir yang sudah diproses `(menggunakan JSON atau db)`

- Pagination Intelligence       : **done** - di spider: `(yield response.follow(posisi button))`
- Prioritization Queue          : **done** - di spider: `(priority=100), per kelipatan 10 yang berada di yield`

- Session Management            : belum diterapkan pada scrapy

- Anti-Duplicate                : **done** - di pipeline: `(schedule default scrapy, item buat manual dengan enkripsi dan diterpakan di spider)`
- Data Validation               : **done** - di pipeline: `(buat manual lalu panggil dari settings.py -> items_pipeline)`
- Data Cleaning                 : **done** - di pipeline: `(buat manual lalu panggil dari settings.py -> items_pipeline)`

- Monitoring                    : **not done** - berada di: `spider, Pipeline, Extension, Middleware` dimana parameter stats collector meliputi: `set_value(key, value), inc_value(key, count=1, start=0), max_value(key, value), get_value(key, default=None), get_stats()`
- Alerting                      : Email, Slack, Telegram -> apa triggernya? `(Spider selesai, Spider gagal, Selector berubah, Website down, Duplicate meningkat, Error tinggi, Success rate rendah)`

- Selector Versioning           : **done** - membuat versi beberapa file yang berada di `selectors`
- Headless Browser Automation   : `scrapy-playwright`
- Asset Download                : **done**: `FilesPipeline` -> untuk file namun bisa gambar, `ImagesPipeline` -> untuk ambil data gambar lebih detail **(perlu install pillow)**
- Distributed Crawling          : `scrapy-redis`, Scrapyd
- Metadata Collection           : Response Metadata

untuk menerapkan hal tersebut minimal data yang ingin di scrape **dijadikan items dulu**, artinya **bukan dalam bentuk dict**

untuk web dinamis yakni scrapy dengan playwright bisa dilihat pada [tutorial](https://www.scrapingbee.com/blog/scrapy-playwright-tutorial/)

untuk web base monitoring bisa dengan [scrapyd](https://www.zenrows.com/blog/scrapyd#endpoints-with-for-crawling-and-monitoring)

untuk latihan bisa mencoba pada [testing](https://www.scrapingcourse.com/)

untuk **json masih layak jika datanya masih di bawah 10.000**, serta:
```bash
100 buku

500 gambar

1000 artikel
```

metadata yang diambil datanya:

## Contoh Metadata

Crawl Metadata:
```txt
crawl_id
scraped_at
job_id
spider_name
scrapy_version
python_version
started_at
finished_at
duration
items_scraped
errors
```

Request Metadata
```text
crawl_id
url
status_code
response_time
referer
depth
hostname