# Registro REANCLAJE-21 — auditoría causal y adjudicación contractual de L8 (2026-09-19)

Estado: **auditoría de los 131 kills-por-colección y adjudicación individual
de los 39 supervivientes ejecutadas y reconciliadas; corrección documental de
G-META-1 publicada como nota sucesora; controles propuestos para el código no
instrumentado. Sin reparaciones, sin ratificaciones, sin recampaña.** El bruto
R20 se conserva intacto: 398 = 359 KILLED + 39 SURVIVED. Las clasificaciones
sucesoras de esta auditoría se presentan SEPARADAMENTE del bruto.

## 1. Base, identidades y aislamiento

- Cabeza comunicada `72c25c61b3eb4c9bc60e1378df9968a6aea28efc` == remoto
  `origin/codex/reanclaje-p03a-fase1` == commit del registro R20. Sin avance
  posterior (la copia local de la rama está simplemente retrasada, 0 commits
  propios). PR #56 en borrador, OPEN.
- Main de referencia `8a379d64…` == merge-base (rama estrictamente por
  delante). Tag `v1.0.0b3.dev1` → `8a379d6` = main, intacto.
- SHA auditado: `72c25c61b3eb…` (todo el análisis contractual y de fuentes
  se leyó del árbol committed en ese SHA, no de copias de trabajo).
- Expediente aislado `build/tmp/reanclaje21-20260919/` con clon local de raíz
  Git propia en `tree/` (checkout detached en el SHA auditado) y CUATRO
  copias privadas del árbol instrumentado congelado de R20 (`mutants-coord`,
  `mutants-agenteA`, `mutants-agenteB`, `mutants-verifier`), cada una
  verificada contra `sellos-R20.json` (4 fuentes instrumentadas + 3 archivos
  de tests byte-idénticos) antes de cada corrida por el lanzador fail-closed.
- Checkout principal, su índice y expedientes históricos INTACTOS (verificado
  por el verifier). Runtime: Python 3.13.14, pytest 9.1.1, mutmut 3.7.0
  (trampolines del instrumentado).

## 2. Verificación del sello R20 antes de reutilizar artefactos

`MANIFIESTO-REANCLAJE20.sha256`: **79/80 miembros OK; exactamente 1 miembro
divergente: `logs/00-ledger-guardian.csv`** (mtime 15:50:40 > sello 15:35).
Caracterización exacta: la divergencia es **puramente aditiva** — el prefijo
sellado de 907 líneas hashea exactamente al digesto sellado
(`adc6d840…5196d`); se añadieron **17 filas post-sello** (1 fila V del
verifier final de R20 — que consolida 4 reejecuciones en su nota — y las 16
filas PUB01–PUB08 de publicación). El sello original NO se reconstruye como
íntegro: se usa el prefijo sellado como evidencia y las filas post-sello
como evidencia separada de publicación. Ningún otro miembro diverge; el
ledger de campaña (`B-ledger-campana.json`), los logs B/C/A y la custodia
están íntegros. (Conteo verificado dos veces: 924 líneas totales − 907 del
prefijo; una primera transcripción propia dijo «18» por artefacto del split
y fue corregida tras el dictamen del verifier.)

## 3. Mecanismo del clasificador y límites del preprobe (lo que R20 acreditó y lo que no)

- `campana-20.py` clasifica **KILLED** cualquier rc=1 acompañado de líneas
  `FAILED` o `ERROR`, bajo `-q --tb=no -x` con la selección congelada de 580.
  Con `--tb=no` la evidencia por ID de los 131 fue UNA línea truncada
  (archivo + tipo de excepción + mensaje parcial): **la campaña no acreditó
  por sí sola ni la traza ni la activación dentro del proceso de pytest**.
- `lanzador.py` (R20) verifica hashes/identidad/activación en el proceso
  LANZADOR y su sonda ambiental importa `pytest_decode_events` en un proceso
  PREVIO — no las fuentes L8 dentro del proceso de pytest. Una etiqueta
  `LANZADOR-OK` no sustituye la atribución causal in-process.
- **R21 cierra esa brecha por sondeo**: cada reejecución con `--tb=long`
  muestra, DENTRO del proceso de pytest, el frame del trampolín de mutmut
  (`mutated_func(*call_args, **kwargs)`, trampoline.py:88), el frame de la
  variante (`def x__…__mutmut_N`) con la línea mutada marcada, y la cadena de
  colección completa (§4). El control ORIGINAL en el mismo entorno (580
  passed) excluye causas ambientales, de dependencias y de árbol equivocado.
- Cadena causal de colección (verificada fila a fila en los 95 sondados):
  `CASES = _build_cases()` (nivel de módulo) → `_pa12_cases()` →
  `_decode_golden()` → `decode_pytest_journal(GOLDEN, …)` — el SUT completo
  decodifica el journal dorado aprobado (§8) durante la colección del módulo
  de tests. Un consumidor legítimo ejecuta el SUT para construir sus casos.

## 4. Frente A — auditoría causal de los 131 KILLED-por-colección

Conjunto derivado por diferencia del ledger sellado: KILLED ∧ n_fallos=0 ∧
n_errores>0 = **131 IDs exactos** (cada uno con exactamente 1 ERROR y 0
FAILED, todos en `tests/unit/test_pytest_observation.py`); los otros 228
KILLED tienen FAILED sin ERROR; 0 estados intermedios. Agente A con copia
privada y lanzador-21 (controles 1-7 de R20 intactos).

**Resultado: A1=95 · A2=0 · A3=0 · A4=36.**

- **95 A1 — defecto contractual detectado durante colección, con causa
  sustentada**: en los 95, fila completa acreditada EN PROCESO (rc=1 bruto,
  trampolín + variante + línea mutada en el traceback, cadena de colección
  completa, tipo de excepción coincidente con el log sellado en el 100 %).
  La línea del traceback coincide exactamente con el diff sellado en 66; en
  los 29 restantes la discrepancia es mecánica y explicada (28 delecciones
  donde el traceback marca la sentencia `return Clase(` contenedora + 1
  asignación-a-None que aflora en la línea consumidora siguiente).
- **36 A4 — evidencia insuficiente (sonda individual no ejecutada por
  agotamiento del sobre S global)**: los 31 `x_decode_journal` + 5
  `x_consume_header` restantes de `pytest_schema.py`. Cada uno conserva fila
  individual (diff estático del instrumentado sellado + excepción sellada +
  clase causal de contexto), pero SIN la acreditación in-process que este
  encargo exige para A1. No se promueven por afinidad.
- **Familias causales medidas (95 A1)**: KeyError por literal de clave mutado
  (XXwrap/upcase) ×50; TypeError de constructor con argumento eliminado ×28
  (cubre 28/28 campos de las 4 clases con builder nombrado); TypeError de
  aridad en ayudante de wire ×11; comparación con None ×2; operando
  aritmético None ×1; None en función exigente ×3.
- **Caso anómalo `TypeError: x__consume_header__m…` (2 IDs, en el residuo)**:
  determinación estática: la CAUSA es el defecto semántico del mutante
  (aridad del sitio de llamada `_consume_header(job)` / `(data,)`); el NOMBRE
  del mensaje es artefacto de visualización — el despacho cae al alias
  `x__consume_header__mutmut_orig` del trampolín (trampoline.py:79). No es
  fallo instrumental (A2): el trampolín despachó correctamente. El verifier
  lo reejecutó dinámicamente (§9). Quedan A4 por falta de sonda individual.
- **Por qué no hay A3**: la detección nunca depende de que el andamiaje
  llame a internals no contratados: los ayudantes privados mutados se
  alcanzan a través de la API pública `decode_pytest_journal` sobre el GOLDEN
  aprobado (§8). Los 228 kills por fallo de test NO se reabrieron: ningún
  invalidante los alcanza.
- Control ORIGINAL: **580 passed, rc=0** (mismo entorno, misma selección).

## 5. Frente B — adjudicación contractual de los 39 supervivientes

Conjunto derivado por diferencia (SURVIVED) = **39 IDs exactos**; diffs
extraídos estáticamente del instrumentado sellado (398/398 con diff; los 39
coinciden con la agrupación descriptiva de R20). Agente B con escenario
discriminante bajo lanzador-21 y lectura contractual
(`PROPUESTA-P03.md` + feature PA01–PA12).

**Resultado: B1=0 · B2=29 · B3=10 (propuestas, SIN ratificar) · B4=0 ·
B5=0 · B6=0.**

| Grupo | IDs | Medición | Adjudicación | Fundamento contractual |
|---|---|---|---|---|
| Placeholders `build_execution_start` | 8 (`1/7/8/9/19/35/36/37`) | igual en golden y en cabecera alternativa con digests no triviales (`b*64`): el valor final SIEMPRE viene de la cabecera | **B3 propuesta** | §3 l.165-167 (role/digests se reconstruyen desde la cabecera); `_reconstruct_refs` (pytest_decode_events.py l.102-112) reemplaza INCONDICIONALMENTE antes de construir el `JournalEvent`; defecto intermedio descarta el evento completo — el placeholder no puede escapar |
| Atribución de findings | 22 | diferencia medida en los 22 (18 en sonda principal; 4 `_deselection_rule` requirieron escenarios suplementarios de marker-cambiado/propiedad-inesperada): `execution_id`/`nodeid`/`offset` del finding cambian (y nodeid/offset pueden REORDENAR la salida pública vía `_sort_key`) | **B2** | §7 l.478-480 («identifica execution/nodeid/phase/offset»; «Offset apunta al evento causante»; `execution_id=None` RESERVADO al finding global de decoder) + §7 l.482-486 (orden determinista) + §2 l.84-85; los oráculos actuales (`_assert_reconciled_codes`, l.2752-2767) asiertan SOLO códigos |
| Frontera de cabecera | 5 | `consume_header_10/13`: igual en los 5 escenarios (línea sin LF re-deriva `truncated_line` idéntico por el camino de línea — convergencia en `_finish`); `14/15/16`: diferencia medida exactamente en la frontera (código de defecto `limit_exceeded` vs `noncanonical_json` invertido en 65536/65537 exactos) | **B3×2 + B2×3** | §2 l.97 (línea ≤64 KiB INCLUYENDO LF) + precedencia §4 l.253 (límite antes que JSON). La frontera exacta NO es alcanzable por cabeceras canónicas (esquema fijo, 573 bytes), pero sí por bytes admitidos por la API cuya clasificación está contratada |
| Fronteras del builder | 4 (`31/32/46/47`) | diferencia medida en el valor discriminante exacto: original rechaza exit −256/256 y signal 65 con `invalid_field` y acepta signal 1; los mutantes invierten exactamente eso (−255/255/2/64: igual) | **B2** | §3 l.211 (`exit_code:int -255..255 o N`; `signal:int 1..64 o N`) + §4 l.272-273 + §5 l.359-367. El camino MANUAL ya está testeado (l.1743-1749); el hueco es el camino WIRE |

- **Caso especial `x__selection_findings__mutmut_3`** (`covered.update(None)`):
  la premisa de que «lanzaría TypeError» es **falsa** —
  `Counter.update(None)` es no-op en CPython. La línea SE EJECUTA en cada
  reconcile; el efecto medido es la pérdida del multiconjunto de
  deseleccionados: falsos `selection_mismatch` (0→2) y desaparición del real.
  Sobrevive porque ningún caso combina deselección legítima con
  `codes_exclude=("selection_mismatch",)`. **B2** (§7 l.440-442).
- **B1=0** porque los 39 pasaron la selección COMPLETA (580) en rc=0: no
  existe test pertinente que los detecte hoy. **B4=0**: toda diferencia
  medida está fijada por contrato vigente (por eso B2 y no B4). No se
  trasladó automáticamente la conclusión del canal inerte de L4: aquí la
  diferencia fluye por la salida pública ordenada y por campos con semántica
  reservada.
- Las 10 B3 son **propuestas acotadas** (medición + estructura + invalidantes
  documentados); ninguna equivalencia queda ratificada.

## 6. Frente C — código no instrumentado: controles propuestos

| Elemento | Contrato | Evidencia existente | Perturbación plausible | Control propuesto | Limitación |
|---|---|---|---|---|---|
| 17 lambdas de `_BUILDERS` | §3 (conversión por clase desde el vector wire) | coercers medidos en L2 y en las 4 funciones nombradas (228+95 kills); cableado de campos: **P-C1 medida** — swap `argument_exit↔observed_exit` en SessionEnd **DETECTADA** (3 failed/580) | swap de campos o coercer erróneo en las 16 lambdas no medidas (p. ej. `PluginClaim.name↔module`, `min_len=1→0`) | matriz literal por builder bajo decisión D-D: dict wire canónico → payload esperado independiente del SUT | mutmut 3.7 no registra lambdas en literales de dict de módulo (0 IDs) |
| `ObservationError.__init__` | §2 (excepción normal, `code` cerrado, `field` nombrado) | **P-C2b medida** — swap `self.code↔field` en el cuerpo ejecutado **DETECTADA** (134 failed/580); tests existentes de code/field | variantes físicas del instrumentado (p. ej. `super().__init__(None)`) | ya cubierto conductualmente; opcional transcripción del catálogo de `code` (4 valores) | **precisión a R20**: el dunder SÍ recibió trampolín físico (8 variantes `xǁObservationErrorǁ__init____mutmut_*` en el instrumentado sellado); lo que hubo es **0 IDs registrados en el inventario** — la campaña no los ejecutó |
| Tablas `PROPERTY_FINDING_CODES`/`NON_BLOCKING_CODES` | §7 l.470-476 (catálogo) | cobertura conductual: los códigos se emiten y ordenan en casos PA06/PA07 | añadir/quitar un código del conjunto (clasificación blocking↔no-blocking) | transcripción literal del catálogo (como R16 hizo para L4), bajo decisión D-D | asignaciones de módulo no trampolineadas |
| `ExecutionInventory` | tipo interno de construcción, sin contrato §2 directo | conductual transitiva vía funciones inventory (153 IDs) | — | ninguno requerido salvo decisión | no instrumentable como clase |
| Fachada `__all__` (schema y demás) | SIN contrato de inventario literal (como la fachada de payloads en R19); `EVENT_CATALOG` ya transcrita | — | — | **NINGUNO**: no se impone test literal de `__all__` sin contrato | — |

Perturbaciones temporales discriminantes (P-C1/P-C2b): en copia desechable
`perturb-coord` (destruida tras la medición; `mutants-coord` re-verificada
intacta por hash), claramente separadas de los 398 históricos y NO sumadas al
bruto. «0 IDs» no se convierte en cobertura, equivalencia ni conformidad.

## 7. Corrección documental de G-META-1 (nota sucesora a R20, sin reescribir historia)

- R20 §8 afirmó «254 hallazgos del gate» para G-META-1. **Corrección: 254 es
  la duración en MILISEGUNDOS del check** — la cabecera de
  `logs/I02-gate-commit.log` es `GATE · STATUS · MS · SUMMARY` y el 254 vive
  en la columna MS. Se retira expresamente su interpretación como cantidad de
  violaciones.
- Inventario REAL de drift, medido con `wct integrity check` sobre el SHA
  auditado (`logs/I04-integrity-check.log`, recontado y reejecutado por el
  verifier con resultado idéntico): **36 hallazgos = 2 «modificado»
  (`governance/lint/vulture_whitelist.py`, `tools/wct/accept/mutation_cases.py`)
  + 34 «nuevo protegido»** (módulos `pytest_*` de evidence y
  `mutation_policy.py`). El único hallazgo resumido por el gate en R20
  (`vulture_whitelist.py`) coincide con la primera línea de esta salida.
  (Una primera transcripción propia dijo «38 = 2+36» por descomposición
  errónea del conteo total; corregida tras el dictamen del verifier.)
- El drift fue introducido por la PR #56 (nuevos módulos de producto bajo
  patrón protegido + 2 ediciones autorizadas históricamente sin bless).
  **Delta de ESTE encargo documental: 0** — solo añade un documento bajo
  `docs/`, fuera de los patrones protegidos (verificado con el documento ya
  presente: mismo inventario). Ninguna cifra fue inventada ni copiada sin
  recálculo; 34 (nuevos protegidos) ≠ 36 (total).
- Un error de transcripción no invalida por sí mismo las campañas de R20.

## 8. Presupuestos, incidentes y modalidad

Sobres del encargo (reloj monotónico, guardián preventivo por agente con
ledger propio; consolidación global del coordinador):

| Sobre | Cap | Gastado | Detalle |
|---|---|---|---|
| S (autores A/B/C) | 900 s | **≈916.5 s — EXCEDIDO ≈16.5 s, declarado** | coordinador 94.26 (incl. 12.0 s de smokes/depuración consolidados y 5.5 s de huérfano declarado por A) + agente A 523.33 + agente B 298.85 |
| V (verifier) | 240 s | 60.47 s | V1–V6 + escenario B extra + verificaciones documentales; incluye 1 arranque inválido (fila start sin end) |
| I (local, compartida con verifier) | 300 s | 63.10 s | uv sync (quality), integrity check ×2 (I01–I04, incl. 2 intentos fallidos de ruta/modo), recount del verifier (60.06 s de intento sin cwd agotado a timeout + 0.59 s válido) |
| PUB | 180 s | (§11) | hooks y publicación |

- **Incidente 1 (exceso S)**: las 8 corridas suplementarias `findings-prop`
  del agente B (22.40 s), ejecutadas tras cerrar su sonda principal,
  llevaron el global de ≈888.5 a 910.9 s; el huérfano declarado de A (~5.5 s,
  hijo del lanzador de A095 completado tras el kill del padre) lleva el real
  a ≈916.5 s. El coordinador ordenó ALTO total a ambos autores; cero corridas
  adicionales desde entonces. Los datos de las corridas del exceso se usan
  como evidencia (técnicamente válidos) y el exceso queda declarado con su
  cifra. Sin transferencias entre sobres; sin ampliación silenciosa.
- **Incidente 2 (corte con corridas en vuelo)**: la orden de corte al agente
  A llegó con su gasto en ≈507.6 s; A092–A094 completaron (+15.7 s, dentro de
  su 523.33 ledgerado) antes del kill.
- Incidentes menores: arranque de probe-b rechazado por su propia verificación
  de LINE_MAX_BYTES (0 s de S); primera versión del escenario suplementario
  sin `unexpected_property` (re-medida incluida en el exceso); pkill
  autocompatible de A sin consecuencias; tabla de A reconstruida desde los 96
  logs en disco reusando la MISMA `parsear()` sin reejecutar mutantes.
- Modalidad: autores A y B en copias privadas con subagentes independientes;
  verifier distinto de los autores, sin escritura sobre lo auditado; solo el
  coordinador escribe el documento versionado.

## 9. Dictamen del verifier independiente

**FAVORABLE con dos disidencias aritméticas contra este documento, ambas
corregidas antes del sellado** (dictamen completo:
`verifier/V-DICTAMEN.md`; reejecuciones sobre copia privada
`mutants-verifier` con los controles 1-7; V: 60.47/240 s).

- **Reconciliación de conjuntos: exacta.** Derivación propia del ledger
  sellado: K131 ∧ K228 ∧ S39 particionan los 398; las tablas de A (131
  claves) y B (39 medidas) coinciden Δ=∅ en ambos sentidos, sin duplicados
  ni solapamiento A∩B; los totales declarados (95+36, 29+10) cuadran fila a
  fila; los 131 tienen rc=1 con exactamente 1 ERROR en
  `test_pytest_observation.py` (contado por el verifier en los 131 logs
  sellados) y los 39 rc=0 con «580 passed».
- **Clasificador y preprobe: correctamente caracterizados.** El
  clasificador R20 conflata dos clases evidencialmente distintas (kill por
  fallo de test vs kill por error de colección) — ambas kills reales, pero
  la descomposición de R21 es «correcta y necesaria». El control 7 corre en
  proceso previo y NO acredita activación dentro de pytest; esa acreditación
  la aportan las sondas A en 95/95. `lanzador-21.py` diff-verificado: misma
  semántica, ningún control relajado.
- **Reejecuciones V1–V6 + V-B032: todas concuerdan con los autores.** V1/V5/
  V6: 580 passed rc=0 (ORIGINAL, placeholder, frontera −256). V2/V3 (clases
  dominantes A1): rc=1 con trampolín + variante + línea mutada. **V4 cerró
  dinámicamente la clase anómala del residuo** (`x_decode_journal_25`):
  causa = aridad del sitio de llamada `_consume_header(job)`; el nombre del
  mensaje es el alias trampolín `x__consume_header__mutmut_orig` — coincide
  con la determinación estática de A. V-B032 (wrapper de B sin modificar)
  reprodujo byte a byte el diferencial de `selection_findings_3`.
- **Citas contractuales: las 6 principales + 4 de apoyo, todas fieles**
  (leídas por número de línea en PROPUESTA-P03.md).
- **B3/B2: sólidamente sustentadas, sin ratificación.** El verifier verificó
  en fuente el replace incondicional en `_reconstruct_refs` antes de
  construir el `JournalEvent` (y que `_inventory_key` no lee esos campos) y
  la re-derivación de `truncated_line` con la misma precedencia; confirmó
  con el intérprete que `Counter.update(None)` es no-op en CPython. Sin
  saltos detectados.
- **Disidencia 1 (aceptada y corregida en §7)**: el inventario de drift es
  **36 hallazgos (2+34), no 38** — evidencia: I04 + reejecución propia del
  verifier (rc=1, idéntico).
- **Disidencia 2 (aceptada y corregida en §2)**: las filas post-sello del
  ledger divergente son **17 (1 V + 16 PUB01–PUB08), no 18**.
- Anomalía del verifier registrada: una fila `start` de V1 sin `end` (arranque
  con directorio de logs inexistente; 0 s cargados). Verificador sin
  escritura sobre lo auditado; distinto de los autores; no ratifica
  decisiones humanas.

## 10. Estado final de los frentes

- **L8 permanece ABIERTO** con estas disposiciones pendientes: (a) 36 A4 del
  residuo de colección sin sonda individual (una de sus clases cerrada
  dinámicamente por V4; persiste la exigencia de sonda individual por ID);
  (b) 29 B2 con oráculos por escribir; (c) 10 B3 propuestas sin ratificar;
  (d) decisión humana D-D sobre la matriz de lambdas y la transcripción del
  catálogo; (e) bless/drift de integridad de la PR (36 hallazgos) pendiente
  de decisión humana.
- L2, L3 y L4 conservan sus cierres: esta auditoría no encontró invalidante
  que los alcance (los 228 kills por fallo de test no se reabrieron).
- L1 sigue pendiente de TEST-007. L5–L7 y L9 no se ejecutan. Binding
  PA01–PA12 pausado.

## 11. Custodia y publicación

- Expediente `build/tmp/reanclaje21-20260919/` con: herramientas
  (`lanzador-21.py` fail-closed heredero de los controles 1-7 de R20,
  `guardian21.py`, `extraer-diffs-21.py`, `sellar-21.py`, sondas por agente),
  `tablas/diffs-por-id.json` (398 diffs estáticos), custodia verificada,
  ledgers por agente y deliverables A/B/verifier.
- Sello: manifiesto `MANIFIESTO-REANCLAJE21.sha256` sobre los miembros del
  expediente (sin autoincluirse; copias privadas mutants-* fuera — su
  identidad es la custodia R20); digesto guardado FUERA de los miembros en
  `NOTA-SELLO-21.txt`. Publicación/hooks/CI fuera del sello.
- Commit documental único sobre la rama de PR #56 desde el clon aislado (el
  checkout principal no se toca). Allowlist de UN documento:
  `docs/evolution/plans/BETA3/EXECUTION/REANCLAJE-21-L8-AUDITORIA-ADJUDICACION.md`.
  diff --check + gate fast sobre el árbol pertinente + hooks verificados
  activos ANTES del commit. PR permanece en borrador. CI observada con
  seguimiento acotado y resultado reportado como observado (§12).

## 12. Próximo incremento mínimo PROPUESTO (no ejecutado)

1. **REANCLAJE-22 (reparación acotada L8)**, en tres pasos separables:
   a. Sondas de residuo A: 36 reejecuciones `--tb=long` (~220 s) para cerrar
      los A4 en A1/A2/A4 con evidencia individual.
   b. Oráculos B2 (29): tuplas (code, execution_id, nodeid, offset) en casos
      PA06/PA07; caso de deselección legítima con
      `codes_exclude=("selection_mismatch",)`; fronteras exit −256/256,
      signal 1/65 por vía wire; cabecera exacta 65536/65537 → códigos de
      defecto contratados.
   c. Decisión humana previa: ratificar o rechazar las 10 B3; decidir D-D
      (matriz de lambdas + transcripción del catálogo §7); decidir el drift
      de integridad (38) — las (a)/(b) NO requieren tocar gobernanza.
2. Solo tras (b) y (c): única recampaña L8.
3. Allowlist propuesta para la reparación:
   `tests/unit/test_pytest_schema.py` + `tests/unit/test_pytest_observation.py`
   + `docs/evolution/plans/BETA3/EXECUTION/REANCLAJE-2*.md`.

**Prompt de reparación propuesto (NO ejecutado):** ver
`build/tmp/reanclaje21-20260919/PROMPT-REPARACION-22.md` en el expediente.
