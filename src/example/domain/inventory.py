from __future__ import annotations

from dataclasses import dataclass


class InsufficientStockError(ValueError):
    """Raised when a reservation exceeds available stock."""


@dataclass(frozen=True)
class Inventory:
    """Available units for one product."""

    product: str
    units: int

    def reserve(self, quantity: int) -> Inventory:
        """Return the inventory state after reserving a positive quantity."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if quantity > self.units:
            raise InsufficientStockError(f"requested {quantity}, available {self.units}")
        return Inventory(self.product, self.units - quantity)
