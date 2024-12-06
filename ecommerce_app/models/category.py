from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: str
    name: str
    description: Optional[str]