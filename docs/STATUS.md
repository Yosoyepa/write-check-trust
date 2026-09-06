# STATUS — Estado real del proyecto (verificable)

> **Regla para agentes y lectores**: este documento puede quedar desactualizado.
> Si un comando y este documento discrepan, **gana el comando** — y repórtalo
> como bug de este documento. El estado real siempre es derivable con el kit
> de abajo; ninguna prosa (ni PLAN.md, ni RESEARCH.md, ni esta) es evidencia.

Última verificación: 2026-09-06 · `v1.0.0-beta.2` · **beta** — política en [RELEASES.md](../RELEASES.md).

## Kit de verificación (~30 s)

| Comando | Qué demuestra |
|---|---|
| `uv run wct --version` | Versión del harness |
| `uv run wct doctor` | Salud: YAML de gobernanza, Python, hooks cableados (9 eventos) |
| `uv run wct gate --tier commit` | Gates ACTIVOS con estado real (hoy: fast 7 / commit 21 / pr 27 / full 34; suite 345 tests) |
| `uv run wct ratchet check --require coverage-total,docstring-coverage` | Ratchets exigibles: la métrica que no puede medirse bloquea, no salta |
| `uv run wct selftest redteam` | Red team: 30/30 adversarios F1–F15 (2 por modo de fallo), sin heurísticas |
| `uv run wct report` | Reglas y perfil vivos |
| `ls tools/wct/` | Módulos existentes: accept, archmetrics, cognitive, dry, hotspots, introvert, mutate, ratchet, size, splitplan… |
| `ls governance/baselines/` | Ratchets activos (12: coverage, docstrings, dead-code, per-file-ignores, dry-clusters, gherkin-ir-dry, file-size, archmetrics-zones, introverted-tests, suppressions, debt-markers) |
| `uv run wct hotspots` | Deuda priorizada por churn × complejidad (advisory) |
| `gh issue list --repo Yosoyepa/write-check-trust` | Deuda trackeada con owner |

> **Colisión de nombre en PATH**: en Fedora, `wct` a secas resuelve a
> `/usr/sbin/wct` — paquete `ncid-gateways`, el cliente "Whozz Calling" de
> NCID, no este harness. Invoca siempre `uv run wct` (o
> `uv run python -m tools.wct`): el harness vive en el venv del proyecto,
> nunca en el PATH del sistema.

## Implementado — con dónde se cerró

| Capacidad | Cerrada en | Evidencia rápida |
|---|---|---|
| DRY estructural fuzzy (AST normalizado + Jaccard) | pre-0.2.0 | `wct dry`; gate G-DRY |
| Honestidad de tests (introvert) | pre-0.2.0 | `tools/wct/introvert/`; G-INTROVERT |
| Métricas A/I/D + zonas pain/useless | pre-0.2.0 | `wct archmetrics`; G-ARCHMETRICS |
| Mutación diferencial con manifiesto + Gherkin mutada | v0.2.0 (PR #8, #9) | `wct mutate scan`; G-ACCEPT-MUT en CI |
| Split-plan (partición fachada TEST-007) | v0.2.0 (PR #8) | `wct split-plan <archivo>` |
| G-SIZE (500 LOC tokenize) | v0.3.0 (PR #13) | `wct gate --tier commit` → fila G-SIZE |
| G-COGNITIVE (≤15, Campbell/S3776) | v0.3.0 (PR #13) | ídem → fila G-COGNITIVE |
| Auditoría per-file-ignores como ratchet | v0.3.0 (PR #13) | `governance/baselines/per-file-ignores.json` (33, solo baja) |
| G-DRY-TOK con diente (`--exit-code 1`) | v0.3.0 (PR #15, #16) | full tier → G-DRY-TOK PASS; ya cazó duplicación real en CI |
| `wct hotspots` (churn × complejidad) | v0.3.0 (PR #14) | `wct hotspots` |
| Runner particionado (488 LOC, bajo el techo de 500) | v0.3.0 (PR #14, #16) | `wct gate --tier commit` → G-SIZE PASS |
| Válvulas anti-deadlock del Stop hook (observer + cortacircuito) | **v0.4.0 (PR #17)** | `tools/wct/hooks/guard.py::stop_gate`; `WCT_HOOK_ROLE=observer` |
| G-WIRE (anti-patrones de inyección DI en domain/ y application/) | **v0.5.0 (Fase β-1)** | `wct gate --tier commit` → fila G-WIRE PASS |
| G-LCOM (cohesión LCOM4 advisory + ratchet) | **v0.5.0 (Fase β-1)** | `wct lcom --json`; gate G-LCOM en full tier |
| G-DRY-TPL (clones de plantilla AST anonimizada + ratchet) | **v0.5.0 (Fase β-1)** | `wct dry --normalized`; gate G-DRY-TPL en full tier |
| Ciclo de vida del arnés vendido (`wct adopt lock/check/sync`) | **v0.5.0 (Fase β-2)** | `wct adopt lock`, `check`, `sync`; `tools/wct/adopt/` |
| Honestidad del reporte + scope/baseline de cobertura propia | **v1.0.0-beta.2 (PR #28, #29)** | `wct report` con perfiles y completitud |
| Conformidad configuración → runtime | **v1.0.0-beta.2 (PR #30)** | gates comparan policy/thresholds contra lo ejecutado |
| Red team productivo (motores reales, 0 heurísticas) | **v1.0.0-beta.2 (PR #31)** | `wct selftest redteam` 30/30 |
| G-MUT real (sobrevivientes fallan; sin redenciones) | **v1.0.0-beta.2 (PR #34)** | `wct mutate run` con exit semántico |
| Veredicto de mutación (inventario completo clasificado) | **v1.0.0-beta.2 (#37)** | `tools/wct/mutate/verdict.py` |
| Ratchets exigibles + G-INTROVERT en tier commit | **v1.0.0-beta.2 (#39)** | `wct ratchet check --require …`; fila G-INTROVERT en commit |
| CI del template exige ratchets medidos sobre su propio LCOV | **v1.0.0-beta.2 (#40)** | `quality.yml` + `tests/unit/test_workflow_contract.py` |

Los seis roles de pipeline (specifier, coder, cleaner, architect, hardener,
verifier) están en `.claude/agents/`; el plugin en `plugins/write-check-trust/`.

## Abierto — real y trackeado

1. **Issue #12** — 6 archivos conservan 33 códigos exentos en per-file-ignores
   (archmetrics/analyzer, cli, accept/pipeline, dry/analyzer, introvert/analyzer,
   selftest/redteam). Rastreado; `wct hotspots` da el orden de ataque.
2. **Issue #35** — narrativa Gherkin: pendiente de decisión de diseño.
3. **Publicar el plugin** en el marketplace de Claude Code (existe, no publicado).
4. **GA (1.0.0)**: 3 adoptadores externos, co-maintainer documentado, 30 días
   de beta estable — ver [RELEASES.md](../RELEASES.md).
5. Opcionales: tach opt-in, variante polyglot (JS/TS), benchmarks de
   boilerplate (tiangolo), wizard de migración con medición de baselines.

## Historial de versiones

- **v0.2.0** — PR tier con paridad de CI, feedback del piloto fases 22–24
  (split-plan, diagnóstico de manifiestos, Definition of done del coder),
  endurecimiento de workflows.
- **v0.3.0** — hotspots, G-SIZE, G-COGNITIVE, auditoría de per-file-ignores,
  G-DRY-TOK con diente en CI, partición del runner, ratchet de docstrings.
- **v0.4.0** — válvulas anti-deadlock del Stop hook (hallado en el piloto).
- **v0.5.0** — métricas estructurales (β-1: G-WIRE, G-LCOM, G-DRY-TPL) y
  ciclo de vida del vendido (β-2: `adopt lock/check/sync`, validado contra
  el piloto).
- **v1.0.0-beta.1** — **beta declarada** con política de madurez
  ([RELEASES.md](../RELEASES.md)), CHANGELOG, ADOPTERS y smoke-test de
  adopción en CI (`adoption-smoke.yml`: clon limpio → verde, ≤120 s).
- **v1.0.0-beta.2** — **endurecimiento del harness**: el conjunto
  POST-PR36 hace reales los controles que podían salir verdes sin
  verificar (G-MUT con sobrevivientes, diff-cover con base real, red
  team productivo, conformidad config→runtime, perfiles/completitud),
  clasifica el veredicto de mutación (#37), y agrega ratchets exigibles
  + G-INTROVERT en commit (#39) y la cadena de CI que exige mediciones
  sobre su propio LCOV (#40). Ver CHANGELOG para la guía de
  actualización beta.1→beta.2.
