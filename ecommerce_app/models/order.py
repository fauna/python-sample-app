from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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


def order_summary() -> Query:
    return fql("{id: order.id, status: order.status, createdAt: order.createdAt}")

def order_response() -> Query:
    return fql("""
        {
            id: order?.id,
            payment: order?.payment,
            createdAt: order?.createdAt.toString(),
            status: order?.status,
            total: order?.total,
            items: order?.items.toArray().map(item => {
                product: {
                    id: item.product?.id,
                    name: item.product?.name,
                    price: item.product?.price,
                    description: item.product?.description,
                    stock: item.product?.stock,
                    category: {
                        id: item.product?.category?.id,
                        name: item.product?.category?.name,
                        description: item.product?.category?.description
                    }
                },
                quantity: item.quantity
            }),
            customer: {
                id: order?.customer?.id,
                name: order?.customer?.name,
                email: order?.customer?.email,
                address: order?.customer?.address
            }
        }
    """)
