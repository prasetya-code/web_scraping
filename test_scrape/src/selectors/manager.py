import logging

from .books_select import (
    BooksSelectorV1,
    BooksSelectorV2,
)

logger = logging.getLogger(__name__)


class SelectorManager:
    """ 
    - Daftar seluruh selector yang tersedia disimpan sebagai class, bukan object.
    - Daftar ini akan diurutkan berdasarkan VERSION (terbaru -> terlama), hanya satu kali saat modul pertama kali di-load.
    """
    SELECTORS = sorted(
        (
            BooksSelectorV1,
            BooksSelectorV2,
        ),
        key=lambda selector: selector.VERSION,
        reverse=True,
    )

    def get(self, response):
        """
        Mengembalikan selector yang cocok dengan halaman saat ini.
        """

        try:

            # Mencoba setiap selector berdasarkan urutan VERSION.
            for selector_class in self.SELECTORS:

                # Membuat object selector.
                selector = selector_class()

                # Mengecek apakah selector sesuai dengan struktur halaman.
                if selector.match(response):

                    print(f"\n{'=' * 30}")
                    logger.info(f"Menggunakan selector: {selector_class.__name__}")
                    print(f"{'=' * 30}\n")

                    # Mengembalikan object selector yang cocok.
                    return selector

            # Tidak ada selector yang cocok.
            raise LookupError(f"Tidak ditemukan selector yang sesuai.")

        except Exception as e:
            logger.error(f"Gagal menentukan selector: {e}")
            raise