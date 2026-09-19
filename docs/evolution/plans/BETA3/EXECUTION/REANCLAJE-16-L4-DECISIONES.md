# Acta REANCLAJE-16 — decisiones humanas registradas para el cierre de L4 (2026-09-19)

Estado: **registro prospectivo de las decisiones autorizadas por el encargo
REANCLAJE-16, verificadas contra los diffs sellados ANTES de implementar
controles o ejecutar experimentos.** Ninguna aprobación histórica se inventa:
las decisiones proceden de este encargo. Identidades resueltas contra
`custodia/inventario-nuevo-ids.json` + `custodia/diffs-por-id-nuevo.txt`
(byte-idénticos a los sellos R12) y `custodia/07-adjudicacion-46.json`
(byte-idéntico al sellado R13). Hash de las tres fuentes vigentes:
`pytest_decode_header.py ed6f6bc1…`, `pytest_decode_events.py d73b5b26…`,
`pytest_sequence.py 01447409…` (== corte técnico 0487448 == candidato ae67ae0:
delta técnico→documental sin cambios de fuentes).

## D-A — RATIFICADAS las 12 equivalencias acotadas de R13

Ámbito: exclusivamente los fundamentos estructurales, dominios y
precondiciones acreditados por ID en R13 §4 (evidencia `logs/07` de R13), sobre
las fuentes vigentes. No se extiende a otros operadores por semejanza ni a
entradas excluidas por esos fundamentos.

| ID completo (módulo::función) | Diff exacto | Fundamento R13 | Invalidantes |
|---|---|---|---|
| `…pytest_decode_events.x__validated_vector__mutmut_13` | `dict(zip(names, values, strict=True))` → `strict=None` | zip-strict tras raise de longitud desigual previo EN LA MISMA FUNCIÓN (`len(values) != len(names)` → invalid_field): el strict jamás dispara | reordenar/quitar el chequeo previo de longitud; cambiar la aridad |
| `…x__validated_vector__mutmut_16` | → `zip(names, values, )` | idem | idem |
| `…x__validated_vector__mutmut_17` | → `strict=False` | idem | idem |
| `…pytest_decode_header.x__match_executions__mutmut_10` | `zip(wire_execs, executions, strict=True)` → `strict=None` | idem (`len(wire_execs) != len(executions)` → invalid_field antes) | idem |
| `…x__match_executions__mutmut_13` | → `zip(wire_execs, executions, )` | idem | idem |
| `…x__match_executions__mutmut_14` | → `strict=False` | idem | idem |
| `…pytest_sequence.x__inventory_key__mutmut_9` | `getattr(payload, "phase", "")` → `None` | el default jamás se usa: el guard `cls is PhaseMake or PhaseLog` solo deja pasar clases con `phase: str` REQUERIDO (payload_classes L165+) | admitir en el guard una clase sin `phase` |
| `…x__inventory_key__mutmut_12` | → `getattr(payload, "phase", )` | idem | idem |
| `…x__inventory_key__mutmut_15` | → `getattr(payload, "phase", "XXXX")` | idem | idem |
| `…pytest_decode_events.x__validated_vector__mutmut_24` | `fields["nodeid"] = _int_in(fields["nodeid"], 0, SEQ_MAX)` → clave `fields["XXnodeidXX"]` | asignación a clave basura: el RHS `_int_in(...)` se evalúa IDÉNTICO (raise incluido) y la clave destino es inerte para los builders por clave (reclasificación H1 verifier R13) | builders que consuman la clave mutada; cambio de aridad |
| `…x__validated_vector__mutmut_25` | → clave `fields["NODEID"]` | idem | idem |
| `…pytest_decode_header.x__bad_wire_strings__mutmut_5` | `wire[2:5]` → `wire[2:6]` | slice truncado por `len(wire) != 5` que raise antes; `_EVENT_VECTOR_FIELDS=5` y el literal de ejecuciones tiene exactamente 5 | vector de ejecución con ≠5 elementos admitido |

Evidencia histórica por ID: campaña R12 exit 0 + sonda fresca
SURVIVED-REPRODUCIDO (R12 logs/13) + batería 293 exit 0 (R13 logs/04) +
fundamento estructural R13 `logs/07`. Dominio admitido: journals/headers bajo
el contrato P03 vigente. Disposición tras ratificación: **permanecen
survived con disposición RATIFICADA-EQUIVALENTE** (una ratificación cambia la
disposición, no el resultado instrumental).

## D-B — RATIFICADAS las 11 equivalencias por canal de atribución inerte

Condición del encargo verificada doblemente: (1) **inercia del canal en el
original** — `finding.execution_id` es constantemente None en todo camino
alcanzable: `attributed` se consume únicamente como argumento de
`_execution_index`, y sus dos ramas de raise (invalid_field: `type(ex_value) is
not int`; foreign_reference: `ex_value` fuera de `[0, len)`) contradicen la
guarda `type(ex_value) is int and 0 <= ex_value < len` de `_attributed_execution`,
luego el argumento vale None ya en el original; ningún otro raise del paquete
pasa ejecución; `_finish` copia `defect.execution_id` (None). Sonda empírica R14
(logs/08): defecto con ex=0 válido → `execution_id=None` → `_decoder_blocks`
bloquea ambas ejecuciones. (2) **CADA diff concreto conserva la inercia y no
introduce otra divergencia observable** — verificado por lectura de cada diff
contra la traza anterior:

| ID completo | Diff | Por qué conserva la inercia |
|---|---|---|
| `…x__attributed_execution__mutmut_2` | guarda → `type(None) is int and …` | el retorno solo alimenta el argumento de `_execution_index`, que en el original ya es None en ambas ramas de raise y no se lee en la rama válida |
| `…x__attributed_execution__mutmut_4` | `0 <=` → `1 <=` | cambia el retorno para ex=0; ese retorno solo se consume donde el original ya aporta None (ramas de raise) o no se lee (rama válida) |
| `…x__attributed_execution__mutmut_5` | `0 <=` → `0 <` | idem |
| `…x__decode_event__mutmut_19` | `attributed = None` | idem: solo alimentaba ese argumento |
| `…x__decode_event__mutmut_20` | `attributed = _attributed_execution(None, state)` | `type(None) is not int` → devuelve None: idéntico consumo |
| `…x__decode_event__mutmut_39` | `_execution_index(ex_value, state, None)` | pasa None donde el original ya pasaba None en las ramas que lo leen; la rama válida retorna sin leerlo |
| `…x__execution_index__mutmut_4` | `raise _DefectError("invalid_field", None)` | en esa rama `attributed` ya es None por contradicción de guardas |
| `…x__execution_index__mutmut_6` | `raise _DefectError("invalid_field", )` | idem (argumento omiso = None) |
| `…x__execution_index__mutmut_14` | `raise _DefectError("foreign_reference", None)` | en esa rama `attributed` ya es None por contradicción de guardas |
| `…x__execution_index__mutmut_16` | `raise _DefectError("foreign_reference", )` | idem |
| `…x__finish__mutmut_5` | `execution_id=defect.execution_id,` → `execution_id=None,` | `defect.execution_id` es None en todo raise alcanzable del paquete (D-B.1) |

NO se aprueba nueva obligación de atribución por ejecución; NO se modifica
`finding.execution_id` ni su tratamiento productivo. **Invalidantes comunes**:
poblar el canal en producto, cambiar su contrato, o cualquier callers/refs que
lea `attributed`/`defect.execution_id` con semántica distinta. Dominio: API
pública del decoder bajo contrato vigente. Evidencia: R14 §7 + logs/08; R13 §4;
campaña R12 exit 0 por ID.

## D-A2 — RATIFICADAS las 3 equivalencias observables de R15

Fundamento: las mutaciones solo afectan al diagnóstico (código alzado) de la
rama `type(index) is not int` de `_resolve_field_nodeid`, que ningún llamador
admitido alcanza (validación previa obligatoria `_int_in` con condición de
llamada idéntica; doble análisis independiente R15). Diffs: `raise
_DefectError("invalid_field")` → `None` / `"XXinvalid_fieldXX"` /
`"INVALID_FIELD"` para `x__resolve_field_nodeid__mutmut_6/7/8`. Invalidantes:
nuevo llamador sin validar, alteración intermedia del campo, exposición del
helper como frontera admitida, contrato independiente que obligue a aceptar
ese estado. NO se restaura el test retirado ni se elimina la guardia
productiva. Evidencia: R15 §2/§3 + sondas rc=0 con activación acreditada y
canario rojo.

## D-C — ADMITIDO consume_line__mutmut_22 como defecto detectado

Identidad completa verificada contra el inventario sellado:
`tools.wct.evidence.pytest_decode_events.x__consume_line__mutmut_22`
(función `_consume_line` en `pytest_decode_events.py`; fuente `d73b5b26…`).
Diff exacto: `if defect is not None:` → `if defect is None:`. Bajo la evidencia
R12/R13: original terminante en entorno equivalente (2.78 s verde vs mutante
SIGXCPU −24, rematado −9, en el mismo entorno e imports); ausencia de progreso
causada por el operador mutado (la línea limpia retorna `(None, offset)` sin
decodificar ni avanzar; el bucle público repite el offset idéntico); obligación
contractual de retorno (§4: retornar la observación para toda entrada dentro
del límite); límite de CPU (117.3 s) impuesto por el arnés (RLIMIT_CPU de
mutmut), no SLA del producto. **El bruto histórico conserva su estado
TIMEOUT.** Esta admisión no convierte timeouts genéricos en kills. Si aparece
evidencia que refute la causalidad, la disposición se suspende.

## D-D — AUTORIZADOS los controles de módulo pendientes

`_CATALOG` (transcripción desde la especificación aprobada; inventario,
correspondencias y consumo observable; sensibilidad por perturbación
discriminante en copia desechable), `_CAPPED` (conjunto y obligaciones desde la
fuente contractual; inventario independiente; reutilización de PA09/PA10 donde
correspondan) y **frontera real 20000/20001 declaraciones por API pública**
(sin constantes reducidas, sin ampliar límites, sin estados internos
simulados; entradas válidas respecto de las demás restricciones para aislar el
límite; frontera inclusiva + exceso con diagnóstico contractual y prefijo
conservado). Se conservan los controles acreditados de `expected_seq` y del
tope 10000 (frontera real medida). NO se concede equivalencia ni excepción
automática a los sitios sin IDs.

## Condición común

Si un diff, contrato o premisa no coincidiera: separar el caso, conservar la
evidencia, detenerse antes de la campaña y solicitar decisión sobre la
diferencia. Verificado hoy: 26/26 diffs coinciden con los conjuntos del
encargo; la inercia D-B está confirmada por diff; el candidato ae67ae0
conserva las fuentes selladas. No se amplió ningún dominio.

## Correcciones documentales (encargo §3)

- **(a)** Ratificar un superviviente cambia su DISPOSICIÓN
  (RATIFICADA-EQUIVALENTE), nunca su resultado instrumental: los 26 siguen
  `survived` en el bruto.
- **(b)** Las capas son separadas: causalidad (demostrada) ≠ estado bruto
  (timeout) ≠ admisión humana (D-C). Un eventual rechazo de admisión NO
  convertiría el caso en "fallo instrumental".
- **(c) Reconciliación de los 9.71 s del verifier R15:** cada segundo se midió
  UNA sola vez en UN solo ledger (el del verifier). La presentación "I
  266.87/900 agregado" del registro R15 §10 SUMÓ esos 9.71 s al agregar,
  mientras también se reportaban en SV: doble conteo solo en la presentación
  agregada, no en los ledgers. Total de ejecución real de R15: S 20.94 + SV
  9.71 + I(autor) 257.16 + PUB 5.73 = **293.54 s** (límite R15: 1680). No se
  repiten pruebas para corregir aritmética documental.
