# Registro REANCLAJE-7 — resultado del lote L2 (wire puro): campaña de mutación reconciliada (2026-09-18)

Estado: **campaña L2 ejecutada y reconciliada bajo la autorización expresa**
(generación + campaña + sondas causales SOLO sobre los cuatro módulos wire;
publicación documental en PR #56 en borrador). Sin reparaciones de
producto/tests, sin adjudicaciones implícitas, sin otros lotes, binding,
Q-ACCMUT, cobertura/CRAP/DRY/full, bless, merge, bump, tag ni release.

## 1. Identidades

- Base medida: `8b8868ac0420f0aa7b2f442129c3d8b9bfb4de72` (= origin
  `codex/reanclaje-p03a-fase1` = headRefOid PR #56, en borrador; baseRefOid =
  merge-base = main `8a379d64…`; tag `v1.0.0b3.dev1` intacto). Expediente
  REANCLAJE-6 verificado antes de ejecutar: digest comunicado
  `68d2b1c080515e2f2aa3d929ae1f3c89cb5cd4a755627470328902582de01fe5` (6/6).
- Copia de ejecución `build/tmp/reanclaje7-20260918/run`: checkout detached
  de la base, tree `097ca3e2d1f081d8d20af3ccf102e554223d597a`, venv propio
  (`uv sync --all-groups`; Python 3.13.14, pytest 9.1.1, **mutmut 3.7.0**,
  ruff 0.16.4, mypy 2.3.1). cwd de ejecución = copia; PATH con el bin del
  venv; imports acreditados dentro de la copia (`__file__`, logs/05).
- Única modificación de la copia: sección experimental `[tool.mutmut]` en
  `pyproject.toml` (original `f27de519…` / experimental `e49a25cb…`,
  sellados por separado; receta heredera de la calibración
  `p03a-mutcal-4m5r7b`). Las 4 fuentes autorizadas permanecen
  **byte-idénticas al sello R8** durante todo el encargo (apertura y cierre:
  logs/01 y logs/19): `pytest_wire_values.py` `63e25807…`,
  `pytest_wire_fields.py` `35e74471…`, `pytest_wire_composites.py`
  `8977f5b4…`, `pytest_wire_framing.py` `a6261613…`.

## 2. Receta reproducible

1. Selección declarada (126 nodeids, property excluida por marcador):
   `tests/unit/test_pytest_schema.py` (98) + 28 case-IDs PA02/PA03 de
   `tests/unit/test_pytest_observation.py` (logs/02).
2. Baseline fuera del árbol instrumentado: `pytest -m "not property"
   <selección> -q` → **126 passed, exit 0, 0 skips/xfails** (2.13 s).
3. pyproject experimental: `source_paths` = exactamente las 4 rutas;
   `also_copy=["tools","features","src"]`; `pytest_add_cli_args_test_selection`
   = selección declarada.
4. **Generación pura** (firma admisible documentada, precedente
   ANEXO-PREPARACION-GS3 P5): `mutmut run ZZ_…_NO_MATCH` → «4 files mutated,
   0 ignored, 0 unmodified» + stats (8.51 s) + assert «Filtered for specific
   mutants, but nothing matches» ANTES de todo test → cero mutantes
   ejecutados; snapshot de stats conservado antes de cualquier consulta
   (logs/08).
5. Campaña: `mutmut run --max-children 1 <278 IDs explícitos>` bajo
   `timeout --signal=INT --kill-after=30s 1800`.
6. Sondas: `lanzador.py` fail-closed (valida ID exacto del inventario
   congelado, hashes sellados, árbol instrumentado; (re)asigna
   `MUTANT_UNDER_TEST` en el proceso que lanza pytest) + `cd mutants` para
   ejecutar contra los trampolines.

## 3. Métricas separadas (no equiparadas)

- **220 sitios WCT** (49+60+46+65; métrica del motor WCT): usada SOLO como
  control de identidad — concilia con REANCLAJE-6 §1.2.
- **278 mutantes reales** (values 66, fields **0**, composites 85, framing
  127) sobre **23 funciones**; 278/278 asociaciones función↔IDs↔tests no
  vacías (logs/10). **64 sitios WCT de nivel de módulo NO instrumentados**
  por mutmut 3.7 (60 de wire_fields — módulo sin funciones, tablas puras —
  más 1/1/2 de values/composites/framing): límite instrumental DECLARADO;
  ni cubiertos ni equivalentes.

## 4. Activación y canario

- Control ORIGINAL en mutants/: 98 passed (schema), exit 0, sin activación.
- Canario `x__u__mutmut_1`: **rojo atribuible** — 38 failed;
  `AssertionError: 'invalid_field' == 'limit_exceeded'` en
  `test_wire_inventory_cap_at_the_real_boundary[excedido]` (test del conjunto
  asociado); causa: `value→None` en `_u` fuerza invalid_field en bordes.
- Negativos del lanzador (exit 2 ANTES de pytest): ID desconocido;
  selección vacía; hash adulterado (fuente restaurada y revalidada).
- El propio `mutmut run` corre su forced-fail test (arnés) antes de la
  campaña; la campaña ejecuta cada mutante SOLO contra sus tests asociados
  bajo `MUTANT_UNDER_TEST=<id>`.

## 5. Bruto reconciliado

Campaña serial: **224.3 s wall, exit 0** (guardián 1800 s no alcanzado).
Reconciliación **por conjuntos** (logs/14; re-verificada independientemente
en el cierre): conjunto generado (278 .meta) = conjunto autorizado
(inventario congelado) = conjunto de resultados; **0 duplicados, 0 ajenos,
0 faltantes, 0 no-ejecutados, 0 solape**; exactamente un estado final por
ID. **Bruto: 233 killed (exit 1) + 45 survived (exit 0)**. La expectativa no
era «todo killed»: se informa lo medido.

## 6. Clasificación causal sucesora (logs/18)

- **KILLED-EVIDENCIADO: 233** — canario con sonda fresca y causa citada
  (§4) + 232 por campaña con arnés acreditado (asociaciones verificadas,
  canario, forced-fail, control original). El verifier final reejecutó una
  sonda fresca adicional de un killed distinto (`x__opt_s__mutmut_1`: 1
  failed `AssertionError: 573 == 2097152` con original verde) — muestra
  causal independiente adicional. Sondas individuales de los 232 restantes:
  no ejecutadas (sobre de sondas agotado); disponibles a demanda.
- **SURVIVED-CONFIRMADO: 45** — 1 con sonda fresca independiente
  (`x__argv__mutmut_12`: 126 passed, exit 0, activación acreditada;
  re-confirmada por el verifier en 6.08 s) + 44 por campaña (exit 0 sobre
  conjunto asociado completo). Diffs reales de los 45 conservados
  (logs/16; 43/45 de una línea física, 2 con reflujo de formato de un
  único argumento — hallazgo menor del verifier). Sondas independientes de
  esos 44: ejecutadas pero salida no conservada (defecto de captura,
  §8) — quedan enumeradas (logs/15). **Adjudicación de sobrevivientes
  (hueco de oráculo vs equivalente): PENDIENTE, decisión humana** — nadie
  ratifica equivalencias ni excepciones en este encargo.
- INSTRUMENTAL/DISCREPANCIA: 0 IDs. Una discrepancia de proceso declarada
  (§8: exceso del sobre de sondas).

## 7. Presupuesto real (ledger logs/20)

| Sobre | Techo | Real | Estado |
|---|---:|---:|---|
| generación (incluye preflight) | 120 s | ~17.8 s | ✔ |
| ejecución campaña | 1800 s | 224.3 s | ✔ |
| sondas causales | 300 s | ~390 s | **✗ excedido ~90 s, declarado** |
| revisión experimental | 300 s | ~13 s | ✔ |
| **agregado** | **2520 s** | **~645 s** | ✔ |

Causa doble del exceso: costo real 8 s/sonda en árbol con trampolines (~4×
la estimación) + defecto de captura (buffering del lanzador reordenó
LANZADOR-OK al final del pipe; `tail -1` perdió los resúmenes pytest de las
45 sondas ejecutadas). **Guardián aplicado: cero sondas nuevas** tras
detectar el exceso. Sin transferencia entre sobres.

## 8. Dictámenes

- **Verifier previo a la campaña** (solo lectura, distinto del autor):
  **FAVORABLE, 0 bloqueantes** — corte/hashes contra sello R8, allowlist sin
  quinta ruta (trampolines solo en los 4 wire), baseline/colección 126 sin
  property, inventario 278/23 funciones/0 asociaciones vacías, límite
  wire_fields verificado por AST propio, canario reproducido con los 38
  fallos exactos, firma de generación pura confirmada en el fuente de
  mutmut (assert antes de todo test), presupuesto correcto. Hallazgos
  menores documentales incorporados (ledger tabulado, numeración de sondas).
- **Verifier final del cierre** (solo lectura, distinto del autor):
  **FAVORABLE, 0 bloqueantes** — reejecutó sello (26/26), reconciliación
  independiente por conjuntos (278/233/45/0 exactos, conteo crudo anti
  colapso JSON), sonda fresca propia de un killed con causa semántica y
  control original verde, sonda del survivor confirmado (126 passed),
  brutos/clasificación separados, cero adjudicaciones de equivalencia
  (grep: 44 menciones todas «PENDIENTE — decisión humana»), presupuesto con
  exceso declarado y no oculto, árbol de la copia sin cambios de
  producto/tests (solo pyproject experimental), candidato del PR intacto.

Ambos dictámenes verifican este expediente; no sustituyen adjudicación
humana ni acreditan P03a/beta.3 completos.

## 9. Expediente y sellos

`build/tmp/reanclaje7-20260918/`: ENTREGA.md + logs/01–20 + lanzador.py,
sellados en `MANIFIESTO-REANCLAJE7.sha256` (26 miembros, sin auto-hash),
digest `4687309f8148a83778675346d2e32636f4e200d4f30f8724ef5e38579ba87766`
(verificación fuera de sus miembros). El árbol `run/mutants/` (instrumentado)
y los .meta (bruto) se conservan in situ.

## 10. Siguiente acción mínima propuesta

**PROPUESTO — NO EJECUTAR SIN AUTORIZACIÓN.** Encargo de **adjudicación
humana asistida de los 45 sobrevivientes L2** (precedente
ADJUDICACION-SOBREVIVIENTES-SCAN-CLOSERS): por cada ID, diff + lectores
reales + sonda de comportamiento contra la API pública; clasificación
hueco-de-oráculo (→ oráculo TDD en rutas aprobadas) vs equivalente (→ acta
con justificación estructural/empírica); presupuesto ~600 s; sin cambios de
producto más allá de oráculos en tests aprobados. Alternativa paralela:
cualquier otro lote del plan REANCLAJE-6 §4 (L4 decoder es el siguiente
recomendado). Nada de esto se ejecutó aquí.
