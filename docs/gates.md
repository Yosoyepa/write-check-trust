# Catálogo de gates

Cada gate es un verificador ejecutable con código de salida autoritativo.

> [!NOTE]
> Un gate que crashea retorna exit 2 y **bloquea** (fail-closed): un error
> del harness nunca se interpreta como permiso. Los estados son `PASS`,
> `FAIL`, `SKIP` (desactivado por `policy.yaml`) y `ERROR` (guard crash,
> bloqueante).

La composición exacta de cada tier vive en `tools/wct/gate/runner.py` → `TIERS`;
esta tabla es su espejo documentado.

## Tiers

| Tier | Cuándo corre | Presupuesto | Gates |
|---|---|---:|---:|
| `fast` | feedback en edición y PostToolUse | 10 s | 7 |
| `commit` | pre-commit, Stop y handoff | 120 s | 17 |
| `full` | release, hardener y CI programada | 30 min | 24 |

```bash
uv run wct gate --tier fast    # 7/7
uv run wct gate --tier commit  # 17/17
uv run wct gate --tier full    # 24/24
```

## fast — 7 gates

| Gate | Qué exige | Verificador |
|---|---|---|
| `G-META-2` | toda regla nombra verificadores conocidos | `wct` (análisis de `governance/rules/`) |
| `G-RULES-DRIFT` | copias por proveedor sincronizadas con la fuente | `wct rules check` |
| `G-SUPPRESS` | ratchet de supresiones (`# noqa`, `# type: ignore`…): solo baja | `wct` (conteo contra baseline) |
| `G-DEBT` | TODOs/ponytail con owner e issue | `wct` (escaneo de marcadores) |
| `G-LINT` | cero findings de lint | `ruff check --config governance/lint/ruff.toml .` |
| `G-FMT` | todo el árbol formateado | `ruff format --check` |
| `G-TYPE` | tipado estricto sin errores | `mypy tools/wct src` |

## commit — añade 10

| Gate | Qué exige | Verificador |
|---|---|---|
| `G-META-1` | lock de integridad sin drift en rutas protegidas | `wct integrity check` |
| `G-TEST` | suite unit + integration verde | `pytest -q tests/unit tests/integration` |
| `G-ARCH` | Dependency Rule y contratos de capas | `lint-imports` (import-linter) |
| `G-ARCHMETRICS` | grafo de dependencias sano, métricas A/I/D fuera de zonas, sin ciclos | `wct archmetrics` |
| `G-DEPS` | dependencias declaradas = dependencias usadas | `deptry src tools` |
| `G-DEAD` | sin código muerto | `vulture --min-confidence 80` |
| `G-SAST-BANDIT` | cero findings de seguridad estáticos | `bandit -q -r src` |
| `G-SECRET` | sin secretos nuevos (baseline de solo lectura) | `detect-secrets scan --slim` |
| `G-MUT-SITES` | archivos fuente dentro del presupuesto de sitios de mutación | `wct` (manifiesto diferencial) |
| `G-ACCEPT` | Gherkin parseable, sin repetición estructural | `wct accept parse` |

## full — añade 7

| Gate | Qué exige | Verificador |
|---|---|---|
| `G-COV-TOTAL` | cobertura total ≥ umbral ratchet | `pytest --cov --cov-branch` |
| `G-CRAP` | CRAP ≤ 6 por función | `crap4py --max-crap 6` |
| `G-CC` | complejidad ciclomática ≤ 10 | `xenon --max-absolute B` |
| `G-DRY` | sin duplicación estructural accionable | `wct dry` |
| `G-INTROVERT` | honestidad de tests: aserciones sobre el SUT | `wct introvert` |
| `G-SAST-SEMGREP` | cero findings ERROR de reglas semánticas | `semgrep --config governance/semgrep` |
| `G-AUDIT` | cero CVEs críticos/altos en dependencias desplegables | `pip-audit` (export del lock) |
| `G-SBOM` | SBOM generado | `cyclonedx-py environment` |
| `G-REDTEAM` | el harness resiste a sus 30 adversarios (F1–F15) | `wct selftest redteam` |

## Gates de flujos específicos

Registrados pero fuera de los tiers: los invocan pre-commit, el pipeline de
aceptación o el hardener de forma dirigida.

| Gate | Flujo | Verificador |
|---|---|---|
| `G-COV-DIFF` | cobertura ≥ 90 % sobre líneas nuevas/modificadas | `diff-cover --fail-under=90` |
| `G-MUT` | cero mutantes sobrevivientes en el changeset | `mutmut run` |
| `G-ACCEPT-MUT` | escenarios Gherkin sobreviven mutación | `wct accept mutate` |
| `G-PROP` | property tests (separados, fuera de coverage) | `pytest -q tests/property` |
| `G-TEST-RANDOM` | tests pasan en orden aleatorio | `pytest --randomly-seed=last` |
| `G-DRY-TOK` | duplicación léxica por tokens | `jscpd src tools` |
| `G-DOC` | cobertura de docstrings (ratchet) | `interrogate src` |
| `G-COMMIT-MSG` | conventional commits | `cz check --commit-msg-file` |

## Alias para reglas

Las reglas de `governance/rules/` nombran verificadores con alias que
resuelven al mismo gate subyacente: `G-ARCH-CYCLE` → `G-ARCHMETRICS`,
`G-CVE` → `G-AUDIT`, `G-SAST` → `G-SAST-BANDIT`, `G-TEST-FAST` → `G-TEST`,
`G-TODO` → `G-DEBT`, `G-IMPORT-ORDER` → `G-LINT`, `G-RULES-SYNC` →
`G-RULES-DRIFT`, `G-HOOKS-WIRED` → `wct doctor`.

## Desactivar un gate

Solo vía `governance/policy.yaml` → `gates.disabled` (ruta protegida por el
lock de integridad: requiere [bless humano](runbook.md)). Un gate desactivado
se reporta como `SKIP`, nunca desaparece del output: la omisión es visible.
