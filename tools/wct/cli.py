from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from tools.wct import __version__
from tools.wct.accept.pipeline import accept_verdict, generate, ir_dry, parse_feature, run_mutations
from tools.wct.adopt import (
    check,
    inspect_repository,
    lock,
    render_check,
    render_inventory,
    render_lock,
    render_sync,
    sync,
)
from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.config import ConfigError, find_root
from tools.wct.doctor.checks import diagnose
from tools.wct.dry.analyzer import analyze as analyze_dry
from tools.wct.dry.tpl import analyze_template
from tools.wct.fmt.engine import run as run_fmt
from tools.wct.gate.runner import TIERS, run_tier
from tools.wct.hooks.guard import dispatch as dispatch_hook
from tools.wct.hotspots.engine import render as render_hotspots, report as hotspot_report
from tools.wct.integrity.engine import bless, review, write_lock
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.lcom.engine import scan as scan_lcom
from tools.wct.mutate.engine import run as run_mutation, scan as scan_mutation, update_manifest
from tools.wct.ratchet.measure import check as check_ratchets, record as record_ratchets
from tools.wct.report.overview import overview
from tools.wct.report.render import json_report, text_report
from tools.wct.rules.engine import build as build_rules, drift as rule_drift
from tools.wct.selftest.redteam import run as run_redteam
from tools.wct.splitplan.engine import plan as plan_split, render as render_split
from tools.wct.webhook import send_from_environment

_MIN_NORMALIZE_TOKENS = 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="wct", description="Write, Check, Trust hardening harness")
    root.add_argument("--version", action="version", version=f"wct {__version__}")
    sub = root.add_subparsers(dest="command", required=True)

    gate = sub.add_parser("gate", help="run a quality gate tier")
    gate.add_argument("--tier", choices=sorted(TIERS), default="fast")
    gate.add_argument("--json", action="store_true")
    gate.add_argument("--quiet", action="store_true")

    rules = sub.add_parser("rules", help="build or check provider rule copies")
    rules.add_argument("action", choices=["build", "check"])

    sub.add_parser("doctor", help="diagnose installation and hook wiring")

    integrity = sub.add_parser("integrity", help="protect gate configuration")
    integrity.add_argument("action", choices=["lock", "check", "bless"])
    integrity.add_argument("--reason")
    integrity.add_argument("--approved-by")

    hook = sub.add_parser("hook", help="execute a lifecycle guard")
    hook.add_argument("event")

    arch = sub.add_parser("archmetrics", help="calculate fan-in/out, I, A, D and zones")
    arch.add_argument("--json", action="store_true")

    dry = sub.add_parser("dry", help="find fuzzy structural duplication")
    dry.add_argument("paths", nargs="*")
    dry.add_argument("--json", action="store_true")
    dry.add_argument(
        "--normalized", action="store_true", help="use template normalization (G-DRY-TPL)"
    )

    introvert = sub.add_parser(
        "introvert", help="classify whether test assertions trace to the SUT"
    )
    introvert.add_argument("paths", nargs="*")
    introvert.add_argument("--json", action="store_true")

    mutate = sub.add_parser("mutate", help="differential mutation workflow")
    mutate.add_argument("action", choices=["scan", "run", "update-manifest"])
    mutate.add_argument("--approved-by", help="solo humanos: bendice el lock en el mismo paso")
    mutate.add_argument("--reason", help="cita la aprobación (URL o #N de PR/issue)")

    accept = sub.add_parser("accept", help="Gherkin acceptance pipeline")
    accept.add_argument("action", choices=["parse", "ir-dry", "generate", "run", "mutate"])
    accept.add_argument("feature", nargs="?", default="features/example.feature")
    accept.add_argument("--output", default="tests/acceptance/generated/test_acceptance.py")
    accept.add_argument("--runner", nargs=argparse.REMAINDER)

    fmt = sub.add_parser("fmt", help="format only the changeset (never the whole tree)")
    fmt.add_argument("--staged", action="store_true", help="solo archivos staged")
    fmt.add_argument(
        "--diff-only",
        action="store_true",
        help="changeset completo vs main/master y árbol de trabajo (por defecto)",
    )
    split = sub.add_parser(
        "split-plan", help="propose a facade partition for a mutation-heavy file (TEST-007)"
    )
    split.add_argument("file", help="archivo fuente a planear")
    split.add_argument("--json", action="store_true", help="salida JSON")

    hotspots = sub.add_parser(
        "hotspots", help="churn x complejidad: dónde refactorizar primero (asesor)"
    )
    hotspots.add_argument("--days", type=int, default=90)
    hotspots.add_argument("--top", type=int, default=10)
    hotspots.add_argument("--json", action="store_true", help="salida JSON")

    lcom = sub.add_parser("lcom", help="calculate LCOM4 class cohesion (advisory)")
    lcom.add_argument("--json", action="store_true")

    selftest = sub.add_parser("selftest", help="attack the harness with known-bad inputs")
    selftest.add_argument("suite", choices=["redteam"])

    sub.add_parser("report", help="show rule-to-gate coverage")

    ratchet = sub.add_parser("ratchet", help="check or record measured baselines")
    ratchet.add_argument("action", choices=["check", "record"])
    ratchet.add_argument("--approved-by")
    ratchet.add_argument("--reason")
    ratchet.add_argument("--metric", help="re-registra solo esta métrica (p.ej. coverage-total)")

    adopt = sub.add_parser("adopt", help="inventory repository or manage adopted harness lifecycle")
    adopt.add_argument(
        "--inventory-target",
        default=None,
        metavar="RUTA",
        help="ruta a inventariar (forma flag de `wct adopt <ruta>`)",
    )
    adopt_sub = adopt.add_subparsers(dest="adopt_command")

    lock_p = adopt_sub.add_parser("lock", help="lock vendor paths to an upstream commit")
    lock_p.add_argument("--source", required=True, help="path to local upstream clone")
    lock_p.add_argument("--paths", nargs="+", default=["tools/wct"], help="paths to lock")
    lock_p.add_argument(
        "--force", action="store_true", help="overwrite existing .wct-upstream.json"
    )

    check_p = adopt_sub.add_parser(
        "check", help="check drift, behind changes and conflict candidates"
    )
    check_p.add_argument("--source", required=True, help="path to local upstream clone")
    check_p.add_argument(
        "--ref", default="HEAD", help="upstream ref to compare against (default: HEAD)"
    )
    check_p.add_argument("--json", action="store_true", help="output report as JSON")

    sync_p = adopt_sub.add_parser("sync", help="propose unified patch for upstream changes")
    sync_p.add_argument("--source", required=True, help="path to local upstream clone")
    sync_p.add_argument("--ref", required=True, help="upstream ref to sync against")
    sync_p.add_argument("--out", default="build/tmp/wct-sync.patch", help="patch destination path")
    sync_p.add_argument("--json", action="store_true", help="output report as JSON")

    webhook = sub.add_parser("webhook", help="send a signed, sanitized lifecycle event")
    webhook.add_argument("event")
    webhook.add_argument("--data", default="{}", help="small JSON object; secrets are forbidden")

    return root


def _json_object(raw: str) -> dict[str, object]:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise TypeError("--data debe ser un objeto JSON")
    return value


def normalize_adopt_invocation(argv: list[str]) -> list[str]:
    """Preserva `wct adopt <ruta>` como inventario junto a lock/check/sync.

    argparse no admite un posicional raíz conviviendo con subparsers: el
    primer token siempre se interpreta como subcomando. La normalización
    reescribe la forma posicional histórica a un flag antes de parsear.
    """
    adopt_subcommands = {"lock", "check", "sync"}
    if len(argv) < _MIN_NORMALIZE_TOKENS:
        return argv
    if argv[0] != "adopt" or argv[1] in adopt_subcommands or argv[1].startswith("-"):
        return argv
    return ["adopt", "--inventory-target", *argv[1:]]


def main(argv: list[str] | None = None) -> int:
    tokens = sys.argv[1:] if argv is None else list(argv)
    args = parser().parse_args(normalize_adopt_invocation(tokens))
    try:
        root = find_root()
        if args.command == "gate":
            results = run_tier(root, args.tier)
            print(json_report(results) if args.json else text_report(results, quiet=args.quiet))
            return 1 if any(result.blocking for result in results) else 0
        if args.command == "rules":
            if args.action == "build":
                for path in build_rules(root):
                    print(path.relative_to(root))
                return 0
            differences = rule_drift(root)
            for path in differences:
                print(f"DRIFT {path.relative_to(root)}", file=sys.stderr)
            return bool(differences)
        if args.command == "doctor":
            checks = diagnose(root)
            for ok, message in checks:
                print(f"{'PASS' if ok else 'FAIL'}  {message}")
            return 1 if any(not ok for ok, _ in checks) else 0
        if args.command == "integrity":
            if args.action == "lock":
                print(write_lock(root).relative_to(root))
                return 0
            if args.action == "check":
                problems, warnings = review(root)
                for warning in warnings:
                    print(f"aviso: {warning}")
                print("\n".join(problems))
                return bool(problems)
            if not args.reason or not args.approved_by:
                print("bless requiere --reason y --approved-by", file=sys.stderr)
                return 2
            print(bless(root, args.reason, args.approved_by).relative_to(root))
            return 0
        if args.command == "fmt":
            return run_fmt(root, staged_only=args.staged)
        if args.command == "split-plan":
            report = plan_split(root, root / args.file)
            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(render_split(report))
            return 0 if report["ok"] else 1
        if args.command == "lcom":
            report = scan_lcom(root)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0
        if args.command == "hotspots":
            hotspots = hotspot_report(root, days=args.days, top=args.top)
            if args.json:
                print(json.dumps(hotspots, indent=2, ensure_ascii=False))
            else:
                print(render_hotspots(hotspots))
            return 0
        if args.command == "hook":
            return dispatch_hook(args.event)
        if args.command == "archmetrics":
            report = analyze_architecture(root)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return bool(report["violations"])
        if args.command == "dry":
            paths = [root / path for path in args.paths] if args.paths else None
            if args.normalized:
                report = analyze_template(root, paths)
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return 0
            report = analyze_dry(root, paths)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return bool(
                report["errors"]
                or any(item["ai_actionability"] == "EXTRACT" for item in report["candidates"])
            )
        if args.command == "introvert":
            paths = [root / path for path in args.paths] if args.paths else None
            report = analyze_tests(root, paths)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0
        if args.command == "mutate":
            if args.action == "scan":
                report = scan_mutation(root)
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return bool(report["over_limit"])
            if args.action == "update-manifest":
                print(
                    update_manifest(
                        root,
                        approved_by=args.approved_by or "",
                        reason=args.reason or "",
                    ).relative_to(root)
                )
                return 0
            return run_mutation(root)
        if args.command == "accept":
            feature = root / args.feature
            ir = parse_feature(feature)
            if args.action == "parse":
                print(json.dumps(ir, indent=2, ensure_ascii=False))
                return 0
            if args.action == "ir-dry":
                report = ir_dry(ir)
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return bool(report["count"])
            generated = generate(ir, root / args.output)
            if args.action == "generate":
                print(generated.relative_to(root))
                return 0
            if args.action == "run":
                return subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", str(generated.relative_to(root))],
                    cwd=root,
                    check=False,
                ).returncode
            command = args.runner or [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                str(generated.relative_to(root)),
            ]
            report = run_mutations(ir, command)
            failed, failures = accept_verdict(ir, report)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            for failure in failures:
                print(f"wct: {failure}", file=sys.stderr)
            return 1 if failed else 0
        if args.command == "selftest":
            count, failures = run_redteam(root)
            for failure in failures:
                print(f"FAIL  {failure}")
            print(f"{count - len(failures)}/{count} adversarios rechazados")
            return bool(failures)
        if args.command == "report":
            print(json.dumps(overview(root), indent=2, ensure_ascii=False))
            return 0
        if args.command == "ratchet":
            if args.action == "check":
                failures = check_ratchets(root)
                print("\n".join(failures) if failures else "Todos los ratchets se mantienen.")
                return bool(failures)
            if not args.approved_by or not args.reason:
                print("record requiere --approved-by y --reason", file=sys.stderr)
                return 2
            for path in record_ratchets(root, args.approved_by, args.reason, metric=args.metric):
                print(path.relative_to(root))
            return 0
        if args.command == "adopt":
            if args.adopt_command == "lock":
                report = lock(root, Path(args.source), paths=args.paths, force=args.force)
                print(render_lock(report))
                return 0
            if args.adopt_command == "check":
                check_report = check(root, Path(args.source), ref=args.ref)
                if args.json:
                    print(json.dumps(check_report, indent=2, ensure_ascii=False))
                else:
                    print(render_check(check_report))
                return 0
            if args.adopt_command == "sync":
                out_path = Path(args.out) if args.out else None
                sync_report = sync(root, Path(args.source), ref=args.ref, out=out_path)
                if args.json:
                    print(json.dumps(sync_report, indent=2, ensure_ascii=False))
                else:
                    print(render_sync(sync_report))
                return 0
            inventory_target = (
                Path(args.inventory_target).resolve() if args.inventory_target else root.resolve()
            )
            print(render_inventory(inspect_repository(inventory_target)))
            return 0
        if args.command == "webhook":
            data = _json_object(args.data)
            print(send_from_environment(root, args.event, data))
            return 0
    except (ConfigError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"wct: {exc}", file=sys.stderr)
        return 2
    return 2
