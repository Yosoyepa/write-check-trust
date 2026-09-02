from __future__ import annotations

from collections.abc import Sequence
import json

from tools.wct.model import GateResult, Status


def text_report(results: Sequence[GateResult], *, quiet: bool = False) -> str:
    if quiet:
        return "\n".join(f"{r.gate_id} {r.status}: {r.summary}" for r in results if r.blocking)
    width = max((len(r.gate_id) for r in results), default=4)
    lines = [f"{'GATE':<{width}}  STATUS  MS      SUMMARY"]
    for result in results:
        lines.append(
            f"{result.gate_id:<{width}}  {result.status:<6}  "
            f"{result.duration_ms:<6}  {result.summary}"
        )
    # model.Status es la fuente de verdad; FAIL/ERROR agrupa los bloqueantes
    # (ADR-A1-03): SKIP no es PASS y no puede fusionarse en el agregado.
    passed = sum(result.status is Status.PASS for result in results)
    skipped = sum(result.status is Status.SKIP for result in results)
    failed = len(results) - passed - skipped
    lines.append(f"\n{len(results)} gates: {passed} PASS · {skipped} SKIP · {failed} FAIL/ERROR")
    return "\n".join(lines)


def json_report(results: Sequence[GateResult]) -> str:
    return json.dumps([result.as_dict() for result in results], indent=2, ensure_ascii=False)
