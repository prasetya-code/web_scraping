import hashlib
import logging

logger = logging.getLogger(__name__)


def _hash(value: str | None, algorithm: str) -> str:
    """
    Generate a hexadecimal hash using the specified algorithm.
    """
    try:
        value = value or ""

        hasher = hashlib.new(algorithm)
        hasher.update(value.encode("utf-8"))

        fingerprint = hasher.hexdigest()    # generate string fingerprint

        # print(f"\n{'=' * 30}")
        # logger.debug(f"'{algorithm.upper()}'fingerprint generated successfully.")
        # print(f"{'=' * 30}\n")

        return fingerprint

    except Exception:
        logger.exception(f"Failed to generate '{algorithm.upper()}' fingerprint.")
        raise


def sha256(value: str | None) -> str:
    return _hash(value, "sha256")


def md5(value: str | None) -> str:
    return _hash(value, "md5")