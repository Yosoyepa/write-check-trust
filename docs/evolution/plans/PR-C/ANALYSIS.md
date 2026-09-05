# ANALYSIS — PR-C: evidencia y factibilidad

## 1. Evidencia (verificada contra `97a9282`)

- `tools/wct/selftest/redteam.py:18-69` — `_reject()` implementa 17
  reconocedores ad-hoc (regex/lógica duplicada): `duplicate` re-implementa
  deduplicación por `return`, `cycle` re-implementa DFS de ciclos
  (`_contains_cycle`, líneas 72-82), `secret` re-implementa la regex de
  secretos — compitiendo con las reglas productivas en vez de probarlas.
- `redteam.py:93-95` — `REGISTRY` solo valida que el nombre del gate exista:
  **ningún caso invoca jamás un gate**.
- 4/30 casos (F14/F15) llaman `pre_tool_use` real (`redteam.py:63-68`).
- `quality/redteam/cases.yaml` — 30 casos, 15 modos × 2, con `checker` y
  `payload` textuales.

## 2. Factibilidad por caso (mapeo motor productivo)

### gate-engine (10) — engine Python importable, aislado y rápido

| Caso | Gate declarado | Motor productivo a invocar | Fixture mínimo |
|---|---|---|---|
| F1-a | G-DRY | `dry.analyzer.analyze` (o tpl si aplica: elegir por semántica del payload) | archivo con 2 funciones estructuralmente idénticas |
| F3-a | G-INTROVERT | `introvert.analyzer.analyze` | test que asierte sin trazar al SUT |
| F3-b | G-INTROVERT | ídem | test mock-only (`assert_called` sin aserción de valor) |
| F4-a | G-SUPPRESS | `ratchet.engine.suppression_count` | archivo con `# pragma: no cover` |
| F13-a/b | G-SUPPRESS | ídem | `# noqa` / `# type: ignore` sin justificación |
| F5-a | G-MUT-SITES | `mutate.engine.mutation_sites` | archivo generado programáticamente con >100 sitios (p.ej. N expresiones binarias) |
| F6-b | G-ARCHMETRICS | `archmetrics.analyzer.analyze` | mini-árbol `application` importando de `entrypoints` |
| F7-a/b | G-ARCH-CYCLE | detección de ciclos de archmetrics (misma ruta que el gate) | 2 módulos que se importan cíclicamente (2-ciclo y 3-ciclo) |

Nota: los engines esperan la estructura/config del proyecto — el fixture
incluye lo mínimo (dirs de capas, config de policy si el motor la lee); el
paso 0 del SPEC exige verificar qué consume cada motor y replicarlo.

### gate-tool (12) — función de gate productiva, herramienta externa

| Casos | Gate | Herramienta | Fixture |
|---|---|---|---|
| F1-b, F11-a/b | G-DEAD | vulture | archivo con función/constante nunca referenciada |
| F6-a | G-ARCH | import-linter | mini-árbol domain→adapters |
| F8-a/b | G-SAST-SEMGREP | semgrep | domain/application importando sqlalchemy/fastapi |
| F9-a/b | G-ARCH | import-linter | domain usando subprocess / application usando tkinter |
| F10-a/b | G-DEPS | deptry | `import imaginary_sdk` sin declaración |
| F12-a/b | G-SECRET | detect-secrets | AWS key / BEGIN PRIVATE KEY |

Herramienta ausente → el caso se reporta **SKIP visible** (contado por
arnés, nunca como rechazado ni como silencio).

### heuristic residuo (4) — justificación en ADR-C-02

F2-a y F5-b (semántica de mutación: corrida real de mutmut en fixture),
F2-b (test hardcoded que pytest aprueba por diseño — solo mutación lo
expone), F4-b (diff-cover con fixture git + rama base).

## 3. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Runtime: herramientas externas ×12 sobre fixtures (1-3 s c/u) alargan `selftest redteam` (vive en G-REDTEAM, tier pr) | Fixtures mínimos (1-3 archivos); presupuesto objetivo: ≤ +25 s sobre la corrida actual; VERIFICATION lo mide contra la base |
| Falsos negativos: el defecto plantado no coincide con lo que el gate real detecta | ESO ES EL PUNTO: si el gate real no caza el defecto, el caso falla en rojo y el handoff lo declara — es un hallazgo del instrumento, no del test (ver ADR-C-01 §error-rollback) |
| Engines esperan config del repo (policy.yaml) que el fixture no tiene | Fixture incluye config mínima; paso 0 verifica consumos por motor; fallback documentado si un motor exige más contexto del razonable |
| Aislamiento: un caso contamina el estado de otro | Cada caso construye SU tmpdir (tmp_path por caso) y corre dentro; cero estado compartido |
| Divergencia fixtures↔gate: el engine cambia firma y el red team queda viejo | Los fixtures llaman por la MISMA API que el gate usa (import del engine, no reimplementación); G-ARCH-CYCLE/G-ARCHMETRICS usan la función que su gate usa |
| cases.yaml compartido entre workstreams | Partición por archivo: cases.yaml (hook+residuo, edición solo R1), cases-engine.yaml (R1), cases-tool.yaml (R2); el runner tolera archivos ausentes para que cada worktree sea verde independiente |

## 4. Rollback

Tres commits (framework+engine, tools, residuos/docs); el runner nuevo
reemplaza al viejo en un commit revertible. Sin cambios de governance/**,
sin umbrales, sin manifiestos manuales.
