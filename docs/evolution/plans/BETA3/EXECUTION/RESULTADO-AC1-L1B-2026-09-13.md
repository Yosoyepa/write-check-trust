# AC1 L1b — endurecimiento de aserciones y repetición del lote (2026-09-13)

Estado: cierre del lote L1 con **493 killed + 5 survived**, siendo los cinco
supervivientes equivalentes ratificados. AC1 **sigue sin acreditar** globalmente
(quedan fuentes sin medir y controles posteriores). No bless, merge, tag, bump
ni release; no se avanza a aceptación/CRAP/DRY/tier full en este incremento.

Autorización ejecutada (2026-09-13): contrato exacto exclusivo de los 13
diagnósticos de §6 de `ADJUDICACION-SUPERVIVIENTES-AC1-L1-2026-09-12.md`,
verificación previa de los cinco IDs por el verifier, repetición de L1 con
receta comparable, addenda al registro previo y revisión independiente.

## 1. Endurecimiento de aserciones (punto 1 del encargo)

Archivo autorizado: `tests/unit/test_accept_verdict.py` (único archivo tocado;
producto intacto; `strict=True` conservado). Ocho pruebas modificadas y una
nueva; ningún caso retirado; las aserciones de estado, causa y comportamiento
se conservan (las tablas paramétricas mantienen su patrón palabra-a-palabra
para los diagnósticos que NO son de los 13).

Los 13 diagnósticos fijados como contrato observable exacto:

1. `invalid campaign: planned inventory`
2. `invalid campaign: results inventory`
3. `0 mutaciones ejecutadas: TEST-010 exige Examples`
4. `escenarios sin Examples: <lista>` (separador `, ` observable)
5. `campaign has survived/error/not_run results`
6. `invalid campaign: result must be an object`
7. `invalid campaign: result status`
8. `invalid campaign: result reason`
9. `invalid campaign: result exit type`
10. `invalid campaign: result exit/status`
11. `invalid campaign: missing evidence directory`
12. `invalid campaign: missing/invalid baseline`
13. `invalid campaign: baseline reason`

Cobertura focal tras el endurecimiento: **115 passed** (114 previos + 1 prueba
nueva de dos escenarios sin Examples, que hace observable el separador del
join que `outcome_20` muta).

## 2. Verificación independiente de los cinco IDs (punto 2)

El verifier de sólo lectura repitió las sondas con el runtime original de L1
(`sh-p01-CND-80B8`, Python 3.13.14, mutmut 3.7.0, pytest 9.1.1) y revisó las
precondiciones estructurales, con enfoque adversarial: matriz ampliada (42/42
casos receipt, 24/24 verdict, idénticos), canarios de detección de falsos
equivalentes (`x__read__mutmut_24` y `x__accounting__mutmut_2` sí se distinguen),
sincronía byte a byte de los cuerpos `x__…__mutmut_orig` del lote contra el
worktree, y argumentos universales (`read(n)=min(n,size)` bajo las flags
exactas; identidad del CodecInfo para `utf-8`/`UTF-8`; poscondición de
`_inventory` como única puerta del `zip` con llamador único y sin mutación
intermedia). **Dictamen: CONFIRMADO — 5/5 EQUIVALENTE-DEMOSTRADO, ningún
contraejemplo.** Evidencia (local):
`build/tmp/adjudicacion-ac1-l1/verifier/VEREDICTO.md`
(SHA-256 `7f3c37b9df38d12336c378543b7daafd7ec103b3e88f79475b707a42553adcdc`).
Las equivalencias quedan registradas como definitivas conforme a la
autorización humana; el resultado bruto nunca las mezcla (§4).

## 3. Demostración original-pasa / mutantes-fallan (punto 4a)

Arnés: copia del árbol de mutantes de L1 (`build/tmp/adjudicacion-ac1-l1/harness/`)
con el test endurecido, 30 corridas de pytest bajo el runtime original con
`MUTANT_UNDER_TEST` por ID:

- **25 mutantes de mensajes: exit 1**, cada uno muerto por la aserción exacta
  prevista (`outcome_20` muere exclusivamente por la nueva prueba de dos
  escenarios vacíos; `exit_21/22` mueren además por la prueba de contradicción
  residual).
- **5 equivalentes: exit 0** (control de equivalencia). Precisión: el arnés
  corrió únicamente `tests/unit/test_accept_verdict.py` (51 pruebas); la
  confirmación de los dos mutantes de `receipt` contra la receta focal
  completa (incluido `test_accept_receipt.py`) la da la campaña r1b, donde
  sobrevivieron con 115 pruebas en verde.

Resultado bruto: `build/tmp/adjudicacion-ac1-l1/harness-30-resultados.txt`
(SHA-256 `3aa2b6f11615e714e0789e3becd3773c434d7bb0e28e4cf51e1441dc0b68389f`).

## 4. Repetición del lote: `mutation-code-lot-r1b` (punto 4b)

Campaña **nueva** sobre copia nueva; no se reutilizan veredictos de r1.

- **Receta comparable**: manifiesto de entradas idéntico al de r1 salvo
  `tests/unit/test_accept_verdict.py` (endurecido: `33166e50…` contra
  `e499ce2f…`). Las cuatro fuentes de producto y el `pyproject.toml` de receta
  son byte a byte idénticos a r1 (`52e92965…`, `ab6cca0b…`, `3990babd…`,
  `3c131a99…`, `e5287ae5…`).
- **Inventario comparable**: AST independiente 23 funciones (4/7/5/7), 498
  sitios (59/140/130/169). Preflight focal: **115 passed**.
- **Campaña**: `timeout --signal=INT --kill-after=30s 1800s mutmut run
  --max-children 1 '*'` bajo el runtime original; 51,704 s; exit crudo 0 (no
  constituye PASS por sí mismo).
- **Resultado bruto** (`mutation-code-lot-r1b-results-all.log`): 498 sitios =
  **493 killed + 5 survived + 0** en timeout/suspicious/skipped/no-tests/error.
- **Los 5 supervivientes son exactamente** `receipt.x__read__mutmut_23`,
  `receipt.x__read__mutmut_36`, `verdict.x__accounting__mutmut_14/17/18` — los
  IDs ratificados como equivalentes. La expectativa 493+5 se cumple; se conserva
  como expectativa declarada, no como premisa: el resultado bruto manda.

## 5. Verificación del árbol (punto 5)

Con el runtime original del expediente (`sh-p01-CND-80B8`), entorno privado
comparable al baseline previo:

- Colección global: **641 tests** (640 + 1 nueva).
- Suite normativa no-property: **640 passed, 1 deselected, exit 0** (112,2 s).
- Property separada: **1 passed**.
- `wct gate --tier fast`: **7 PASS, 0 SKIP, 0 FAIL/ERROR**.

Recetas inválidas separadas (no atribuidas a producto, precedente del
expediente): (a) una corrida normativa con el `.venv` del worktree (sin
semgrep/bandit) produjo 1 failed (`test_gate_secrets`) y 28 skipped; es
artefacto de entorno y se descartó al repetir con el runtime original; la firma
de fallo quedó reproducida y archivada como
`descarte-receta-uvvenv-normative.log` (1 failed, 611 passed, 28 skipped;
SHA-256 `26ab3f966b55f508e6bcceec4e97dc84c3659f45f6844d2a983c2ec9fa536938`);
(b) la primera corrida del fast gate tras el endurecimiento dio G-LINT/G-FMT
FAIL por una línea de 104 caracteres; corregida con `ruff format`, corrida
final verde.

Discrepancia declarada (revisión independiente): el campo
`candidate_status_porcelain` de `mutation-code-lot-r1b-plan.json` dice `[]`,
pero al generarse el plan el worktree ya tenía los cambios del incremento sin
commit (test endurecido, addenda y este registro). La comparabilidad de la
receta no depende de ese campo — quedó demostrada a nivel de bytes por los
manifiestos de entradas (§4) — y el artefacto no se edita a mano; queda así
registrada la discrepancia y su alcance.

## 6. Evidencia local (sin custodia externa)

Bajo `build/tmp/ac1-r2-qualification/evidence/` del worktree de la PR:

| Artefacto | SHA-256 |
|---|---|
| Plan r1b | `3f4c838dac251666b4eac8d772519faced9ec54a6efed49f1b836752e84b864e` |
| Preflight r1b (115 PASS) | `b42378ad3895f6283041964769ed2340ab48ff39521f927f2f80f9ec0bcfc112` |
| Metadatos de corrida r1b | `ebec6fb908cfd1fefad737a0182f44fa5a4832b4b7e429bd7160ccae11fc6541` |
| Log crudo de campaña r1b | `25046d9a3963d4546ea703c72d8fae8c0cb50486a990345be8d8022450ff6f25` |
| Resultados completos r1b | `33314aa821ca1f3133ebe37f13dfacdf3096eea28dc7119ba203e02dcbc02c49` |
| Diffs de supervivientes r1b | `54687d036bacf7838671174a0e684a47dd4a69da432ed41946c307beb5490028` |
| Reconciliación r1b | `f44c882a7e22996d003f39f6515a1b19f12c0c23473fdc922d2570f214b28041` |
| Colección (641) | `c005314b8af3f6f9ee57057b9f327c96188796b42d13bb3d34d8ce4bccf41739` |
| Normativa (640 passed) | `5a65f40559ad471b481c0cbcdf7c2978a45d44a5b66315700927f950bc1756ae` |
| Property (1 passed) | `9b52bfb8b13f1297999ec68d0eea9bdf9e1591be26cd1b4acca5b7cf28ba4a49` |
| Fast gate (7 PASS) | `60c26d036972b7ed363ccf686e1722643958ee0b5cb005396969ddd89aee44fb` |

Verificación del arnés y del verifier: `build/tmp/adjudicacion-ac1-l1/`
(fuera del worktree; hashes individuales citados en §3).

## 7. Siguiente lote (punto 6)

Se entrega `mutation-code-lot-r2` (denominación de lote de mutación de código,
sin relación con el delta R2 de reparación de baseline): núcleo puro de
`accept/` — `parsing.py`, `ir_checks.py`, `semantic.py`, `generation.py`,
`mutation_cases.py` — con foco en `test_accept_pipeline.py` +
`test_accept_verdict.py`. El transporte (`campaign.py`, `process.py`,
`pytest_receipt.py`, `pipeline.py`) y `gate/*` quedan como lotes pendientes.
Su resultado se registra en `RESULTADO-AC1-LOTE-R2-2026-09-13.md`. No se
avanza a aceptación/CRAP/DRY/tier full y AC1 no se declara acreditado.

## 8. Revisión independiente (realizada)

Revisión de sólo lectura del incremento por el verifier (PROC-005: quien
escribió no se auto-verifica), con corridas propias bajo el runtime original y
evidencia recalculada: **dictamen APROBADO-COMMIT** — 7/7 áreas PASS (diff del
test, focal 115, campaña r1b, comparabilidad de receta, arnés, suite normativa,
honestidad documental). Tres observaciones no bloqueantes, todas atendidas:
(1) discrepancia del campo `candidate_status_porcelain` del plan r1b —
declarada en §5; (2) artefactos de las recetas inválidas — el descarte del
`.venv` del worktree quedó reproducido y archivado en §5; (3) precisión del
alcance del arnés — añadida en §3.
