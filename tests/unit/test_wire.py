from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from tools.wct.gate.runner import TIERS
from tools.wct.wire.engine import scan


def test_alias_instantiates_adapter_in_domain_flags_with_resolved_origin(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory(package="example")
    domain_dir = root / "src/example/domain"
    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "service.py").write_text(
        "from example.adapters.persistence.repo import Repo as R\n"
        "\n"
        "def create_repo():\n"
        "    return R()\n",
        encoding="utf-8",
    )

    report = scan(root)

    assert len(report["findings"]) == 1
    finding = report["findings"][0]
    assert finding["file"] == "src/example/domain/service.py"
    assert finding["line"] == 4
    assert finding["symbol"] == "R"
    assert "adapters.persistence.repo" in finding["origin"]


def test_protocol_as_type_without_call_is_clean(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory(package="example")
    domain_dir = root / "src/example/domain"
    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "ports.py").write_text(
        "from typing import Protocol\n"
        "\n"
        "class InventoryPort(Protocol):\n"
        "    def get_stock(self, product_id: str) -> int:\n"
        "        ...\n"
        "\n"
        "def check_availability(port: InventoryPort, product: str) -> bool:\n"
        "    return port.get_stock(product) > 0\n",
        encoding="utf-8",
    )

    report = scan(root)

    assert report["findings"] == []


def test_construction_in_entrypoints_is_clean(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory(package="example")
    entrypoints_dir = root / "src/example/entrypoints"
    entrypoints_dir.mkdir(parents=True, exist_ok=True)
    (entrypoints_dir / "wire.py").write_text(
        "from example.adapters.memory_inventory import MemoryInventory\n"
        "\n"
        "def build_container():\n"
        "    return MemoryInventory()\n",
        encoding="utf-8",
    )

    report = scan(root)

    assert report["findings"] == []


def test_module_level_call_in_domain_is_flagged(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory(package="example")
    domain_dir = root / "src/example/domain"
    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "service.py").write_text(
        "def init_logger():\n    pass\n\ninit_logger()\n",
        encoding="utf-8",
    )

    report = scan(root)

    assert len(report["findings"]) == 1
    finding = report["findings"][0]
    assert finding["file"] == "src/example/domain/service.py"
    assert finding["line"] == 4
    assert finding["symbol"] == "init_logger"
    assert finding["rule"] == "module-level-call"


def test_star_import_in_application_is_flagged(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory(package="example")
    app_dir = root / "src/example/application"
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "service.py").write_text(
        "from example.domain.inventory import *\n",
        encoding="utf-8",
    )

    report = scan(root)

    assert len(report["findings"]) == 1
    finding = report["findings"][0]
    assert finding["file"] == "src/example/application/service.py"
    assert finding["line"] == 1
    assert finding["symbol"] == "*"
    assert finding["rule"] == "star-import"


def test_current_repo_has_zero_wire_flags() -> None:
    report = scan(Path())
    assert report["findings"] == []


def test_wire_gate_is_in_commit_pr_and_full_tiers() -> None:
    assert "G-WIRE" in TIERS["commit"]
    assert "G-WIRE" in TIERS["pr"]
    assert "G-WIRE" in TIERS["full"]
    assert "G-WIRE" not in TIERS["fast"]
