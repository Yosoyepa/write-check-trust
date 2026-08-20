from hypothesis import given, strategies as st

from example.domain import Inventory


@given(
    stock=st.integers(min_value=1, max_value=1_000),
    quantity=st.integers(min_value=1, max_value=1_000),
)
def test_reservation_conserves_units_when_quantity_is_available(stock: int, quantity: int) -> None:
    if quantity <= stock:
        result = Inventory("book", stock).reserve(quantity)

        assert result.units + quantity == stock
