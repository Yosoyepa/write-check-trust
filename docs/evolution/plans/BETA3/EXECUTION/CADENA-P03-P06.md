# Cadena P1 — cortes de arquitectura P02b a P06

Fecha: 2026-09-07. Rol: arquitecto. **Plan de contratos, no implementación ni
aprobación D1.** Descompone [SPEC-P1](../specs/SPEC-B3-P1-evidencia.md) sin
cambiar los ejes, el perfil beta3-p1 o el formato legacy. P02a se concreta en
[su propuesta](PROPUESTA-P02a.md); sus tipos requieren revisión antes de cerrar
los demás API. No dar al coder esta tabla como permiso de completar ambigüedades.

## 1. Puntos de reutilización y límites comprobados

| Fuente del corte 4666927 | Observación | Decisión para el siguiente contrato |
|---|---|---|
| `tools/wct/evidence/identities.py:215` | Kernel puro de tres tuplas; no observa procesos | Reutilizar igualdad/diagnósticos; nunca convertir match en éxito |
| `tools/wct/gate/exec.py:15` | `_captured` retorna Status/resumen/output combinado, no exit crudo/fases | Capturar argv/exit/fases en la frontera nueva; no reconstruir desde texto |
| `tools/wct/model.py:18` | GateResult tiene seis campos y blocking FAIL/ERROR | Mantenerlo intacto; el vínculo ejecución→resultado vive en la envoltura |
| `tools/wct/gate/checks.py:62` | Builder de coverage fija LCOV histórico y piso del baseline | Parametrización opt-in revisada; conservar receta/defaults y par --cov-fail-under |
| `tools/wct/ratchet/measure.py:117` | Porcentaje (LH+BRH)/(LF+BRF), no solo ramas | Reutilizar semántica; no añadir otro umbral ni fórmula |
| `tools/wct/ratchet/measure.py:141` | Lector por registros de la vía exigible acumula contadores | Validación de SF/terminación privada separada; el tolerante real es `lcov_percent`/`coverage_total` (117/133) y conserva su contrato |
| `tools/wct/ratchet/measure.py:223` | Exigible valida contadores/coherencia | Reutilizar comprobaciones; presencia no prueba productor ni frescura |
| `tools/wct/ratchet/measure.py:392` | Required es aditivo y usa ruta global | Entrada privada explícita en camino nuevo; no monkeypatch ni copiar artefacto al global |
| `tools/wct/accept/pipeline.py:165` | Genera una función por escenario; no una por fila | Vincular fila→nodeid→terminal en P1; parse verde no es ejecución |
| `tools/wct/cli.py:45` | No existe comando evidence | Ensamblaje nuevo en P06; no anunciar CLI por entregar kernels |

Estas son restricciones de reutilización, no acusaciones de defecto contra
contratos históricos que no prometen esas capacidades. El scope inicial sigue
siendo WCT/Python; no hay shell arbitrario ni motor genérico de workflows.

## 2. P02b — propiedad del workspace

Entrada contractual por cerrar: snapshot P02a, run ID, directorio padre
autorizado y límites. Salida: identificador propio y rutas de artefactos
relativas a ese directorio, sin acreditar tests. La creación debe ser exclusiva,
no `exists()` seguido de uso; raíz y componentes symlink/traversal se rechazan.

Casos obligatorios: control nuevo válido; ID existente; symlink interno,
externo y roto; dos árboles con pruebas homónimas; productor interrumpido;
destino de otro run conservado byte a byte. No borrar parciales ni «reutilizar
el último run». La identidad portable de contenido no sustituye posesión.

Antes del coder: definir atomicidad de creación/escritura terminal, API/errores y
tratamiento de carreras; calificar Linux. No afirmar protección frente a mismo
UID malicioso ni proponer limpieza automática de evidencia en esta pieza.

## 3. P03 — observación de pytest

Congelar protocolo antes del adaptador: ID de ejecución, lista argv efectiva,
selección, inventario recolectado, eventos con nodeid/fase/outcome, terminación,
exit real y referencias a logs. Se preservan secuencia y duplicados hasta
validación; un diccionario por nodeid no debe ocultar dos ejecuciones.

Solo setup+call+teardown conformes satisfacen una obligación PASS. Un fallo
observado también debe conservarse como fallo; no ocultarlo bajo incompletitud.
La falta legítima de call tras fallo de setup debe distinguirse de un protocolo
truncado. Esta matriz requiere decisión explícita antes de implementar.

Calificación mediante procesos reales: pasa/falla, error de import/colección,
vacío, skip, xfail/xpass, error setup/teardown, cancelación/crash, eventos
duplicados o truncados y deselection inesperada. Una línea de stdout del test
que parezca un recibo no constituye un evento confiable. Tests property se
inventarían fuera de las obligaciones seleccionadas. Plugins rerun/xdist y
opciones de selección no autorizadas se rechazan inicialmente, sin instalarlos
ni modificar el entorno global para «probar» ese rechazo.

No se ha elegido aquí una API de hooks sin comprobarla: antes de coder leer
la versión instalada, fijar hook/serialización y ensayar un positivo y cada
fase fallida sobre micro-fixtures propios. Esa verificación es parte del
contrato P03, no se delega su semántica al implementador.

## 4. P04 — LCOV privado y ratchet

Separar dos incrementos si el cambio deja de ser pequeño:

- P04a: pertenencia/estructura/inventario SF, conservando la validación actual
  de contadores y porcentaje. Positivos con archivo medible y vacío opcional;
  negativos antiguo/ajeno/truncado/SF sustituido a N constante/duplicado,
  negativos malformados y cubiertas sin total. Denominador previo, no LCOV.
- P04b: consumidor exigible con artefacto explícito y parámetros de productor,
  sin cambiar ruta ni bytes por defecto de las APIs actuales. Todas las
  comparaciones adicionales del ratchet permanecen; required no filtra rojos.

El archivo se identifica al producir/consumir y su digest debe corresponder a
los mismos bytes validados, evitando validar un path y leer otro estado sin
comprobarlo. Inputs/config/runner/calificación se vinculan por referencia
observada, no por un hash decorativo que el propio resultado inventa.

Definir fixtures de líneas/ramas esperadas a mano. En código general P1 acredita
inventario por archivo/coherencia, no conoce independientemente todos los arcos
que coverage debería descubrir. Preservar LF sin LH válido en la vía legacy;
cualquier completitud más fuerte vive en un perfil explícito.

## 5. P05 — cierre puro

Separar ejes validity/completeness/result/calibration y reasons antes de decidir
el resumen. Precedencia fija: invalid > incomplete > rejected > accredited.
Mantener todo FAIL relevante aunque una causa de invalidez domine el titular.
El cierre puro no lanza procesos ni reinterpreta stdout; consume resultados
observados/validados con versiones y referencias exactas.

Matriz mínima: solo válido; solo FAIL; FAIL+input cambiado; FAIL+SKIP; productor
fallido sin artefacto; productor fallido con artefacto histórico; cobertura
bajo piso con terminales completos; capability requerida desconocida;
calificación ausente; vacío; IDs sustituidos con igual cantidad; missing/extra
en referencias. Rechazar todo falla el control válido y una segunda solución
válida. No derivar expected del mismo algoritmo ni usar media de dimensiones.

## 6. P06 — ensamblaje y puerta hacia moldes

Cerrar schema/errores y fixtures serializados antes del coder. CLI objetivo:
`wct evidence run --profile beta3-p1 --expectations <manifest> [--json]`.
Exit 0 solo accredited; 1 para rejected/incomplete/invalid; 2 para error de uso
previo a crear run. Desconocidos/referencias inexistentes no se descartan.

Un único productor de cobertura ejecuta la suite normal seleccionada; no
duplicar G-TEST para sumar un badge. Consumir exclusivamente su LCOV privado,
guardar resultado nativo de ratchet y seis campos GateResult sin modificaciones.
Compatibilidad con bytes fijos en texto/JSON/quiet y smoke CLI real adicional.
Registro inconcluso/interrumpido nunca se lee como éxito.

La puerta exige todas las filas de [Gherkin P1](../GHERKIN-P1.md), controles
causales y válidos por ruta real, registro de artefactos/inputs, presupuesto
emparejado y verificador distinto. Solo entonces puede arrancar implementación
P07; sus contratos/fixtures pueden prepararse antes, como en esta ola.

## 7. No realizado / decisión pendiente

No hay nuevas funciones, tests o features productivas en este documento.
P02b–P06 todavía necesitan sus firmas, esquema concreto, Gherkin y allowlists
por subcorte. Esta lista de necesidades impide confundir plan de arquitectura
con paquete ya autorizado para un coder. No se mueven umbrales, releases ni
G1b. Para calificar costes/recursos, aplicar la matriz de la campaña, no las
duraciones históricas de una suite como estimación del producto futuro.
