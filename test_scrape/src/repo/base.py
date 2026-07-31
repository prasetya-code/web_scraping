from __future__ import annotations

import logging

from abc import (
    ABC,
    abstractmethod,
)

from typing import (
    Any,
    Iterable,
)


logger = logging.getLogger(__name__)

"""
- Bertugas menjadi lapisan abstraksi antara pipeline dengan media penyimpanan (JSON, CSV, SQLite, PostgreSQL, dsb).
- Seluruh backend repository WAJIB mengimplementasikan class ini.
"""
class BaseRepository(ABC):
    """
    - Menyamakan interface seluruh backend.
    - Memudahkan pergantian storage tanpa mengubah pipeline.
    - Mengurangi coupling antara pipeline dan storage.
    """

    def __init__(self, location: str) -> None:
        """
        Parameters
        ----------
        location:
            Lokasi penyimpanan.

            Contoh:

            JSON
                storage/data/books.json

            CSV
                storage/data/books.csv

            SQLite
                storage/data/books.db

            PostgreSQL
                postgresql://user:password@host/database
        """

        self.location = location

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def open(self) -> None:
        """
        Membuka resource apabila diperlukan.

        Contoh:

        - membuka koneksi database
        - membaca file
        """

        logger.info(f"{self.__class__.__name__} opened.")

    def close(self) -> None:
        """
        Menutup resource.
        """

        logger.info(f"{self.__class__.__name__} closed.")

    # ==========================================================
    # CRUD
    # ==========================================================

    @abstractmethod
    def exists(self, fingerprint: str) -> bool:
        """
        Mengecek apakah fingerprint sudah ada.
        """

        raise NotImplementedError

    @abstractmethod
    def get(self, fingerprint: str) -> dict[str, Any] | None:
        """
        Mengambil satu record berdasarkan fingerprint.
        """

        raise NotImplementedError

    @abstractmethod
    def save(self, item: dict[str, Any]) -> None:
        """
        Menyimpan record baru.
        """

        raise NotImplementedError

    @abstractmethod
    def update(self, fingerprint: str, item: dict[str, Any]) -> None:
        """
        Memperbarui record.
        """

        raise NotImplementedError

    @abstractmethod
    def delete(self, fingerprint: str) -> None:
        """
        Menghapus record.
        """

        raise NotImplementedError

    # ==========================================================
    # Query
    # ==========================================================

    @abstractmethod
    def all(self) -> Iterable[dict[str, Any]]:
        """
        Mengambil seluruh record.
        """

        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """
        Menghitung jumlah record.
        """

        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Menghapus seluruh data.
        """

        raise NotImplementedError

    # ==========================================================
    # Utility
    # ==========================================================

    def __len__(self) -> int:

        return self.count()

    def __contains__(self, fingerprint: str) -> bool:

        return self.exists(fingerprint,)

    def __enter__(self) -> "BaseRepository":

        self.open()

        return self

    def __exit__(self, exc_type, exc, traceback) -> None:

        self.close()