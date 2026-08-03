from pathlib import Path
import csv
import logging

from ..base import BaseExporter

logger = logging.getLogger(__name__)


class CsvExporter(BaseExporter):
    """
    Exporter untuk menyimpan hasil scraping ke dalam format CSV.
    """

    def __init__(self, export_dir):
        """
        Inisialisasi exporter.
        """

        # Mengubah string path menjadi objek Path agar manipulasi file lebih mudah dan bersifat cross-platform.
        self.export_dir = Path(export_dir)

        # Object file CSV.
        self.file = None

        # Object DictWriter.
        self.writer = None

    def open(self, spider):
        """
        Tugas method ini:

            1. Membuat direktori export.
            2. Membuka file CSV.
            3. Menyiapkan resource penulisan.
        """

        # Membuat direktori apabila belum ada.
        self.export_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Nama file mengikuti nama spider.
        file_path = self.export_dir / f"{spider.name}.csv"

        # Membuka file CSV.
        #
        # mode="w"
        #     Membuat file baru atau menimpa file lama.
        #
        # newline=""
        #     Menghindari baris kosong tambahan pada Windows.
        #
        # encoding="utf-8-sig"
        #     Menambahkan BOM agar Microsoft Excel dapat membaca
        #     karakter UTF-8 dengan benar.
        self.file = open(
            file_path,
            mode="w",
            newline="",
            encoding="utf-8-sig",
        )

        logger.info(f"CSV export: {self.file_path}")

    def export_item(self, data):
        """
        data : dict
            Dictionary yang telah diproses oleh ExportPipeline.
        """

        # Header CSV akan mengikuti key pada item pertama.
        if self.writer is None:

            self.writer = csv.DictWriter(

                # File tujuan penulisan.
                self.file,

                # Nama kolom CSV.
                fieldnames=data.keys(),

                # Abaikan field tambahan apabila muncul.
                extrasaction="ignore",

                # Menggunakan titik koma sebagai pemisah kolom.
                delimiter=";",
            )

            # Menulis header CSV.
            self.writer.writeheader()

        # Menulis satu baris data.
        self.writer.writerow(data)

    def close(self):
        """
        Bertugas menutup file sehingga:

            - seluruh buffer tersimpan.
            - resource dilepaskan.
            - file tidak corrupt.
        """

        if self.file:

            self.file.close()

            logger.info(f"CSV export selesai.")