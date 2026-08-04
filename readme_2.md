# Teknik Menghindari Deteksi (untuk scraping yang wajar, bukan menyerang sistem)

- Rotasi User-Agent dan header lain agar mirip browser asli
- Rotasi proxy/IP (residential proxy biasanya lebih "aman" daripada datacenter proxy yang mudah terdeteksi)
- Rate limiting & delay acak antar request — jangan membombardir server
- Menghormati robots.txt dan Terms of Service situs
- Menangani CAPTCHA — idealnya dengan mendesain scraper agar jarang memicu captcha, bukan bypass otomatis
- Manajemen session/cookies agar terlihat seperti user biasa
- Headless browser detection bypass (banyak situs mendeteksi navigator.webdriver, dsb.) — pelajari teknik stealth plugin seperti playwright-stealth

# Infrastruktur & Skalabilitas

- Queue system (misalnya Redis, RabbitMQ) untuk scraping skala besar
- Database untuk menyimpan hasil (PostgreSQL, MongoDB)
- Containerization (Docker) supaya scraper mudah di-deploy
- Monitoring & logging supaya tahu kalau scraper "patah" karena perubahan struktur situs

# Masing-masing memiliki peran yang berbeda:

- HTTPX untuk komunikasi HTTP tercepat ketika API atau HTML statis sudah cukup.
- CSS & XPath Selector masih dalam satu rumpun dimana yang membeakan pada bagian path -> CSS path mengambil nilai dari css XPath mengambil nilai path
- Playwright untuk menangani situs yang memerlukan browser dan JavaScript.
- BeautifulSoup/lxml untuk mengekstrak data dari HTML secara nyaman dan efisien.
- Scrapy untuk mengelola crawling berskala besar dengan fitur seperti penjadwalan, retry, dan concurrency.

# Bagaimana scraper profesional bekerja?

Biasanya mereka tidak langsung menggunakan Playwright.

Mereka melakukan langkah berikut:
```bash
1. Buka DevTools
2. Cek tab Network
3. Cari API
4. Kalau ada API
      ↓
   HTTPX
5. Kalau tidak ada
      ↓
   Playwright
6. Parsing HTML
      ↓
BeautifulSoup/lxml
```

# Rekomendasi untuk proyek baru

Jika Anda memulai proyek scraping baru pada 2026, kombinasi yang paling saya sarankan adalah:

- Playwright untuk mengambil dan merender halaman, termasuk yang menggunakan JavaScript.
- BeautifulSoup atau lxml (atau selectolax jika mengutamakan performa) untuk parsing HTML.
- HTTPX untuk permintaan HTTP biasa atau kebutuhan async.
- Scrapy jika proyek berkembang menjadi crawler berskala besar dengan ribuan hingga jutaan halaman.

# Praktik terbaik (best practice)

- Prioritaskan API resmi jika tersedia.
- Scrape hanya halaman publik (tanpa login).
- Hormati robots.txt sebagai etika teknis, meskipun secara hukum tidak selalu mengikat.
- Gunakan rate limit (misalnya jeda acak antar permintaan) agar tidak membebani server.
- Jangan bypass CAPTCHA, autentikasi, atau mekanisme anti-bot.
- Jangan scrape data pribadi kecuali Anda memiliki dasar hukum yang sesuai, terutama jika digunakan untuk tujuan komersial.
- Simpan metadata sumber (URL, waktu pengambilan) untuk keperluan audit dan pembaruan data.
- Jangan menjual ulang konten yang dilindungi hak cipta, seperti artikel lengkap, foto, atau karya kreatif.
- Review Terms of Service situs target sebelum scraping dalam skala besar.
- Sediakan mekanisme penghapusan data jika Anda menyimpan data pribadi dan ada permintaan yang sah.

# Tingkat risiko berdasarkan jenis scraping

- 🟢 Rendah: Mengambil data open data pemerintah atau statistik publik.
- 🟢 Rendah–Sedang: Memantau harga produk publik untuk analisis pasar.
- 🟡 Sedang: Mengumpulkan listing marketplace untuk riset internal.
- 🟠 Sedang–Tinggi: Scraping profil publik media sosial atau jaringan profesional untuk produk komersial.
- 🔴 Tinggi: Mengumpulkan email/nomor telepon untuk lead generation atau pemasaran.
- 🔴 Sangat Tinggi: Bypass login, CAPTCHA, autentikasi, atau menjual database hasil scraping yang berisi data pribadi.

# Jika saya mendesain startup scraping di Indonesia

Saya akan menetapkan aturan internal berikut:

- Hanya scrape halaman publik.
- Tidak pernah bypass login, CAPTCHA, atau proteksi teknis.
- Rate limit yang konservatif dan menghormati kapasitas server.
- Menghindari data pribadi kecuali ada dasar hukum yang jelas menurut UU PDP.
- Menggunakan API resmi bila tersedia dan layak.
- Menyimpan log pengambilan data dan dokumentasi tujuan pemrosesan.
- Memiliki prosedur untuk menanggapi permintaan penghapusan data atau keberatan dari pemilik data.

Dengan mengikuti prinsip-prinsip tersebut, risiko hukum akan jauh lebih rendah dibanding model scraping yang mengabaikan pembatasan teknis atau mengumpulkan data pribadi secara massal. Namun, untuk bisnis yang sangat bergantung pada scraping (misalnya agregator data atau platform intelijen pasar), sebaiknya lakukan legal review sebelum produk diluncurkan agar arsitektur teknis dan model bisnis selaras dengan kewajiban hukum yang berlaku di Indonesia.


# Roadmap Belajar Web Scraping Profesional

Tujuan roadmap ini: membawa kamu dari nol sampai bisa membangun scraper yang tangguh, cepat, dan sopan (tidak melanggar aturan situs). Setiap tahap berisi langkah konkret + contoh kode yang bisa langsung dicoba.

Official testing web scrap:
1. [books sample for testing platform](https://books.toscrape.com/)
2. [quotes sample for testing platform](https://quotes.toscrape.com/)
3. [realistic e-commerce testing platform](https://web-scraping.dev/)