# Must install app postgreSQL dan pip install psycopg[binary]

"""
PostgreSQL Repository.

Repository backend menggunakan PostgreSQL sebagai media
penyimpanan data.

Seluruh item disimpan dalam format JSON agar repository
tetap generic dan tidak bergantung pada struktur item.
"""

from __future__ import annotations

import json
import logging

import psycopg

from psycopg.rows import dict_row

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


class PostgresRepository(BaseRepository):
    """
    PostgreSQL Repository.

    Table:

        records
        ----------------------------
        fingerprint TEXT PRIMARY KEY
        data        JSONB
    """

    TABLE_NAME = "records"

    def __init__(
        self,
        location: str,
    ):

        super().__init__(
            location,
        )

        self.connection: psycopg.Connection | None = None

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def open(
        self,
    ) -> None:

        super().open()

        try:

            self.connection = psycopg.connect(
                self.location,
                row_factory=dict_row,
            )

            self._create_table()

        except Exception as e:

            logger.exception(
                "Failed opening PostgreSQL repository."
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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                SELECT 1
                FROM {self.TABLE_NAME}
                WHERE fingerprint = %s
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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                SELECT data
                FROM {self.TABLE_NAME}
                WHERE fingerprint = %s
                """,

                (
                    fingerprint,
                ),

            )

            row = cursor.fetchone()

            if row is None:

                return None

            return row["data"]

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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                INSERT INTO {self.TABLE_NAME}
                (
                    fingerprint,
                    data
                )
                VALUES
                (
                    %s,
                    %s
                )
                """,

                (
                    fingerprint,
                    json.dumps(
                        item,
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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                UPDATE
                    {self.TABLE_NAME}
                SET
                    data = %s
                WHERE
                    fingerprint = %s
                """,

                (
                    json.dumps(
                        item,
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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                DELETE
                FROM {self.TABLE_NAME}
                WHERE fingerprint = %s
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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                SELECT data
                FROM {self.TABLE_NAME}
                """

            )

            rows = cursor.fetchall()

            return [

                row["data"]

                for row in rows

            ]

    def count(
        self,
    ) -> int:

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                SELECT COUNT(*)
                FROM {self.TABLE_NAME}
                """

            )

            return cursor.fetchone()[
                "count"
            ]

    def clear(
        self,
    ) -> None:

        with self.connection.cursor() as cursor:

            cursor.execute(

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

        with self.connection.cursor() as cursor:

            cursor.execute(

                f"""
                CREATE TABLE IF NOT EXISTS
                {self.TABLE_NAME}
                (

                    fingerprint TEXT PRIMARY KEY,

                    data JSONB NOT NULL

                )
                """

            )

        self.connection.commit()