# Registro REANCLAJE-22 — Reparación acotada de L8: atribución cerrada, oráculos de los 29 y controles de módulo

Estado: **candidato reparado y congelado (pre-revisión de Architect): los 131
kills-por-colección quedan acreditados individualmente (95 reutilizados de R21
+ 35 sondas nuevas + 1 reutilizado de V4), los 29 objetivos B2 tienen
sensibilidad sustentada con los oráculos nuevos, las diez ratificaciones D-A
se comprueban sin divergencia y los controles de módulo miden conducta e
independencia con perturbaciones temporales 6/6 detectadas. SIN recampaña
completa, sin bless, sin merge/bump/tag/release.** El bruto histórico R20 se
conserva intacto: **398 = 359 killed + 39 survived**.

Complementa a `REANCLAJE-22-L8-DECISIONES.md` (decisiones D-0, D-A, D-D, D-E9,
allowlist, arnés y presupuestos), que se registró ANTES de sondear.

## 1. Base, identidades y aislamiento

- Base comunicada y HEAD técnico congelado:
  `b7604c8dc915cd6965061f8d51a8e98013f73aa8`.
- `origin/codex/reanclaje-p03a-fase1` == `b7604c8…` (verificado con
  `git ls-remote`; sin avance). PR #56 en borrador (estado heredado; en este
  entorno NO hay `gh` instalado: la observación de PR/CI se reporta como no
  observable desde aquí, sin leer tokens ni usar otros servicios).
- Main de referencia `8a379d64ba13bbe43a707fcfd8df0ea336dd97ed` == merge-base
  (rama estrictamente por delante). Tag `v1.0.0b3.dev1` anotado:
  objeto `5aeb9ce5…`, peeled `8a379d64…` = main, intacto.
- Copia aislada con raíz Git propia:
  `build/tmp/reanclaje22-20260921/tree` (clon local, checkout detached,
  `.venv` propio con `uv sync --frozen --offline --group quality`).
  Runtime: Python 3.13.12, pytest 9.1.1, mutmut 3.7.0 (la máquina de R21 usó
  3.13.14; diferencia de patch declarada).
- El expediente R21 llegó por migración desde otra máquina
  (`/home/jandradeu/…`): su identidad material viaja en los sellos R20
  (`custodia/sellos-R20.json`) y en el manifiesto R21. Este encargo
  reconstruyó las copias instrumentadas DESDE la custodia sellada y verificó
  cada hash antes de usarlas (lanzador fail-closed).
- Checkout principal, su índice, `main`, tags y expedientes históricos: sin
  tocar (verificación de preservación en §7).

## 2. Frente A — tabla causal sucesora de los 131

Conjunto derivado por diferencia del ledger sellado R20 (KILLED ∧ n_fallos=0
∧ n_errores>0 = 131) menos los 95 ya acreditados por R21 = **36 de residuo**.

**Resultado sucesor: A1 = 131 · A2 = 0 · A3 = 0 · A4 = 0.** Fuentes de
evidencia separadas:

| Bloque | IDs | Evidencia | ¿Sonda nueva? |
|---|---|---|---|
| A1 R21 | 95 | `reanclaje21-20260919/agenteA/logs/A-tabla-131.json` (95 filas con trampolín + variante + línea mutada + cadena de colección + tipo de excepción; rc=1 bruto) + `verifier/V-DICTAMEN.md` + `verifier/V-reconciliacion.json` (conjuntos exactos, sin solapamiento A∩B) | No (reutilizada, sin invalidante) |
| A1 V4 | 1 (`x_decode_journal__mutmut_25`) | `verifier/logs/V4.log` con sha256 `82ee920f…251f` == línea 250 del `MANIFIESTO-REANCLAJE21.sha256` (identidad recalculada); LANZADOR-OK con `MUTANT_UNDER_TEST` del ID; frame del trampolín + frame de la variante con línea mutada `consumed, defect = _consume_header(job)`; causa `TypeError ... missing 1 required positional argument: 'job'`; fase de colección (CASES → _pa12_cases → _decode_golden → decode_pytest_journal) | No (reutilizada SOLO ese ID, con recálculo e identidad) |
| A1 R22 | 35 | `reanclaje22-20260921/A/residuo-22.json` + `A/logs/A001…A035-*.log` (cada uno con `LANZADOR-OK`, trampolín de mutmut, frame `def x__…__mutmut_N(`, línea mutada, cadena de colección de 6-7 marcadores, rc=1 bruto y tipo de excepción coincidente 35/35 con el log sellado R20) | Sí (35 reejecuciones `--tb=long`, tests sellados, selección completa) |

- Control ORIGINAL en entorno equivalente: `rc=0`, **580 passed** (mismos 3
  archivos, misma selección).
- Clases causales nuevas: aridad de sitio de llamada (KeyError/TypeError de
  constructor y de helper), None propagado a `find`, `decode`, `run_id`,
  `executions`, `append`, `len()`, `_Job.__init__` y `_finish` (las dos
  familias dominantes del residuo). La clase anómala del nombre
  `x__consume_header__mutmut_orig` queda cerrada por V4 y NO se promueve por
  afinidad (solo ese ID).
- Precisión: el bruto histórico R20 (398) no se reescribe; estas
  clasificaciones sucesoras se presentan aparte, como en R21.

## 3. D-A — las diez ratificaciones por ID (comprobadas, sin divergencia)

Ratificación humana registrada en DECISIONES §3. Comprobación por ID contra
el diff sellado, la fuente instrumentada y la frontera pública:

| ID | Mutación exacta (diff sellado) | Frontera pública | Fundamento | Invalidantes comprobados | Resultado sobre el candidato |
|---|---|---|---|---|---|
| `build_execution_start` 1 | `role=""` → `role=None` | `decode_pytest_journal` → `decode_journal` → `_decode_event` → `_reconstruct_refs` | El role se reemplaza INCONDICIONALMENTE desde la cabecera antes de publicar el `JournalEvent`; los caminos de error descartan el evento | Ningún test llama al builder fuera de `_decode_event`; ningún camino publica el payload intermedio | Sobrevive |
| 7 | `input_sha256=""` → `None` | ídem | ídem (digest sustituido desde la cabecera) | ídem | Sobrevive |
| 8 | `context_sha256=""` → `None` | ídem | ídem | ídem | Sobrevive |
| 9 | `recipe_sha256=""` → `None` | ídem | ídem | ídem | Sobrevive |
| 19 | `role=""` → `"XXXX"` | ídem | ídem | ídem | Sobrevive |
| 35 | `input_sha256=""` → `"XXXX"` | ídem | ídem | ídem | Sobrevive |
| 36 | `context_sha256=""` → `"XXXX"` | ídem | ídem | ídem | Sobrevive |
| 37 | `recipe_sha256=""` → `"XXXX"` | ídem | ídem | ídem | Sobrevive |
| `consume_header` 10 | `_line_defect(data, unterminated=True)` → `unterminated=None` | `decode_pytest_journal` → `decode_journal` → `_consume_header` → `_line_defect` | Sin LF, el mutante devuelve `(0, None)`: `decode_journal` continúa (defect es None) y `_consume_line` re-clasifica la MISMA línea con `unterminated=True` (no hay LF), con idéntico orden límite → UTF-8 → `truncated_line` y el mismo offset/consumo/eventos/tail | Ningún caso diverge: la convergencia es por re-clasificación de la misma línea, no por valor de verdad del flag; no se extiende a llamadas directas al helper | Sobrevive |
| `consume_header` 13 | `unterminated=True` → `False` | ídem | ídem | ídem | Sobrevive |

- Hash de fuente instrumentada (4 fuentes selladas R20):
  `pytest_types.py` `b2b2b05c…`; `pytest_builders.py` `f3252d1a…` (sede de los
  8 placeholders); `pytest_schema.py` `b53db023…` (sede de los 2 unterminated);
  `pytest_inventory.py` `c9…`; originales verificados contra
  `sellos-R20.json` antes de cada corrida.
- Comprobación ejecutada: **selección completa** de los 3 archivos bajo cada
  uno de los 10 IDs, intérprete fresco, modo `sealed`/`working` según fase:
  `603 passed` en los diez (estado X); comprobación final sobre el congelado
  Y': **`605 passed` en los diez** (§7).
- Sin divergencias: ninguna premisa falló, ningún ID se forzó y no se tocó
  ningún test para conservar su supervivencia.

## 4. Frente B — sensibilidad de los 29 objetivos

Protocolo: copia `mutants-sens` (instrumentado sellado + tests del candidato
byte-idénticos a `tree/`), lanzador fail-closed en modo `working`, intérprete
fresco por ID con activación antes del primer import, nodeids explícitos del
oráculo nuevo/reforzado, rc bruto conservado y causa esperada obligatoria.

| Objetivo | Oráculo (nodeid) | Original | Mutante |
|---|---|---|---|
| `finding` 2 | `test_observation_case[PA07-property-selected]` (+6 casos reforzados) | verde | rc=1, 6 failed; `('selection_mismatch', None, None, 1489) != (… 'producer-1' …)` |
| `finding` 3 | ídem | verde | rc=1, 5 failed; nodeid None en findings |
| `selection_findings` 3 | `[PA07-valid-property]` (deselección legítima) | verde | rc=1; aparece `selection_mismatch` falso en ambas ejecuciones (`covered.update(None)` pierde el multiconjunto) |
| `selection_findings` 7 | `[PA06-duplicate-item]` | verde | rc=1; `execution_id=None` en el finding de selección |
| `selection_findings` 8 | ídem | verde | rc=1; `offset=None` en el finding de selección |
| `deselection_rule` 8/9 | `[PA07-property-marker-change]` | verde | rc=1; execution_id/nodeid None en `property_marker_changed` |
| `deselection_rule` 20/21 | `[PA07-normal-deselected]` | verde | rc=1; execution_id/nodeid None en `unauthorized_deselection` |
| `deselection_rule` 32/33 | `[PA07-property-extra]` | verde | rc=1; execution_id/nodeid None en `unexpected_property` |
| `deselection_findings` 3 | `[PA07-property-marker-change]` | verde | rc=1; execution_id None en los tres findings de regla |
| `deselection_findings` 13 | `[PA07-property-duplicate]` | verde | rc=1; execution_id None en `duplicate_property` |
| `duplicate_findings` 4/5 | `[PA07-property-duplicate]` | verde | rc=1; execution_id/nodeid None |
| `missing_findings` 2/3 | `[PA07-normal-deselected]` | verde | rc=1; execution_id/nodeid None en `missing_property` |
| `property_findings` 9 | `[PA07-property-marker-change]` | verde | rc=1; 4 failed; execution_id None en reglas de deselección |
| `property_findings` 21/22/23 | `[PA07-property-selected]` | verde | rc=1; execution_id/nodeid/offset None en `unauthorized_selection` |
| `property_findings` 32 | `[PA07-normal-deselected]` | verde | rc=1; execution_id None en `missing_property` |
| `consume_header` 14/15/16 | `test_header_64kib_boundary_admits_exact_and_limits_excess_before_json` | verde | rc=1; `noncanonical_json` vs `limit_exceeded` invertidos en la frontera exacta |
| `build_execution_end` 31/32/46/47 | `test_wire_execution_end_bounds_are_exact_at_the_boundary` | verde | rc=1; aceptación/rechazo invertidos en −256/−255, 255/256, 1/2 y 64/65 |

- **29/29 con rc=1**, cero errores de colección, cero timeouts, causa
  prevista en todos (`B/sensibilidad-29.json` + `B/logs/B1xx-*.log`).
- Caso de deselección legítima (`selection_findings_3`): se refuerza
  `PA07-valid-property` con `findings_exact=()` y
  `codes_exclude=("selection_mismatch",)`, y se añade la conservación del
  multiconjunto como expectativa exacta (no basta «algún código aparece»).
- Esperados derivados del contrato y de la entrada construida (offsets
  calculados por el propio test con `_offset_of_code` sobre las líneas
  construidas), sin llamar a funciones productivas que calculen findings.
- Contrato observado: `execution_id` ≠ None (reservado a hallazgos de decoder
  globales), `nodeid`/`offset` reales salvo ausencia de evento causante
  (`duplicate_property`/`missing_property` con offset None, como prescribe el
  contrato: no se exige offset no nulo donde corresponde None) y el orden del
  §7 (offset → código → identidad) verificado de forma exacta.

## 5. Frente C — controles de módulo

- **Matriz de las 17 lambdas de `_BUILDERS`** (+ las 4 funciones nombradas)
  desde el camino de decodificación admitido:
  `test_wire_builder_matrix_yields_contractual_payload[21 filas]` construye
  bytes por la API pública (un evento por clase, con declaración previa donde
  procede), coteja tipo exacto del payload y valores literales del contrato y
  de la entrada. Campos susceptibles de intercambio con valores distintos
  (`PluginClaim.name≠module≠distribution≠version`; `SessionEnd.argument_exit≠observed_exit`;
  `ExecutionStart.argv/cwd/log_start/monotonic_ns`; `CollectionEnd`).
  Esperados independientes: no se llama al builder, coercer ni tabla
  productiva para calcularlos.
- **Catálogo de `inventory`**: transcripción literal de los 6 códigos
  property + 2 no bloqueantes (§7 l.470-476) y prueba de efecto:
  emisión/orden en `property_findings`, exclusión de `selection_mismatch` y
  no bloqueo del cierre de protocolo (con un caso que emite ambos). No se
  reduce a comparar dos constantes del andamiaje.
- **Perturbaciones temporales** (copia desechable `perturb-C`, hashes antes y
  después idénticos; contabilizadas aparte de los 398):
  1. intercambio `PluginClaim.name↔module` → matriz en rojo;
  2. intercambio `SessionEnd.argument_exit↔observed_exit` → matriz en rojo;
  3. omisión de la resolución de nodeid en `TestStart` → matriz en rojo;
  4. quitar `unauthorized_selection` del catálogo → transcripción y efecto en rojo;
  5. agregar `selection_mismatch` al catálogo property → transcripción y efecto en rojo;
  6. quitar `selection_mismatch` de no bloqueantes → transcripción y efecto en rojo.
  **6/6 detectadas** (`C/perturbaciones-C.json` + `C/logs/C0xx-*.log`).
- Justificación de reutilización: el intercambio `argument_exit↔observed_exit`
  ya estaba detectado por la perturbación P-C1 de R21 (3 failed/580) y la
  matriz lo cubre determinísticamente; el intercambio de `PluginClaim`, la
  omisión de `TestStart` y las alteraciones de pertenencia NO tenían cobertura
  y requirieron el oráculo nuevo.
- `ObservationError`: se conserva la precisión — hay 8 variantes físicas de
  trampolín en el instrumentado sellado, pero **0 IDs registrados** en el
  inventario histórico; se reutiliza la evidencia existente (P-C2b: swap
  `code↔field` en el cuerpo ejecutado DETECTADA con 134 failed/580; tests
  existentes de code/field) y **no se ejecutó campaña nueva** de esas
  variantes. No se declara cobertura exhaustiva a partir de una perturbación.
- Sin contrato: no se impone test literal de `__all__` ni estructura a
  `ExecutionInventory`; no se refactorizó producto para instrumentarlo.

## 6. Fidelidad, congelación y selección

- Los tests pueden nacer verdes como caracterización de un original conforme:
  no se inventó ningún rojo del original.
- **Colección real**: 605 nodeids únicos = 580 históricos (⊆, cero bajas
  silenciosas) + 25 nuevos (21 filas de matriz + 1 frontera de cabecera + 1
  frontera de builder + 2 catálogo), sin property. Digest SHA-256 de la
  selección: `284b7e8140ca483f0ab19caedf22bbd96199d69cf2b1ec57966fb5f62f1b73dc`.
- **Hashes congelados** (`sello-candidato-22.json`):
  `test_pytest_schema.py 00c17eea…`; `test_pytest_observation.py 03034dd4…`;
  fuente originales == sellos R20 (byte-idénticas);
  `lanzador22.py 4d2eb14d…`; `guardian22.py f80e8633…`.
- **Correcciones X→Y declaradas** (tras medir, antes de entregar):
  a) los casos PA07 `normal-deselected` y `property-extra` usaban conteos
  declarados (1,2) que no correspondían a su inventario, lo que inyectaba un
  `collection_count_mismatch` ajeno; se corrigieron a (1,1) coherentes y se
  incorporó `missing_property` a la secuencia exacta; b) formato/lint ruff
  (STYLE-001) sobre los dos archivos; c) los tests de catálogo no existían en
  la primera pasada de perturbaciones (3 intentos rc=4 registrados) y se
  añadieron antes de la pasada definitiva. Comprobaciones afectadas repetidas
  sobre el estado sucesor Y (sensibilidad, ratificados, perturbaciones) y de
  nuevo sobre el congelado Y' con el resultado definitivo: **29/29
  sensibilidad, 10/10 ratificados, 6/6 perturbaciones** y batería completa
  verde (§7).

## 7. Colección, baterías, presupuestos, incidentes y verificación

- **Colección conciliada antes/después**: 580 históricos presentes en la
  colección de 605; conjuntos idénticos antes y después del formateo.
- **Verificación final sobre el congelado Y'** (repetición de las
  comprobaciones afectadas por X→Y): sensibilidad **29/29** (nodeid previsto
  fallando, causa contractual, cero errores de colección), ratificados
  **10/10** (`605 passed` en cada uno), perturbaciones **6/6** detectadas;
  colección final **605 únicos == selección congelada**; focal ORIGINAL
  **579 passed**; suite normativa **1360 passed**; property **1 passed** por
  separado; G-FAST **7/7 PASS**; tier commit **20 PASS + 1 FAIL (G-META-1)**.
- **Baterías** (con PATH del venv, como `uv run`):
  - G-FAST: **7/7 PASS** (G-LINT 61, G-FMT 46, G-TYPE 3397, G-META-2,
    G-RULES-DRIFT, G-SUPPRESS 257, G-DEBT 106).
  - Suite normativa canónica `tests/unit tests/integration -m "not property"`:
    **1360 passed** (rc=0). Property por separado: **1 passed** (1361 deselected).
  - Tier commit: **20 PASS · 1 FAIL/ERROR — G-META-1** (rojo declarado del PR
    por drift de integridad; duración 262 ms separada del número de hallazgos;
    referencia, no cifra impuesta). Ningún otro rojo.
  - Ruff format --check y ruff check (config de gobernanza): limpios.
- **Presupuestos** (reloj monotónico, guardián con reserva previa y ledger;
  incluye intentos inválidos y las repeticiones X→Y→Y'):

  | Sobre | Cap | Gastado | Detalle |
  |---|---|---|---|
  | A | 600 s | 148.69 s | control ORIGINAL + 35 sondas + overhead |
  | B | 1200 s | 422.32 s | focales ORIGINAL, 29 sensibilidad ×2, 10 ratificados ×2, X→Y |
  | C | 600 s | 11.83 s | 6 perturbaciones ×2 pasadas; intentos rc=4 contados |
  | V | 360 s | **0.00 s** | RESERVADO a Architect/verifier; no consumido |
  | I | 900 s | 645.44 s | colección ×5, ruff, fast ×2, normativa ×2, commit ×2, integridad |
  | PUB | 180 s | 0.00 s | hooks/commit/push pendientes de dictamen |
  | Total | 3840 s | ≈1228.3 s usados (más V reservado) | sin transferencias entre sobres |
- **Incidentes** (todos registrados): (1) bug propio de f-string en
  `lanzador22.py` que invalidó el primer lote de 36 corridas (26.4 s cargados,
  re-ejecutado; lote archivado en `A/incidentes/`); (2) tres intentos rc=4 de
  perturbaciones de catálogo antes de existir el oráculo (contados); (3) los 7
  fallos de la primera suite normativa eran de PATH (herramientas no
  encontradas), no del árbol: con el PATH canónico pasan 1360/1360; (4) dos
  errores de ruta propios en scripts auxiliares, corregidos sin efecto sobre
  la evidencia (los pasos repetidos se contaron en el ledger). Los totales
  gastados incluyen todos los reintentos.
- **Verificación independiente**: PENDIENTE. V=360 s reservado en exclusiva
  a Architect/verifier (dictamen previo al commit); este registro no consume
  V ni delega un segundo verifier sin coordinación.
- **Arnés para V** (reejecuciones independientes sin tocar el ledger
  sellado): `herramientas/v-run.py` (cap 360 s; ledger propio
  `V/00-ledger-v.csv`, estado `V/v-state.json`) y `V-COMANDOS.md` con los
  comandos exactos por familia (control ORIGINAL, sensibilidad de los 29,
  ratificados de los 10, atribución histórica sellada, fronteras). Las
  copias `mutants-sens` y `mutants-22` permiten reejecutar sin reconstruir
  nada; el lanzador verifica hashes en cada paso.

## 8. Sellos históricos frente al sucesor y publicación separada

- **Recálculo material del sello R21** (sin heredar conteos): manifiesto con
  253 miembros + 1 cabecera; **252 OK, 1 divergente
  (`logs/00-ledger-guardian.csv`)**. El ledger diverge de forma puramente
  aditiva: 67 líneas / 5182 bytes / 67 LF; el **prefijo sellado de 63 líneas**
  reproduce exactamente el digest del manifiesto (`aecf6bb2…`) y las **4 filas
  post-sello** son `PUB02-commit` (start/end) y `PUB03-push` (start/end). Se
  corrige así el conteo heredado de «5 filas»: las filas efectivas añadidas
  son 4. El original se conserva; no se presenta como íntegro.
- Sello R20: se mantiene la caracterización de R21 (79/80 miembros OK; única
  divergencia aditiva del ledger con prefijo sellado de 907 líneas íntegro +
  filas post-sello de verifier/publicación), usada como evidencia separada.
- El sello sucesor de este incremento quedó producido:
  `MANIFIESTO-REANCLAJE22.sha256` (miembros del expediente, sin auto-hash;
  digest y política en `NOTA-SELLO-22.txt` FUERA de los miembros). Excluidos
  por política (identidad por otras vías): `tree/` (base git b7604c8 + hashes
  en `sello-candidato-22.json`), `mutants-22/` y `mutants-sens/`
  (instrumentado sellado R20), `perturb-C/` (hashes en
  `C/perturbaciones-C.json`), `logs-pub/` y `SELLO-*` (publicación separada).
- Ledgers separados por mandato: el ledger sellado de presupuestos
  (`logs/00-ledger-guardian.csv`) no recibe filas de PUB ni de V; la
  verificación usa `V/00-ledger-v.csv` (vía `herramientas/v-run.py`) y la
  publicación usará `logs-pub/`.
- Publicación con ledger distinto desde el inicio (PUB01…), sin re-añadir PUB
  a archivos sellados; commit de tests y commit documental separados; sin
  `git add -A`, sin bypass, sin force push; PR #56 permanece en borrador.
  Estado actual: **revisión de Architect PENDIENTE; sin autorización de
  commit/push** (respuesta `msg_bd5b19b570ce`: candidato congelado, sin
  repetir baterías, V reservado).

## 9. Drift medido y CI real

- **Integridad re-medida** sobre el candidato: `wct integrity check` →
  **36 hallazgos = 2 «modificado»** (`governance/lint/vulture_whitelist.py`,
  `tools/wct/accept/mutation_cases.py`) **+ 34 «nuevo protegido»** (módulos
  `pytest_*` de evidence y `mutation_policy.py`); idéntico al inventario de
  R21 sobre la misma base ⇒ **delta de este incremento = 0** (solo tests y
  docs dentro de allowlist; ningún patrón protegido nuevo). G-META-1 es el
  único rojo del tier commit y queda como rojo declarado de la PR; el bless
  NO corresponde a este encargo.
- **CI real**: se observará sobre el SHA publicado tras el push autorizado y
  el dictamen; se reportará el resultado observado y, si integridad bloquea
  los pasos siguientes, se declararán NO EJECUTADOS. Sin pronóstico
  post-bless. Restricción de entorno declarada: `gh` no está instalado en
  este host; si no hay método de observación disponible, se reportará como no
  observable con la evidencia real del push (refs y salida de git).

## 10. Estado: candidato reparado listo para recampaña

- Los 29 objetivos B2 tienen sensibilidad sustentada por su obligación
  prevista; las 10 ratificaciones se comprueban; los 131 quedan acreditados
  individualmente; los controles de módulo (matriz, catálogo, perturbaciones)
  son fieles e independientes.
- **Dictamen técnico de Architect: FAVORABLE a la reparación Y2** (gate real
  20 PASS + G-META-1 único rojo; drift 36 = 2+34; V independiente muestreada).
  NO cierra L8/beta3, NO declara conformidad retroactiva de custodia y NO
  autoriza publicación todavía (ver §14).
- **L8 NO queda cerrado**: falta la recampaña completa posterior (no
  autorizada aquí) y el bless sigue fuera de este encargo.
- Residuo exacto: ninguno pendiente dentro del alcance autorizado. Fuera de
  alcance (no ejecutado): recampaña completa, binding PA01–PA12, otros lotes,
  los 928 IDs, bless, merge, bump, tag, release.

## 11. Prompt preparado (NO ejecutado) para la recampaña L8

> **REANCLAJE-23 — Recampaña L8 única sobre el candidato reparado (NO
> EJECUTAR sin autorización humana).** Base: candidato congelado del
> expediente `build/tmp/reanclaje22-20260921/` (tests `00c17eea…`/`03034dd4…`,
> selección 605 nodeids digest `284b7e81…`, fuentes == sellos R20). Ejecutar
> UNA campaña completa de los 398 IDs sobre copy con raíz Git propia y
> venv propio, con: selección congelada (605 nodeids ∪ ningún añadido
> posterior), activación de `MUTANT_UNDER_TEST` dentro del proceso antes del
> primer import (lanzador fail-closed heredado, sin `mutmut run`), causalidad
> por fase (fallo de test vs error de colección, con `--tb=long` por ID),
> timeout por ID y presupuesto propio estimado por calibración previa (no
> heredado), puerta previa independiente (dictamen favorable antes de la
> campaña), ledger por ID y reconciliación generado==autorizado==ejecutado==
> resultados==398. La expectativa eventual **388 killed + 10 survived** es
> SOLO una hipótesis comprobable, condicionada a que las premisas de las diez
> equivalencias sigan confirmadas; nunca se reconstruye sumando campañas ni
> se impone al instrumento. Entregables: bruto reconciliado, tabla sucesora
> frente a R20/R21/R22, presupuestos con residuo, sellos y CI observada.
> Sin bless, sin merge/bump/tag/release, sin otros lotes.

## 12. Iteración Y2 — correcciones aprobadas, arnés sucesor y verificación acotada

Autorizada por Architect (sin publicación): (a) arreglar el arnés/documento
para reproducir A con copia histórica independiente; (b) añadir eventos y
tail contractuales al test de frontera de cabecera; (c) corregir el
fundamento de la ratificación `consume_header` 10/13. Techos de esta
iteración: A 45 s · B 300 s · C 20 s · I 245 s · V 0 · PUB 0 (techos dentro
del saldo original; el ledger sucesor `logs-it2/00-ledger-guardian.csv`
hereda el gasto sellado y no lo resetea).

- **Arnés sucesor** (no sobrescribe el sello histórico): `lanzador22b.py`
  (en modo `sealed` verifica los tests históricos contra la copia
  independiente `tree-hist/`, clon en `b7604c8` con tests sellados; `tree/`
  sigue aportando fuentes e intérprete) y `guardian22b.py` (ledger/estado
  propios con gasto heredado). `V-COMANDOS-V2.md` corrige los comandos:
  los pasos con lanzador requieren `--cwd "$EXP"`; los pytest crudos usan
  `--cwd "$EXP/tree"`.
- **Corrección del test de cabecera**: se añaden los observables que
  faltaban — `events == ()` y `tail_sha256 == sha256(bytes enviados)` — en
  las ramas de 65536 (noncanonical_json) y 65537 (limit_exceeded), además de
  longitud efectiva con LF y consumo 0 ya presentes.
- **Corrección D-A**: el fundamento de `consume_header` 10/13 queda como
  convergencia por re-clasificación (mutante devuelve `(0, None)`,
  `decode_journal` continúa y `_consume_line` re-clasifica la MISMA línea),
  no por valor de verdad del flag (§3).
- **Resultados Y2 con el arnés sucesor** (`Y2/`):
  - A: acreditación del arnés — control ORIGINAL `sealed` rc=0 **580 passed**
    con LANZADOR-OK, y sonda `x_decode_journal__mutmut_1` rc=1 con trampolín
    y variante (`Y2/A/acreditacion-arnes-A.json`). Gastado A 12.11/45 s.
  - B: **29/29 sensibilidad** (rc=1, nodeid previsto fallando) y **10/10
    ratificados sobreviven** (selección completa) re-ejecutados sobre Y2 con
    `lanzador22b` (`Y2/B/sensibilidad-29-Y2.json`, `Y2/B/ratificados-10-Y2.json`).
    Gastado B 157.3093/300 s (incluye la cota P4 de 7.00 s en dos cargas).
  - C: **6/6 perturbaciones** re-ejecutadas con los tests Y2
    (`Y2/C/perturbaciones-C-Y2.json`). Gastado C 4.13/20 s.
  - I: colección **605 únicos == selección congelada**; focal ORIGINAL
    **579 passed**; G-FAST **7/7 PASS**; normativa canónica **1360 passed**;
    property **1 passed** por separado (`Y2/I/`). Gastado I 124.38/245 s.
  - **Residuo declarado**: el tier commit NO se ejecutó sobre Y2 porque no
    cabe en el techo I restante (quedaban 120.62 s y la corrida medida es
    ~117.4 s sin margen de timeout); no se prestó de V ni PUB. Su parte
    sustantiva queda cubierta por fast + normativa + property, y la medición
    de integridad/G-META-1 permanece como referencia del estado X/Y (no se
    presenta como medición final Y2).
- **Ejecuciones NO repetidas y fundamento (reutilización por identidad, no
  por semejanza)**: (1) los 95 A1 de R21 no se repiten: sus artefactos
  (instrumentado sellado R20, tests sellados, logs) no cambian con Y2 y la
  auditoría V de R21 los reconcilió; (2) V4 no se repite: identidad por hash
  en el manifiesto R21 y recálculo documental; (3) las 35 sondas A no se
  repiten sobre Y2: los tests históricos viven en `mutants-22`/`tree-hist`
  verificados contra el sello en cada corrida del lanzador, y Y2 solo cambió
  el test de cabecera del candidato (que no participa del camino A); el
  arnés sucesor se re-acreditó con control + 1 sonda; (4) las baterías X/Y/Y'
  se conservan como historia y NO se transfieren como resultado Y2; (5) las
  comprobaciones afectadas por el cambio de arnés SÍ se repitieron (29+10+6)
  sobre Y2.
- **Sello sucesor separado**: `MANIFIESTO-REANCLAJE22-Y2.sha256` +
  `NOTA-SELLO-22-Y2.txt` (no reescriben el sello X `5a274c6b…`, que sigue
  siendo el registro del estado pre-corrección). `ADENDA-22-A.md` documenta
  la transición X→Y2, hashes y política.

## 13. Revisiones de la auditoría independiente (coder2) — P1–P4 incorporadas

- **P1 — X→Y2 registrado, sin sobrescribir el original**: el cambio de hash
  del test de schema `00c17eea…` (X) → `6720bde6…` (Y2) corresponde a la
  corrección autorizada (eventos/tail); no es evidencia por sí sola de
  alteración histórica. El sello X (`MANIFIESTO-REANCLAJE22.sha256`, digest
  `5a274c6b…`) no se reescribe; el sello sucesor Y2 es separado
  (`MANIFIESTO-REANCLAJE22-Y2.sha256` + `NOTA-SELLO-22-Y2.txt`) y la
  transición queda registrada en `ADENDA-22-A.md`.
- **P2 — correcciones iniciales omitidas, documentadas** (ambas PREVIAS a
  cualquier medición; no son transferencias X→Y por parecido):
  (a) `_padded_header` comparaba `HEADER_LITERAL` (str) con bytes y producía
  `TypeError` en la primera corrida focal; corregido con
  `_CONTRACT_HEADER_BYTES = HEADER_LITERAL.encode()` (evidencia: corrida
  focal inicial con 6 fallos, registro B00; verde B01 de 577).
  (b) Tres filas de la matriz usaban strings donde `_enum` espera índice
  entero (`collection-report`, `phase-make`, `phase-log`); corregidas a los
  índices contractuales (1, 1, 2) antes de medir sensibilidad.
- **P3 — conteo físico de variantes de `ObservationError`**: reconteo sobre
  `custodia/instrumentado-R20-pytest_types.py` (hash instrumentado
  `f981c3db…`) = **3 variantes + orig**
  (`xǁObservationErrorǁ__init____mutmut_1/2/3`), **no 8**. La cifra «8» se
  heredó de la nota de R21 y se retira aquí. Precisión conservada: 0 IDs
  registrados en el inventario histórico; evidencia existente de code/field
  reutilizada; sin campaña nueva y sin modificar históricos.
- **P4 — intento abortado B03 reconstruido con cota acreditada, cargado
  UNA vez**: evidencia: filas 351/354 del ledger sellado (dos `start` para
  `B03-original-focal-Yprima` con saldo 939.65 repetido) y una sola fila
  `end` (8.09 s, saldo 931.56); `I/B/logs` inexistente y sin log de la
  primera corrida ⇒ el primer `start` abortó en `log_file.open('wb')` antes
  de `Popen`. La ausencia de `Popen` NO se usa sola como cota: la cota
  temporal superior acreditada es el intervalo entre ambos `start`
  (14:08:29 → 14:08:35 = 6 s) **+ 1 s de resolución = 7.00 s**. Cargado en el
  ledger sucesor (`logs-it2/00-ledger-guardian.csv`) en dos filas que suman
  la cota una sola vez: `B2-recarga-B03-abortado` (1.00 s inicial) y
  `B2-recarga-B03-delta-cota` (6.00 s de delta), sin resetear saldos ni tocar
  el ledger sellado. Resultante: gastado B it2 157.3093 s ⇒ gasto total
  B 422.3229 + 157.3093 = **579.6322 s** y saldo **620.3678/1200**.
- **Frontera de cabecera 14 vs 15/16 (precisión)**: `consume_header_14`
  (`header_end - 1 >`) se discrimina en el **exceso** (65537:
  `noncanonical_json` en vez de `limit_exceeded`); `consume_header_15`
  (`+2 >`) y `16` (`+1 >=`) se discriminan en el **exacto** (65536:
  `limit_exceeded` en vez de `noncanonical_json`).
- **Hasheos: original e instrumentado, sin confundirlos**:

  | Fuente | Original (sello R20) | Instrumentada (sello R20) |
  |---|---|---|
  | `pytest_types.py` | `b2b2b05c…` | `f981c3db…` |
  | `pytest_builders.py` | `cb0ea790…` | `f3252d1a…` |
  | `pytest_schema.py` | `899ad41a…` | `b53db023…` |
  | `pytest_inventory.py` | `c9086154…` | `cb9c86d7…` |

- Sin cambios de tests por estas revisiones: son documentales (allowlist) y
  no alteran el estado Y2 ya congelado.

## 14. Dictamen técnico, verificación V independiente y estado final de la entrega

- **Dictamen técnico de Architect**: FAVORABLE a la reparación Y2; NO cierra
  L8/beta3, NO declara conformidad retroactiva de custodia y NO autoriza
  publicación todavía. PR #56 observada por Architect con gh nativo: OPEN,
  draft=true, head=b7604c8, rama correcta, base main. La CI la observará
  Architect sobre el SHA publicado.
- **Gate real sobre Y2** (iteración 3; ledger `logs-gate/`): rc=1;
  `21 gates: 20 PASS · 0 SKIP · 1 FAIL/ERROR`; único rojo **G-META-1**
  (295 ms; `modificado: governance/lint/vulture_whitelist.py`); G-LINT,
  G-FMT, G-TYPE, G-TEST y G-INTROVERT PASS. Drift medido: **36 = 2
  modificados + 34 nuevos protegidos**, con ruta y sha256 de cada uno en
  `logs-gate/gate-resumen.json`; gasto 108.08 s con reserva 120 s, sin
  timeout ni reintento.
- **Verificación V independiente** (Architect; ledger `V/00-ledger-v.csv`):
  **75.3145/360 s** (saldo 284.6855), 17 pasos. Muestras: V07 manifiesto Y2
  74/74; V08 A-original sealed 580 passed; V09 A mutante
  `x_decode_journal__mutmut_1` rc=1 con traza in-process; V10 original
  instrumentado Y2 605 passed; V11 `consume_header_16` rc=1 (frontera
  exacta); V12 `build_execution_end_46` rc=1; V13 `finding_2` rc=1;
  V14 muestra de ratificación (`consume_header_10`, 605 passed; NO es
  reejecución independiente de los diez); V15 sello X preservado 200/200;
  V16 manifiesto Y2b; V17 manifiesto GATE. Las sensibilidades muestreadas
  fallan por la obligación prevista, no por errores de colección.
- **Diferenciación de evidencia (coder vs V)**: los **131** (95 de R21 + 35
  sondas + 1 V4) son evidencia del coder con la auditoría V de R21 y el
  recálculo documental; V muestreó la vía A (V08/V09). Los **29** objetivos
  tienen sensibilidad del coder contra su obligación prevista; V muestreó 3
  familias (header16, wire46, finding2). Los **10** ratificados tienen
  comprobación del coder (10/10 sobre selección completa); V muestreó 1
  (`consume_header_10`). Las **6** perturbaciones de módulo son evidencia del
  coder. Nada se transfiere por semejanza.
- **Incidente de custodia, sin eufemismo y sin autorización retroactiva**:
  la iteración correctiva editó **5 miembros del sello Y2**; Y2 ya **no
  verifica íntegro** (5 FAILED) y **los bytes originales de esos miembros NO
  se conservan como copia verificable**: solo permanecen sus hashes en
  `MANIFIESTO-REANCLAJE22-Y2.sha256` y la caracterización en
  `NOTA-CORRECCIONES-Y2.md` y `NOTA-CUSTODIA-Y2.md`. Eso no es un sello
  íntegro, no hay conformidad retroactiva y no legitima futuras ediciones de
  miembros sellados. El estado corregido se cubre con Y2b.
- **Sellos a la entrega**: X `MANIFIESTO-REANCLAJE22.sha256` 200/200
  (`5a274c6b…`), intacto; Y2 74 miembros en la entrega con 5 divergencias
  documentadas (`a0211b90…`); Y2b 75/75 (`8ed6a293…`); GATE adicional 10/10
  (`bfbbfe67…`). Ningún manifiesto se reescribe.
- **Presupuestos finales exactos** (míos; gasto = sellado + it2 + it3):
  A **160.8072**/600 (saldo 439.1928) · B **579.6322**/1200 (620.3678) ·
  C **15.9573**/600 (584.0427) · I **877.9059**/900 (22.0941) · V propio 0
  (el V independiente es de Architect: 75.3145/360) · PUB de esta fase en
  ledger nuevo (saldo se declara en la entrega).
- **Preparación de recampaña: NO ejecutada** (prompt REANCLAJE-23 en el
  expediente; campaña futura condicionada a autorización, calibración y
  puerta previa; la expectativa 388/10 es hipótesis comprobable).
- **Estado de publicación**: PENDIENTE de dictamen final. Preparada en la
  copia Git aislada nueva `publicacion/tree` (misma base `b7604c8`, tests Y2
  byte-idénticos, solo los 2 docs de allowlist actualizados), hooks
  instalados/activos sin bypass, staging explícito de 4 rutas,
  `git diff --cached --check` limpio y freeze de hashes fuera del árbol
  mutable. Sin commit/push.

## 15. Trazabilidad de evidencias (rutas)

- Frente A: `build/tmp/reanclaje22-20260921/A/` (`residuo-22.json`, logs,
  `incidentes/`), `decisiones/A-tabla-131-r21.json`, expedientes R20/R21.
- Frente B: `B/` (`sensibilidad-29.json`, `sensibilidad-29-resumen.json`,
  `ratificados-10.json`, logs `B1xx/B2xx`, `incidentes/`).
- Frente C: `C/` (`perturbaciones-C.json`, logs), `perturb-C/` (desechable,
  restaurada y hasheada antes/después).
- Integración: `I/` (colección, integridad, gates), `B/logs/B0x-*`.
- Verificación independiente: `herramientas/v-run.py`, `V-COMANDOS.md`,
  `V/00-ledger-v.csv` (propio de V), `V/v-state.json`.
- Sellos y custodia: `MANIFIESTO-REANCLAJE22.sha256`, `NOTA-SELLO-22.txt`,
  `custodia/`, `sello-candidato-22.json`,
  `I/integridad-y-sellos.json`, `guardian-state.json`, `logs/00-ledger-guardian.csv`.
