# Piezas, contratos y ensamblaje hasta beta.3

Estado: secuencia de arquitectura, **solo P01 tiene aquí un encargo de
implementación completo**. Los otros cortes tienen reglas/salida definida;
sus APIs/fixtures/diffs se cierran antes de delegar, sin un «implementa todo».

## 1. Secuencia y contratos de integración

| Pieza | Se corresponde con | Entrada → salida / consumidor | Criterio discriminador de salida |
|---|---|---|---|
| SH-P01 Identidades | P1a, parte | tres tuplas → IdentityComparison → P03/P05 | mismos N con otros IDs, vacío y duplicados no dan match; controles válidos sí |
| SH-P02 Inputs y propiedad | resto de P1a | scope/expectativas revisadas → snapshot + workspace exclusivo → P03/P04/P06 | cambios unstaged/nuevos/ignorados, exclusiones, symlinks, conflictos de propiedad y dos árboles distintos |
| SH-P03 Ejecución observada | P1b, parte | plan/argv/snapshot → colección y eventos terminales → P01/P05 | skip/xfail/xpass/setup/teardown/crash/cancelación no fabrican éxito; identidad por fila |
| SH-P04 LCOV propio | resto de P1b | productor/archivo/expected SF → comprobación + ratchet aditivo → P05 | viejo/ajeno/truncado/sustituido/imposible no acredita; no contaminar path histórico |
| SH-P05 Cierre | P1c, parte | hallazgos/ejes/capacidades → cierre con causas → P06 | invalid > incomplete > rejected > accredited; FAIL simultáneo conservado; nada acreditado por un dato ausente |
| SH-P06 Ensamblaje P1 | resto de P1c | perfil y manifest → CLI opt-in/envelope versionado | positivo E2E y toda matriz P1; compatibilidad de CLI/GateResult; presupuesto técnico medido |
| SH-P07 Plan del molde | P2a | instancia/mapeo → plan efectivo versionado | clasificación exhaustiva, contradicciones/roots desconocidos bloquean; dos layouts equivalentes |
| SH-P08 Consumidores del molde | P2b | plan único → imports/arquitectura/contexto declarado | cada campo tiene consumidor/test; una regla cambiada cambia su veredicto, incluso en el harness seleccionado |
| SH-P09 Piezas de negocio y adopción | P3/P4, dividir por contrato | puertos/mapeo → adapter contract tests, ruta real y paquete de tarea | otra implementación válida encaja; retorno sin persistencia y firma inventada fallan; plan no escribe |
| SH-P10 Calificación y salida | P5/P6 | candidato congelado/corpus → dictámenes y release candidate | ensayo ciego documentado, compatibilidad/migración, SHA final y claims exactos; publicación aparte |

P01 por sí sola no es una feature completa de evidencia ni beta.3. P07 no
empieza como compilador productivo antes de P06 calificado, siguiendo D0. Sí
pueden prepararse sus contratos/fixtures ahora sin inferencia ni producto.

## 2. Condiciones precisas para las siguientes especificaciones

### P02: qué hace falta fijar antes del coder

- `run_id`, versión de perfil, inputs/config/baselines/runner/deps, roots,
  inclusión de nuevos/ignorados y exclusiones solo de outputs/caches.
- Tres freezes de GOBERNANZA: el hash del candidato no se exige antes de que
  exista. Manifest revisado antes del productor; comparación final de inputs.
- Nueva propiedad exclusiva de outputs; colisiones/symlinks/traversal se
  rechazan sin borrar ajenos. Mantener evidencia parcial tras cancelación.
- Plataforma inicial Linux/Python calificado; no prometer Windows o seguridad
  frente a cambios transitorios restaurados entre snapshots.

### P03: el adaptador de pytest no decide el negocio

- Capturar `argv` como lista en lanzamiento y exit real, no reconstruirlos de
  GateResult.command/summary. Colección fallida o vacía visible.
- En P1: tests no-property; expected revisado, colección y terminales exactos.
  Un test requiere setup/call/teardown satisfactorios para éxito. Fallo de
  setup/teardown conserva causa; falta de fases no se inventa.
- Prohibir reruns/xdist/selección inesperada inicialmente o calificarlos antes;
  fase no es otra identidad de test. Manejar los skips de call por setup fallido.
- El generador actual agrupa filas: decidir binding de filas a contract tests
  parametrizados o protocolo adicional calificado; nunca inferir cada fila
  de un único test verde. Cambiar generador/handler requiere frontera propia.

### P04: un adaptador pequeño sobre el comparador actual

- Reusar receta y semántica LCOV/ratchet. Parametrizar la ruta solo en opt-in;
  defaults históricos y bytes de tolerante se preservan.
- Validar pertenencia, datos imposibles/malformados, SF únicos esperados y
  completitud por archivo. No anunciar completitud independiente de todas
  las ramas del repo: solo fixtures de ramas con expected manual están calibrados.
- `--require` sigue aditivo. Cobertura no exigida mantiene la política vigente;
  P1 exige coverage-total explícitamente. No reabrir Caso C sin autorización.

### P05/P06: cierre y producto utilizable

- P01 match es solo una entrada. Para accredited se necesitan ejecución,
  pertenencia/validez/completitud y umbral dentro del perfil elegido.
- Propiedad/inputs inválidos dominan; faltantes y limitaciones requeridas
  producen incomplete; resultados semánticos fallidos conservan FAIL.
- Comando global propuesto por SPEC-P1:
  `wct evidence run --profile beta3-p1 --expectations <manifest> [--json]`.
  **Hoy no existe**. Nueva salida separada; no sustituir lista JSON histórica.
- Tests E2E sin confiar en resumen candidato, compatibilidad, dos runs/árboles
  y cinco pares locales para el presupuesto técnico P1. No atribuir p95 con N=5.

### P07–P09: moldes y piezas verdaderamente ensambladas

- `hexagonal-python` se ejecuta sobre dos layouts equivalentes. El primer
  perímetro del harness es explícito, no «todo tools» por cambiar un root.
- Contracts de dominio/aplicación independientes de frameworks; puertos en
  consumidor. Cada adapter cumple la misma suite, incluyendo errores/efectos.
- Caso de reserva existente: devuelve y persiste S−Q; errores conservan stock,
  producto ajeno intacto, persistente sobrevive reapertura. No prometer
  idempotencia o concurrencia que el contrato no contiene.
- Plan de adopción no escribe; debt por identidad y autoría, no reiniciar el
  ratchet. Contexto deriva de plan/firmas actuales sin expected privado.
- Si personalAssistant requiere otra política (p. ej. Pydantic en dominio),
  tratar compatibilidad/shadow explícita; no reescribirlo para que gane la demo.

## 3. Quién evalúa el evaluador

En cada pieza se conservan soluciones/fixtures válidas y negativos causales.
El verifier demuestra sensibilidad antes de promover el nuevo control. El
instrumento manual inicial Q0 no se reemplaza con la señal de la pieza que
está calificando. El código del candidato y sus tests de desarrollo no pueden
redefinir la suite protegida de adjudicación.

Después de P06: congelar un lote Wn y compararlo con W0 en tareas no usadas para
calibrarlo. Desarrollo de P07+ produce Wn+1 para otro lote. No ir actualizando
la herramienta entre intentos del mismo experimento y atribuir todo al modelo.

## 4. Definition of done de cada pieza

- Contrato/escenario aprobado, allowlist y lectura acotada; sin ambigüedades
  críticas en datos, errores y consumidor.
- Coder usa solo modelo asignado, guarda historial de intentos y entrega
  evidencia real; no se pone calificación a sí mismo.
- Tests observables, controles positivos/negativos, cobertura/colección por
  identidad y comprobación del perímetro realmente cambiado.
- Verifier distinto y revisión arquitectónica ciega sobre el patch final.
- Integridad pre-bless declarada; ningún otro rojo oculto; sin cambios de
  policy/umbral/dependencias «para arreglar» la métrica.
- Consumo/tiempos de todas las entregas conservados, aun con coste monetario
  diferido. Semillas/plugins/alcance de aleatorización registrados si se corre.
- Promoción solo tras decisión humana e integración verificada en CI/SHA final.

## 5. Qué permite decir que beta.3 está lista

**GO técnico:** cadena P1 calificada, molde/consumidores/adopción/contexto
comprometidos funcionando por ruta real, compatibilidad, gates y presupuesto
técnico documentados, sin bloqueantes, SHA final calificado. Si solo P01–P06
están listas, hace falta recortar la promesa de release; no marcar P07–P09 done.

**GO de aprendizaje:** resultados internos completos incluso si son negativos,
defectos por clase, coste posterior reconciliable, instrumentos/limitaciones
versionados. La primera automejora no exige resultado positivo para ser útil.

**GO de ahorro/sustitución:** requiere comparación y datos de coste, no solo
GO técnico. Sin estos datos se publica experimental con hipótesis abierta.
No hay un porcentaje de ahorro comprometido por este diseño.

**GO de publicación:** autorización independiente; bump protegido, tag/SHA,
SBOM/procedencia, smoke del tag y `isPrerelease=true` verificado remotamente.
No se publica nada por terminar un dossier o recibir un autoinforme verde.

G1b, PR #33, issue #35 y revisión del canal beta.2 mantienen sus carriles. No
quedan cerrados por estas piezas ni autorizados para cambios remotos aquí.
