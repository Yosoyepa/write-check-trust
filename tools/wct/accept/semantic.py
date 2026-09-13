"""Public marker separating observed semantic disagreement from broken tests."""


class SemanticMismatchError(AssertionError):
    """A completed observable assertion disagreed with the supplied oracle."""


SemanticMismatch = SemanticMismatchError


def phase_status(
    phase: str, outcome: str, exception: BaseException | None, *, wasxfail: bool
) -> str:
    """Classify raw exceptions jointly with the final pytest report."""
    if wasxfail or outcome == "skipped":
        return "error"
    if outcome == "passed" and exception is None:
        return "pass"
    return _failure(phase, outcome, exception)


def _failure(phase: str, outcome: str, exception: BaseException | None) -> str:
    if phase == "call" and outcome == "failed" and isinstance(exception, SemanticMismatch):
        return "mismatch"
    return "error"


def scenario_status(phases: dict[str, str]) -> str:
    """Require all three phases; errors dominate semantic mismatches."""
    if phases.keys() != {"setup", "call", "teardown"} or "error" in phases.values():
        return "error"
    return "mismatch" if "mismatch" in phases.values() else "pass"
