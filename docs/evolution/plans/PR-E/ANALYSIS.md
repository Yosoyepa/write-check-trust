# ANALYSIS — PR-E: evidencia y factibilidad

## 1. Evidencia (verificada contra `9feac78`, mediciones propias 2026-09-05)

### G-MUT hoy: barato pero huérfano

- `tools/wct/gate/runner.py:456` — `G-MUT = external("G-MUT", ["mutmut",
  "run"], optional=True, scope=("src/example",))`. No pertenece a ningún
  tier (hallazgo del perfil de capacidades de PR-D: `tiers: []`).
- `pyproject.toml:88-95` — `[tool.mutmut]` con `source_paths =
  ["src/example"]` y selección de tests del ejemplo.
- **Medición**: `mutmut run` sobre main = 43 mutantes, **todos cazados,
  1.9s reales** (165 mutantes/seg con cache; frío sigue siendo segundos —
  el suite del ejemplo es diminuto). Cablearlo a `full` no mueve el
  presupuesto del tier (full local hoy ~45s).
- `wct mutate scan`/G-MUT-SITES usan el manifiesto diferencial sobre
  `src/example`; el alcance no cambia en esta PR.

### Los números que matan el wholesale (medidos hoy)

- `tools/wct`: **4.235 sitios de mutación en 57 archivos**; **16 archivos
  sobre el presupuesto de 100** de G-MUT-SITES (runner.py 469, cli.py 415,
  accept/pipeline.py 259, gate/checks.py 252, adopt/lifecycle.py 247…).
- Cada mutante corre la suite que lo selecciona; la suite completa del
  repo hoy tarda ~18-20s → 4.235 × 18s ≈ **21 horas** por corrida.
- Entrar al manifiesto además encendería G-MUT-SITES contra los 16
  archivos → exigencia de partición TEST-007 a escala masiva.

### Contrato exit-code de mutmut (matriz preliminar — el paso 0 la cierra)

| Estado del fixture | Exit observado | Validez de la observación |
|---|---|---|
| Tests corren, todos los mutantes cazados | 0 | válida (corrida sobre main) |
| Tests corren, hay sobreviviente | **2** | válida (probe con entorno funcional; sin pipe) |
| Tests NO pueden correr | desconocido | **arte de pipe** (`$?` capturó a `tail`) — obligatorio re-medir |

La tercera fila es load-bearing: si `mutmut run` devuelve 0 con un runner
roto, G-MUT aprueba en falso sobre fixtures rotos y esa PR debe
documentarlo o cerrarlo. El paso 0 de E1 mide la matriz completa SIN pipes
(redirigir a archivo, luego leer `$?`).

### Factibilidad de las corridas reales sobre fixtures (probe)

Un fixture con `[project] name`, `[tool.mutmut] source_paths=["src"]` y
selección de tests corrió mutmut de verdad con un entorno funcional y el
sobreviviente disparó exit 2. Los detalles de resolución de imports del
fixture (conftest/sys.path o proyecto instalable) los fija el paso 0 de
E1 — la factibilidad está demostrada.

### ruff desnudo a nivel árbol (repro del coder de PR-D)

`uv run ruff check .` (con el `extend` de ADR-D-03 activo) reporta **622
errores** (S101 en tests); `--config governance/lint/ruff.toml` pasa. El
footgun quedó reducido (por-archivo funciona) pero vivo a nivel árbol.
Root-cause pendiente: comparar settings efectivos entre ambas
invocaciones (`ruff check --show-settings`).

## 2. Factibilidad por caso (las 3 redenciones)

| Caso | Adversario plantado | Catch esperado |
|---|---|---|
| F2-a | fixture src real SIN tests | mutmut corre, TODOS los mutantes sobreviven → gate FALLA |
| F2-b | test que asierte una constante sobre un camino NO ejercitado (p. ej. `assert total([]) == 0` con producción `sum(items) * 1.0`) | el mutante del camino no ejercido SOBREVIVE → gate FALLA — el caso demostración |
| F5-b | test débil que no cubre la semántica | ≥1 sobreviviente → gate FALLA |

Los tres son `harness: gate-tool`, `gate: G-MUT`, `tool: mutmut` — el
despachador de PR-C ya soporta el arnés (SKIP visible si mutmut falta);
el runner NO cambia. Reconocedores: `hardcoded` y `survivor` mueren con
su último usuario; `testless` SOBREVIVE porque F4-b (que queda heuristic)
lo sigue usando.

Desglose final del red team: **30 = 13 gate-engine · 12 gate-tool ·
4 hook · 1 heuristic**. Modos: F2 ambos tool ✓ · F5 engine+tool ✓ ·
F4 engine+heuristic ✓.

## 3. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Runtime del selftest (+3 corridas mutmut sobre fixtures) | fixtures diminutos (2-4 mutantes); presupuesto objetivo ≤ +15s sobre los ~5s actuales; medir 3 corridas |
| mutmut escribe cache/`mutants/` en el cwd del fixture | el fixture vive en tmpdir del sistema (contrato PR-C de gates de subproceso); verificar que nada escapa al repo |
| contrato exit-code distinto al presumido | paso 0 obligatorio con matriz medida SIN pipes; si tests-rotos → exit 0, documentar el hueco de G-MUT como hallazgo y (si es cerrable barato) cerrarlo |
|imports del fixture no resuelven en el runner | paso 0 fija la convención (probe funcional existe); documentarla en el builder |
| G-MUT en full alarga CI local | medido 1.9s sobre scope actual; budget en VERIFICATION |

## 4. Rollback

Commits independientes (conversiones, tier wiring, ruff); cada uno
revertible. Sin cambios de umbrales ni baselines; el manifiesto de
mutación no cambia de alcance.
