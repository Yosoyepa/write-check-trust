# Acta de decisiones finales de mutación de fuentes y Q-ACCMUT (2026-09-16)

Registro único del encargo «registrar las decisiones humanas pendientes,
verificar el cierre adjudicado de mutación de fuentes y ejecutar Q-ACCMUT
únicamente si la puerta previa queda conforme» (2026-09-16). Ratifica por ID
lo autorizado, registra la excepción humana puntual a TEST-002 para B1–B5 y
`terminate__7`, acepta la comprobación alternativa de los dos hooks, delimita
el alcance de los 928 IDs por identidad/diff postpartición y, solo tras el
dictamen favorable de un verifier independiente, ejecuta Q-ACCMUT sobre el
candidato congelado. **No** repite campañas históricas de fuentes, no ejecuta
los 928 IDs, no cambia producto, tests, features, gobernanza, umbrales,
manifests, ratchets, lock ni versión; no bendice, no hace merge, bump, tag,
release ni declara cierre integral beta.3. El documento ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` permanece intacto, sin
seguimiento y fuera del incremento. La evidencia citada bajo `build/tmp/` es
temporal: no es custodia durable.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`. HEAD medido
  `192c869f1d465f64cea002431ea0a47f494cb751` = `origin` = `headRefOid` de la
  PR #53 (OPEN, draft, `mergeStateStatus` BLOCKED), sin avances remotos
  posteriores al corte comunicado. Sin reset, rebase, force push, `git add -A`
  ni sobrescritura de trabajo ajeno; el checkout principal solo se consulta
  (tiene trabajo no rastreado ajeno que no se toca).
- Índice al iniciar y al cerrar: vacío salvo el untracked ajeno citado.
- Runtime acreditado: `.venv` del worktree — Python 3.13.14, pytest 9.1.1,
  mutmut 3.7.0 — invocado con `UV_NO_SYNC=1` o por ruta; nada instalado,
  sincronizado ni modificado.
- Anclajes de fuentes vigentes (sha256 medidos en este encargo):
  `tools/wct/accept/process.py` `84b9340f…`, `campaign.py` `686070cd…`,
  `pytest_receipt.py` `d4f136ae…`; evidencia r3 sellada
  `build/tmp/ac1-r2-qualification/evidence/mutation-code-lot-r3-survivor-diffs.log`
  sha256 `51d99c9b…`. Coinciden con los anclajes del plan §3 y de la
  disposición previa.
- Inventario sellado de fase G (959 IDs): copia `fb7f725` en el `build/tmp/`
  compartido del checkout principal
  (`/home/jandradeu/Documents/well_code_template/build/tmp/lot-gate-selftest-fase-g.8KslOz/`,
  fuera del worktree) — `evidence/ids-all.txt` (959),
  `evidence/ids-objetivo.txt` (31), `evidence/ids-por-modulo.txt`
  (660 `tools.wct.gate.checks` + 299 `tools.wct.selftest.fixtures_tools`).
  Las fuentes G/E (`checks.py` `4797460040…`, `fixtures_tools.py`
  `3834548749…`, `runner.py` `6e568767…`) son byte-idénticas entre el corte
  `fb7f725` y el pre-partición `b27f01e`, y los cuerpos postpartición se
  comprobaron por AST (§2.4).

## 2. Decisiones humanas registradas

Las decisiones de §3.1–3.6 del encargo se registran ligadas a sus IDs
completos, fuentes, hashes, runtime y evidencia. Ninguna se extiende por
analogía a otros IDs, operadores, fuentes o codificaciones.

### 2.1 A1/A2 — equivalencias ratificadas

IDs exactos del inventario sellado r3 (log `51d99c9b…`):

- `tools.wct.accept.campaign.x__attempt__mutmut_4`:
  `json.dumps(ir, ensure_ascii=False)` → `ensure_ascii=None`. En CPython
  `ensure_ascii` se consume como valor falsy; `None` y `False` producen los
  mismos bytes. Ratificado **solo** para este ID: no se extiende a otros
  valores falsy (`0`, `""`) ni a otros operadores de `json.dumps`.
- `tools.wct.accept.campaign.x__attempt__mutmut_9`:
  `.encode("utf-8")` → `.encode("UTF-8")`. Alias canónico del códec (la
  búsqueda de códecs es insensible a mayúsculas); mismos bytes. Ratificado
  **solo** para este ID y codificación; no se extiende a otros códecs.

Fuente `campaign.py` `686070cd…` (vigente y en r3); runtime Python 3.13.14 /
pytest 9.1.1 / mutmut 3.7.0; precondiciones de la matriz R3. El bruto r3 no
cambia (497 = 450 + 47). Invalidante: cambio de fuente, de runtime o del
operador `json.dumps`/códec. Evidencia consumida: log sellado
`51d99c9b…` (líneas 1–12 y 40–51), adjudicación R3, matriz §A.

### 2.2 A4–A11 — ocho `typing.cast`: ratificación y transferencia

IDs: `tools.wct.accept.process.x__observe__mutmut_7/11/12/13/22/26/27/28`
(primer argumento de `cast` en los dos puntos de registro del selector:
`process.stdout` — `_7`, `_11`, `_12`, `_13` — y `process.stderr` — `_22`,
`_26`, `_27`, `_28`; variantes `None`, `"XXBinaryIOXX"`, `"binaryio"`,
`"BINARYIO"`). `typing.cast` es identidad en runtime: retorna el segundo
argumento sin evaluar el primero. Ratificados como equivalencia runtime de los
ocho IDs, con estas precondiciones documentadas:

- `typing.cast` ordinario, no sustituido; `BinaryIO` importado y resoluble;
  streams idénticos; runtime Python 3.13.14.

**Correspondencia con el hash actual y transferencia.** La evidencia r3 se
tomó sobre `process.py` sha256 `bdbb5646…`; el hash vigente es `84b9340f…`.
La copia sellada del lote r3 (`mutation-code-lot-r3/tools/wct/accept/process.py`)
tiene sha256 `bdbb5646…` medido en este encargo; el diff contra el vigente
contiene **exactamente dos líneas** — `cast("BinaryIO", …)` →
`cast(BinaryIO, …)` en `_observe` (líneas 38–39) — introducidas por `b4403c5`
(descomillado por G-DEAD, con T5 y regresiones de transporte 213/213). Los
ocho sitios de mutación siguen existiendo en el hash actual con las mismas
variantes aplicables al primer argumento; la reparación no cambió el segundo
argumento ni la semántica de `cast`. Las 213 pruebas de la reparación son
evidencia histórica de no regresión, no una campaña nueva. No se renumeran ni
reutilizan inventarios: la ratificación es de los ocho IDs históricos; no se
extiende a otros IDs ni a un cambio de la frontera de tipos. Invalidante:
cualquier cambio relevante adicional de `process.py`, del runtime o del
mecanismo de `cast` invalida la transferencia automática.

### 2.3 Hooks decorados — comprobación alternativa aceptada

Se acepta la comprobación alternativa ya ejecutada de los dos hooks, en el
alcance de sus oráculos y controles discriminantes. Registrado por separado:

- **Limitación de instrumentación.** `_Recorder.pytest_runtest_makereport` y
  `_Recorder.pytest_sessionfinish` no son IDs de mutmut: mutmut omite
  funciones decoradas. No hay mutantes generados para estos hooks.
- **Evidencia alternativa realizada** (`OLEADA-TECNICA-CIERRE-AC1-2026-09-15.md`
  §2.3; receta corregida del plan §3-D). Tres corridas en
  `build/tmp/ac1-r2-qualification/r3-hook-alternative/` con canario de plugin
  (raíz + sha256 del módulo cargado; control `d4f136ae…` = hash vigente):
  control (pytest exit 1, caso/evento mismatch, `validate_receipt` →
  `("mismatch", "semantic mismatch")`); HOOK-MR-01 (clasificación del call
  mismatch→pass, exit real 1, validador → `invalid` por contradicción
  status/exit); HOOK-SF-01 (`document["exit"]=0`, exit real 1, validador →
  `invalid` por exit discordante). `summary.json` conservado.
- **Funciones y conductas cubiertas.** `pytest_runtest_makereport`: la
  clasificación falsa de un mismatch como pass es rechazada por
  contradicción con el exit real. `pytest_sessionfinish`: la manipulación del
  exit persistido es rechazada por discordancia con el exit observado. El
  control acredita el rechazo correcto del mismatch semántico (exit no cero
  solo no discrimina).
- **Límites que siguen vigentes.** La limitación de instrumentación de mutmut
  permanece (los hooks siguen sin IDs); estos controles **no** se contabilizan
  como mutantes generados ni killed de mutmut y **no** convierten el bruto
  497 en otra cosa; la evidencia es temporal bajo `build/tmp/`; si cambia el
  plugin (hash) o los validadores, la comprobación debe re-ejecutarse.

### 2.4 Alcance de los 928 IDs históricos — delimitación por identidad

Se aprueba delimitar fuera de la campaña diferencial de este incremento los
IDs de cuerpos preexistentes sin cambio semántico, sustentado por el mapa de
identidad/diff postpartición. Comprobaciones ejecutadas en este encargo
(evidencia `build/tmp/decisiones-finales-qaccmut/evidence/`):

- **Enumeración por identidad, no por exclusión de archivos.** Los 928 IDs
  (959 generados − 31 objetivo) se extrajeron del inventario sellado de fase G
  y se agruparon por función portadora: **649** en
  `tools.wct.gate.checks`, **279** en `tools.wct.selftest.fixtures_tools`,
  sobre **38 funciones distintas** (19 + 19), ninguna huérfana
  (`enum-928-por-identidad.json`).
- **Comprobación de cuerpos.** Para cada una de las 38 funciones, el cuerpo
  AST normalizado del corte G/E y el del módulo vigente postpartición son
  **idénticos** (0 faltantes, 0 discrepancias). La comparación completa de
  símbolos preexistentes da 23/23 idénticos en `checks.py` y 33/33 en
  `fixtures_tools.py` (`BUILDERS` permanece en la fachada; `Builder` en
  `fixtures_governance`; ambos con AST idéntico). Las fuentes pre-partición
  son byte-idénticas entre G/E y `b27f01e`.
- **Cambios de resolución.** El único cambio es el módulo contenedor
  (qualname): los destinos por función están en el JSON de enumeración
  (`checks_debt`/`checks_quality`/`checks_scanners`,
  `fixtures_governance`/`fixtures_git`/`fixtures_adversarial`). La resolución
  de nombres quedó acreditada por la auditoría de partición
  (`RECALIFICACION-POSTPARTICION-Y-A12-2026-09-16.md` §4: 0 ciclos, imports de
  consumidores resuelven, suite normativa 689 passed, mypy estricto) y por
  comprobación propia: `ruff --select F821` 0 hallazgos y parseo AST 6/6.
- **Cambios de wiring/composición tratados explícitamente.** El reparto del
  literal `REGISTRY` (22+14+8+3), `derived(base)`, `TIERS`/`_COMMIT_GATES`,
  reexportaciones y puntos de parche P1/P2/P2′/P2″ están enumerados y
  cubiertos con sus discriminantes D1–D4 y PX-REG en
  `RECALIFICACION…` §4 y `PARTICION-TEST007-Y-CIERRE-R3-2026-09-16.md` §4;
  ninguno pertenece a las 38 funciones portadoras de los 928.
- **Ningún cambio semántico nuevo queda excluido por ser un traslado.** Todas
  las diferencias estructurales conocidas están enumeradas (división del
  literal, construcción derivada, `Builder`/`BUILDERS`) y ninguna afecta a
  los cuerpos de los 928; la suite y los controles anteriores lo respaldan.
- **Estado histórico conservado.** Los 928 IDs permanecen **NO EJECUTADOS y
  sin veredicto**: ni la campaña r3 (solo `tools/wct/accept/*`), ni la
  recalificación postpartición (31 IDs objetivo; 333 no objetivo
  `not checked`) los ejecutaron. La delimitación no excluye archivos
  completos ni veredictos; los 31 IDs re-anclados conservan su tratamiento
  separado (recalificación 31 killed, lote propio).

Resultado de la comprobación: las 38 funciones portadoras satisfacen las
condiciones; no hay IDs que separar por falta de comprobación. Invalidantes:
cualquier cambio de cuerpo, de resolución o de wiring de esas funciones
revoca la delimitación y exige revisar el alcance. TEST-007 permanece
aplicable a cambios futuros.

### 2.5 B1–B5 — contrato de presentación y excepción puntual TEST-002

Se aprueba conservar como contrato: el contenido semántico de los JSON (no su
indentación exacta), la identificación de la causa y el rechazo correcto (no
toda su grafía) y el funcionamiento del plugin (no su nombre interno por sí
mismo). Comprobación por ID (evidencia r3: log `51d99c9b…`; consumidores
verificados en este encargo en `tools/`, `tests/`, `features/`, `src/`):

| Familia | IDs | Diferencia | Comprobación de ámbito |
|---|---|---|---|
| B1 | `campaign.x__attempt__mutmut_86/88/89` | `indent=2` → `None`/omitido/`3` en `attempt.json` | Solo representación textual; el único consumidor (`test_accept_campaign.py:386`) hace `json.loads`; ningún campo, tipo ni valor cambia |
| B2 | `campaign.x_run_mutations__mutmut_89/91/92` | idem en `report.json` | Solo representación textual; consumidores `json.loads` (`test_accept_campaign.py:148/156/636`); esquema/cuentas intactos |
| B3 | `campaign.x__results__mutmut_22/23` | literal de `reason` (`"XX…XX"`, mayúsculas) | Solo grafía; consumidores (`campaign.py:48-49/90`, `verdict_validation.py:23-24/49-50`, `verdict.py:56`) exigen string no vacío y clasifican por estado, no por literal; rechazo y clasificación intactos |
| B4 | `pytest_receipt.xǁ_Recorderǁ__init____mutmut_10/11/12` | grafía de `"AC1 original IR hash mismatch"` | Solo grafía; el rechazo (`raise ValueError`) persiste y el test consumidor usa regex `(?i)hash.*mismatch` (`test_accept_pytest.py:104`), que las tres variantes satisfacen |
| B5 | `pytest_receipt.x_pytest_configure__mutmut_5/7/8/9` | nombre de registro (`None`, omitido, `XX…XX`, mayúsculas) | Solo nombre consultable; el registro y el despacho de hooks funcionan en las cuatro variantes (comprobación runtime propia: `registrado=True`, hookimpls=1); el único consumidor del nombre (`test_accept_pytest.py:295`) opera por la vía sin protocolo y exige ausencia del observer, no un nombre activo |

Ninguna variante afecta otra obligación o consumidor; no se clasifican como
equivalentes: sus resultados de presentación difieren donde el contrato
elegido no fija nada. Quedan **survivors** y se disponen por la excepción
puntual de §3. Obligaciones exigibles: contenido semántico íntegro (campos,
tipos, cuentas, esquema), causa identificable y rechazo correcto, rechazo de
hash incorrecto y funcionamiento de los consumidores existentes.

### 2.6 `terminate__7` — excepción puntual TEST-002

ID: `tools.wct.accept.process.x__terminate__mutmut_7` (`wait(timeout=1)` →
`wait(timeout=2)`). No se impone `wait=1 s` como contrato exacto. Se acepta la
diferencia `wait(1)→wait(2)` exclusivamente para este ID documentado y el
candidato acotado, siempre que no viole otro presupuesto o contrato operativo
vigente: la terminación sigue acotada (2 s ≤ 30 s/intento y 600 s/campaña),
la recolección del hijo directo se mantiene y la regresión permanente
`test_terminate_gives_up_on_slow_reap_within_bounded_budget` pasa verde bajo
la variante (`OLEADA…` §2.2). No se extiende a espera ilimitada, otros plazos
ni otros IDs. Fuente `process.py` `84b9340f…`; runtime y precondiciones
documentados. Queda como **survivor** dispuesto por la excepción de §3.

## 3. Excepción humana puntual a TEST-002 — registro explícito

### 3.1 Texto de la autorización y su procedencia

Procedencia: decisión humana comunicada en el encargo de este acta
(2026-09-16), capítulo 4. Texto operativo registrado:

> «Para B1–B5 y terminate__7 autorizo una excepción humana puntual a TEST-002
> para la salida incremental de PR #53, únicamente para los IDs que satisfagan
> las condiciones anteriores. No es una modificación global de TEST-002. No
> autoriza subir umbrales, modificar baselines, cambiar gates ni editar
> manifests a mano.»

### 3.2 Mecanismo vigente

TEST-002 (`governance/rules/10-testing.yaml`, `severity: hard`, `fails: [F3, F5]`;
`governance/thresholds.yaml` → `mutation.max_survivors_changed: 0`) es regla
dura y **no** tiene procedimiento de excepción para comportamiento no
contratado. El mecanismo vigente que cabe en esta autorización documental es
el registro humano explícito por acta, con el precedente H-01
(`RATIFICACION-AC1-R2B-H01-H04-2026-09-13.md`). No se edita gobernanza
(SEC-005/PROC-010), no se suben umbrales, no se tocan baselines ni manifests,
no se cambia ningún gate. Esta acta no declara PASS de G-MUT ni lo sustituye:
al no ejecutarse G-MUT en este encargo, la excepción queda registrada para la
adjudicación que corresponda en su ejecución futura; un superviviente
exceptuado **sigue siendo superviviente en el bruto** 497 = 450 + 47 y no se
convierte en killed, equivalente ni PASS.

### 3.3 IDs completos y diffs (fuente: log sellado `51d99c9b…`)

- B1 — `tools.wct.accept.campaign.x__attempt__mutmut_86`:
  `json.dumps(result, indent=2)` → `indent=None`;
  `_88`: → `json.dumps(result, )`; `_89`: → `indent=3` (línea 66 vigente).
- B2 — `tools.wct.accept.campaign.x_run_mutations__mutmut_89`:
  `json.dumps(report, indent=2)` → `indent=None`; `_91`: → `json.dumps(report, )`;
  `_92`: → `indent=3` (línea 124 vigente).
- B3 — `tools.wct.accept.campaign.x__results__mutmut_22`:
  `reason="prior attempt did not pass protocol"` → `"XXprior attempt did not pass protocolXX"`;
  `_23`: → `"PRIOR ATTEMPT DID NOT PASS PROTOCOL"` (línea 82 vigente).
- B4 — `tools.wct.accept.pytest_receipt.xǁ_Recorderǁ__init____mutmut_10`:
  `raise ValueError("AC1 original IR hash mismatch")` → `"XX…XX"`;
  `_11`: → `"ac1 original ir hash mismatch"`; `_12`: → `"AC1 ORIGINAL IR HASH MISMATCH"`
  (línea 21 vigente).
- B5 — `tools.wct.accept.pytest_receipt.x_pytest_configure__mutmut_5`:
  `config.pluginmanager.register(_Recorder(), "wct-accept-receipt-observer")` → `(..., None)`;
  `_7`: → `register(_Recorder(), )`; `_8`: → `"XXwct-accept-receipt-observerXX"`;
  `_9`: → `"WCT-ACCEPT-RECEIPT-OBSERVER"` (línea 107 vigente).
- `terminate__7` — `tools.wct.accept.process.x__terminate__mutmut_7`:
  `process.wait(timeout=1)` → `process.wait(timeout=2)` (línea 18 vigente).

### 3.4 Fuente / hash / runtime

- `tools/wct/accept/campaign.py` sha256 `686070cd…` (B1, B2, B3).
- `tools/wct/accept/pytest_receipt.py` sha256 `d4f136ae…` (B4, B5).
- `tools/wct/accept/process.py` sha256 `84b9340f…` (terminate__7).
- Runtime: Python 3.13.14, pytest 9.1.1, mutmut 3.7.0 (`.venv` del worktree).
- Evidencia: log r3 sellado `51d99c9b…`; adjudicación R3; comprobaciones de
  consumidores y runtime de §2.5/§2.6.

### 3.5 Resultado bruto conservado

Bruto r3 **497 = 450 killed + 47 survived** (inmutable). Los 16 IDs de §3.3
pertenecen a los 47 `survived`; el bruto se conserva tal cual y los intentos
reales de las sondas/regresiones no se recalculan.

### 3.6 Obligaciones que siguen siendo exigibles

- B1/B2: contenido semántico de `attempt.json`/`report.json` (esquema, campos,
  tipos, cuentas, identidad, persistencia) y comportamiento de todo consumidor
  que los carga como JSON.
- B3: causa identificable (string no vacío), clasificación correcta
  (`invalid`/parada de campaña) y propagación de la razón del intento.
- B4: rechazo del hash incorrecto (`raise ValueError`) con causa reconocible
  por el consumidor vigente.
- B5: funcionamiento del plugin y del despacho de hooks, registro consultable
  y cooperación del observer con el protocolo.
- `terminate__7`: terminación acotada, captura exigida y limpieza del hijo.
- TEST-002 sigue vigente para todo lo demás; esta excepción no crea
  precedente automático ni se transfiere a otros IDs, fuentes o incrementos.

### 3.7 Justificación de la aceptación del comportamiento no contratado

Las diferencias de B1–B5 caen exclusivamente en el ámbito autorizado
(presentación JSON / grafía de causa / nombre interno del plugin) según la
comprobación por ID y consumidores de §2.5, sin pérdida de información,
tipos, campos obligatorios, clasificación, rechazo de hashes incorrectos ni
cambios en consumidores existentes. En `terminate__7` la diferencia preserva
todas las obligaciones operativas (acotación, captura, limpieza) y no viola
presupuestos. Se aceptan como comportamiento distinto no contratado, no como
equivalencias.

### 3.8 Invalidantes

Cambios relevantes de fuente (hash distinto en `campaign.py`,
`pytest_receipt.py` o `process.py`), de contrato (configuración explícita de
indentación/grafía/nombre como API), de consumidor (nuevo lector que dependa
del texto exacto, de la grafía o del nombre del plugin) o de runtime
(versiones distintas de las acreditadas) revocan esta excepción y obligan a
revisar los 16 IDs.

### 3.9 Alcance

PR #53 y su candidato incremental (HEAD `192c869` más los commits
documentales de este encargo). No alcanza a todo WCT ni a beta.3 completa;
no modifica cobertura/CRAP, DRY, full, bless, merge, bump, lock, tag ni
release.

## 4. Decisiones ya registradas que se incluyen sin reabrir

Verificado el no-invalidante (fuentes `84b9340f…`/`686070cd…`/`d4f136ae…` sin
drift, runtime idéntico, regresiones presentes en el árbol):

- **A12** (`process.x__read__mutmut_12`): equivalencia respecto del contrato
  aclarado, con la divergencia timeout/exceso en la ventana del deadline
  conservada; registro en `DISPOSICION-FINAL…` §2. La pregunta de precedencia
  no contratada de `RECALIFICACION…` §3 quedó respondida por el encargo de
  este acta (§3.1 del encargo: cualquiera de ambos motivos bloqueantes es
  válido).
- **A13** (`process.x__read__mutmut_14`): equivalencia observable acotada
  (verifier independiente confirmó el argumento completo).
- **execute__28/29** (`process.x__execute__mutmut_28/29`): equivalencia
  deductiva por alcanzabilidad.
- **A14** (`process.x__read__mutmut_17`), **terminate__6**
  (`process.x__terminate__mutmut_6`), **C2**
  (`process.x__observe__mutmut_33`): defectos detectados por regresiones
  permanentes; C2 con su aclaración contractual aplicada.
- **A3** (`process.x__execute__mutmut_30`) y **execute__31/32**: defectos con
  regresión permanente.
- **11 `DEFECTO_FUNCIONAL` r3**: regresiones permanentes (`6e4398e`,
  `fa3558d`); 11/11 caen.

Sin reapertura: no hay invalidante declarado. Ninguna de estas disposiciones
convierte `survived` histórico en `killed`.

## 5. Ledger actualizado — capas separadas, sin agregaciones

| Capa | Contenido | Estado |
|---|---|---|
| Campañas históricas | r3 AC1 **497 = 450+47** (log `51d99c9b…`); fase E **27+4**; GS-1 **280+2**; GS-2 **102+16**; GS-3 **74+34** | Inmutables; no re-ejecutadas |
| Recalificación postpartición | `_declared`/`f9_a` re-anclados: **31 killed + 0 survived** (lote propio, 25 s); 333 no objetivo `not checked` | Cerrada en su alcance; no modifica historia |
| Regresiones posteriores | 11 funcionales + A14, terminate__6, C2, A3, execute__31/32; regresiones C2 y limpieza/captura | Permanentes en tests; sensibilidad contra mutantes reales |
| Equivalencias ratificadas | A12, A13, execute__28/29 (previas) + **A1, A2, A4–A11** (esta acta) = **14** | Acotadas a fuente/runtime/precondiciones |
| Excepciones humanas puntuales | **B1–B5 (15 IDs)** y **terminate__7** (esta acta) | Survivors conservados; excepción local a PR #53 |
| Comprobaciones alternativas de hooks | 2 hooks; control + 2 semillas; no son IDs mutmut | Aceptadas en su oráculo; no suman al bruto |
| Alcance no ejecutado | **928 IDs** (649+279) delimitados por identidad/diff; 17 archivos de la partición sin campaña fresca | No ejecutados, sin veredicto; cubiertos por controles estructurales |
| Pendientes reales | G-MUT de fuentes **no ejecutado** (sin PASS); Q-ACCMUT (esta acta); cobertura/CRAP, DRY, full, bless, merge, bump/lock, tag, release | Abiertos para sus encargos |

Contabilidad: las 14 equivalencias ratificadas no convierten `survived` en
`killed`; los 16 IDs exceptuados siguen en el bruto; G-MUT no se ejecutó y no
se declara su PASS.

## 6. Comprobaciones de este incremento

- `git diff --check`: limpio.
- Fast (`UV_NO_SYNC=1 uv run wct gate --tier fast`): resultado en §6.1.
- Integridad (`wct integrity check`): exit 1, drift **recalculado 37 = 7
  modificadas + 30 nuevas** (no se asume el número: medido; este incremento
  solo añade documentos no protegidos y no altera el conjunto). G-META-1
  sigue siendo el rojo pre-bless conocido; no se ejecutó bless.
- No se ejecutan cobertura/CRAP, DRY ni tier full: fuera de este encargo.

### 6.1 Resultado de las comprobaciones

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio (antes y después de Q-ACCMUT) |
| Fast (corrida final, tras Q-ACCMUT) | **7/7 PASS** (G-META-2 36 ms, G-RULES-DRIFT 71 ms, G-SUPPRESS 186 ms, G-DEBT 76 ms, G-LINT 16 ms, G-FMT 12 ms, G-TYPE 162 ms), exit 0 |
| Integridad | exit 1; drift medido **37 = 7 modificadas + 30 nuevas** (`integrity-before.txt` e `integrity-final.txt`, conjunto idéntico), sin ruta nueva de este incremento |
| Colección/focales | No re-ejecutadas como batería pesada: el incremento no toca tests ni producto |

## 7. Puerta previa — dictamen del verifier independiente

Agente distinto del autor (`.claude/agents/verifier.md`, sin permiso de
escritura), informe propio bajo `build/tmp/`. Debe comprobar: aplicabilidad de
cada decisión a sus IDs; ausencia de cambios conductuales ocultos fuera del
ámbito autorizado; sustento de la delimitación de alcance; que el
procedimiento permite avanzar con las excepciones registradas; y que no se
declara ningún gate verde sin ejecutarlo.

### 7.1 Dictamen

Informe: `build/tmp/verifier-qaccmut-decisions/VEREDICTO.md`
(`build/tmp/decisiones-finales-qaccmut/verifier-run.log` conserva la salida).
Re-ejecuciones propias: ≈9,5 s de los 120 s autorizados; sin mutmut, campañas,
bless ni tocar el índice. Re-ejecutó: anclas sha256; diff de dos líneas
`bdbb5646…`→`84b9340f…` y los 8 IDs de `cast` (identidad runtime verificada);
hunks A1/A2 con reproducción de bytes; consumidores B1–B5 y registro runtime
con las cuatro variantes de nombre; hunk de `terminate__7` y su regresión
focal (1 passed en 0,19 s); comparación AST independiente de los 928
(38/38 cuerpos idénticos; 928 = 649+279 sobre 19+19 funciones; objetivos 31);
evidencia de hooks; ausencia de cambios protegidos; `git diff --check`; drift
37 = 7+30 re-medido; fast re-ejecutado 7/7.

**Dictamen: `APROBAR-Q-ACCMUT`** — cierre adjudicado suficiente según las
decisiones y el procedimiento aplicables; sin cambios conductuales ocultos y
sin gates verdes falsos (G-MUT declarado no ejecutado; bruto 497 = 450+47 con
los 16 exceptuados conservados como survivors). Reservas no bloqueantes: el
verifier buscó el inventario sellado de fase G en la ruta relativa del
worktree y no lo halló (vive en el `build/tmp/` compartido del checkout
principal; compensó con vías independientes); no re-ejecutó `ruff F821`
(compensado con parseo AST propio y G-LINT/G-TYPE); los discriminantes de
wiring D1–D4/PX-REG los auditó documentalmente (fuera de las 38 portadoras);
varianza normal de tiempos del fast.

## 8. Q-ACCMUT — ejecutado

### 8.1 Preflight

- **Interfaz real del CLI verificada** (`tools/wct/cli.py:95-99,299-329`):
  `wct accept {parse,ir-dry,generate,run,mutate}` con `--output` (default
  histórico `tests/acceptance/generated/test_acceptance.py`); `mutate`
  ejecuta `parse_feature` → `generate(ir, root/--output)` →
  `run_mutations(ir, command)` con comando por defecto
  `[sys.executable, -m pytest, -q, <generado>]`. Operador histórico
  `mutation_cases._changed`/`mutations` (una celda por campo, en orden); no
  se injertó P03a ni otro operador.
- **`--output` privado**:
  `build/tmp/decisiones-finales-qaccmut/qaccmut/generated/test_acceptance.py`.
  El generado histórico **no** se sobrescribió (sha256 `118295099f…` medido
  antes y después). La copia privada del encargo conserva el generado previo
  y no se publica.
- **Hashes** (`hashes.txt`, 21 rutas): fuentes `tools/wct/accept/*.py` (con
  `process.py` `84b9340f…`, `campaign.py` `686070cd…`,
  `pytest_receipt.py` `d4f136ae…`), feature `0b9aa268…`, bindings
  `tests/acceptance/steps.py` `5b6863ed…`, `campaign_steps.py` `f81b238d…`,
  `protocol_runner.py` `35ad31a1…`, generado histórico `118295099f…`,
  `pyproject.toml` `c3a1b3e7…`; runtime Python 3.13.14 / pytest 9.1.1 /
  mutmut 3.7.0.
- **Inventario independiente y exacto**: **47 celdas = 40+7** (2 escenarios:
  5 filas × 8 campos + 1 fila × 7 campos), reproducido con
  `parse_feature` + `mutations` (no se forzó el número; el inventario real
  coincide). **Trazabilidad 48 históricos → 47 nuevos**: test
  `test_ac1_feature_inventory_traces_the_48_historical_coordinates` verde.
- **Baseline exterior verde**: 2 passed en 0,76 s, exit 0; ambos escenarios
  realmente ejecutados.
- **Controles negativos del arnés** (6 tests focales, 15 casos, 0,46 s):
  selector desconocido → error instrumental (nunca killed); selector de
  veredicto desconocido → error; Then numérico alterado → `SemanticMismatch`;
  aborto de baseline independiente de todos los modos válidos; oráculo de
  inventario rechaza corrupción; trazabilidad 48→47.
- **Activación, aislamiento, recibos y contabilidad**: acreditados por
  mutante en §8.2; sin errores instrumentales.

### 8.2 Ejecución

- Comando: `UV_NO_SYNC=1 uv run wct accept --output
  build/tmp/decisiones-finales-qaccmut/qaccmut/generated/test_acceptance.py
  mutate features/wct-acceptance-evidence-001.feature`. Resultado bruto del
  motor conservado: **rc=0**, duración exterior **61 s**, baseline `pass`
  (exit 0, dos casos `pass`), **planned=47, killed=47, survived=0, errors=0,
  not_run=0**; stderr vacío. No se ejecutó una reconciliación propia que
  sustituyera al motor; el dictamen bruto (`report.json`) es el del `mutate`.
- Evidencia: `build/tmp/wct-accept-ldk_w15y/` (`report.json`, `baseline/`,
  `mutation-0..46/`), manifiesto `manifest-evidencia.sha256` (289 entradas,
  sin auto-hash), copia de logs y validación propia en
  `build/tmp/decisiones-finales-qaccmut/qaccmut/`. Intento inválido: ninguno.
  Presupuesto por intento: máximo 1,90 s de los 30 s del contrato; campaña
  61 s de 600 s.
- **Clasificación** (regla del encargo): los 47 rechazos son **semánticos
  contractuales**, no instrumentales: `attempt.json` status `mismatch`,
  exit 1, recibo válido (`attempt_id`/`ir_sha256` ligados a los bytes del
  IR mutado), `errors` vacío; el diff contra el IR original es **exactamente
  la celda objetivo**; el escenario mutado queda `mismatch` y el escenario
  hermano `pass`. Ningún selector desconocido, fallo de setup, colección o
  launcher. Residuo: **0**. Ambos escenarios cubiertos (40 celdas del primer
  Outline y 7 del Outline de aborto).
- **Sin reparaciones**: no se modificaron producto, bindings, feature ni
  operador; `git status --porcelain` idéntico al inicio salvo los documentos
  de este acta.
- **Verifier independiente de campaña**:
  `build/tmp/verifier-qaccmut-campaign/VEREDICTO.md` — dictamen
  **`APROBAR-QACCMUT-EJECUTADO`** (≈15 s de 90 s). Re-ejecutó: baseline
  exterior (2 passed), inventario (47=40+7) y trazabilidad, clasificación
  causal de los 47 (0 desviaciones), una activación en vivo (`mutation-0`,
  exit 1, recibo `[{mismatch},{pass}]`), hashes 21/21, manifiesto 289/289 y
  ausencia de reparaciones. Reservas no bloqueantes: `vacuous` aparece en el
  stdout del CLI y no en `report.json` (se añade en memoria después de
  persistir el reporte, `verdict.py`); `receipt.events.json` con formas
  esperables por la estructura del generado; una sola re-ejecución en vivo.

## 9. Presupuestos

- Comprobaciones previas de este acta (hashes, enumeración 928, cuerpos AST,
  resolución, consumidores, runtime, drift, hooks, hooks runtime): lecturas
  locales, `rg`, `sha256sum`, dos scripts de análisis y una comprobación
  runtime mínima; **≈40 s** acumulados, muy por debajo de los 180 s.
- Revisión documental contabilizada aparte.
- Q-ACCMUT: preflight (hashes, inventario, controles negativos, generación y
  baseline exterior) ≈10 s; campaña 61 s exteriores (máx. 1,90 s/intento de
  30 s; 61 s de 600 s/campaña); verifier de campaña ≈15 s; **≈86 s de los
  900 s exteriores**. Sin intentos inválidos propios de la campaña; sin
  ampliaciones ni transferencias de presupuesto.

## 10. Próxima puerta mínima

Con la puerta conforme y Q-ACCMUT ejecutada (o declarada no ejecutada):
G-MUT de fuentes en un encargo propio (adjudicación sobre el bruto conservado
y las excepciones registradas, sin bless), luego Q-COVCRAP → Q-DRY → tier
full PRE-BLESS con la revisión humana del diff protegido (E9: drift 37 = 7+30)
→ E10/E11 (versión, custodia, salida de borrador). Nada de esto se autoriza
aquí.

## 11. Límites

No ratifica equivalencias fuera de las registradas; no ejecuta campañas
históricas de fuentes ni los 928 IDs; no modifica producto, tests, features,
gobernanza, manifests, ratchets, lock ni versión; no bendice, no hace merge,
bump, tag ni release; no declara cierre integral AC1/beta.3. La evidencia
citada bajo `build/tmp/` es temporal, no custodia durable. La publicación de
este registro y las filas afectadas de la matriz es el único cambio
versionado de este encargo.
