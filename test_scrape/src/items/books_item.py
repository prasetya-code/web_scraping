from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True, slots=True)
class BookItem:
    # unique
    fingerprint: Optional[str] = None

    # display
    title: Optional[str] = None
    price_euro: Optional[str] = None
    rating: Optional[str] = None
    link: Optional[str] = None
    image: Optional[str] = None

    # detail
    upc: Optional[str] = None
    product_type: Optional[str] = None
    excl_tax_euro: Optional[str] = None
    incl_tax_euro: Optional[str] = None
    tax: Optional[str] = None
    stock: Optional[str] = None
    reviews: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None