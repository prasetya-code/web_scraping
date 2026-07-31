"""
JSON Repository.

Repository backend menggunakan file JSON sebagai media
penyimpanan data.
"""

from __future__ import annotations

import json
import logging

from pathlib import Path

from src.repo.base import BaseRepository
from src.repo.types import (
    Fingerprint,
    Record,
    Records,
)

from src.repo.exceptions import (
    DuplicateRecordError,
    RecordNotFoundError,
    StorageNotFoundError,
)

logger = logging.getLogger(__name__)


class JsonRepository(BaseRepository):
    """
    Repository menggunakan file JSON.

    Struktur file:

    {
        "fingerprint": {

            "title": "...",

            "price": ...

        }
    }
    """

    def __init__(
        self,
        location: str,
    ):

        super().__init__(
            location,
        )

        self.path = Path(
            location,
        )

        self._data: dict[
            Fingerprint,
            Record,
        ] = {}

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def open(
        self,
    ) -> None:

        super().open()

        self._load()

    def close(
        self,
    ) -> None:

        self._flush()

        super().close()

    # ==========================================================
    # CRUD
    # ==========================================================

    def exists(
        self,
        fingerprint: Fingerprint,
    ) -> bool:

        return fingerprint in self._data

    def get(
        self,
        fingerprint: Fingerprint,
    ) -> Record | None:

        return self._data.get(
            fingerprint,
        )

    def save(
        self,
        item: Record,
    ) -> None:

        fingerprint = item[
            "fingerprint"
        ]

        if self.exists(
            fingerprint,
        ):
            raise DuplicateRecordError(
                fingerprint,
            )

        self._data[
            fingerprint
        ] = item

    def update(
        self,
        fingerprint: Fingerprint,
        item: Record,
    ) -> None:

        if not self.exists(
            fingerprint,
        ):
            raise RecordNotFoundError(
                fingerprint,
            )

        self._data[
            fingerprint
        ] = item

    def delete(
        self,
        fingerprint: Fingerprint,
    ) -> None:

        if not self.exists(
            fingerprint,
        ):
            raise RecordNotFoundError(
                fingerprint,
            )

        del self._data[
            fingerprint
        ]

    # ==========================================================
    # Query
    # ==========================================================

    def all(
        self,
    ) -> Records:

        return list(
            self._data.values()
        )

    def count(
        self,
    ) -> int:

        return len(
            self._data,
        )

    def clear(
        self,
    ) -> None:

        self._data.clear()

    # ==========================================================
    # Private
    # ==========================================================

    def _load(
        self,
    ) -> None:
        """
        Membaca file JSON.
        """

        if not self.path.exists():

            logger.info(
                "JSON storage belum ada. Membuat repository baru."
            )

            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self._data = {}

            return

        with self.path.open(
            mode="r",
            encoding="utf-8",
        ) as fp:

            self._data = json.load(
                fp,
            )

    def _flush(
        self,
    ) -> None:
        """
        Menulis seluruh data ke file JSON.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            mode="w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                self._data,
                fp,
                indent=4,
                ensure_ascii=False,
            )