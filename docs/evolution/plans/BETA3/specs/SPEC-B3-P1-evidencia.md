# SPEC-B3-P1 — Una cadena de evidencia, opt-in y compatible

Estado: **lista para revisión D1; no aprobada ni implementada**. Precisa la
rebanada de SPEC-B3-02. [D0](../D0.md) propone este recorte para que P1 no dependa
de construir P2. [Gherkin y matriz](../GHERKIN-P1.md) son parte del contrato.

## 1. Comportamiento y scope exactos

El usuario ejecuta una cadena de tests/cobertura y recibe un registro que
distingue el resultado de sus pruebas, las unidades faltantes y la validez de
los artefactos. Un LCOV viejo no permite acreditar una corrida nueva fallida.

**Cadena única P1:** inventario revisado → colección pytest → ejecución pytest
no-property con cobertura de rama (`G-COV-TOTAL`) → consumo exigible del LCOV
por el ratchet existente → registro/cierre. No ejecutar G-TEST por segunda vez
para añadir un badge: el productor de cobertura ya ejecuta esos tests.

En el checkout WCT de referencia:

| Dimensión | Alcance exacto / disposición |
|---|---|
| Negocio | Raíz `src`, único paquete `example`; los nueve `.py` actuales, incluidos `__init__.py`, se inventarían por identidad |
| Verificador medido | `.py` de `tools/wct`; inventario separado del paquete de negocio |
| Cobertura efectiva | `tool.coverage.run.source=[src, tools/wct]`, branch=true; omit actual `tests/*`, `tools/wct/__main__.py`. Publicar omisiones y ficheros sin unidades, sin convertirlos en cubiertos |
| Tests | `testpaths=[tests]`, `-m "not property"`, sin `-k`, sin `--lf`, sin selección incremental. Incluye unit, integration y aceptación recolectada; property queda fuera por contrato |
| Piso | Baseline `coverage-total` vigente (en la base: 74.5, higher_is_better); no nuevo umbral. Total es (líneas+arcos cubiertos)/(líneas+arcos medibles), no solo porcentaje de ramas |
| Consumidor | Semántica actual de `ratchet check --require coverage-total`; mantiene sus comparaciones adicionales. Sus fallos no se filtran. La acreditación nueva se limita a tests/LCOV, no certifica procedencia de todas las otras métricas |
| Escenarios | Solo escenarios/filas explícitamente vinculados a tests terminales en expectativas P1. Gherkin histórico no vinculado se publica como parseado/no acreditado; no afirmar ejecución de todas las features |
| Plataforma inicial | Linux/Python del entorno fijado para la calificación; versión exacta y lock en cada registro. Otra plataforma necesita calificación; sin promesa 3.11–3.14 por metadatos |

Este perfil fija el scope histórico WCT para su primera integración. No acepta
roots/paquetes arbitrarios como si P2 ya existiera. Los micro-fixtures reproducen
la misma disposición, con inventarios menores etiquetados. Soportar un nuevo
perfil/scope requiere expectativas revisadas y calificación propia.

Fuera de P1: conformidad hexagonal, traducción de policy, migración/adopción,
contexto, `G-COV-DIFF`, causalidad de tests, mutación, seguridad de código hostil
y acreditación de todos los ratchets/tiers. Reportar esas capacidades como
`not-accredited` con motivo, no como PASS, y no rebajar sus controles históricos.

## 2. Interfaz propuesta y compatibilidad

Interfaz nueva propuesta (no disponible hoy):

```text
wct evidence run --profile beta3-p1 --expectations <manifest-revisado> [--json]
```

No se añade un flag a `gate --tier fast/full/pr/commit` que cambie su significado.
No se cambia `wct report`, `wct ratchet check` sin opciones nuevas ni sus exits.
El perfil no acepta comandos arbitrarios en el manifest: selecciona esta
cadena registrada. No hay `--force`, auto-bless ni creación automática de
expectativas a partir de la corrida que pretende acreditar.

- `GateResult` mantiene exactamente `gate_id,status,summary,duration_ms,details,
  command`, defaults, orden de serialización y `blocking` (FAIL/ERROR).
- `run_tier` sigue retornando `list[GateResult]`; Status sigue PASS/FAIL/SKIP/ERROR.
- JSON histórico sigue siendo lista de esos seis campos; texto/quiet y
  tratamiento de aliases/SKIP conservan bytes con resultados fijos. Las
  duraciones reales varían: la prueba de bytes inyecta resultados constantes,
  además de un smoke por CLI real para comprobar compatibilidad semántica.
- La nueva salida JSON es **un objeto** con `schema_version=1`, tipo
  `wct-run-evidence`, resultados históricos embebidos y ejes separados.
  No sustituye listas por objetos en consumidores históricos.
- Se captura `argv` antes de subprocess como lista y exit crudo por ejecución;
  no se interpreta `GateResult.command` para recuperar argumentos.
- La selección del LCOV privado necesita una entrada explícita en el camino
  opt-in de productor/consumidor. Sus defaults siguen apuntando al artefacto
  histórico. No reescribir globals ni copiar el LCOV nuevo a la ruta compartida.
- La CLI nueva entrega exit **0** solo para `accredited`; **1** para rejected,
  incomplete o invalid; **2** para error de uso/manifest no interpretable antes
  de crear un run. Cancelación capturable conserva run incompleto y causa;
  SIGKILL puede dejar registro pendiente: al leerlo jamás se interpreta como 0.

## 3. Inventario independiente: qué cuenta como esperado

Hay dos denominadores distintos, ambos no vacíos para su obligación:

1. **Archivos:** enumeración previa del filesystem sobre las raíces de input,
   independiente de los `SF` que luego emita coverage. Cada identidad contiene
   ruta POSIX relativa, tipo y SHA-256 de bytes. Se incluyen archivos nuevos e
   ignorados dentro del scope de fuente, sin depender solo de `git diff`.
   Los `__init__.py` vacíos tienen disposición explícita sin unidades medibles;
   un archivo con código omitido exige motivo revisado, no inferido de su
   ausencia en LCOV. Cada archivo esperado con unidades debe aparecer en SF.
   Un archivo revisado sin unidades puede aparecer como registro vacío o no
   aparecer: se registra esa disposición antes del productor. Formalmente,
   `SF_obligatorios ⊆ SF_observados ⊆ SF_obligatorios ∪ SF_vacios_opcionales`;
   no se permite ningún SF ajeno/duplicado. El inventario completo de archivos
   conserva también esos vacíos y las exclusiones, sin sumarlos como cobertura.
2. **Obligaciones de prueba:** manifest aprobado antes del productor, mantenido
   por specifier/reviewer ajenos al código bajo prueba. Contiene nodeids con
   parámetros estables y requisito/escenario/fila→nodeids exigidos. Una colección
   de revisión en snapshot fijado ayuda a confeccionarlo, pero su salida no
   aprueba ni actualiza automáticamente el manifest. Para cada run se comparan
   esperado, recolectado y ejecutado terminalmente, por conjuntos e identidades.

El manifest de fixtures se escribe desde su especificación, nunca desde el
compilador del molde, results, LCOV o un log del agente. Para el repo WCT real
la colección completa revisada se congela junto al snapshot; aún no se ha
confeccionado/aprobado ese manifest en este turno. Borrar un test requiere una
nueva revisión de obligaciones, no refrescar un snapshot expected con un botón.

Para el perfil congelado la colección seleccionada debe coincidir con las
expectativas. Cada test tiene setup/call/teardown y terminación registradas;
skip, xfail, xpass, deselection inesperada y falta de teardown no satisfacen una
obligación de PASS. Las exclusiones property se inventarían separadamente y
nunca se cuentan en la suite acreditada. Repetir un nodeid o reemplazar uno por
otro conservando el conteo no satisface igualdad. Si se cambian parámetros o
plugins que alteran nodeids, revisar el manifest antes del run.

La completitud de cobertura P1 es por **identidades de archivos** y coherencia
del artefacto. No demuestra independientemente la totalidad de statements/arcos
que coverage.py debería instrumentar en cualquier programa. Su semántica se
califica con fixtures de líneas/ramas esperadas a mano; esa limitación figura
en el registro. Tests verdes tampoco prueban suficiencia de sus aserciones.

## 4. Identidad de inputs, propiedad y artefactos

Antes del productor se fija un manifest de inputs. En WCT se incluyen los
archivos regulares tracked y untracked del proyecto, con exclusiones exactas de
outputs/caches (`build`, `.coverage*`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`,
`__pycache__`, `.venv`) y metadatos Git tratados por separado. Ninguna exclusión
genérica puede ocultar una fuente/test/config declarada; si hay intersección,
se rechaza el scope. Recursos de fixtures fuera de src también se incluyen.
Dependencias, ejecutables/plugins, intérprete, lock e imagen/entorno se fijan
como entradas; no hashear indiscriminadamente caches del usuario.

Registrar HEAD/base, estado del índice y cambios staged/unstaged/untracked;
el digest del contenido ejecutado es la identidad primaria. Registrar versión
y digest del runner y de expectations, pyproject, policy/thresholds/baselines,
reglas y configuración consumida. Entorno: allowlist no secreta de selección y
opciones efectivas (incluidos PYTEST_ADDOPTS/PYTHONPATH/COVERAGE_FILE si aplican);
una variable de selección no declarada bloquea. No serializar secretos.

El productor corre sobre árbol cooperativo con manifest antes/después. Un cambio
persistente, incluso mismo HEAD, invalida la correspondencia; no acredita el
nuevo árbol. Esta comprobación **no detecta toda modificación transitoria
restaurada**, ni protege de un escritor malicioso con igual permiso. Autenticidad
de runner/expectations requiere ancla fijada fuera de edición del agente; una
comparación de hashes locales solo detecta drift cooperativo. D2 exige aislamiento
del scorer para ejecutar código no confiable; P1 no lo reemplaza.

Cada invocación crea exclusivamente su directorio nuevo en `build/tmp`, con ID
no reutilizable, `.coverage` y LCOV privados. El consumidor verifica productor,
run, digest de inputs/config/scope y digest del artefacto. Nunca usa mtime ni
busca «el último archivo». Registrar logs completos o truncamiento explícito,
exit, tiempo, abortos y escritura terminal del registro; límites de logs no
truncan silenciosamente el inventario autoritativo de ejecución.

P1 rechaza symlinks en raíces declaradas, inputs seleccionados y destinos de
evidencia, incluidos internos/rotos; no promete seguirlos correctamente. La
raíz seleccionada se normaliza, rutas de artefacto no aceptan traversal/absolutas
ajenas. No borrar `mutants/**`, outputs históricos ni workspaces de terceros.
Dos evidence runs pueden usar outputs propios sobre árbol estable; si no puede
asegurarse su independencia se rechaza uno visiblemente. Árboles diferentes
con IDs de tests iguales nunca comparten registro. No reclamar exclusividad de
todos los procesos del usuario mediante un lock que solo respeta esta CLI.

## 5. Cierre sin otro motor de veredictos

GateResult conserva lo que decidió el gate. La envoltura calcula exclusivamente
validez/completitud del perfil y conserva fallos simultáneos. Orden de resumen:
**invalid > incomplete > rejected > accredited**. No se pierde un rechazo por
haber además un artefacto inválido.

| Eje | Condición mínima | Ejemplos |
|---|---|---|
| Validez | inputs finales iguales, versiones/esquema/anchor aceptados y outputs pertenecen al productor/run | Árbol/config/runner/artefacto distinto → invalid |
| Completitud | productores terminales; IDs esperados presentes una vez; toda obligación satisfecha o fallo observado | Tool ausente, truncamiento de IDs, skip requerido, cancelación, cero unidades → incomplete |
| Resultados | resultados originales y exits del consumidor, sin filtro de rojos | Test que falla o cobertura válida bajo piso → rejected si cadena válida y completa |
| Calificación | versión del instrumento/fixture y plataforma registradas | Sin calificación vigente no se anuncia accredited; causa incomplete |

Productor fallido + LCOV histórico: conservar FAIL del productor y marcar ese
artefacto como ajeno/invalid; no ejecutar ratchet sobre él. Productor fallido
sin artefacto: incomplete con fallo presente. Productor no cero por piso bajo
pero con tests terminales y LCOV íntegro: rejected, no «herramienta ausente».
El contador `source SF` completo no salva tests faltantes, ni viceversa.

El registro publica, al menos: schema/run, snapshot y inputs, expectativas,
scope por capacidad, ejecución y artefactos, GateResults originales, resultado
del ratchet (incluidos fallos adicionales), ejes/reasons, límites, calificación,
y costo por recurso con `exact/estimated/unavailable`. No interpreta ausencia
de precio/CPU como cero. No incluye score agregado de confianza ni ahorro.

Contrato de campos de schema 1 propuesto para esa envoltura:

| Campo | Contenido obligatorio |
|---|---|
| `schema_version`, `record_type`, `run_id` | Entero 1, `wct-run-evidence`, identidad única; versión desconocida impide consumir |
| `profile` | ID `beta3-p1`, versión/digest y lista cerrada de capacidades requeridas. Capacidad adicional sin productor calificado → incomplete, no se ignora |
| `inputs` | Base/HEAD, digest del índice, manifest de paths/tipos/hashes, digest inicial/final, configuración y herramientas efectivas; rutas de salida separadas |
| `expectations` | ID/digest y revisión del manifest; archivos obligatorios/vacíos/excluidos, nodeids seleccionados y escenarios/filas requeridos |
| `executions` | Lista por ID: productor, argv, cwd relativo al root identificado, versión de herramienta, inicio/fin, exit crudo nullable si no terminó, termination y refs de logs/colección/terminales |
| `artifacts` | Lista por ID: tipo, ruta relativa a directorio propio, SHA-256, producer execution ID, run ID, input/config/scope digests y consumidores |
| `results` | Lista intacta de GateResult obtenidos, con vínculo externo execution ID→índice; no añadir campos a cada GateResult. Resultado nativo de ratchet se conserva en `ratchet_result` con ejecución y fallos |
| `capabilities` | Por claim: required, expected/observed IDs, estado, límites, omisiones y ref de calificación; no aliases contados dos veces |
| `closure` | `validity`, `completeness`, `result`, `summary_state` y lista ordenada de reasons con identidad afectada. No solo un booleano |
| `costs` | Por recurso: unidad, valor nullable, calidad exact/estimated/unavailable y método; monedas/tarifas si existen |

Unknown keys o referencias entre IDs inexistentes se rechazan, nunca se
descartan silenciosamente. Un registro en progreso carece de cierre terminal
y no sirve como evidencia de éxito. Parent/task refs pueden ser null en P1;
no se inventa un experimento para ejecutar evidencia local. Las listas de
identidades son estables/únicas; timestamps y durations no participan del
digest semántico de configuración. La representación de schema 1 queda
congelada en D1 junto a fixtures de lectura/escritura y compatibilidad.

## 6. Presupuesto técnico propuesto para D1, todavía sin medir

Sin tarifas/modelos ni llamadas de inferencia. Valores siguientes son **techos
de planificación propuestos**, no mediciones ni umbrales de governance:

- Medición: tres fixtures (válido, inválido, frontera) y WCT de referencia;
  cinco pares beta.2/candidato por fixture y condición fría/caliente, orden
  alternado: 80 corridas locales como máximo. Repetición adicional exige explicar
  qué incertidumbre resuelve. Mediana/rango/N, no p95 con N=5.
- Tope inicial por corrida WCT: 10 minutos de pared, 2 vCPU, 4 GiB RSS, 250 MiB
  de outputs; hasta 2 MiB de metadata JSON excluyendo logs. Tope de campaña:
  6 horas de pared y 10 GiB de artefactos. Alcanzarlo interrumpe y conserva el
  registro: si impide completar el diseño, resultado «presupuesto insuficiente».
- Objetivo de overhead de evidencia, excluida la suite existente: mediana ≤20%
  del camino base comparable y ≤5 s por corrida, reportando ambos criterios.
  Medir por separado hashing, colección adicional, ejecución, consumo y reporte;
  no ocultar la colección extra como costo del modelo.
- No contexto LLM en P1: bytes de contexto no aplican. Registrar bytes de
  registro/log, RSS máximo, CPU-segundos y wall time. Costo monetario local es
  unavailable hasta acordar tarifa; inferencia es no ejecutada.
- No desactivar tests, bajar piso ni estrechar el denominador para cumplir
  presupuesto. Si excede, volver a revisar alcance/receta con el humano.

La medición histórica anterior de fast o de 43 mutantes no es el presupuesto
de esta cadena. El humano puede modificar estos techos antes de D1; todavía no
se han autorizado ni corrido las 80 mediciones.

## 7. Frontera del siguiente encargo

P1a/b/c de D0 son el único alcance implementable tras aprobación. Posibles
consumidores afectados: CLI, captura de gates, productor de cobertura, lector
del ratchet y reporte; reusar API/fachadas existentes. Antes de funciones nuevas
aplicar búsqueda por comportamiento y DRY; los módulos protegidos/grandes
requieren el proceso habitual y partición si exceden sitios de mutación.

No tocar policy/thresholds/workflows/pyproject/lock para implementar este contrato.
Tests/feature futuros deben invocar el entrypoint real además de probar unidades;
la generación actual de aceptación del ejemplo no entiende vocabulario P1.
Es parte de P1 conectar esos escenarios a ejecución específica y demostrar
colección, no solo añadirlos al parser. No se requiere generador universal.

No hay trabajo de P2 hasta que el contrato P1 esté aprobado y su cadena cumpla
la matriz, compatibilidad y presupuesto. Verifier distinto del coder, sin
permiso de escritura, confirma los resultados del diff final. En esta entrega
solo se verifica documentación y se corre fast sobre código preexistente.
