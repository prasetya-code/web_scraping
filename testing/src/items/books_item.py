from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True, kw_only=True)
class SpiderMetadata:
    """
    - Metadata yang berkaitan dengan spider.
    - Nilainya hampir selalu sama untuk seluruh item selama satu proses crawling.
    """

    spider_name: Optional[str] = None
    scrapy_version: Optional[str] = None
    hostname: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class RequestMetadata:
    """
    - Metadata yang berasal dari request / response.
    - Nilainya dapat berbeda pada setiap item.
    """

    crawl_id: Optional[str] = None

    url: Optional[str] = None
    referer: Optional[str] = None

    status_code: Optional[int] = None
    response_time: Optional[float] = None

    depth: Optional[int] = None


@dataclass(slots=True, kw_only=True)
class BookItem:
    """
    Data utama hasil scraping buku.
    """

    # ==========================
    # Unique Identifier
    # ==========================

    fingerprint: Optional[str] = None

    # ==========================
    # Display Information
    # ==========================

    title: Optional[str] = None
    price_euro: Optional[str] = None        # must into flot
    rating: Optional[str] = None            # norm into int
    link: Optional[str] = None
    image: Optional[str] = None

    # ==========================
    # Detail Information
    # ==========================

    upc: Optional[str] = None
    product_type: Optional[str] = None
    category: Optional[str] = None

    excl_tax_euro: Optional[str] = None     # must into float
    incl_tax_euro: Optional[str] = None     # must into float

    tax: Optional[str] = None               # must into float
    stock: Optional[str] = None             # must into int
    reviews: Optional[str] = None           # must into int

    description: Optional[str] = None

    # ==========================
    # Metadata
    # ==========================

    spider: SpiderMetadata = field(
        default_factory = SpiderMetadata
    )

    request: RequestMetadata = field(
        default_factory = RequestMetadata
    )