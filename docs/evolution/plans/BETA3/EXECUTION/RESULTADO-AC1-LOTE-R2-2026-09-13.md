# AC1 lote R2 — mutación del núcleo puro de accept/ (2026-09-13)

Estado: **FAIL-survivors-stop**. El lote queda entregado con su inventario de
supervivientes preservado para la próxima adjudicación; **no se adjudican aquí**,
no se avanza a aceptación/CRAP/DRY/tier full y AC1 no se declara acreditado.
No bless, merge, tag ni bump. (La denominación «lote r2» es la secuencia de
lotes de mutación de código —r1, r1b, r2, r2b— y no guarda relación con el
delta R2 de reparación de baseline.)

Alcance autorizado (punto 6 del encargo): siguiente lote de mutación de código
pendiente. Selección del arquitecto: núcleo puro de `accept/` — `parsing.py`,
`ir_checks.py`, `semantic.py`, `generation.py`, `mutation_cases.py` (22
funciones AST; 486 sitios) — dejando el transporte (`campaign.py`,
`process.py`, `pytest_receipt.py`, `pipeline.py`) y `gate/*` para lotes
posteriores.

## Corrida 1: `mutation-code-lot-r2` — defecto de receta detectado

Receta: foco `test_accept_pipeline.py` + `test_accept_verdict.py`; runtime
original `sh-p01-CND-80B8`; serial; presupuesto 3600 s; 58,2 s.

Resultado bruto: 486 sitios = **413 killed + 22 survived + 51 no-tests**.

Los 51 no-tests son **todas** las mutaciones de `semantic.py` (sus tres
funciones `phase_status`, `_failure`, `scenario_status` no tienen asociación
con los tests de esa selección). Es un **defecto de la receta de esta
corrida** — el fichero focal natural de `semantic.py` es
`tests/unit/test_accept_pytest.py`, omitido en la selección inicial — y no un
hallazgo de producto. Se conserva la corrida completa como parte del
expediente y se corrige repitiendo el lote.

## Corrida 2: `mutation-code-lot-r2b` — selección corregida (autoritativa)

Copia nueva con `test_accept_pytest.py` añadido a la selección (119 tests
focales, preflight PASS); no se reutilizan veredictos de r2. Runtime y receta
idénticos en lo demás; 523,2 s.

Resultado bruto: 486 sitios = **462 killed + 24 survived + 0** en
no-tests/timeout/suspicious/skipped/error. La corrección de selección convirtió
los 51 no-tests en 49 killed + 2 survived; ninguna clase distinta apareció.

## Inventario de supervivientes (24, sin adjudicar)

| Grupo | IDs |
|---|---|
| `parsing` (17) | `xǁ_Parserǁ__init____mutmut_2/7/8`, `xǁ_Parserǁ_scenario__mutmut_18`, `xǁ_Parserǁ_examples__mutmut_13`, `xǁ_Parserǁ_header__mutmut_17–23`, `xǁ_Parserǁrow__mutmut_11/18/21/22`, `x_parse_feature__mutmut_9` |
| `generation` (3) | `x_scenario_names__mutmut_14`, `x_generate__mutmut_3`, `x_generate__mutmut_63` |
| `mutation_cases` (2) | `x_mutations__mutmut_7`, `x_mutations__mutmut_9` |
| `semantic` (2) | `x_phase_status__mutmut_3`, `x_phase_status__mutmut_4` |

Los 22 supervivientes de la corrida 1 persisten idénticos en la corrida 2; los
2 de `semantic` solo pudieron observarse al corregir la selección. Diffs
individuales preservados en `mutation-code-lot-r2b-survivor-diffs.log` para la
adjudicación del próximo incremento, que deberá distinguir: hueco de aserción,
equivalente demostrado, comportamiento no contratado o defecto de receta (en
`semantic`, verificar primero si el fichero focal cubre realmente esas
funciones).

## Evidencia local (sin custodia externa)

Bajo `build/tmp/ac1-r2-qualification/evidence/` del worktree de la PR:

| Artefacto | SHA-256 |
|---|---|
| Plan r2 | `8c3572e8ea4f6ccfcebd9ff50f9d59bda8f0daf0936bcfcc8e7db8aba1feaf5b` |
| Preflight r2 (89 PASS) | `fd06990e173b8f3ec02fe8c07527cf1d4179e93eeccf17997d5e26e18c489195` |
| Metadatos r2 | `45e7255fd1c315d4afec67a659dccd7132d845d4e43714e6b26f75277ec6d792` |
| Log crudo r2 | `1f47f9c071ae166c5b3e726e50a3c99dd12c17ba6055a16a2c1612fd22099304` |
| Resultados completos r2 | `b5d2b3090c4beeabf798b0e8674f9561c49094cebd3357686233a04f4fd95e30` |
| Diffs r2 (22) | `f83d1ff8602099b61c81e5c4770591082fcf110899e794b66a66d6710bc446d6` |
| Reconciliación r2 | `225358094b113c5bf2f11ca4a67da76656c3cf9d186ad830e042203ac43e808b` |
| Plan r2b | `34243faf14af68a253732e682e38afde2dd7fc91a41825bdc4cb9ac017bc4869` |
| Preflight r2b (119 PASS) | `e53e11cee19f9ba5303889bbadbe4fb1b14bad43226ffca4f4bc8914c9e6e2fa` |
| Resultados completos r2b | `bd48c8dfe6cf2726fe4869855c11b3104338e6375fd58ece3f47f981340d43df` |
| Log crudo r2b | `1de66473c5067fc0593b5d082223f5f1f0f77888e20c046eaf5285e9dffd0770` |
| Diffs r2b (24) | `09408e7237cfabb4b4657c47e950a54a5cc95070f95719e04a228e31427811d6` |
| Reconciliación r2b | `d7658739162bc44077cf2562147b82c43db7fe65d8bd83481f7b65b7c4ed1876` |
| Metadatos r2b | `09a6521576b1761a923d97ff75bcab997b4b2d8599ee5e3ac190be366c2d08c6` |

Nota: la primera versión de esta tabla citó dos hashes erróneos (metadatos y
diffs de r2 compartían el mismo valor, y faltaba el log crudo); se corrigió
recalculando sobre los archivos en disco antes del commit. El error fue de
transcripción del documento, no de los artefactos.

## Siguiente decisión necesaria

Adjudicar los 24 supervivientes (incremento siguiente, mismo método que L1:
diffs, pruebas focales, sondas y verificador independiente). Solo tras cerrar
este lote y el de transporte corresponde evaluar los controles posteriores.
