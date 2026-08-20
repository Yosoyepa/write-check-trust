from __future__ import annotations

import argparse

from example.adapters import MemoryInventoryRepository
from example.application import ReserveStock
from example.domain import Inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product")
    parser.add_argument("quantity", type=int)
    parser.add_argument("--stock", type=int, default=10)
    args = parser.parse_args(argv)
    repository = MemoryInventoryRepository([Inventory(args.product, args.stock)])
    remaining = ReserveStock(repository).execute(args.product, args.quantity)
    print(remaining.units)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
