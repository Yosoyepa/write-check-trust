import pytest

from example.domain import InsufficientStockError, Inventory


def test_reserve_returns_remaining_units() -> None:
    result = Inventory("book", 10).reserve(3)

    assert result == Inventory("book", 7)


@pytest.mark.parametrize("quantity", [0, -1])
def test_reserve_requires_a_positive_quantity(quantity: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        Inventory("book", 10).reserve(quantity)


def test_reserve_rejects_insufficient_stock() -> None:
    with pytest.raises(InsufficientStockError, match="requested 11, available 10"):
        Inventory("book", 10).reserve(11)
