from example.adapters import MemoryInventoryRepository
from example.application import ReserveStock
from example.domain import Inventory


def test_reservation_is_persisted_through_the_port() -> None:
    repository = MemoryInventoryRepository([Inventory("book", 10)])

    result = ReserveStock(repository).execute("book", 3)

    assert result.units == 7
    assert repository.get("book") == result
