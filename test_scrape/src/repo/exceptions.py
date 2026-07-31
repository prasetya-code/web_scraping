"""
Repository Exceptions.

Seluruh exception yang berhubungan dengan repository
didefinisikan pada module ini agar mudah dikelola dan
digunakan oleh seluruh backend.
"""


class RepositoryError(Exception):
    """
    Base exception seluruh repository.

    Seluruh exception repository sebaiknya mewarisi class ini.
    """

    pass


# ==========================================================
# Connection
# ==========================================================

class RepositoryConnectionError(
    RepositoryError,
):
    """
    Terjadi ketika gagal membuka koneksi.

    Contoh:

    - SQLite tidak dapat dibuka.
    - PostgreSQL tidak dapat dihubungi.
    - File JSON tidak dapat diakses.
    """

    pass


class RepositoryClosedError(
    RepositoryError,
):
    """
    Repository sudah ditutup tetapi masih digunakan.
    """

    pass


# ==========================================================
# Record
# ==========================================================

class RecordNotFoundError(
    RepositoryError,
):
    """
    Record dengan fingerprint tertentu tidak ditemukan.
    """

    def __init__(
        self,
        fingerprint: str,
    ):

        super().__init__(
            f"Record '{fingerprint}' not found."
        )

        self.fingerprint = fingerprint


class DuplicateRecordError(
    RepositoryError,
):
    """
    Record dengan fingerprint yang sama sudah ada.
    """

    def __init__(
        self,
        fingerprint: str,
    ):

        super().__init__(
            f"Record '{fingerprint}' already exists."
        )

        self.fingerprint = fingerprint


# ==========================================================
# Validation
# ==========================================================

class InvalidFingerprintError(
    RepositoryError,
):
    """
    Fingerprint tidak valid.
    """

    def __init__(
        self,
        fingerprint,
    ):

        super().__init__(
            f"Invalid fingerprint: {fingerprint}"
        )

        self.fingerprint = fingerprint


class InvalidRecordError(
    RepositoryError,
):
    """
    Record yang diberikan tidak valid.
    """

    pass


# ==========================================================
# Storage
# ==========================================================

class StorageNotFoundError(
    RepositoryError,
):
    """
    File atau database repository tidak ditemukan.
    """

    def __init__(
        self,
        location: str,
    ):

        super().__init__(
            f"Storage not found: {location}"
        )

        self.location = location


class StorageAlreadyExistsError(
    RepositoryError,
):
    """
    Storage sudah ada.
    """

    def __init__(
        self,
        location: str,
    ):

        super().__init__(
            f"Storage already exists: {location}"
        )

        self.location = location


class StoragePermissionError(
    RepositoryError,
):
    """
    Tidak memiliki izin mengakses storage.
    """

    def __init__(
        self,
        location: str,
    ):

        super().__init__(
            f"Permission denied: {location}"
        )

        self.location = location


# ==========================================================
# Backend
# ==========================================================

class UnsupportedBackendError(
    RepositoryError,
):
    """
    Backend repository tidak didukung.
    """

    def __init__(
        self,
        backend: str,
    ):

        super().__init__(
            f"Unsupported backend: {backend}"
        )

        self.backend = backend