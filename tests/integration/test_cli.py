import pytest

from example.entrypoints.cli import main


def test_cli_prints_remaining_stock(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["book", "3", "--stock", "10"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "7\n"


def test_cli_uses_ten_units_as_default_stock(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["book", "3"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "7\n"
