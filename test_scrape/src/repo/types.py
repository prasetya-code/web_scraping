from __future__ import annotations

from pathlib import Path

from typing import (
    Any,
    Literal,
    TypedDict,
    TypeAlias,
)


"""
Module ini berisi seluruh type alias yang digunakan oleh
repository agar seluruh backend menggunakan tipe datayang konsisten.
"""

# ==========================================================
# Primitive Types
# ==========================================================

Fingerprint: TypeAlias = str

Record: TypeAlias = dict[str, Any]

Records: TypeAlias = list[Record]

StorageLocation: TypeAlias = str | Path


# ==========================================================
# Backend Types
# ==========================================================

BackendName: TypeAlias = Literal[
    "json",
    "csv",
    "sqlite",
    "postgres",
]


# ==========================================================
# Change Detection
# ==========================================================

ChangeStatus: TypeAlias = Literal[
    "NEW",
    "UPDATED",
    "UNCHANGED",
    "DELETED",
]


IncrementalStatus: TypeAlias = Literal[
    "NEW",
    "EXISTING",
]


# ==========================================================
# Repository Result
# ==========================================================

class RepositoryResult(
    TypedDict,
):
    """
    Hasil operasi repository.
    """

    success: bool

    message: str


class SaveResult(
    RepositoryResult,
):
    """
    Hasil operasi save().
    """

    fingerprint: Fingerprint


class UpdateResult(
    RepositoryResult,
):
    """
    Hasil operasi update().
    """

    fingerprint: Fingerprint


class DeleteResult(
    RepositoryResult,
):
    """
    Hasil operasi delete().
    """

    fingerprint: Fingerprint


# ==========================================================
# Change Detection Result
# ==========================================================

class ChangeResult(
    TypedDict,
):
    """
    Hasil proses change detection.
    """

    fingerprint: Fingerprint

    status: ChangeStatus

    changed_fields: list[str]


# ==========================================================
# Repository Metadata
# ==========================================================

class RepositoryMetadata(
    TypedDict,
):
    """
    Metadata repository.
    """

    backend: BackendName

    location: str

    total_records: int


# ==========================================================
# Snapshot
# ==========================================================

Snapshot: TypeAlias = dict[
    Fingerprint,
    Record,
]