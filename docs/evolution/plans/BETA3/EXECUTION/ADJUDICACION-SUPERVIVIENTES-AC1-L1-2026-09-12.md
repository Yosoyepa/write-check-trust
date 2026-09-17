# Adjudicación de los 30 supervivientes — lote AC1 L1 (2026-09-12)

Estado: adjudicación técnica propuesta, **pendiente de ratificación humana**. No
acredita AC1, no autoriza bless, merge, tag, bump ni release. La PR #53 sigue en
borrador. Cumple el encargo acotado: sin ampliar la campaña y sin modificar
producto. Base de la PR: `88de60e329f8c2b501c689c090c71824a3f70116`.

Fuente de verdad de la campaña: `RESULTADO-AC1-R2-REANUDACION-2026-09-13.md` y
`MANIFIESTO-AC1-R2-REANUDACION-2026-09-13.json` (mismo directorio). Este
documento no los reemplaza: los verifica y corrige un punto de su narrativa.

## 1. Ubicación real del expediente

La ruta `build/tmp/ac1-r2-composition` citada en la PR no está en el checkout
principal porque la rama de la PR vive como **worktree del propio repositorio**,
no como checkout externo:

- Worktree: `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration`
  (`codex/beta3-ac1-r2-integration` @ `88de60e3`, sincronizada con `origin`).
- Mapa de composición (39 entradas): `build/tmp/ac1-r2-composition/evidence/composition-source-map.tsv`
  (relativo a ese worktree).
- Expediente de cualificación: `build/tmp/ac1-r2-qualification/evidence/`
  (relativo a ese worktree).

Verificación de los 7 artefactos declarados en el manifiesto — todos los
SHA-256 coinciden con los bytes en disco:

| Artefacto | SHA-256 declarado | Verificación |
|---|---|---|
| Plan de campaña (`mutation-code-lot-r1-plan.json`) | `66dbf02f…44c991` | COINCIDE |
| Preflight (`mutation-code-lot-r1-preflight.log`) | `a0178916…57622` | COINCIDE |
| Log crudo (`mutation-code-lot-r1-run.log`) | `ad6893d9…e09c91` | COINCIDE |
| Metadatos (`mutation-code-lot-r1-run.json`) | `1503078f…358ca48` | COINCIDE |
| Resultados completos (`…results-all.log`) | `38434d37…72a3248` | COINCIDE |
| Diffs de supervivientes (`…survivor-diffs.log`) | `0376c494…8c22824c` | COINCIDE |
| Reconciliación (`…reconciliation.json`) | `b73a4d52…48644832` | COINCIDE |

## 2. Conciliación del inventario: lote, no campaña integral

Reconteo independiente sobre `mutation-code-lot-r1-results-all.log` (498
líneas, una por sitio): **468 killed, 30 survived, 0** en timeout, suspicious,
skipped, no-tests y error. Coincide con el manifiesto. Sitios por módulo:
`receipt.py` 59, `receipt_validation.py` 140, `verdict.py` 130,
`verdict_validation.py` 169 = 498. Los 30 IDs de sobrevivientes del log
coinciden uno a uno con los grupos del manifiesto (receipt 2,
receipt_validation 0, verdict 12, verdict_validation 16).

**Alcance medido**: únicamente 4 módulos con 2 archivos de test focal (114
tests). Es un **lote**, no la campaña integral de AC1. Fuentes compuestas aún
sin medir por mutación de código: `accept/{campaign,generation,ir_checks,mutation_cases,parsing,pipeline,process,pytest_receipt,semantic}.py`,
`gate/{checks,runner,semgrep,semgrep_schema,semgrep_scope,semgrep_verdict}.py`,
`selftest/fixtures_tools.py` y sus tests asociados. Controles no ejecutados
tras el hallazgo: mutación de aceptación, cobertura/CRAP, DRY y tier full. La
CI de la PR falla en integridad (20 rutas protegidas de `tools/wct/**`) y no
llegó a ejecutar los controles posteriores; ese drift es esperado y sigue
pendiente de revisión humana — fuera del alcance de este documento.

## 3. Verificación experimental de las candidatas a equivalencia

Método: se ejecutó el **código mutante real generado por mutmut 3.7.0** — las
funciones `x__read__mutmut_23`, `x__read__mutmut_36`, `x__accounting__mutmut_14/17/18`
del árbol `mutation-code-lot-r1/mutants/` (el árbol físico de mutantes sobrevive
dentro del lote; el JSON de reconciliación lista los archivos instrumentados) —
contra la misma matriz de entradas que el original, comparando vectores de
comportamiento completos (resultado o excepción con tipo y mensaje).

- Runtime del experimento: Python 3.12.13, mutmut 3.7.0 (venv principal). La
  campaña L1 corrió con el runtime `sh-p01-CND-80B8` (Python 3.13.14). La
  diferencia se declara; las conclusiones descansan en semántica estable de
  `io`/`codecs` y en argumentos estructurales que no dependen del parche menor.
- `orig` de verdict = cuerpo `x__…__mutmut_orig` del mismo árbol generado, vía
  trampolino sin `MUTANT_UNDER_TEST`; mutantes de verdict vía
  `MUTANT_UNDER_TEST` (mismo mecanismo de despacho de la campaña).
- Evidencia: `/home/jandradeu/Documents/well_code_template/build/tmp/adjudicacion-ac1-l1/`
  — drivers `receipt_driver.py` (`1e40ab81…443b28`), `verdict_driver.py`
  (`72f9500a…896eb`), vectores y `summary.json` (`9cad81c6…823884`).

Resultado: **los vectores de los 5 mutantes son byte a byte idénticos a los del
original** (SHA-256 iguales: `f8030f77…` para los tres vectores de receipt;
`dd0ee9bf…` para los cuatro de verdict).

- `receipt.x__read__mutmut_23` (`RECEIPT_LIMIT + 1 → + 2`): matriz de 7 casos
  (LIMIT−1, LIMIT, LIMIT+1, LIMIT+2, LIMIT+100, multibyte, UTF-8 inválido) con
  salidas idénticas; en LIMIT+1 **ambas variantes rechazan** con
  `receipt exceeds byte limit`. Para un archivo regular, `read(n)` con
  `n ≥ LIMIT+1` es indistinguible bajo el chequeo posterior
  `len(raw) > RECEIPT_LIMIT`: cualquier archivo mayor que LIMIT produce
  `len(raw) > LIMIT` con cualquiera de los dos topes.
  **Corrección al relato de la PR**: no es un «hueco funcional». El test de
  frontera ya existe — `test_receipt_exact_byte_limit_and_one_byte_excess`
  (`tests/unit/test_accept_receipt.py:89`, aserción exacta en :94–99) — y pasa
  bajo el mutante, que es precisamente por qué sobrevive.
- `receipt.x__read__mutmut_36` (`"utf-8" → "UTF-8"`): los códecs son alias
  canónicos (`codecs.lookup("utf-8") is codecs.lookup("UTF-8")`), y hasta el
  mensaje de `UnicodeDecodeError` es idéntico. Ninguna entrada distingue ambas
  variantes.
- `verdict.x__accounting__mutmut_14/17/18` (`zip(strict=True)` → `None`,
  omisión, `False`): `_inventory` — invocada dos líneas antes en la misma
  función — lanza `results inventory` salvo que `len(results) == len(inventory)`;
  los casos de desajuste mueren antes de llegar al `zip` (verificado en la
  matriz). `strict` es inobservable: equivalente por precondición impuesta.

Estas son **equivalencias demostradas, no aprobadas**: el registro vigente
exige ratificación humana explícita; este documento no la concede.

## 4. Adjudicación por ID

Categorías: **EQUIVALENTE-DEMOSTRADO** (5) y **HUECO-DE-ASERCION** (25). No hay
«comportamiento no contratado» sin prueba asociada ni problema del
instrumento: los 25 restantes tienen test que ejercita el camino, pero con
aserción tolerante que por construcción admite la mutación.

| ID (mutmut) | Mutación | Categoría | Evidencia |
|---|---|---|---|
| `receipt.x__read__mutmut_23` | `+1 → +2` en tope de lectura | EQUIVALENTE-DEMOSTRADO | §3; test de frontera ya existente |
| `receipt.x__read__mutmut_36` | `utf-8 → UTF-8` | EQUIVALENTE-DEMOSTRADO | §3; alias canónico |
| `verdict.x__accounting__mutmut_14` | `strict=True → None` | EQUIVALENTE-DEMOSTRADO | §3; precondición `_inventory` |
| `verdict.x__accounting__mutmut_17` | `strict=True` omitido | EQUIVALENTE-DEMOSTRADO | §3; ídem |
| `verdict.x__accounting__mutmut_18` | `strict=True → False` | EQUIVALENTE-DEMOSTRADO | §3; ídem |
| `verdict.x__inventory__mutmut_11/12` | `"planned inventory"` → `XX…XX` / MAYÚSCULAS | HUECO-DE-ASERCION | `test_report_corruption_blocks` usa `all(word in …lower())` (`test_accept_verdict.py:77`) |
| `verdict.x__inventory__mutmut_22/23` | `"results inventory"` → ídem | HUECO-DE-ASERCION | `:158` substring + `.lower()` |
| `verdict.x__outcome__mutmut_16/18` | `"0 mutaciones…TEST-010…"` → ídem | HUECO-DE-ASERCION | `:142` solo `"TEST-010" in messages[0]`; ambas variantes contienen `TEST-010` |
| `verdict.x__outcome__mutmut_20` | separador `", " → "XX, XX"` | HUECO-DE-ASERCION | ningún test fija `messages[1]`; con un solo escenario vacío el separador ni aparece |
| `verdict.x__outcome__mutmut_27/28` | `"campaign has survived/error/not_run results"` → ídem | HUECO-DE-ASERCION | `:189–190` checks de palabra/status |
| `verdict_validation.x__identity__mutmut_4/5` | `"result must be an object"` → ídem | HUECO-DE-ASERCION | `:238` `all(word in …lower())` |
| `verdict_validation.x__result__mutmut_21/22` | `"result status"` → ídem | HUECO-DE-ASERCION | `:102` patrón palabra-a-palabra |
| `verdict_validation.x__result__mutmut_33/34` | `"result reason"` → ídem | HUECO-DE-ASERCION | `:102` ídem |
| `verdict_validation.x__exit__mutmut_6/7` | `"result exit type"` → ídem | HUECO-DE-ASERCION | `:102` ídem |
| `verdict_validation.x__exit__mutmut_21/22` | `"result exit/status"` → ídem | HUECO-DE-ASERCION | `:213–214` substring |
| `verdict_validation.x__header__mutmut_24/25` | `"missing evidence directory"` → ídem | HUECO-DE-ASERCION | `:77` patrón palabra-a-palabra |
| `verdict_validation.x__baseline__mutmut_20/21` | `"missing/invalid baseline"` → ídem | HUECO-DE-ASERCION | `:77` ídem |
| `verdict_validation.x__baseline__mutmut_33/34` | `"baseline reason"` → ídem | HUECO-DE-ASERCION | `:167` substring + `.lower()` |

Diagnóstico de fondo: el mismo archivo mezcla **dos convenciones**. Algunos
diagnósticos ya son contrato exacto (`test_accept_verdict.py:52` exige
`messages == ["invalid campaign: unsupported campaign schema"]`; `:117`,
`:129–131` y `:225–230` igualan listas completas), mientras los parametrizados
usan `all(word in messages[0].lower() for word in cause)`, que admite
prefijos/sufijos `XX` y mayúsculas por construcción. Los mutantes de mensajes
eran inevitables bajo la convención tolerante; la resolución no puede ser
«ignorarlos» (no son equivalentes: cambian la salida observable del veredicto).

## 5. Decisiones de contrato recomendadas (requieren ratificación humana)

- **D1 — Mensajes = contrato observable exacto.** Los diagnósticos
  `ValueError` de los cuatro módulos y las razones de `_outcome` viajan en la
  tupla `(failed, reasons)` de `accept_verdict` y son la salida que consumen
  recibos, CI y operadores. Tres diagnósticos ya se asertan exactos; extender
  esa convención al resto mata los 25 con aserciones de igualdad y hace la
  política homogénea. Coste aceptado: reescribir un mensaje romperá tests —
  que es exactamente el contrato deseado.
- **D2 — Alias UTF-8: ratificar equivalencia.** Ningún test puede matarlo y un
  `# pragma` sería peor. Queda como sobreviviente ratificado con la evidencia
  de §3 adjunta al expediente.
- **D3 — `zip(strict=…)`: ratificar equivalencia.** Alternativa posible:
  eliminar `strict=True` (simplificación revisable que disuelve los 3
  mutantes), pero obliga a re-campaña sin ganancia de protección; se recomienda
  conservar `strict=True` como defensa documentada y ratificar los 3.
- **D4 — Corrección narrativa.** El punto «hueco funcional» de
  `RESULTADO-AC1-R2-REANUDACION-2026-09-13.md` y del body de la PR queda
  corregido por §3: la regresión que allí se proponía ya existía. Corregir en
  el próximo registro, sin borrar historia.

El mecanismo de ratificación es el precedente P02a (54 excepciones autorizadas
con expediente); aquí serían 5, con evidencia individual ya adjunta.

## 6. Regresiones propuestas (solo tras ratificar D1; únicamente tests)

Sustituir en `tests/unit/test_accept_verdict.py` las aserciones tolerantes por
igualdad exacta, añadiendo una columna de mensaje esperado a las dos tablas
parametrizadas (las tablas siguen siendo matrices de cobertura, MIN-008):

| Diagnóstico exacto esperado | Mutantes que mata | Prueba |
|---|---|---|
| `invalid campaign: planned inventory` | `inventory_11/12` | `test_report_corruption_blocks`, casos `planned` |
| `invalid campaign: results inventory` | `inventory_22/23` | `test_results_requires_list_even_when_tuple_inventory_matches` |
| `0 mutaciones ejecutadas: TEST-010 exige Examples` | `outcome_16/18` | `test_zero_mutations_has_vacuous_warning`, igualdad de `messages[0]` |
| `escenarios sin Examples: S1, S2` | `outcome_20` | nuevo caso con **dos** escenarios sin Examples e igualdad de `messages[1]` (con uno solo el separador no aparece) |
| `campaign has survived/error/not_run results` | `outcome_27/28` | `test_valid_residual_is_not_misreported_as_invalid_instrument`, igualdad de lista |
| `invalid campaign: result must be an object` | `identity_4/5` | `test_non_object_result_names_the_shape_defect` |
| `invalid campaign: result status` | `result_21/22` | tabla paramétrica, caso `status=unknown` |
| `invalid campaign: result reason` | `result_33/34` | ídem, `reason=""` |
| `invalid campaign: result exit type` | `exit_6/7` | ídem, `exit=True` |
| `invalid campaign: result exit/status` | `exit_21/22` | ídem, `exit=0`; y `test_residual_exit_contradiction_is_instrument_invalid` |
| `invalid campaign: missing evidence directory` | `header_24/25` | ídem, `evidence_dir=""` |
| `invalid campaign: missing/invalid baseline` | `baseline_20/21` | ídem, `baseline=None` |
| `invalid campaign: baseline reason` | `baseline_33/34` | `test_baseline_reason_is_nonempty_text` |

13 cadenas de diagnóstico → 25 mutantes. `receipt_validation.py` no aporta
sobrevivientes (0/140) y no requiere cambios.

## 7. Próximo incremento mínimo

1. Ratificación humana de D1–D3 (D4 solo toma nota).
2. Hijo de tests: endurecer las aserciones de §6; cero cambios de producto.
3. Re-campaña del **mismo lote L1** con la misma receta congelada: resultado
   esperado 493 killed + 5 sobrevivientes ratificados como equivalentes,
   registrados con el mecanismo de excepción documentado.
4. Solo entonces continuar la cadena en el orden obligatorio: mutación de
   aceptación → cobertura/CRAP → DRY → tier full, y el resto de fuentes AC1
   conforme se autoricen lotes.

## 8. Revisión independiente solicitada

Se pide revisión de solo lectura sobre este documento y la evidencia citada:
(1) repetir el reconteo de §2 sobre `mutation-code-lot-r1-results-all.log`;
(2) ejecutar o inspeccionar los drivers de §3 y sus vectores; (3) validar la
tabla de §4 contra `mutation-code-lot-r1-survivor-diffs.log`; (4) pronunciarse
sobre D1–D4. El verificador no debe reutilizar este turno: quien escribió este
documento no puede verificación propia (PROC-005).
