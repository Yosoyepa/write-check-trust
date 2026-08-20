from __future__ import annotations

from typing import Protocol

from example.domain import Inventory


class InventoryRepository(Protocol):
    """Port owned by the use case that consumes it."""

    def get(self, product: str) -> Inventory: ...

    def save(self, inventory: Inventory) -> None: ...


class ReserveStock:
    """Reserve units without depending on storage details."""

    def __init__(self, repository: InventoryRepository) -> None:
        self._repository = repository

    def execute(self, product: str, quantity: int) -> Inventory:
        inventory = self._repository.get(product).reserve(quantity)
        self._repository.save(inventory)
        return inventory
