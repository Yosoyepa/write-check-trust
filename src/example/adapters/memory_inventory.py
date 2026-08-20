from __future__ import annotations

from example.domain import Inventory


class MemoryInventoryRepository:
    """In-memory adapter useful for tests and local execution."""

    def __init__(self, inventories: list[Inventory] | None = None) -> None:
        self._items = {item.product: item for item in inventories or []}

    def get(self, product: str) -> Inventory:
        return self._items[product]

    def save(self, inventory: Inventory) -> None:
        self._items[inventory.product] = inventory
