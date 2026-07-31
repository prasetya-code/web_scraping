"""
CSV Repository.

Repository backend menggunakan file CSV sebagai media
penyimpanan data.
"""

from __future__ import annotations

import csv
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
)

logger = logging.getLogger(__name__)


class CsvRepository(BaseRepository):
    """
    Repository menggunakan file CSV.

    Seluruh data dimuat ke memori sebagai dictionary
    dengan fingerprint sebagai primary key.

    File CSV hanya digunakan sebagai media persistensi.
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

        self._fieldnames: list[str] = []

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

        self._update_fieldnames(
            item,
        )

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

        self._update_fieldnames(
            item,
        )

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
        Membaca file CSV.
        """

        if not self.path.exists():

            logger.info(
                "CSV storage belum ada. Membuat repository baru."
            )

            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self._data = {}

            self._fieldnames = []

            return

        with self.path.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as fp:

            reader = csv.DictReader(
                fp,
            )

            self._fieldnames = (
                reader.fieldnames
                or []
            )

            for row in reader:

                fingerprint = row[
                    "fingerprint"
                ]

                self._data[
                    fingerprint
                ] = row

    def _flush(
        self,
    ) -> None:
        """
        Menulis seluruh data ke file CSV.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self._fieldnames:

            return

        with self.path.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as fp:

            writer = csv.DictWriter(
                fp,
                fieldnames=self._fieldnames,
            )

            writer.writeheader()

            for row in self._data.values():

                writer.writerow(
                    row,
                )

    def _update_fieldnames(
        self,
        item: Record,
    ) -> None:
        """
        Menjaga agar seluruh kolom CSV tetap konsisten.
        """

        for key in item.keys():

            if key not in self._fieldnames:

                self._fieldnames.append(
                    key,
                )