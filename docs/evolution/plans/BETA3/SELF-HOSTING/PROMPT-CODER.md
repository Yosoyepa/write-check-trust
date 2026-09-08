# Encargo del coder ciego — primera pieza SH-P01

**Uso:** el usuario envía el bloque siguiente para aprobar `sh-p01/1`, su
Gherkin y su allowlist y comenzar **solo P01**. Este archivo preparado por el
arquitecto no es, por sí solo, constancia de esa aprobación. Modelo y precio
permanecen ocultos; no hay requisito de compartir presupuesto monetario.

La ruta del dossier original es
`/home/jandradeu/Documents/well_code_template/docs/evolution/plans/BETA3/SELF-HOSTING/`.
No es necesario volver a investigar toda beta.3 ni leer sus informes históricos
como si fueran resultados de la implementación que todavía no existe.

---

Asume el rol coder para WCT beta.3. **Apruebo el contrato `sh-p01/1`, sus
escenarios GHERKIN-P01 y la frontera exacta de P01-IDENTIDADES; implementa solo
SH-P01.** Esta autorización no cubre otras piezas, bless, publicación ni cambios
de criterios. Trabaja con el modelo asignado a esta sesión, sin identificarlo
en el handoff, buscar sus tarifas, cambiarlo o escalar a otro modelo.

Tu código será revisado por separado y a ciegas; no te autoapruebes. La calidad
se puntuará antes de conocer el coste. Usa IDs ciegos de tarea/candidato; los
recibos OpenRouter y la identidad del modelo los custodia el usuario, no el
arquitecto. Si falta telemetría, declara unavailable sin inventar tokens/coste.

Lee AGENTS.md y `.claude/agents/coder.md`. Para este encargo concreto prevalece
**entrega sin commit/push/PR/bless** sobre el DoD genérico de publicación del
rol. Lee P01-IDENTIDADES.md y GHERKIN-P01.md completos; de GOBERNANZA.md aplica
autoridad, freezes e integridad; de MOLDE-WCT.md aplica el perímetro puro P01.
Usa REGISTROS.md para el handoff. Las APIs de piezas posteriores son contexto,
no permiso de implementarlas.

1. Verifica base, rama y estado. La referencia inspeccionada es
   `8de9107184288f1aa72c9578a14913686c47ad7c`. Si HEAD de producto difiere,
   reconcilia y reporta antes de editar. Preserva toda documentación y trabajo
   ajeno. Trabaja en copia/rama propia `codex/beta3-sh-p01-identidades`; puedes
   preparar un worktree nuevo y exclusivo bajo `build/tmp/` si no existe,
   leyendo el dossier desde su ruta original. No hagas checkout/stash/reset del
   árbol compartido ni sobreescribas un worktree/rama existente. Registra la
   ruta real de implementación y digests del contrato que has leído.
2. Registra task/run/candidate IDs ciegos, alcance, comienzo y estado inicial.
   Si el operador no ha asignado IDs, usa IDs locales opacos nuevos y díselo;
   no inventes metadatos del proveedor. Esta corrida es **SH-D desarrollo**,
   no un benchmark causal. No inspecciones settings/cuentas para revelar modelo.
3. Revisa reuso por comportamiento: `mutate.verdict.classify_inventory` no
   compara expected/collected/executed y no debe modificarse. Implementa la
   función pura `compare_identities` y los dos tipos de P01 con stdlib. Los
   strings son identidades opacas, los duplicados/vacíos se diagnostican y
   todas las causas se conservan. `match` no significa ejecución ni PASS.
4. TDD y tabla literal I01–I18, pruebas I19–I22 con IDs de colección. Coteja
   status y findings completas obtenidas del SUT. Guarda rojas reales; distingue
   bootstrap por import ausente de rojo semántico. No generes el expected con
   el mismo algoritmo que estás verificando. Conserva controles válidos.
5. Solo puedes crear los cuatro archivos de la allowlist de P01 y tu registro
   nuevo de entrega. No cambiar archivos existentes, thresholds, baselines,
   policy, workflows, locks, manifests, GateResult, CLI o pasos del ejemplo.
   Si el alcance resulta insuficiente, detente y explica el motivo y el diff
   necesario; no amplíes por tu cuenta. Sin interfaces/plugins/esqueletos futuros.
6. Copia el feature verbatim aprobado; comprueba parse/ir-dry. Conecta sus
   filas a tests de contrato parametrizados que llaman la API real. No uses
   el handler histórico de reserva para afirmar aceptación de estos steps.
   No ejecutes mutación de aceptación que solo falle por steps ausentes y la
   anuncies como protección. Ensamblaje CLI y G1b siguen fuera de esta pieza.
7. Corre colección completa, pruebas de contrato y suite completa, tipos/lint
   y fast; `git diff --check`, commit tier y ratchets con salida/alcance reales.
   Pruebas focales no sustituyen gates. No deduzcas cobertura/mutación del
   módulo nuevo de controles que solo inspeccionan src/example. Registra lo
   no ejecutado y cualquier flake. No instales dependencias ni alteres selección
   para producir verde. Si necesitas una prueba de calidad fuera del alcance
   actual, pide su calificación/autorización y declárala pendiente.
8. El código nuevo de `tools/wct` es protegido: integridad pre-bless puede
   informar drift esperado. Consérvalo y nombra rutas; no conviertas FAIL a
   PASS ni digas «solo G-META» sin comprobar todos los demás. No ejecutes
   `update-manifest`, `ratchet raise` ni inventes aprobación de `yosoyepa`.
9. Entrega el **primer candidato completo**: diff y manifiesto de archivos
   nuevos con hashes, tests realmente coleccionados, matriz Ixx→nodeid→resultado,
   outputs/exits, todos los intentos y correcciones, límites y desviaciones.
   No hagas commit, push, PR, bless ni empieces P02. No elijas un verifier de
   otro modelo; el operador/arquitecto coordinarán la revisión independiente.

El criterio no es «muchos tests verdes», sino conformidad observable y mínima
del diff con P01, respetando la autoridad de los controles. Si detectas un
defecto o una ambigüedad del contrato, repórtalo con reproducción y alternativa;
no lo soluciones reescribiendo el examen. La siguiente reparación, si hace
falta, será otra entrega identificada, sin borrar el resultado de esta.

---

## Lo que el arquitecto pedirá al recibirlo

El diff real (no únicamente un resumen), la ruta del worktree/candidate hash y
el handoff ciego. Revisará primero calidad usando
[REVISION-Y-FEEDBACK](REVISION-Y-FEEDBACK.md); después se reconciliarán costes.
Un nuevo dictamen quedará asociado a esos bytes, no a un HEAD anterior ni a una
versión modificada mientras se revisaba.
