# Acta de cierre acotado GS-3 (2026-09-15)

Registra las decisiones humanas D1–D3 comunicadas en el encargo «Cierre
acotado GS-3 y plan ejecutable de cierre AC1/beta.3» (2026-09-15) y cierra
GS-3 **en su alcance medido**. Este documento es documental: no ejecuta
campañas ni sondas de mutantes, no corre sondas bytes/string, no implementa
reparaciones, no modifica producto, tests, features, gobernanza, dependencias
ni umbrales, y **no** bendice, no actualiza el manifiesto, no hace merge, bump,
tag ni release. La PR #53 permanece en borrador.

Fuentes de la transcripción: el encargo citado (decisiones D1–D3) y los
registros del incremento que obran en esta rama:

- `GS3-SEMGREP-RESULTADO-2026-09-15.md` (campaña y atribución).
- `ADENDA-GS3-ADJUDICACION-2026-09-15.md` (adjudicación 13 A + 14 B + 7 C).
- `GS3-CONTRATOS-REGRESIONES-Y-EQUIVALENCIAS-2026-09-15.md` (D1–D5 de
  `G-SAST-SEMGREP`, 27 regresiones, 4 equivalencias `check`).
- `GS3-DOMINIO-BYTES-STRING-2026-09-15.md` (dictamen A de 24/29/33).

## 1. Decisiones humanas transcritas

### D1 — Ratificación de las tres equivalencias bytes/string

Texto de la decisión:

> Ratifico las equivalencias de `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_24`,
> `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_29` y
> `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_33`, exclusivamente bajo
> las precondiciones documentadas (Semgrep 1.174.0 y productor identificado;
> COMMAND exacto del expediente; stdout directo del productor, sin wrapper que
> altere los bytes; salida JSON UTF-8 sin BOM; decodificación efectiva UTF-8).
> No es equivalencia general para cualquier instalación o entrada. Si cambian
> fuente, productor, comando, runtime o condiciones relevantes, la ratificación
> debe revisarse. La calificación final deberá comprobar estas precondiciones y
> conservar su evidencia; si no se cumplen, no podrá trasladar la ratificación.

Los tres IDs, con su mutación medida en el expediente GS-3:

| ID completo | Mutación | Clase de adjudicación |
|---|---|---|
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_24` | `subprocess.run(..., text=True)` → `text=None` | C (equivalencia acotada) |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_29` | `text` omitido (bytes); el `run` recibe el default | C (equivalencia acotada) |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_33` | `text=False` (bytes) | C (equivalencia acotada) |

Precondiciones ratificadas (las cinco del texto de D1, sin ampliación):

1. **Semgrep 1.174.0 y productor identificado**: binario de esa versión, con
   procedencia registrada; serializador JSON del productor sin BOM.
2. **COMMAND exacto del expediente**: la tupla `COMMAND` del gate congelado
   (`semgrep --quiet --error --severity ERROR --config governance/semgrep
   --json`), sin variantes.
3. **Stdout directo**: salida capturada directamente del productor, sin
   wrapper, proxy ni interposición que altere los bytes.
4. **Salida JSON UTF-8 sin BOM**.
5. **Decodificación efectiva UTF-8** en el consumidor
   (`subprocess.run(text=True)` resuelve a UTF-8; sin `PYTHONUTF8=0` ni locale
   no-UTF-8).

Alcance y caducidad: la ratificación es **específica de estas precondiciones
y de este dominio**, no una equivalencia general. Cambios de fuente,
productor, comando, runtime o condiciones relevantes obligan a revisarla. No
se ratifica por analogía ninguna otra variante (`text=True` sigue vigente como
implementación; las diferencias fuera de dominio —BOM UTF-8/UTF-16, locale no
UTF-8— permanecen como contraejemplos documentados en
`GS3-DOMINIO-BYTES-STRING-2026-09-15.md` §4).

### D2 — Tratamiento actual del decode error

Texto de la decisión:

> Mantener para este incremento el tratamiento actual del decode error. La
> evidencia indica que el runner lo convierte en ERROR y el CLI bloquea. No
> autorizo modificar producto para convertirlo ahora en «salida ilegible». No
> presentar esto como diagnóstico ideal ni como nueva garantía universal.

Hechos que la decisión conserva (registrados en
`GS3-DOMINIO-BYTES-STRING-2026-09-15.md` §2 y §5):

- El gate directo captura `(SemgrepScopeError, OSError)`;
  `UnicodeDecodeError` queda fuera de esa captura y se propaga.
- El **runner** la convierte en `GateResult(ERROR, "guard crash:
  UnicodeDecodeError: …")` (`tools/wct/gate/runner.py:545-554`); `ERROR`
  bloquea (`tools/wct/model.py:29-30`); el CLI devuelve 1 si hay resultados
  bloqueantes (`tools/wct/cli.py:211`).
- El contrato fail-closed de `docs/gates.md` («un error del harness nunca se
  interpreta como permiso») **se cumple**, pero la causa no se clasifica como
  «salida ilegible» sino como guard crash.
- No se localizó obligación estructurada que exija la clasificación
  «salida ilegible» para entrada indecodificable; convertirla es un cambio de
  producto **no autorizado** en este incremento.

D2 no declara este comportamiento idóneo ni universal: queda como decisión de
alcance del incremento, revisable en un incremento futuro con autorización
propia.

### D3 — Registro de cierre GS-3

Texto de la decisión:

> Registrar GS-3: «Cerrado en su alcance medido mediante evidencia sucesiva y
> equivalencias ratificadas con precondiciones explícitas». Conservar: bruto
> histórico 108 = 74 killed + 34 survived; 27 regresiones posteriores
> demostradas; 7 equivalencias ratificadas en sus respectivos alcances; sin
> nueva campaña conjunta 108/108; sin PASS automático de G-MUT, acreditación
> AC1 ni cierre beta.3.

## 2. Cuatro equivalencias ya ratificadas (referencia, sin re-ratificar)

Se referencian las cuatro equivalencias `check` ratificadas en
`GS3-CONTRATOS-REGRESIONES-Y-EQUIVALENCIAS-2026-09-15.md` §3; **no se
re-ratifican aquí ni bajo condiciones distintas**:

- `tools.wct.gate.semgrep.x__topology__mutmut_6` (`check=False` → `None`).
- `tools.wct.gate.semgrep.x__topology__mutmut_11` (`check` omitido).
- `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_26` (`check=None`).
- `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_31` (`check` omitido).

Alcance original: solo esos IDs, runtime Python 3.13.14 con
`subprocess.run` y la semántica `if check and retcode`; no se extiende a
`check=True`; revisión obligatoria si cambian fuente, runtime o precondiciones.

## 3. Capas de evidencia y contabilidad histórica (sin agregación)

| Capa | Contabilidad | Estado |
|---|---|---|
| Campaña bruta GS-3 | **108 = 74 killed + 34 survived** | Inmutable; no se repite |
| Adjudicación | 34 = **13 A + 14 B + 7 C** | Completa |
| Contratos y regresiones | Contratos D1–D5 de `G-SAST-SEMGREP` en `docs/gates.md`; **27/27** A+B con regresión permanente y sensibilidad medida (sin campaña) | Cerrado en alcance |
| Equivalencias | **7 ratificadas** en sus respectivos alcances: 4 `check` + 3 bytes/string (D1) | Cerrado en alcance |
| Campaña conjunta 108/108 | **No ejecutada** | No exigida por este cierre |
| G-MUT / AC1 / beta.3 | **Sin PASS automático, sin acreditación, sin cierre** | Abiertos en la matriz |

Notas de contabilidad:

- Ratificar una equivalencia **no convierte** el `survived` histórico en
  `killed`: el bruto 108 = 74 + 34 no cambia.
- Las 7 equivalencias se ratifican en alcances distintos (4 `check` bajo
  runtime y semántica `if check and retcode`; 3 `text` bajo las
  precondiciones de D1); no se agregan como una única garantía.
- La evidencia durable de cada capa es su registro versionado; los
  expedientes bajo `build/tmp/` son locales y temporales.

## 4. Gate directo y runner: distinción vigente

- **Gate directo** (`tools/wct/gate/semgrep.py`): ante stdout no
  decodificable propaga `UnicodeDecodeError` porque solo captura
  `(SemgrepScopeError, OSError)`.
- **Runner** (`tools/wct/gate/runner.py`): convierte la excepción en
  `GateResult(ERROR, "guard crash: …")`; `ERROR` bloquea y el CLI devuelve 1.

La distinción importa: el fail-closed se satisface por la vía del runner, no
por una clasificación estructurada del gate directo. D2 mantiene ese
comportamiento; no es diagnóstico ideal ni garantía universal.

## 5. Comprobación de entorno para la calificación del SHA final

Estas comprobaciones **deberán ejecutarse al calificar el SHA final** y
conservar su evidencia en el expediente de calificación (no se ejecutan en
este acta; las comprobaciones pesadas pertenecen a la oleada de calificación
del plan). Son precondiciones de traslado de la ratificación D1:

1. **Productor**: `semgrep --version` == `1.174.0`; registrar la ruta
   resuelta del binario y su sha256 (identidad del productor; sin wrapper ni
   proxy en `PATH`).
2. **Fuente del gate**: sha256 de `tools/wct/gate/semgrep.py`; si difiere del
   congelado `0126c4e1bdad3a445a3d3821b46cdd75d1ebec6e2d080ab299fd8d2ebd682657`,
   la ratificación **no se traslada automáticamente** y debe revisarse. El
   literal de `COMMAND` debe coincidir con el del expediente
   (`semgrep --quiet --error --severity ERROR --config governance/semgrep --json`).
3. **Decodificación efectiva**: en el runtime de calificación, registrar
   `subprocess._text_encoding()` con el entorno efectivo y comprobar que
   resuelve a UTF-8, con locale UTF-8 y sin `PYTHONUTF8=0`.
4. **Salida UTF-8 sin BOM**: corrida de control del COMMAND sobre una regla
   de demostración; registrar los primeros bytes del stdout (JSON sin BOM;
   referencia observada del expediente: `7b 22 76`) y conservar la salida
   cruda. Esta comprobación es de precondición, no una repetición de las
   sondas bytes/string.
5. **Conservación**: comandos, versiones, hashes y salidas en el expediente
   de calificación (rutas explícitas), referenciados desde el registro de
   calificación del SHA final.

Si alguna precondición no se cumple en el SHA final, la ratificación de
24/29/33 **no puede trasladarse** y la decisión vuelve al humano.

**Estado ligero verificado al 2026-09-15** (comprobación de identidad, no
campaña): runtime de referencia con Python 3.13.14, `semgrep 1.174.0`,
`subprocess._text_encoding()` → `UTF-8`; `tools/wct/gate/semgrep.py` con
sha256 `0126c4e1…`; expediente `build/tmp/gs3-dominio.2512829890` (checkout
principal) presente, `sha256sum -c gs3-dominio.sha256` conforme y digest del
manifiesto `c2c97d1e…`. Esta comprobación se repetirá formalmente sobre el
SHA final.

## 6. Límites de este acta

No autoriza ni declara: bless, `update-manifest`, merge, bump, tag, release,
cambio de producto/tests/gobernanza/umbrales, campañas nuevas, ratificación de
otros pendientes por analogía u omisión, acreditación AC1, cierre de beta.3 ni
PASS de G-MUT. GS-3 queda cerrado **en su alcance medido**, con los pendientes
de AC1 y beta.3 que el plan ejecutable `PLAN-EJECUTABLE-CIERRE-AC1-BETA3-2026-09-15.md`
inventaría y ordena. G-META-1 (drift de integridad pre-bless) pertenece al
incremento acumulado y sigue pendiente de revisión humana y bless: no es
«ajeno» a la entrega global.
