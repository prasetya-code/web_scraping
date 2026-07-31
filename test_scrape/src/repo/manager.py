"""
Repository Manager.

Manager bertugas mengelola lifecycle repository.

Pipeline cukup menggunakan RepositoryManager sehingga
tidak perlu lagi memanggil RepositoryFactory maupun
open()/close() secara langsung.
"""

from __future__ import annotations

import logging

from scrapy.settings import Settings

from src.repo.base import BaseRepository
from src.repo.factory import RepositoryFactory


logger = logging.getLogger(__name__)


class RepositoryManager:
    """
    Singleton Repository Manager.
    """

    _repository: BaseRepository | None = None

    @classmethod
    def get_repository(
        cls,
        settings: Settings,
    ) -> BaseRepository:
        """
        Mengembalikan repository aktif.

        Repository hanya dibuat satu kali.
        """

        if cls._repository is None:

            cls._repository = RepositoryFactory.create(
                settings,
            )

            cls._repository.open()

            logger.info(
                "Repository initialized."
            )

        return cls._repository

    @classmethod
    def close(
        cls,
    ) -> None:
        """
        Menutup repository.
        """

        if cls._repository is None:

            return

        cls._repository.close()

        logger.info(
            "Repository closed."
        )

        cls._repository = None