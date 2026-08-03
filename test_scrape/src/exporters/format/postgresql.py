# import logging
# from collections.abc import Mapping

# import psycopg

# from ..base import BaseExporter

# logger = logging.getLogger(__name__)


# class PostgreSQLExporter(BaseExporter):
#     """
#     Exporter untuk menyimpan hasil scraping ke database PostgreSQL.

#     Exporter ini mengikuti kontrak BaseExporter sehingga memiliki
#     lifecycle yang sama dengan exporter lainnya.

#         open()
#             │
#             ▼
#         export_item()
#             │
#             ▼
#         close()

#     Pada Part 1 exporter hanya bertugas:

#         - Menyimpan konfigurasi PostgreSQL.
#         - Membuka koneksi database.
#         - Membuat cursor.
#         - Menutup koneksi.

#     Proses berikut akan dibuat pada part selanjutnya:

#         - Flatten nested dataclass.
#         - CREATE TABLE otomatis.
#         - Validasi struktur tabel.
#         - ALTER TABLE otomatis.
#         - INSERT.
#         - Batch insert.
#     """

#     # ==========================================================
#     # PostgreSQL Configuration
#     # ==========================================================

#     #
#     # Seluruh konfigurasi PostgreSQL dipusatkan di sini sehingga
#     # tidak perlu ditulis pada custom_settings spider.
#     #

#     HOST = "localhost"

#     PORT = 5432

#     DATABASE = "books"

#     USER = "postgres"

#     PASSWORD = "123456"

#     SCHEMA = "public"

#     TABLE = "books"

#     #
#     # Jumlah item yang akan diproses dalam sekali transaksi.
#     #
#     # Akan digunakan pada Batch Insert (Part selanjutnya).
#     #
#     BATCH_SIZE = 1000

#     #
#     # False lebih aman karena seluruh transaksi dapat
#     # di-rollback apabila terjadi error.
#     #
#     AUTOCOMMIT = False

#     # ==========================================================

#     def __init__(self):
#         """
#         Inisialisasi exporter.

#         Seluruh konfigurasi dibaca dari class attribute sehingga
#         apabila ingin berpindah server cukup mengubah nilai pada
#         bagian PostgreSQL Configuration.
#         """

#         # Object koneksi PostgreSQL.
#         self.connection = None

#         # Cursor yang digunakan untuk menjalankan SQL.
#         self.cursor = None


#     def _flatten_dict(
#         self,
#         data: dict,
#         parent_key: str = "",
#         separator: str = "_",
#     ) -> dict:
#         """
#         Mengubah dictionary bertingkat (nested dictionary)
#         menjadi dictionary datar (flat dictionary).

#         Contoh
#         -------

#         Input

#         {
#             "title": "Book",

#             "spider": {
#                 "spider_name": "books",
#                 "hostname": "DESKTOP"
#             },

#             "request": {
#                 "url": "...",
#                 "status_code": 200
#             }
#         }

#         Output

#         {
#             "title": "Book",

#             "spider_spider_name": "books",

#             "spider_hostname": "DESKTOP",

#             "request_url": "...",

#             "request_status_code": 200,
#         }

#         Nested dictionary akan dipisahkan menggunakan
#         karakter separator (default "_").
#         """

#         flattened = {}

#         #
#         # Iterasi seluruh pasangan key-value.
#         #
#         for key, value in data.items():

#             #
#             # Membentuk nama key baru.
#             #
#             # Contoh
#             #
#             # parent_key = "spider"
#             # key        = "hostname"
#             #
#             # menjadi
#             #
#             # spider_hostname
#             #
#             new_key = (
#                 f"{parent_key}{separator}{key}"
#                 if parent_key
#                 else key
#             )

#             #
#             # Apabila value masih berupa dictionary,
#             # lakukan flatten secara rekursif.
#             #
#             if isinstance(value, Mapping):

#                 flattened.update(
#                     self._flatten_dict(
#                         value,
#                         new_key,
#                         separator,
#                     )
#                 )

#             #
#             # Apabila value bukan dictionary,
#             # simpan langsung ke dictionary hasil.
#             #
#             else:

#                 flattened[new_key] = value

#         return flattened


#     def open(self, spider):
#         """
#         Dipanggil sekali ketika spider mulai dijalankan.

#         Tugas method ini:

#             1. Membuka koneksi PostgreSQL.
#             2. Mengatur autocommit.
#             3. Membuat cursor.
#             4. Menyiapkan resource database.

#         Method ini BELUM melakukan:

#             - CREATE TABLE
#             - INSERT
#             - VALIDASI
#         """

#         logger.info(
#             "Connecting PostgreSQL %s:%s/%s",
#             self.HOST,
#             self.PORT,
#             self.DATABASE,
#         )

#         try:

#             # Membuka koneksi PostgreSQL.
#             self.connection = psycopg.connect(

#                 host=self.HOST,

#                 port=self.PORT,

#                 dbname=self.DATABASE,

#                 user=self.USER,

#                 password=self.PASSWORD,
#             )

#             # Mengatur mode transaksi.
#             self.connection.autocommit = self.AUTOCOMMIT

#             # Membuat cursor.
#             self.cursor = self.connection.cursor()

#             logger.info(
#                 "PostgreSQL connected successfully."
#             )

#         except Exception:

#             logger.exception(
#                 "Failed connecting PostgreSQL."
#             )

#             raise

#         def export_item(self, data):
#             """
#             Dipanggil setiap kali ExportPipe mengirimkan
#             satu item hasil scraping.

#             Pada Part 2 method ini hanya bertugas
#             melakukan flatten terhadap nested dictionary.

#             Proses INSERT ke PostgreSQL akan
#             diimplementasikan pada Part berikutnya.
#             """

#             #
#             # Mengubah nested dictionary menjadi
#             # dictionary datar.
#             #
#             data = self._flatten_dict(data)

#             logger.debug(
#                 "Flatten item: %s",
#                 data,
#             )

#             #
#             # INSERT akan dibuat pada Part berikutnya.
#             #

#     def close(self):
#         """
#         Dipanggil sekali ketika spider selesai dijalankan.

#         Bertugas:

#             - Commit transaksi.
#             - Menutup cursor.
#             - Menutup koneksi database.
#         """

#         try:

#             #
#             # Commit seluruh transaksi apabila autocommit=False.
#             #
#             if (
#                 self.connection
#                 and
#                 not self.connection.autocommit
#             ):
#                 self.connection.commit()

#         except Exception:

#             #
#             # Rollback apabila commit gagal.
#             #
#             if self.connection:
#                 self.connection.rollback()

#             logger.exception(
#                 "Commit transaction failed."
#             )

#         finally:

#             #
#             # Menutup cursor.
#             #
#             if self.cursor:
#                 self.cursor.close()

#             #
#             # Menutup koneksi PostgreSQL.
#             #
#             if self.connection:
#                 self.connection.close()

#             logger.info(
#                 "PostgreSQL connection closed."
#             )