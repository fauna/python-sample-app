from dataclasses import dataclass

from fauna import fql
from fauna.query import Query

from ecommerce_app.models.category import Category


@dataclass
class Product:
    id: str
    name: str
    description: str
    price: int
    stock: int
    category: Category


def to_product() -> Query:
    return fql("{id: product.id, name: product.name, description: product.description, stock: product.stock, price: product.price, category: ${category}}",
               category=fql("if (product.category != null) {id: product.category?.id, name: product.category?.name} else null"))
