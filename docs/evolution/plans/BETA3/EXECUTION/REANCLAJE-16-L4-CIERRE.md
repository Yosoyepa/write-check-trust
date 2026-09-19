# Acta REANCLAJE-16 — cierre de L4 por resultado medido y adjudicación explícita (2026-09-19)

Estado: **«L4 conforme por resultado medido y adjudicación explícita».** Una
única campaña completa sobre el candidato congelado `96253b8` produjo
**473 = 446 killed + 26 survived + 1 timeout**, exactamente la expectativa
medible. NO se declara «todos killed», NO PASS de G-MUT, NO calificación
integral de P03a, NO cierre de beta.3. Los 26 sobrevivientes quedan
disputados por ratificación explícita; el timeout conserva estado bruto y
admisión causal separada (D-C).

## 1. Identidades

| Elemento | Identidad |
|---|---|
| Base del encargo | `ae67ae0a44c864311185c299f26cb710d34edce1` == remoto == headRefOid PR #56 (borrador); merge-base con main `8a379d64…` = main; sin avance |
| Candidato técnico congelado | `96253b8bb5196e57d19af27c22bfec40094a441f` (commit local del expediente; hooks instalados y verificados ANTES de crearlo, evidencia en `logs-pub/`; push diferido al dictamen) |
| Fuentes selladas | las 3 de L4 idénticas al corte técnico `0487448…` (`ed6f6bc1…`, `d73b5b26…`, `01447409…`) |
| Selección de campaña | 164 = 161 (R15, digest `51674414…`) ∪ 3 controles de módulo; intersección 0; digest `85d6f4b1388e0711bc0cb96c97c389d7e3899442130bb08e6b0edf4505846d78`; ORIGINAL 164 passed, 0 fallos/skips/xfails |
| Instrumento | `run-campana/` desde `git archive 96253b8`; pyproject original `f27de519…` / experimental `798883ba…` (source_paths = exactamente las 3 fuentes; selección 164); generación pura con firma admisible (filtro sin coincidencias tras «done»); inventario 473==473 POR CONJUNTOS; los 3 instrumentados BYTE-IDÉNTICOS a los sellados R12 (los 473 cuerpos de mutante idénticos, diffs sellados aplican por transitividad); runtime mutmut 3.7.0 del venv acreditado |
| Controles previos | baseline ORIGINAL 164/164; canario `check_sequence_7` rc=1; negativos id-desconocido y selección-vacía rc=2 (abortan antes de evidencia) |

## 2. La única campaña

`python -m mutmut run --max-children 1 <473 IDs explícitos del inventario>` —
sin globs, un resultado por ID, sin reparaciones intermedias, serial. Duración
**469.78 s** (sobre B ≤ 1200). Reconciliación: generado == autorizado ==
resultados == 473, cero duplicados/ajenos/faltantes/ocultos.

| Bruto | R12 (sellado) | R16 (medido) |
|---|---|---|
| killed | 426 | **446** |
| survived | 46 | **26** |
| timeout | 1 | **1** |
| total | 473 | **473** |

**Transiciones: exactamente 20, todas 0→1, sin ninguna otra** (logs/11):

- **8 por ampliación de selección** (matados por los 12 PA09/PA10 incorporados;
  sensibilidad medida por R13 logs/06 y confirmada en campaña):
  `decode_event_59/65`, `inventory_key_2/5/6/7/13/14`.
- **12 por oráculos fieles R14/R15** (test y causa acreditados por sonda
  individual en R14 logs/05-06 y confirmados en campaña):
  `attributed_execution_3`, `execution_index_3/5/7/8` (ex no-entero →
  invalid_field sin crash), `decode_event_3` y `bad_execution_1`
  (vector-objeto en evento y en cabecera), `check_sequence_1` (seq=0),
  `check_sequence_7` y `advance_local_11` (fronteras exactas SEQ_MAX),
  `validated_vector_19/20` (índice > SEQ_MAX, precedencia 3-antes-que-4).
  Los tres `resolve_field_nodeid_6/7/8` NO están aquí: quedan survived bajo
  D-A2.

**Sin residuo nuevo**: los 26 sobrevivientes son EXACTAMENTE los 26
ratificados (12 D-A + 11 D-B + 3 D-A2 del acta de decisiones); ningún
sobreviviente fuera de lo ratificado; ninguna equivalencia ratificada divergió
(condición de suspensión no activada). `consume_line__mutmut_22` volvió a
registrar timeout (−24): el bruto conserva su estado y la admisión D-C
(no-terminación causal demostrada) queda registrada SEPARADAMENTE del killed
bruto. FAIL-RESIDUO-STOP no aplicó: no hubo residuo. Sondas posteriores (C):
**0 necesarias** — los 20 nuevos kills tienen test, causa, fase y activación
acreditados por las sondas previas de R13/R14 y los logs de campaña; el
verifier final reejecutó muestras discriminantes (ver §5).

## 3. Controles de módulo (D-D) y conciliación de sitios uno a uno

| Sitio | Disposición | Evidencia |
|---|---|---|
| `expected_seq=1` | control conductual independiente (no mutante) | R14 test primer-seq≠1 + perturbación |
| Tope 10000 inventarios | frontera REAL medida | `test_wire_inventory_cap_at_the_real_boundary` (10 000/10 001), preexistente |
| Tope 20000 declaraciones | frontera REAL medida (§3 l.157) | `test_declaration_cap_at_the_real_boundary_20000` NUEVO: 20 000 exactas pasan (prefijo completo, tail None); 20 001 → limit_exceeded con prefijo y tail conservados |
| `_CATALOG` (DictComp events) | transcripción + consumo posicional | `test_event_catalog_derivation_is_exact_and_consumption_positional` NUEVO (ancla CONTRACT_EVENT_CATALOG de la especificación) |
| `_CAPPED` (5 entradas sequence) | inventario independiente + comportamiento | `test_capped_table_transcribes_contract_and_membership_separates_counters` NUEVO (pertenencia separa contadores; PA09/PA10 cubren el consumo) |
| Docstrings de módulo/clase (5) | documentación, sin equivalencia inventada | R14 §8; sin efecto conductual identificado |

Los tres tests nuevos nacieron verdes (caracterización); sensibilidad
demostrada por perturbación de UNA línea en copias desechables (omisión de
correspondencia en la derivación, intercambio de clave en _CAPPED, off-by-one
`>=`→`>` del tope): rojo en los tres (logs/03). Las perturbaciones NO son IDs
de mutmut ni se suman al inventario de 473.

## 4. Correcciones documentales (encargo §3)

(a) Los 26 ratificados CAMBIAN DISPOSICIÓN (RATIFICADA-EQUIVALENTE), no
resultado: siguen survived en el bruto. (b) Capas separadas: causalidad
demostrada ≠ estado bruto timeout ≠ admisión D-C; un eventual rechazo de la
admisión no convertiría el caso en fallo instrumental. (c) Los 9.71 s del
verifier R15 se midieron UNA sola vez (su ledger); el doble conteo era solo de
presentación agregada en R15 §10; total R15 = **293.54 s** por componentes
redondeados (**293.55** si se suman los crudos y se redondea al final —
diferencia 0.0094 s de presentación, registrada). Sin pruebas repetidas.

## 5. Gates, presupuestos, incidentes, dictámenes

- **Batería (candidato)**: colección 1209 (reconciliada +3), focales 426,
  normativa 1208 passed + 1 deselected, property 1, ruff limpio (invocación
  del gate), **fast rc=0**, commit **20 PASS · 1 FAIL**: G-META-1
  recalculado por rutas y hashes = **36 rutas heredadas** (2 «modificado» +
  34 «nuevo protegido»; ninguna del delta; main limpio). Fuera de allowlist;
  requiere intervención humana (SEC-005); NO se ejecutaron Q-ACCMUT,
  cobertura/CRAP/DRY/full (prohibidos aquí).
- **Presupuestos** (cada ejecución cargada una sola vez): M 11.87/600 ·
  A 22.54/300 · B 469.78/1200 · C 0/600 (sin sondas necesarias) · V 23.30/240
  en los ledgers de los verifiers (puerta previa 3.70 + final 19.60; el sobre
  V del guardián quedó en 0 y el gasto real vive en los ledgers citados — sin
  doble carga) · I 376.81/900 · PUB 6.69 s en `logs-pub/` (hooks + commit del
  candidato; el sobre PUB del guardián, 0, no se usó para evitar escritura
  post-sello). **Total ≈ 911 s de 4020.** Intentos inválidos: 0.
- **Incidentes**: ninguno instrumental. Hooks instalados y verificados ANTES
  del primer commit de este encargo (evidencia `logs-pub/pub01`), ejecución
  real en el commit del candidato (`pub02`: «WCT fast gate… Passed», «
  Conventional commit message… Passed»). El commit se creó ANTES de la
  campaña para congelar el candidato por SHA; el push quedó diferido al
  dictamen (si la puerta hubiera rechazado, el commit habría permanecido
  aislado en el expediente).
- **Dictámenes**: auditor de decisiones — SIN DISCREPANCIAS (26/26 vs sellos;
  inercia D-B diff a diff). Verifier de puerta previa — **APROBADA** (muestreo
  de IDs, controles fieles, selección/instrumento/inventario verificados,
  canario y negativos reejecutados). Verifier final — **FAVORABLE** (recalculó
  446/26/1 y las 20 transiciones; reejecutó 3 kills discriminatorios rc=1 por
  aserciones contractuales, un ratificado con las 164 rc=0, ORIGINAL de
  módulo; cadena de identidad cmp; G-META-1 36 rutas). Informes en
  `…-verifier-puerta/` y `…-verifier-final/`.

## 6. Disposición final por ID (resumen)

446 KILLED (426 históricos conservados + 20 nuevos: 8 selección, 12 oráculos)
· 26 SURVIVED con disposición RATIFICADA-EQUIVALENTE (12 D-A zip-strict/getattr
default/clave basura/slice; 11 D-B canal inerte; 3 D-A2 rama inalcanzable) ·
1 TIMEOUT con admisión D-C por no-terminación causal (bruto intacto). Capa de
admisión separada del bruto en todos los casos.

## 7. Publicación

Con dictamen favorable: push de `96253b8` (tests) + commit documental (actas
DECISIONES y CIERRE) a `codex/reanclaje-p03a-fase1`; staging por rutas
explícitas con inspección de `--cached`; conventional + byline; **PR #56
permanece en borrador**. CI observada: los pasos omitidos por integridad son
NO EJECUTADOS; sin pronóstico post-bless. El resultado real se reporta en la
entrega.

## 8. Estado de L4 y siguiente lote (PROPUESTO, no ejecutado)

**L4: CONFORME por resultado medido y adjudicación explícita.** Con el bruto
446/26/1 y las disposiciones anteriores, el lote L4 del decoder queda cerrado
en los términos admisibles de este encargo. Pendientes EXTERNOS a L4 (no
otorgados aquí): G-META-1 (36 rutas) exige decisión humana de gobernanza antes
de que la CI del PR pueda verdear; Q-ACCMUT, cobertura/CRAP/DRY/full y la
calificación integral de P03a/beta.3 siguen prohibidos y pendientes de sus
propios encargos.

> **Propuesta REANCLAJE-17 (no ejecutar sin encargo):** (1) decisión humana
> sobre `governance/integrity.lock` del PR #56 (refrescar el lock con los 34
> módulos P03a + 2 modificados, o revertirlos) para desbloquear la CI; (2) con
> L4 cerrado, encargo de Q-ACCMUT sobre el lote del aceptación (mutación de
> Gherkin) con sus propios sobres y puerta previa; (3) expediente de
> calificación integral P03a (cobertura/CRAP/DRY/full) sobre el candidato
> publicado. Prohibido trasladar ratificaciones entre lotes.
