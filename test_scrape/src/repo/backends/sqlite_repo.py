"""
SQLite Repository.

Repository backend menggunakan SQLite sebagai media
penyimpanan data.

Seluruh item disimpan dalam format JSON agar repository
tetap generic dan tidak bergantung pada struktur item.
"""

from __future__ import annotations

import json
import sqlite3
import logging

from src.repo.base import BaseRepository

from src.repo.types import (
    Fingerprint,
    Record,
    Records,
)

from src.repo.exceptions import (
    DuplicateRecordError,
    RecordNotFoundError,
    RepositoryConnectionError,
)

logger = logging.getLogger(__name__)


class SQLiteRepository(BaseRepository):
    """
    SQLite Repository.

    Table:

        records
        -------------------------
        fingerprint TEXT PRIMARY KEY
        data        TEXT
    """

    TABLE_NAME = "records"

    def __init__(
        self,
        location: str,
    ):

        super().__init__(
            location,
        )

        self.connection: sqlite3.Connection | None = None

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def open(
        self,
    ) -> None:

        super().open()

        try:

            self.connection = sqlite3.connect(
                self.location,
            )

            self.connection.row_factory = (
                sqlite3.Row
            )

            self._create_table()

        except sqlite3.Error as e:

            logger.exception(
                "Failed opening SQLite repository."
            )

            raise RepositoryConnectionError(
                str(e),
            )

    def close(
        self,
    ) -> None:

        if self.connection is not None:

            self.connection.close()

            self.connection = None

        super().close()

    # ==========================================================
    # CRUD
    # ==========================================================

    def exists(
        self,
        fingerprint: Fingerprint,
    ) -> bool:

        cursor = self.connection.execute(

            f"""
            SELECT 1
            FROM {self.TABLE_NAME}
            WHERE fingerprint = ?
            LIMIT 1
            """,

            (
                fingerprint,
            ),

        )

        return cursor.fetchone() is not None

    def get(
        self,
        fingerprint: Fingerprint,
    ) -> Record | None:

        cursor = self.connection.execute(

            f"""
            SELECT data
            FROM {self.TABLE_NAME}
            WHERE fingerprint = ?
            """,

            (
                fingerprint,
            ),

        )

        row = cursor.fetchone()

        if row is None:

            return None

        return json.loads(
            row["data"],
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

        self.connection.execute(

            f"""
            INSERT INTO {self.TABLE_NAME}
            (
                fingerprint,
                data
            )
            VALUES
            (
                ?,
                ?
            )
            """,

            (
                fingerprint,
                json.dumps(
                    item,
                    ensure_ascii=False,
                ),
            ),

        )

        self.connection.commit()

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

        self.connection.execute(

            f"""
            UPDATE
                {self.TABLE_NAME}
            SET
                data = ?
            WHERE
                fingerprint = ?
            """,

            (
                json.dumps(
                    item,
                    ensure_ascii=False,
                ),
                fingerprint,
            ),

        )

        self.connection.commit()

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

        self.connection.execute(

            f"""
            DELETE
            FROM {self.TABLE_NAME}
            WHERE fingerprint = ?
            """,

            (
                fingerprint,
            ),

        )

        self.connection.commit()

    # ==========================================================
    # Query
    # ==========================================================

    def all(
        self,
    ) -> Records:

        cursor = self.connection.execute(

            f"""
            SELECT data
            FROM {self.TABLE_NAME}
            """

        )

        return [

            json.loads(
                row["data"],
            )

            for row in cursor.fetchall()

        ]

    def count(
        self,
    ) -> int:

        cursor = self.connection.execute(

            f"""
            SELECT COUNT(*)
            FROM {self.TABLE_NAME}
            """

        )

        return cursor.fetchone()[0]

    def clear(
        self,
    ) -> None:

        self.connection.execute(

            f"""
            DELETE
            FROM {self.TABLE_NAME}
            """

        )

        self.connection.commit()

    # ==========================================================
    # Private
    # ==========================================================

    def _create_table(
        self,
    ) -> None:
        """
        Membuat table apabila belum ada.
        """

        self.connection.execute(

            f"""
            CREATE TABLE IF NOT EXISTS
            {self.TABLE_NAME}
            (

                fingerprint TEXT PRIMARY KEY,

                data TEXT NOT NULL

            )
            """

        )

        self.connection.commit()