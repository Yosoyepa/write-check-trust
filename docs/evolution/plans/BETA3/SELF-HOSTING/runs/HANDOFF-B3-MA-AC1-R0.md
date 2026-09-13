# Handoff B3-MA-AC1-R0 — ejecución propia del coder

Estado: **caracterización previa; implementación AC1 no iniciada**.
Worktree exclusivo `build/tmp/beta3-acceptance-engine`, rama
`codex/beta3-acceptance-engine`, HEAD
`932c835ac0eeb75010ec7a1071315b1c51f78eb6`. Sin commit/push/bless.
No se comparte la identidad ni la adjudicación de 54 mutantes de P02a.

## Recibo de contrato y frontera

AGENTS, rol coder Owns/Does Not Own, skills acceptance/architecture/gate/
hardening y SONDA-P03 leídos completos. Contrato original leído SHA
`1e32f88cd370a59feba60334fce3f9b5a3332bc948860683e0668af6ecf3d698`;
actualización autorizando refactorización interna sin cambiar comportamiento
leída SHA `e0eca8700e99eee4dbd6409d973d97f1ed64770ea9b923091c94c1a47a700dff`.
El arquitecto permite únicamente caracterización y este handoff mientras
espera revisión independiente apta del contrato. No se interpreta el texto
general del contrato como permiso para ignorar esa espera explícita.

Reuso buscado por comportamiento: parser/IR-dry/generación/enumeración existen;
no transporte acotado ni validador de recibos equivalentes en main. No se
importan módulos P02/P03 pendientes. Medición previa productiva: pipeline259
sitios; parse_feature95, _relative_source1, módulo1; ir_dry56, generate35.
Radon: parse_feature CC25, ir_dry CC11. La fachada y partición interna deben
resolver complejidad, no mover deuda ni solicitar una exención legacy.

## Caracterización ejecutada antes de refactorizar

Solo se amplió `tests/unit/test_accept_pipeline.py`, preservando sus cinco
tests anteriores. Ahora **18 tests coleccionados y 18 PASS**. Comprueban IR
literal con Background/Scenario/Outline, keywords, orden/líneas, comentarios,
diagnósticos exactos, narrativa rechazada (#35), peculiaridades históricas
de Examples en Scenario y nombre Background, Feature posterior, bytes
generados mediante golden independiente y orden de findings de duplicación.
No se presenta esta caracterización verde como nuevos rojos TDD del protocolo.

Identidad fuente antes/después sin cambio:
`tools/wct/accept/pipeline.py`
SHA `925c89198cd9f8a469b001ec98fe2e0615716cba3d17f5952a88003f19a53cce`.
Test anterior SHA `c49e14a07c1a8690c6438e4dbce9fd0a8aa657d63176f5904824a812404c27fc`;
test caracterizado final SHA
`e65525eaac95c6fc4eece63ce680b3e164ed79af90e89a6ec9d8c6455e625237`.

Evidencia local-only: `build/tmp/b3-ma-ac1-r0/characterization-*.txt` y
manifiestos before/after/final. Runtime compartido P01, uv --no-sync,
PYTHONPATH apuntando al candidato AC1, basetemp diferente por corrida.
Primera ejecución 18 PASS/0.31s; captura siguiente 18 PASS/0.25s. Ruff detectó
cinco findings de tests (dos raises sin match y tres líneas largas); se
corrigieron sin supresiones. El shell inicial terminó con el hash exitoso
después del lint fallido: ese exit global NO acredita lint. Ruff posterior
ejecutado separadamente exit0. Corrida final **18 PASS/0.30s**; colección
final **18/0.21s**, ambos exit0 con pipefail en las capturas.

No se ejecutaron fast/global/commit/full ni calificación pesada en esta
frontera limitada; no se afirma árbol global verde. Resto del allowlist sigue
sin editar. Próximo paso: aprobación independiente del contrato, luego tests
rojos de baseline/recibos/transporte antes de sus implementaciones. Coste de
inferencia unavailable; cohorte asistida B3-MA-D, sin atribución causal.

## Entrega de implementación R0 para revisión — 2026-09-08

El contrato recibió APTO independiente comunicado por root. Sus precisiones
posteriores aprobaron dos módulos de validación, alias de excepción sin
supresiones y controles de lanzamiento/prelaunch/temporales. Última versión
leída completa SHA
`ebbd0408aa10fb1e92d255273e875cbc40d50733e7b669ab0a7322316c4862ba`.
No se modificaron contrato, CALIFICACION-AC1 ni otros dossiers por este coder.

**Candidato congelado:** `build/tmp/b3-ma-ac1-r0/candidate-r0.sha256`, 23 rutas
ordenadas por ruta y hash sha256sum de bytes, digest
`2d92caaa0770d9796d3dab3a730dbf10ec9fabaa332ed36a4c3c1c52a7e91ce0`.
Incluye el archivo generado histórico sin cambio; no fue editado ni
regenerado en el árbol versionado. La prueba CLI usó --output exclusivo en
build/tmp. Los 13 módulos del allowlist, 3 adaptadores/fixtures de aceptación,
5 archivos unitarios, feature y generado suman esas 23 rutas. __init__.py
no cambió; la revisión parcial de 18 archivos lo incluye explícitamente como
dependencia, sin ampliar el diff. HEAD/rama permanecen como al recibo.

### Comportamiento implementado

- Fachada pública conserva parse_feature/ir_dry/generate/mutations/
  run_mutations/accept_verdict y STEP. Parser e IR-dry están particionados
  internamente, conservando caracterización. El arquitecto informó además
  comparación contra HEAD sobre 30 features sin diferencias: evidencia suya,
  no ejecución atribuida a este coder ni prueba exhaustiva.
- Campaña persistente en build/tmp del cwd del caller, baseline explícito
  antes de cualquier mutante, nonces/hashes/rutas propias por intento,
  timeout/cap combinado y kill+reap. IR/recibo/logs/attempt/report conservados;
  prelaunch agotado también deja metadata/logs vacíos. TMPDIR y temporales
  pytest quedan bajo cada intento. No se modifica cwd ni CLI.
- Recibo estricto: lectura regular nofollow acotada, JSON sin duplicados ni
  constantes no JSON, tipos exactos e inventario de escenarios completo.
  Mismatch válido y aislado es killed; pass es survived; errores invalidan y
  detienen. Veredicto coteja metadatos/IDs/cuentas e invalida reportes legacy.
- Plugin pytest cooperativo coteja colección y registra S/C/T/excepción raw,
  wasxfail, errores y completitud; receipt mínimo separado de events.json.
  Error genérico/import/setup/teardown/skip/xfail no equivale a mismatch.
  SemanticMismatch es alias del mismo tipo SemanticMismatchError, conforme
  autorización N818, sin nueva supresión. Se prueba alias, herencia y nombre
  concreto en eventos. No es autenticación contra plugins/runner malicioso.
- Ejemplo conserva lógica productiva y traduce solo desacuerdos especificados.
  Ceros numéricos reconocidos (0/00/-0/0.0) cambian a 1; +0/exponentes siguen
  operador léxico histórico. Feature AC1 tiene seis filas verbatim y ejecuta
  motor+protocol_runner mediante steps→campaign_steps, no binding solamente.
  Modo/veredicto desconocido no cae en pass por defecto.

### Evidencia, TDD y asistencia declarada

Rojos previos reales: baseline-red.txt (runner exit1 original contado antes
como killed1); campaign-red-2.txt (11 fallos sobre runner histórico sin
protocolo); pytest-plugin-red.txt (baseline real sano pero primer mutante del
ejemplo todavía instrumental antes de tipar steps); unknown-mode-red.txt
(token desconocido caía en pass); feature-red.txt (dos missing handler antes
del adaptador); prereview-red.txt (ocho fallos empty-command, metadata
prelaunch, TMPDIR y exits baseline). Todos bajo build/tmp/b3-ma-ac1-r0.

receipt-red.txt es **error de import del módulo inexistente**, no demuestra
sensibilidad semántica por sí solo. Caracterización y ampliaciones posteriores
no se presentan como rojos TDD. Desviaciones declaradas: matrices específicas
del operador cero y del veredicto se añadieron después de sus helpers; los
controles directos de hooks y ampliaciones de límites se añadieron después de
la implementación. Se buscaron equivalentes antes de implementar, pero
`wct dry --against` no se ejecutó antes de cada helper: queda registrado el
incumplimiento de esa comprobación MIN-006, sin reconstrucción retroactiva.

Coder2 `/root/p02a_binding` colaboró en tres fronteras, no como verifier:

- test_accept_pytest.py inicial: 12 integraciones; primer rojo de plugin
  inexistente no era sensibilidad semántica. Reforzó dos controles que podían
  pasar falsamente por missing-plugin. Este coder añadió después hooks
  in-process con CallInfo/TestReport reales y doubles mínimos item/session,
  leyendo recibo/eventos y conservando integraciones de subprocess.
- test_accept_receipt.py: 57 casos, incluido 1MiB exacto/+1, FIFO acotado,
  nested duplicate keys, identidad/exits/cases/FD y positivos alternativos.
  Tests posteriores al producto, sin rojo productivo atribuido.
- test_accept_campaign.py: tres controles de transporte real, cap combinado
  exacto/+1 y timeout con exit/bytes/recolección ECHILD, sin modificar los
  diecisiete previos. También posteriores a implementación.

Sus capturas están en build/tmp/b3-ma-ac1-pytest-tests,
b3-ma-ac1-receipt-tests y b3-ma-ac1-transport-tests. Los handoffs de root
atribuyen las revisiones independientes por separado. No se confunde esta
coautoría con dos tareas independientes exitosas ni con un control de modelos.

### Verificación sobre R0, alcance explícito

- Cinco archivos unitarios AC1: **163 PASS/13.68s**, focal-final-1.txt.
- Colección completa: **558 tests/0.52s**, global-collect-2.txt. No son
  558 tests ejecutados por este coder.
- Ruff del alcance: PASS. Mypy estricto tools/wct/accept: **14 archivos PASS**
  (incluye __init__ sin cambio). Fast: **7/7 PASS, 0 SKIP**, fast-final-1.txt;
  G-TYPE de fast cubre además tools/wct y src con la receta productiva.
- Sitios medidos por engine: máximo100 (parsing); campaign93 y
  verdict_validation96. Radon de funciones y métodos ≤6. Esto no es CRAP
  medido ni sustituye cobertura por rama o mutación.
- CLI real desde raíz: `wct accept mutate features/example.feature --output
  build/tmp/b3-ma-ac1-r0/cli-generated/test_acceptance.py`, uv --no-sync con
  runtime compartido/PYTHONPATH AC1: exit0, baseline pass, 6 planned/6 killed,
  cero demás estados. cli-example.txt y build/tmp/wct-accept-j6es0a2k.
  Es preflight diagnóstico autorizado, **no hardening de aceptación completo
  posterior a mutación de fuentes** ni prueba de CLI desde subdirectorios.
- Feature nueva byte-exacta contra bloque contractual, seis filas e IR-dry0;
  SHA `25b06d60fb95db42266c81cc14e23aed2c07faa4d8bdc512d25f73f88f4cf467`.
  Tests observan seis campañas reales y un oráculo deliberadamente incorrecto
  que produce SemanticMismatch. No se afirma ejecutar 48 mutantes del feature.
- git diff --check limpio; fuente-review-2 conserva sus 18 hashes intactos.

Hubo fallos intermedios de lint/formato/types y dos llamadas apply_patch
rechazadas por contexto/operación duplicada antes de aplicarse. Se corrigieron
sin supresiones. Los comandos shell que continuaron después de lint se
interpretan por sus salidas, no por el último exit de hash/formato. El fast
final y las corridas focales sí tienen exit real y capturas con pipefail.

### Migración y puertas pendientes

Un --runner propio debe leer WCT_ACCEPT_IR y escribir WCT_ACCEPT_RECEIPT con
schema_version=1, attempt_id/ir_sha256 proporcionados, exit real, una entrada
por Scenario y errors. Pass requiere todos pass/exit0/errors vacío; rechazo
semántico requiere mismatch sin errores/exit1. Exit1 sin recibo ya no aprueba.
Plugin histórico generado usa esta adaptación automáticamente en campañas;
el runner always-pass que ignora IR produce supervivientes, no defensa frente
a un runner malicioso que falsifique deliberadamente la procedencia.

**No GO de PR, bless ni beta.** Mutación de fuentes, cobertura focal/global,
CRAP, DRY, commit/full, ratchets y calificación económica siguen pendientes.
La mutación léxica histórica del nuevo feature puede producir vocabulario
inválido o equivalencias; no se convierten en kills ni se descuentan IDs. Su
gate focal de aceptación permanece pendiente/bloqueante hasta decisión de
arquitectura sobre el incremento correspondiente. El ejemplo verde no lo
subsana. La adjudicación de 54 mutantes P02a no aplica a AC1.

Root informó que ejecuta una suite completa propia sobre esta identidad;
su resultado aún no se incorpora aquí ni se atribuye al coder. Fuentes y
tests quedan congelados para esa corrida y para revisión independiente final.
Solo este handoff se actualizó después del freeze. Sin commit, push, PR,
bless, instalaciones, cambios de política/CLI/P02 ni artefactos protegidos.

## Addenda R1 — regresión G-INTROVERT tras la suite global

La suite global ejecutada por root terminó **552 PASS / 6 FAIL**, no verde
(`build/tmp/b3-ma-ac1-r0/root-suite.txt`). Una regresión propia fue el ratchet
introverted=14 frente a baseline=0: doce tests de recibos escondían la llamada
productiva en un helper; otros dos ejercitaban subprocess o el helper de hooks.
Los otros cinco fallos quedan bajo diagnóstico del arquitecto; no los reclasifico
como regresiones ni como pases. La focal inicial no bastó para detectar el escape.

Con autorización de root se modificaron únicamente `test_accept_receipt.py` y
`test_accept_pytest.py`. Se eliminaron las llamadas indirectas al validador,
conservando identidad literal y resultados independientes. El FIFO mantiene su
hijo acotado y coteja después la salida contra la API in-process. El plugin inactivo
conserva la prueba por proceso y comprueba inventario antes/después en un
`PytestPluginManager` real, además de ausencia del observer nombrado. El helper de
hooks recibe explícitamente la clase productiva y se conservan los recibos esperados.
No se añadió una aserción de retorno None ni se cambiaron baselines/supresiones.

Incidente de test: primera repetición **176 PASS / 1 FAIL** porque asumí que el
manager nacía vacío; pytest lo registra a sí mismo. Se corrigió el oráculo del
andamiaje a conservación del inventario y ausencia del observer. No es flake ni
defecto de producto. Se preserva `focal-r1-1.txt`.

Resultado final **177 PASS / 24.66s** en los cinco archivos AC1 más
`test_ratchet_check.py` (`focal-r1-2.txt`), **558 coleccionados**
(`global-collect-r1-final.txt`, repetido tras el último edit) y **fast 7/7**, cero skips/fallos
(`fast-r1-final.txt`). Analizador productivo: cero introverted; informe completo
`introvert-r1.json`. No implica suite global verde ni hardening completo.

R0 conserva su manifiesto. El candidato hijo R1 de 23 archivos queda identificado
por `build/tmp/b3-ma-ac1-r0/candidate-r1.sha256`, digest
`f0a6a119ff29c9d2b76bc8ebce81d046b79d3b3b8158d0511abf8b8d00955f60`.
Las 18 fuentes/feature de `source-review-2.sha256` siguen idénticas, verificadas
18/18; no se modificó producto. Fuentes/tests vuelven a quedar congelados para
revisión independiente. Siguen pendientes mutación de fuentes, aceptación mutada
de la nueva feature y resto de cadena pesada; sin GO de PR ni adjudicaciones AC1.

## Addenda R2 — refuerzo de oráculos, sin modificar fuentes

Root comunicó interrupción de la campaña R1 por carrera instrumental de
`pytest-current`: 148 supervivientes provisionales, 1209 exit1 ambiguos y
124 pendientes. No es una métrica válida de mutación ni acredita esos exit1
como kills. Los inventarios/copia/metas R1 no fueron modificados por este coder.

La lectura de AST de supervivientes permitió proponer contraejemplos. Sondas
aisladas en memoria contrastaron comportamiento original/mutante sin campaña:
results tuple con cardinalidad correcta; baseline reason vacío; recibo con
mismatch junto a estado desconocido. Los tres mutantes aceptaban indebidamente.
Se reforzaron estos contratos y la distinción entre fallo residual legítimo y
reporte instrumental inválido: survivor/error, exit de survivor/not_run,
baseline mismatch exit1/2 y conservación de causas/campos. Los nuevos controles
de diagnóstico no fijan puntuación o capitalización arbitraria. NaN y las dos
Infinity conservan causa de constante JSON inválida. Positivos existentes se
mantienen. No se fabricaron tests para equivalencias propuestas.

Mis cambios R2 están solo en `test_accept_verdict.py` y
`test_accept_receipt.py`: 23 casos añadidos, focal **113 PASS / 0.66s** y ruff
verde (`focal-r2-1.txt`). Mi mensaje preliminar que contó 24 fue corregido:
se retiró antes de la focal un not_run aislado sin causa previa, no representativo
de una campaña real. No cambio de producto ni afirmación TDD de reparación de
producto: se trata de refuerzos posteriores a implementación, previos a nueva
calificación mutada. Sensibilidad de cada nuevo test todavía no medida.

Coder2 (`p02a_binding`) añadió 10 casos en `test_accept_pipeline.py`, conservando
su frontera y fuentes: 36 PASS / 0.34s, 36 collect, ruff verde. Cubre colon,
tablas previas a escenario/Background, celdas X, source fallback, escenarios
distintos/Unicode, placeholder literal y diagnóstico completo de pairwise.
Su evidencia está en `build/tmp/b3-ma-ac1-pipeline-r2/`; contribución de coder,
no verificación independiente.

Congelación nueva: `build/tmp/b3-ma-ac1-r0/candidate-r2.sha256`, 23 archivos,
digest `78441605767e5f3d20f437ad779624c3de178042f91ba6f676752e43965ea63f`.
Las 18 fuentes/feature siguen 18/18 idénticas a source-review-2. Resultado final
sobre esos bytes: **210 PASS / 25.49s** en cinco archivos AC1 más
`test_ratchet_check.py` (`focal-r2-final.txt`), **591 coleccionados**
(`global-collect-r2.txt`), **fast 7/7** (`fast-r2.txt`) y cero introverted
(`introvert-r2.json`: 355 extroverted, 2 conditional, 6 cloistered, 3 questionable).
No es suite global ejecutada ni presupuesto emparejado. Sin nueva campaña de
mutación, coverage, CRAP, DRY o full por mi parte. Queda congelado para revisión
independiente y nueva calificación con aislamiento corregido. Sin GO ni bless.
