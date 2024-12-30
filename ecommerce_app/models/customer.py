from dataclasses import dataclass
from typing import Optional

from fauna import Document, fql
from fauna.query import Query

from ecommerce_app.models.order import Order


@dataclass
class Address:
    street: str
    city: str
    state: str
    postalCode: str
    country: str


@dataclass
class Customer:
    id: str
    name: str
    email: str
    address: Address
    cart: Optional[Order]


def customer_response() -> Query:
    return fql("{id: customer.id, name: customer?.name, email: customer?.email, address: customer?.address, cart: ${getCart}}",
               getCart=fql('if (customer?.cart != null) {id: customer?.cart?.id} else null'))
