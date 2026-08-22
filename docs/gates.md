# Catálogo de gates

Cada gate es un verificador ejecutable con código de salida autoritativo.

> [!NOTE]
> Un gate que crashea retorna exit 2 y **bloquea** (fail-closed): un error
> del harness nunca se interpreta como permiso. Los estados son `PASS`,
> `FAIL`, `SKIP` (desactivado por `policy.yaml`) y `ERROR` (guard crash,
> bloqueante).

La composición exacta de cada tier vive en `tools/wct/gate/runner.py` → `TIERS`;
esta tabla es su espejo documentado. Un tier con variables de entorno exigidas
(`governance/policy.yaml` → `environment_required`) falla ANTES de correr
gates con un `G-ENV` ERROR que nombra las variables ausentes — nunca como
skips silenciosos.

## Tiers

| Tier | Cuándo corre | Presupuesto | Gates |
|---|---|---:|---:|
| `fast` | feedback en edición y PostToolUse | 10 s | 7 |
| `commit` | pre-commit, Stop y handoff | 120 s | 19 |
| `pr` | espejo local de la CI de PR, antes de pushear | 10 min | 25 |
| `full` | release, hardener y CI programada | 30 min | 29 |

```bash
uv run wct gate --tier fast    # 7/7
uv run wct gate --tier commit  # 19/19
uv run wct gate --tier pr      # 25/25  (o `make pr`)
uv run wct gate --tier full    # 29/29
```

## fast — 7 gates

| Gate | Qué exige | Verificador |
|---|---|---|
| `G-META-2` | toda regla nombra verificadores conocidos | `wct` (análisis de `governance/rules/`) |
| `G-RULES-DRIFT` | copias por proveedor sincronizadas con la fuente | `wct rules check` |
| `G-SUPPRESS` | ratchet de supresiones (`# noqa`, `# type: ignore`… y `per-file-ignores` del perfil ruff): solo baja | `wct` (conteo contra baseline) |
| `G-DEBT` | TODOs/ponytail con owner e issue | `wct` (escaneo de marcadores) |
| `G-LINT` | cero findings de lint | `ruff check --config governance/lint/ruff.toml .` |
| `G-FMT` | todo el árbol formateado | `ruff format --check` |
| `G-TYPE` | tipado estricto sin errores | `mypy tools/wct src` |

## commit — añade 12

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
| `G-SIZE` | archivos ≤ 500 LOC; deuda legada en baseline que solo baja | `wct` (contador LOC por tokenize) |
| `G-COGNITIVE` | complejidad cognitiva ≤ 15 por función en src/ | `wct` (walker AST propio, S3776) |

## pr — añade 6 (espejo local de la CI de PR)

Todo lo que `quality.yml` exige de una pull request, ejecutable con un solo
comando antes de pushear. Nació del piloto (fase 25): una entrega pasó el
tier commit 17/17 y CI la tumbó por diff-coverage que ningún tier local
exponía.

| Gate | Qué exige | Verificador |
|---|---|---|
| `G-HOOKS-WIRED` | instalación y hooks diagnosticados | `wct doctor` |
| `G-COV-TOTAL` | suite completa bajo cobertura, artefacto lcov | `pytest --cov --cov-branch` |
| `G-COV-DIFF` | cobertura ≥ 90 % sobre líneas nuevas/modificadas contra la rama base remota | `diff-cover --compare-branch <base> --fail-under=90 --include-untracked` |
| `G-PROP` | property tests aislados (fuera del conteo de coverage) | `pytest -q tests/property` |
| `G-ACCEPT-MUT` | escenarios Gherkin sobreviven mutación | `wct accept mutate` |
| `G-REDTEAM` | el harness resiste a sus 30 adversarios (F1–F15) | `wct selftest redteam` |

`G-COV-DIFF` es deliberadamente duro: si `diff-cover` falta o no hay rama
base resoluble, reporta ERROR (no SKIP) porque la promesa del tier es
paridad con CI. La base se resuelve en orden `origin/$GITHUB_BASE_REF` →
`origin/main` → `origin/master` → `main` → `master`.

## full — añade 10

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
| `G-DOC` | cobertura de docstrings ≥ piso ratchet (34 %) | `interrogate src --fail-under 34` |
| `G-REDTEAM` | el harness resiste a sus 30 adversarios (F1–F15) | `wct selftest redteam` |

## Gates de flujos específicos

Registrados pero fuera de los tiers: los invoca un flujo concreto o quedan
a la espera de decisión del mantenedor.

| Gate | Flujo | Verificador |
|---|---|---|
| `G-MUT` | manual: `make harden` y skills de mutación | `mutmut run` |
| `G-COMMIT-MSG` | pre-commit (commit-msg hook) | `cz check --commit-msg-file` |
| `G-TEST-RANDOM` | sin flujo automático: exige el plugin `pytest-randomly` (decisión pendiente) | `pytest --randomly-seed=last` |
| `G-DRY-TOK` | sin flujo automático: exige `jscpd` de node (decisión pendiente) | `jscpd src tools --exit-code 1` (presupuesto en `.jscpd.json`) |

## Alias para reglas

Las reglas de `governance/rules/` nombran verificadores con alias que
resuelven al mismo gate subyacente: `G-ARCH-CYCLE` → `G-ARCHMETRICS`,
`G-CVE` → `G-AUDIT`, `G-SAST` → `G-SAST-BANDIT`, `G-TEST-FAST` → `G-TEST`,
`G-TODO` → `G-DEBT`, `G-IMPORT-ORDER` → `G-LINT` y `G-RULES-SYNC` →
`G-RULES-DRIFT`.

## Desactivar un gate

Solo vía `governance/policy.yaml` → `gates.disabled` (ruta protegida por el
lock de integridad: requiere [bless humano](runbook.md)). Un gate desactivado
se reporta como `SKIP`, nunca desaparece del output: la omisión es visible.
