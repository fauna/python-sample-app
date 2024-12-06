from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from fauna import fql
from fauna.query import Query


class Status(Enum):
    CART = "cart"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

@dataclass
class OrderItem:
    order_id: str
    product_id: str
    quantity: int

@dataclass
class Order:
    id: str
    status: Status
    createdAt: datetime


def to_order() -> Query:
    return fql("{id: order.id, status: order.status, createdAt: order.createdAt}")