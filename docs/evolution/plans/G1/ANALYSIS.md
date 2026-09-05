# G1 — ANALYSIS: contrato del motor, evidencia tipificada y diseño G1a/G1b

Corte: `0f80122`. Revisiones: este documento incorpora REVIEW-G1 completo
(trazabilidad por sección). Atribución de evidencia por tipo — [O]/[I]/[L]/
[INF] — definida y registrada en [EVIDENCE.md](EVIDENCE.md).

## 1. El defecto actual (F01) — [L]

`tools/wct/gate/mutation.py`: línea 44 `mutmut run` sin nombres; línea 54
descarta el exit de results; líneas 57-62 el veredicto es "ausencia de dos
sufijos". El inventario tiene **1 estado aprobado** (killed), **2
defectuosos** (survived, no tests) y **7 fuera del contrato de
certificación** (timeout, suspicious, not checked, interrupted, skipped,
segfault, caught by type check) que hoy producen PASS.

## 2. Contrato de mutmut 3.7.0 — [L], líneas de la instalación local

- **Estados** (`__main__.py:82-104`): exit 1 y 3 → `killed` (3 = error
  interno de pytest, [contrato oficial](https://docs.pytest.org/en/stable/reference/exit-codes.html));
  0 → survived; 5/33 → no tests; 2 → interrupted; None → not checked;
  34 → skipped; 35 → suspicious; 36/24/152/255/−24 → timeout; 37 → caught
  by type check; −11/−9 → segfault; default → suspicious.
  **El inventario textual pierde la causa: exit 3 (error interno) es
  indistinguible de un kill por aserción** (REVIEW-G1 §4).
- **`results`** (`__main__.py:1554-1565`): omite `killed` por defecto
  (vacío válido, [O] P1); `--all true` imprime el inventario completo;
  llave `<pkg>.<mod>.x_<fn>__mutmut_<n>`; `SourceFileMutationData.load`
  tolera FileNotFoundError (`data.py:112-117`) → **pérdida PARCIAL de
  metas entre fases es invisible para results** (REVIEW-G1 §7).
- **Caché** (`__main__.py:1455-1457`): sin nombres, un resultado no-None
  "se mantiene". Invalidación por hash de FUNCIÓN (`:341-357`); no existe
  invalidación por cambio de tests. [O] P5bis: falso verde E2E completo.
- **Guardianes propios** ([O] P3 + [L]): clean-test control (exit 1),
  forced-fail (aborta), asociación nula ("Stopping early", exit 1).
  Estos hacen que "cero mutantes" y "suite rota" fallen HOY correcto por
  la vía run — el residuo real está en la fase de results.
- **Selección** (`__main__.py:1241-1248`, [O] P6bis): argumentos literales
  con igualdad/fnmatch; los nombrados se RE-EJECUTAN; sin coincidencia →
  AssertionError exit 1.

## 3. Evidencia tipificada (resumen; detalle en EVIDENCE.md)

| Hallazgo | Tipo | ¿Secuencia completa del gate? |
|---|---|---|
| Falso verde por caché (tests debilitados conservan llamadas) | [O] P5bis | SÍ (gate real) |
| Falso verde por timeout (2 colgados) | [O] P8 | SÍ (gate real) |
| interrupted/skipped impresos → PASS | [I] P7/B (representación) | SÍ (gate sobre estado inyectado) |
| results exit 1 (corrupto/ilegible) | [I]+[O] standalone | NO — solo fase results (RG02 la cubre con doble etiquetado) |
| Pérdida total silenciosa (metas borrados → vacío exit 0) | [I]+[O] standalone | NO — recepción: inventario vacío → ERROR |
| Repo main reutiliza veredictos | [O] (mtimes) | Reutilización REPORTADA; validez con tests actuales NO acreditada (REVIEW-G1 §3) |
| Repetición literal `'*'` derrota la herencia | [O] D3 | SÍ — base killed → debilitar → `'*'` → ambos survived, 28 mutations/second |

## 4. Diseño: dos incrementos con claims independientes (REVIEW-G1 D1)

**G1a — recepción y clasificación del reporte del motor.** El gate deja de
derivarse de "ausencia de sufijos": consume `results --all true`, exige
inventario legible no vacío, clasifica TODOS los estados (tabla §2),
detecta identidades duplicadas/renglones desconocidos (fail-closed),
precedencia ERROR>FAIL conservando hallazgos, run-fail = FAIL "ejecución no
completada" (compatibilidad PR-E/redteam F2-a, SIN etiqueta de producto),
SKIP conservado. CLI: cuando mide, misma política que el gate (subprocess
observable); delta cero = informativo. **Claim LIMITADO: "el motor reportó
todo su inventario como killed" — no certifica causa (exit 3 colapsa) ni
frescura (herencia sigue posible dentro de la corrida del gate).**

**G1b — pertenencia, completitud y causa.** Frescura por repetición pública
literal (D3 demostrada; ADR-G1-02), inventario esperado-vs-recibido y
pérdida parcial, discriminación exit 1/3 vía lector versionado del artefacto
del motor (ADR-G1-04), versión soportada, concurrencia/symlinks. Requisitos
bloqueantes enumerados en ADR-G1-04; NADA de G1b queda implementado ni
medido por G1a. F01/F02 quedan PARCIALMENTE cerrados tras G1a (subcriterios:
recepción/clasificación sí; selección diferencial, scope y delta de tests
siguen H0/H1 — REVIEW-G1 §8).

## 5. F02: tres contratos, tres alcances — [L] + [INF]

CLI `wct mutate run` retorna el exit de `mutmut run` (engine.py:169-178) —
[INF] exita 0 con sobrevivientes (cadenas: P2 midió run exit 0 con
survived; el CLI pasa ese exit tal cual — no se ejecutó con delta real en
este turno). G1a unifica el VEREDICTO (misma política al medir); H0/H1
unifican el ALCANCE (policy `[src]` vs `source_paths=[src/example]` vs
scope declarado del registro).

## 6. Presupuesto — estado: POR MEDIR (emparejado, RG12)

Medido hasta ahora (NO emparejado, muestras de 1, entorno único):
base 2 mutantes 1.2–1.8 s; heredado 1.3–1.6 s; repetición literal 1.7 s;
timeout ~5–8 s/mutante (P8: 17 s); `results --all true` 0.5–0.8 s.
**La comparación 1.8 vs 1.9 s del primer dossier no es experimento
emparejado y se retira como evidencia de costo.** G1a debe medir (≥3
repeticiones, mediana y rango, mismo entorno/scope/tests/versiones): suite
base vs nueva, coverage, redteam y gate por separado — el costo CI NO es
nulo porque la suite y el redteam llaman `gate_mutation` (EVIDENCE §
correcciones). El fixture timeout real suma; su costo se reporta aparte.

## 7. Riesgos residuales tras G1a (declarados, no resueltos)

- Herencia DENTRO de la corrida del gate (G1a no fuerza repetición):
  un `mutants/` previo con resultados en pie puede acortar la corrida del
  gate — el PASS de G1a certifica "el motor reportó", con la salvedad de
  pertenencia visible en el diagnóstico. Lo cierra G1b.
- exit 3 → killed: un error interno de pytest puede contar como kill.
  Lo cierra G1b (ADR-G1-04).
- Pérdida parcial entre fases: G1a detecta solo vacío total y renglones
  inválidos; pérdida parcial requiere denominador independiente (G1b, RG06).
- Concurrencia sobre `mutants/`: sin locking; documentado, rechazo visible
  es requisito G1b (RG11).
- `_captured` sin timeout de subprocess: fases de stats/clean pueden
  colgar; diferido a G3 (presupuestos), documentado.
