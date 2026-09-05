"""G-MUT tier membership: real mutation joins the full tier (ADR-E-02)."""

from __future__ import annotations

from tools.wct.gate.runner import TIERS


def test_gmut_runs_in_full_tier_after_coverage() -> None:
    """G-MUT lived in no tier (capability profile: tiers []) until ADR-E-02.

    It must run after the suite already proved green — mutation spending
    on a red tree is wasted budget — so it enters after G-COV-TOTAL.
    """
    assert "G-MUT" in TIERS["full"]
    assert TIERS["full"].index("G-COV-TOTAL") < TIERS["full"].index("G-MUT")


def test_gmut_stays_out_of_local_and_ci_tiers() -> None:
    """fast/commit/pr stay lean: CI budget and mutmut cache artifacts (ADR-E-02)."""
    assert "G-MUT" not in TIERS["fast"]
    assert "G-MUT" not in TIERS["commit"]
    assert "G-MUT" not in TIERS["pr"]
