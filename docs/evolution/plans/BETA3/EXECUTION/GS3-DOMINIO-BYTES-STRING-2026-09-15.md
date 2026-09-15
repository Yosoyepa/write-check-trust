# GS-3 — dominio contractual de bytes/string (2026-09-15)

Nota sucesora de `GS3-CONTRATOS-REGRESIONES-Y-EQUIVALENCIAS-2026-09-15.md`
§4. Resuelve el pendiente de los mutantes
`x_gate_sast_semgrep__mutmut_24/29/33` con un dictamen **A: equivalencia
acotada propuesta**, corrige la afirmación categórica previa sobre el BOM y
separa un hallazgo de robustez. **No ratifica**: la propuesta queda para
decisión humana. Sin cambios de producto, tests permanentes, features,
gobernanza ni dependencias; sin campaña nueva, bless, merge, bump ni release.
El bruto histórico sigue **108 = 74 killed + 34 survived** y las 27
regresiones y las 4 equivalencias `check` ratificadas no se tocan.

## 1. Rastreo del contrato (tres niveles)

### 1.1 Nivel normativo — parcial y no decisivo

- **RFC 8259 §8.1** (https://www.rfc-editor.org/rfc/rfc8259.txt): el texto
  JSON «exchanged between systems that are not part of a closed ecosystem
  MUST be encoded using UTF-8»; «Implementations MUST NOT add a byte order
  mark (U+FEFF)…» a un JSON transmitido por red; los parsers «MAY ignore» el
  BOM. Límite: la cláusula habla de JSON transmitido por red; el stdout de un
  proceso local no queda estrictamente cubierto, así que es cita de apoyo.
- **Documentación oficial Semgrep** (https://semgrep.dev/docs/cli-reference,
  consultada 2026-09-15): `--json` = «Output results in Semgrep's JSON
  format»; con tabla de exit codes. **No localizada** cláusula de encoding o
  BOM en las fuentes de documentación revisadas.
- **Contrato del proyecto**: `docs/gates.md` describe G-SAST-SEMGREP como
  `semgrep --config governance/semgrep`; el COMMAND con `--json` vive en
  `tools/wct/gate/semgrep.py:29-38`, y `semgrep_schema` valida un objeto
  JSON. **No localizada** cláusula normativa de encoding/BOM para este gate.

### 1.2 Nivel implementación del productor (Semgrep 1.174.0 fijado)

- El JSON final se serializa en OCaml por RPC: `semgrep/formatter/json.py` →
  `semgrep/rpc_call.py::format`; en la fuente oficial v1.174.0,
  `src/osemgrep/reporting/Output.ml` (`Json → format … |> print`) y
  `Cli_json_output.json_output = Out.string_of_cli_output` (serializador
  atdgen `*_j`), escrito por `libs/commons/UConsole.ml`
  (`print str = Printf.printf "%s\n%!"`) — bytes crudos, sin BOM. En la ruta
  pysemgrep, `semgrep/output.py` imprime la cadena preformateada
  (`print(output)`), que tampoco inserta BOM. Fuentes citadas en
  `evidence/fuentes-oficiales.md`.
- Es evidencia de implementación de la versión fijada: no es garantía
  normativa general ni compromiso de versiones futuras.

### 1.3 Nivel observación empírica

- Dos corridas reales del binario 1.174.0 con `--json` (regla demo, mensaje
  no-ASCII `café ☕`): stdout JSON válido, primeros bytes `7b 22 76`, sin BOM,
  decodificación UTF-8 estricta sin error y no-ASCII crudo, bajo `LC_ALL=C` y
  default (`evidence/salida-*.json`; intentos sin target quedan invalidados).
- Una salida concreta no agota el espacio de salidas: corrobora, no demuestra.

## 2. Codificación efectiva del consumidor

- Llamada productiva: `subprocess.run(list(COMMAND), cwd=root, text=True,
  capture_output=True, check=False)` (`tools/wct/gate/semgrep.py:83-85`), sin
  `encoding`/`errors`: CPython usa `subprocess._text_encoding()`
  (`subprocess.py:367-384`): `utf-8` si UTF-8 mode está activo; si no,
  `locale.getencoding()`. Medido en el runtime (Python 3.13.14):
  `LANG=es_CO.UTF-8` → locale UTF-8; `LC_ALL=C` → `utf8_mode=1` →
  decodificación UTF-8; locale ISO-8859-1 → latin-1 (mojibake con UTF-8 no
  ASCII: contraejemplo de precondición, `evidence/consumidor-comprobaciones.txt`).
- `json.loads`: con `str` y BOM U+FEFF → `JSONDecodeError`; con `bytes` →
  `detect_encoding` elige `utf-8-sig`/`utf-16`/`utf-32` según BOM y sin BOM
  usa `utf-8` (CPython `json/__init__.py:248-255,341`). En el dominio UTF-8
  sin BOM, la ruta `bytes` aplica exactamente la misma decodificación UTF-8
  que `text=True`.
- Excepciones del gate: captura `(SemgrepScopeError, OSError)`;
  `UnicodeDecodeError` queda fuera (hallazgo separado, §5).

## 3. Comprobaciones (Fase 3) y presupuesto

- Productor real: 3 corridas válidas (control de patrón y las dos `--json`)
  más 2 intentos invalidados por falta de target: **41.472 s**.
- Consumidor: hijos reales con tres locales + `json.loads`/`detect_encoding`:
  **≤3 s (estimado, sin cronometrar)**. Total **≤45 s de 180 s** (revisión documental aparte). Detalle en
  `evidence/presupuesto-dominio.md`.

## 4. Dictamen: A — equivalencia acotada propuesta

**Dominio D**: la salida por stdout del binario Semgrep **1.174.0** con el
COMMAND del gate, producida por su serializador JSON (sin BOM), capturada por
`subprocess.run(text=True)` en un entorno cuyo text encoding resuelve a
**UTF-8**.

Dentro de D, `text=None`/omitido/`False` (mutantes 24/29/33) y `text=True`
original son **observacionalmente equivalentes**:

- todo texto JSON UTF-8 sin BOM se decodifica igual (misma cadena, mismo
  árbol, mismos diagnósticos); el JSON malformado produce el mismo
  `JSONDecodeError` → `salida ilegible`;
- el UTF-8 inválido produce la misma `UnicodeDecodeError` en ambos caminos
  (subprocess o `json.loads`), ya medido;
- la mutación no altera ningún otro campo de `GateResult`.

**Precondiciones completas**: versión 1.174.0; COMMAND exacto y stdout directo
del binario; entorno de decodificación UTF-8 (locale UTF-8 o UTF-8 mode, sin
`PYTHONUTF8=0` ni locale no-UTF-8); el productor no emite BOM.

**Qué invalidaría la conclusión**: cambio de versión o del COMMAND; locale no
UTF-8 (medido: mojibake); `PYTHONUTF8=0`; wrapper/proxy en PATH; cambio del
serializador o emisión de BOM.

**Contraejemplos fuera de D**: BOM UTF-8 (original `salida ilegible` vs
mutante PASS) y BOM UTF-16 (original `UnicodeDecodeError` vs mutante PASS),
solo alcanzables con un productor ajeno al binario fijado; bytes no
decodificables (ambos `UnicodeDecodeError`).

Sigue siendo **propuesta para ratificación humana**: los tres IDs permanecen
no ratificados hasta esa decisión.

## 5. Hallazgo separado de robustez

- Evidencia: una salida indecodificable hace que `gate_sast_semgrep` propague
  `UnicodeDecodeError` en vez de devolver `GateResult`. Extremo a extremo, el
  runner la convierte en `GateResult(ERROR, "guard crash: UnicodeDecodeError:
  …")`   (`tools/wct/gate/runner.py:545-554`), `ERROR` bloquea
  (`tools/wct/model.py:29-30`) y el CLI devuelve 1 si hay resultados
  bloqueantes (`tools/wct/cli.py:211`). El contrato fail-closed de
  `docs/gates.md` («un error del harness nunca se interpreta como permiso»)
  **se cumple**, pero la causa no se clasifica como «salida ilegible» sino
  como guard crash.
- **Obligación estructurada**: no localizada. `semgrep_schema` clasifica
  `JSONDecodeError`, no errores de decodificación de bytes; `docs/gates.md` no
  exige la clasificación estructurada de este caso.
- Decisión pendiente, no corregida aquí: mantener el guard crash actual o
  exigir `GateResult(ERROR, "salida ilegible")` para entrada indecodificable
  (cambio de producto que este encargo no autoriza).

## 6. Corrección sucesora

La frase categórica de `GS3-CONTRATOS-REGRESIONES-Y-EQUIVALENCIAS-2026-09-15.md`
§4 («fuera de dominio: diferencia observable», referida al BOM) **no queda
respaldada como exclusión normativa**: la exclusión del BOM descansa en la
implementación del productor v1.174.0 (serializador atdgen sin BOM + escritura
cruda) y en la observación empírica, no en una cláusula de proyecto
localizada. El BOM sigue siendo una diferencia observable del consumidor ante
un productor distinto del binario fijado. No se edita el documento previo:
esta nota preserva la historia de la hipótesis.

## 7. Estado real

- `mutmut_24/29/33`: **propuesta A pendiente de ratificación humana**; no se
  declaran equivalentes ratificadas.
- `mutmut_6/11/26/31` (check): ratificadas en su alcance, sin cambios.
- 27 regresiones intactas; bruto 108 = 74 + 34 intacto; GS-3, AC1 y beta.3
  **no cerrados**; G-META-1 pre-bless sigue siendo un pendiente global
  separado.
- Expediente local `build/tmp/gs3-dominio.2512829890` (manifiesto y digest al
  cierre); la evidencia durable es este registro.
