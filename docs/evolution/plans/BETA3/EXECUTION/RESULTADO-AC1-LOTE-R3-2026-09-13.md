# AC1 lote R3 — mutación del transporte de aceptación (2026-09-13)

Estado: **FAIL-survivors-stop**. La campaña cerró con 47 supervivientes que
quedan **sin ratificar**: este registro entrega inventario y diffs para la
adjudicación del próximo incremento, no la adjudicación misma. No se avanza a
aceptación/CRAP/DRY/tier full, no se repiten L1/L2, y AC1 no se declara
acreditado. Sin bless, merge, tag, bump ni release. (Denominación de secuencia
de lotes de mutación de código; sin relación con el delta R2 de baseline.)

Autorización ejecutada: incremento r3 de transporte según el encargo de
2026-09-13 y el plan de
`RATIFICACION-AC1-R2B-H01-H04-2026-09-13.md` (§Plan del siguiente lote).

## 1. Preflight H-04 endurecido (puntos 1–4 del encargo)

- **Instrumento bajo build/tmp, sin producto**:
  `build/tmp/ac1-r2-qualification/preflight-h04/preflight_associations_h04.py`
  (SHA-256 `39910db7…1ea0c`). Cero referencias en `tools/` y `src/`; las rutas
  de producto `mutation_preflight.py` siguen sin crearse.
- **Controles negativos** (selftest 11/11, incluye dos controles nuevos):
  inventario vacío, módulo omitido, función sin asociación, nodeid inexistente,
  módulo vacío sin documentar, función uninstrumentable sin diagnóstico y drift
  de fuente **bloquean** (exit no cero, listas explícitas); el camino feliz
  pasa con la declaración obligatoria «asociación no implica discriminación».
  Log: `preflight-h04/selftest-negative-controls.log`
  (SHA-256 `61362d31…460f`).
- **Re-chequeo r2/r2b con la versión endurecida**: r2 → **FAIL**
  (`functions-have-associations`: las tres funciones de `semantic`, módulo
  entero; SHA-256 del JSON `e2ee2170…3776`); r2b → **PASS** 22/22 con nodeids
  reales (SHA-256 `06c0d03b…52377`). El defecto de receta de r2 habría sido
  bloqueado antes de lanzar.
- **Contraste r3**: inventario AST independiente **17 funciones** (campaign 4,
  process 5, pytest_receipt 8, pipeline 0) contra 15 instrumentadas y 2
  diagnosticadas no instrumentables (§2); 90 nodeids de la colección focal
  real; `pipeline.py` documentado `documented-empty` con su hash conservado
  (`af67b206…`) — fachada pura de re-exportaciones, no un módulo omitido.
- **Verificación independiente previa**: verifier de sólo lectura, dictamen
  **APROBAR-CAMPANA, 5/5 PASS** (instrument-design, selftest-rerun reejecutado
  por el verifier, r2-r2b-hardened, uninstrumentable-diagnosis,
  pre-campaign-state).

## 2. Diagnóstico de procedencia y no-instrumentables (punto 4)

Las dos funciones de `pytest_receipt` ausentes del inventario instrumentado
son los hooks wrapper `_Recorder.pytest_runtest_makereport` (:46) y
`_Recorder.pytest_sessionfinish` (:82), ambos con
`@pytest.hookimpl(wrapper=True, tryfirst=True)`. Causa exacta: **mutmut 3.7.0
excluye funciones decoradas** de la mutación
(`mutmut/mutation/file_mutation.py`, `_skip_node_and_children`, «ignore
decorated functions… Exception: @staticmethod and @classmethod»), verificado en
el runtime (línea 281) y en el árbol generado (0 definiciones `__mutmut` para
ambos). No es un hueco de tests ni un fallo del módulo: son funciones **fuera
del universo medible del instrumento**, anotadas en el JSON del preflight con
su evidencia (`preflight-h04/r3-uninstrumentable-evidence.md`,
SHA-256 `2c448ea3…c6ff4`), sin excluir el módulo — las otras 6 funciones de
`pytest_receipt` sí se midieron. Limitación registrada: la cobertura de
mutación del lote alcanza 15 de 17 funciones; medir esos dos hooks exigiría
otro instrumento o cambiar producto, y por tanto decisión humana separada.

## 3. Campaña (punto 5)

- Lote: `build/tmp/ac1-r2-qualification/mutation-code-lot-r3/`, copia nueva
  con fuentes idénticas al worktree en `6dd35ae` (cuyo diff con `daab7e8` es
  docs-only; hashes del acta verificados).
- Receta: `only_mutate` = los 4 ficheros del acta; selección focal =
  `test_accept_campaign.py`, `test_accept_pytest.py`, `test_accept_pipeline.py`
  (`-m "not property"`); runtime `sh-p01-CND-80B8/.venv` (Python 3.13.14,
  mutmut 3.7.0, pytest 9.1.1); serial `--max-children 1`; presupuesto 3600 s.
- Sin reutilizar veredictos: el pase de solo-generación (filtro sin
  coincidencias) produjo 497 sitios todos `not checked` — no-veredictos — y la
  campaña real partió de ahí.
- Duración: **1397,27 s** (dentro del presupuesto). Exit crudo 0: no constituye
  PASS por sí mismo.

## 4. Resultado bruto (punto 6)

`mutation-code-lot-r3-results-all.log`: **497 sitios = 450 killed +
47 survived + 0** en timeout, suspicious, skipped y no-tests. Cero no-tests:
el preflight endurecido cumplió su función. Ni los timeouts inexistentes ni
cualquier fallo instrumental se cuentan como killed; no los hubo.

## 5. Inventario de supervivientes — 47, SIN ratificar

| Módulo | Función (cantidad) | IDs mutmut |
|---|---|---|
| `campaign` (14) | `x__attempt` (7) | 4, 6, 7, 9, 86, 88, 89 |
|  | `x__results` (4) | 11, 12, 22, 23 |
|  | `x_run_mutations` (3) | 89, 91, 92 |
| `process` (26) | `x__terminate` (3) | 1, 6, 7 |
|  | `x__read` (4) | 2, 12, 14, 17 |
|  | `x__observe` (10) | 7, 11, 12, 13, 22, 26, 27, 28, 31, 33 |
|  | `x__execute` (8) | 1, 8, 14, 28, 29, 30, 31, 32 |
|  | `x_run_process` (1) | 25 |
| `pytest_receipt` (7) | `xǁ_Recorderǁ__init__` (3) | 10, 11, 12 |
|  | `x_pytest_configure` (4) | 5, 7, 8, 9 |
| `pipeline` (0) | — | sin funciones propias; sin sitios |

Diffs individuales preservados en
`mutation-code-lot-r3-survivor-diffs.log` (47 bloques cerrados con
`=== <id-mutante> ===`, misma convención que r2b). Su adjudicación (hueco de
aserción, equivalente, comportamiento no contratado o límite del instrumento —
p. ej. mutantes de `process` sobre rutas de señal/timeout difíciles de
discriminar con procesos reales) es el siguiente incremento, con sondas y
verifier, no este registro.

## 6. Evidencia local (sin custodia externa)

Bajo `build/tmp/ac1-r2-qualification/evidence/` del worktree de la PR:

| Artefacto | SHA-256 |
|---|---|
| Plan r3 (con preflight y autorización) | `5dc2655ae13534a55295be2d7dcb712460b9a66edce5d68e76dc66d211760f0d` |
| Log de solo-generación (497 not-checked) | `0cf4a7a9cc8b1551f9f76fe7f388f2c63b999993ee4a3fd066bd75c2d6546a4e` |
| Resultados del solo-generación | `bde2cf8f3375fd2848e9a8ca856d8bc05819d8f8f5e17f62e1e9319a714fed4b` |
| Log crudo de campaña r3 | `88b904fae6c335c1fea539c5e8b14095a6204e9945f239079013e1b1e7c87a7d` |
| Cola y estado de salida de campaña | `4cd05df6c5884a1b6ee71468ab972f2cdf9ce98a757de3725ddb5a4a2952afaf` |
| Resultados completos r3 | `d4a7c29f02aebb6459deaedeebfe10166ee4ea742d5313a93bcedd82fea335e6` |
| Diffs de supervivientes r3 (47) | `51d99c9bdb45679dbed1300f2959bfb96ee27f0178cb5d48a669bf634c204b21` |
| Reconciliación r3 | `18a26f4ea51cf8fad39cc89333529666e72ce768ffcb5d5b776c10805e06d044` |
| Metadatos de corrida r3 | `ee72658d9a91f4a045fc658fbc6b5c4c9967810ec21eff99d1841861522a67c7` |
| Preflight final r3 (PASS) | `b0f212730d67e04aba63cf01cd1e01cfb8a883326b35010e1369c3350b76752f` |
| Diagnóstico JSON (uninstrumentables) | `7cfe6ff69f5ea2947089da85cab487b0071eedceb46d8259dc2a0f07fdaaee34` |
| Evidencia uninstrumentable | `2c448ea3cf2e7009be6dc58ac1c5e2df742714d2e5fd6361acc00fa6f46c6ff4` |
| Hardened r2 (FAIL esperado) | `e2ee217038c118a3a80f318646706a166024330bd0c03909179174292be43776` |
| Hardened r2b (PASS esperado) | `06c0d03be0f66bb4155f0082dd3bf6a4038d54c43c3177ed43e69809b5552377` |

Nota de honestidad: la primera versión de esta tabla incluyó hashes escritos
antes de calcularse; se detectó al cerrar el registro y se sustituyó por los
recalculados sobre disco antes del commit. Los artefactos nunca variaron.

## 7. Siguiente incremento mínimo propuesto (punto 7)

Adjudicar los 47 supervivientes con el método ya establecido (diffs, sondas
focales contra el árbol de mutantes, controles canario, verifier) y, en su
caso, endurecer aserciones sólo en tests. Después: lote `gate/*` +
`selftest/fixtures_tools.py` pendiente, y solo entonces las puertas de
aceptación/CRAP/DRY/tier full. No se propone cambiar producto en este paso;
cualquier reparación de hallazgos será un incremento propio con su TDD.

## 8. Revisión independiente (realizada)

Revisión de sólo lectura por el verifier (PROC-005): **dictamen
APROBADO-COMMIT, 5/5 áreas PASS, sin correcciones exigibles** — estado del
worktree (único cambio docs-only), recuento 497=450+47 con tabla §5
conjunto-idéntica al log, 14/14 hashes §6 recalculados, consistencia de
reconciliación y metadatos, y verificación del diagnóstico de hooks decorados
(decoradores en :46/:82, 0 mutantes generados, regla en mutmut
file_mutation.py:281, function_hashes=15). Fast gate del árbol: 7/7 PASS
(`r3-fast-gate.log`, SHA-256 `4f5b90966569be9b524c3e847a31917c2966a394f871803fd7a8dadfca944547`).
