from pathlib import Path
import json
import logging

from ..base import BaseExporter

logger = logging.getLogger(__name__)


class JsonExporter(BaseExporter):
    """
    Exporter untuk menyimpan hasil scraping ke dalam format JSON.
    """

    def __init__(self, export_dir):
        """
        Inisialisasi exporter.
        """

        # Mengubah string path menjadi objek Path agar manipulasi file lebih mudah dan bersifat cross-platform.
        self.export_dir = Path(export_dir)

        # Path file JSON.
        self.file_path = None

        # Menampung seluruh item sebelum ditulis ke file.
        self.items = []

    def open(self, spider):
        """
        Tugas method ini:

            1. Membuat direktori export.
            2. Menentukan nama file JSON.
        """

        # Membuat direktori apabila belum ada.
        self.export_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Nama file mengikuti nama spider.
        self.file_path = self.export_dir / f"{spider.name}.json"

        logger.info(f"JSON export: {self.file_path}")

    def export_item(self, data):
        """
        data : dict
            Dictionary yang telah diproses oleh ExportPipeline.
        """

        # Menambahkan item ke dalam list sementara.
        self.items.append(data)

    def close(self):
        """
        Bertugas menulis seluruh item ke dalam file JSON.

        Pengaturan JSON:

            ensure_ascii=False
                Mempertahankan karakter Unicode.

            indent=4
                Membuat format JSON lebih mudah dibaca (pretty print).
        """

        with open(
            self.file_path,
            mode="w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.items,
                file,
                ensure_ascii=False,
                indent=4,
            )

        logger.info(f"JSON export selesai: {self.file_path}")