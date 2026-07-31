"""
Repository Factory.

Factory bertugas membuat instance repository sesuai backend
yang dikonfigurasi pada Scrapy Settings.

Pipeline tidak perlu mengetahui backend yang digunakan.
"""

from __future__ import annotations

import logging

from scrapy.settings import Settings

from src.repo.base import BaseRepository

from src.repo.backends.json_repo import (
    JsonRepository,
)

from src.repo.backends.csv_repo import (
    CsvRepository,
)

from src.repo.backends.sqlite_repo import (
    SQLiteRepository,
)

from src.repo.backends.postgres_repo import (
    PostgresRepository,
)

from src.repo.exceptions import (
    UnsupportedBackendError,
)


logger = logging.getLogger(__name__)


class RepositoryFactory:
    """
    Factory untuk membuat repository.

    Contoh:

        repo = RepositoryFactory.create(
            spider.settings,
        )
    """

    DEFAULT_BACKEND = "json"

    @classmethod
    def create(
        cls,
        settings: Settings,
    ) -> BaseRepository:

        backend = settings.get(
            "REPOSITORY_BACKEND",
            cls.DEFAULT_BACKEND,
        )

        location = settings.get(
            "REPOSITORY_LOCATION",
        )

        repository = cls._create_backend(
            backend=backend,
            location=location,
        )

        logger.info(
            "Repository backend: %s",
            backend,
        )

        return repository

    @classmethod
    def _create_backend(
        cls,
        *,
        backend: str,
        location: str,
    ) -> BaseRepository:

        backend = backend.lower()

        if backend == "json":

            return JsonRepository(
                location,
            )

        if backend == "csv":

            return CsvRepository(
                location,
            )

        if backend == "sqlite":

            return SQLiteRepository(
                location,
            )

        if backend in (
            "postgres",
            "postgresql",
        ):

            return PostgresRepository(
                location,
            )

        raise UnsupportedBackendError(
            backend,
        )