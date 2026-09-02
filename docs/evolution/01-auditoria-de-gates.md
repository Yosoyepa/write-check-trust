# Auditoría de gates

## Propósito y alcance

Esta auditoría contrasta la promesa documentada con la ruta ejecutable observada
en la revisión de corte. No evalúa la calidad de una futura implementación ni
modifica umbrales. Sus conclusiones son propuestas de producto, no findings de
seguridad explotables.

Se usaron cinco niveles de evidencia:

| Nivel | Significado |
|---|---|
| **E** — enforced | La ruta productiva bloquea directamente la condición declarada |
| **M** — measured | Se mide y reporta, pero no necesariamente bloquea toda la promesa |
| **H** — heuristic | Es una señal útil con falsos positivos o negativos esperables |
| **P** — process evidence | Solo puede aportar evidencia del proceso, no probarlo por sí sola |
| **U** — unverified | No hay una ruta observable suficiente para sostener la promesa |

Un gate puede ser **E** para una condición estrecha y **U** para una regla más
amplia que se le atribuye. La clasificación debe hacerse por claim, no solo por
nombre del gate.

## Fotografía del sistema

- `fast`: 7 gates y todos pasaron.
- `commit`: 20 gates y todos pasaron.
- `pr`: 26 entradas declaradas; no se usó como evidencia final de esta auditoría.
- `full`: 33 entradas, con 32 `PASS` y un `SKIP` por ausencia de `jscpd`.
- Hay gates o aliases fuera de algunos tiers, como mutación de código, mensaje de
  commit y orden aleatorio.
- `Status.blocking` solo considera `FAIL` y `ERROR`; `SKIP` no bloquea.
- El resultado estructurado contiene identificador, estado, resumen, duración,
  detalles y comando. No contiene de forma nativa valor observado, umbral,
  baseline, scope, versión de herramienta ni digest de configuración.

## Findings prioritarios

### FND-001 — el ratchet de cobertura total no está conectado al gate

`G-COV-TOTAL` ejecuta `pytest --cov --cov-branch` y produce LCOV, pero no pasa un
`--fail-under` ni compara el resultado con el baseline. En la fotografía, el
reporte efectivo fue 97 % mientras el baseline declarado era 100, y el gate
pasó. Por tanto, hoy prueba que la suite bajo cobertura termina con éxito y que
se genera un artefacto; no prueba el ratchet de cobertura total.

**Riesgo:** falso sentido de no regresión y métricas de CRAP/diff construidas
sobre un scope o artefacto incompleto.

**Criterio futuro:** fixtures en `baseline−1`, `baseline` y `baseline+1`, con
branches y archivos sin importar, deben producir resultados esperados y exponer
valor, baseline y scope.

### FND-002 — el harness no se mide a sí mismo en varias métricas críticas

La configuración de coverage y mutmut apunta a `src/example`. El LCOV observado
solo contiene archivos bajo ese paquete. CRAP, complejidad y varias herramientas
se invocan sobre `src`. El núcleo productivo vive en `tools/wct` y concentra los
hotspots principales, por lo que la afirmación histórica “el harness se prueba a
sí mismo” necesita separar:

- tests funcionales de `tools/wct`, que sí existen;
- cobertura y mutación instrumentadas de `tools/wct`, que no forman parte del
  scope observado;
- validación del template de ejemplo, que es un objeto distinto.

**Riesgo:** optimizar la muestra mientras el instrumento queda fuera del
instrumento de calidad.

### FND-003 — los property tests no están aislados de coverage y mutación

`G-PROP` ejecuta la carpeta property de forma independiente, pero
`G-COV-TOTAL` ejecuta `pytest` sin excluir el marker. Además, la selección de
mutmut incluye explícitamente un archivo property. Esto contradice la regla que
exige separar property tests de coverage, mutación, CRAP y DRY.

**Riesgo:** coverage o mutation score inflados por una suite que el contrato dice
que no debe contribuir a esas métricas; resultados no comparables entre repos.

### FND-004 — el red team valida reconocedores paralelos, no los gates reales

La mayoría de casos de `quality/redteam/cases.yaml` entrega un payload a
`_reject`, que implementa expresiones regulares y lógica especializada. El
runner verifica además que el identificador del gate exista, pero no construye
un workspace adversarial ni ejecuta ese gate. Las excepciones parciales son los
casos de hook para escritura protegida y comando prohibido.

Consecuentemente, `30/30` significa que 30 payloads son reconocidos por el
simulador de red team; no que 30 repositorios defectuosos sean rechazados por la
ruta productiva.

También existe drift semántico entre la taxonomía F1–F15 del plan y la asignada
en el corpus actual. Una taxonomía versionada debe tener una fuente única.

**Riesgo:** un reconocedor y el gate real pueden divergir y ambos seguir verdes.

### FND-005 — aceptación sintáctica y aceptación ejecutable están mezcladas

`G-ACCEPT` parsea features y busca duplicación en el IR. No demuestra que todos
los escenarios estén generados, recolectados ni ejecutados. `G-ACCEPT-MUT` usa
por defecto `features/example.feature`; una invocación sin feature no recorre el
corpus completo. La mutación solo cambia valores en `Examples`. Un `Scenario`
sin filas puede producir cero mutaciones y reportar cero sobrevivientes.

La opción declarada `require_parameters` no se observa conectada a esta ruta.

**Riesgo:** éxito vacuo y cobertura de una feature de demostración presentada
como cobertura de aceptación del producto.

### FND-006 — configuración declarativa y comportamiento efectivo divergen

Se observaron claves públicas que se reportan o validan superficialmente, pero no
alteran el comportamiento esperado: perfil, modo, perfil de lint, límites de
aceptación, presupuestos temporales y varios campos de mutación, dependencias,
arquitectura, documentación y minimalismo. Paralelamente, existen valores
operativos fijados en el runner —por ejemplo 90 para diff coverage y 6 para
CRAP— sin trazabilidad directa al archivo de umbrales.

Esto no implica que cada clave deba sobrevivir. Hay dos resultados válidos:
conectarla a un consumidor probado o retirarla de la interfaz pública.

**Riesgo:** el usuario cambia una configuración y cree haber cambiado una
política cuando la ejecución permanece igual.

### FND-007 — `SKIP` no distingue desarrollo local de certificación completa

Un gate opcional ausente no bloquea y el resumen cuenta el tier como “no
bloqueante”. Esto es razonable para algunos flujos locales, pero insuficiente
para una afirmación de capacidad completa. La lista declarada de herramientas
opcionales y los `optional=True` codificados no forman una sola fuente de verdad;
además, `G-DOC` omite por su propia ruta cuando falta su herramienta.

**Riesgo:** dos equipos llaman `full` a conjuntos de capacidades diferentes.

**Modelo propuesto:** reportar por separado:

- **corrección:** ningún control ejecutado falló;
- **completitud:** todas las capacidades requeridas para el perfil estuvieron
  presentes y ejecutaron;
- **validez:** artefactos, scopes y configuración corresponden a esta ejecución.

### FND-008 — el reporte no es todavía un registro de evidencia

`wct report` enumera configuración y reglas, pero no presenta una observación
actual por gate con valor, umbral, tendencia y artefacto. No permite responder si
un `PASS` se obtuvo por estar mejor que el baseline, por ausencia de findings, por
alias a otro gate o por omisión tolerada.

**Riesgo:** auditorías y comparaciones de modelos dependen de parsear texto y de
conocimiento implícito del entorno.

### FND-009 — el sistema de ratchets no cubre todas las promesas ratcheted

El motor de mediciones incluye categorías como supresiones, deuda, introversión,
zonas de arquitectura, ignores por archivo, tamaño, LCOM, templates DRY y
docstrings. La cobertura total no forma parte de esa medición aunque la
documentación la describa como ratchet. Otras herramientas tienen baselines o
semánticas de tolerancia cero fuera de un contrato uniforme.

**Riesgo:** “ratchet” significa mecanismos diferentes según el gate y no siempre
puede reconstruirse la comparación.

### FND-010 — la verificación documental es más estrecha que la regla

`G-DOC` usa cobertura de docstrings. La regla exige además consistencia con
firma, parámetros, retorno y excepciones, y la configuración declara
`pydoclint`. Esa parte no aparece en el gate observado.

### FND-011 — SBOM no equivale a compatibilidad de licencias

`G-SBOM` genera un inventario CycloneDX. La regla SEC-008 afirma que las
licencias deben ser compatibles. Generar el inventario es un insumo, no una
decisión de compatibilidad ni un bloqueo. DeepSeek Harness contiene una
verificación explícita de licencias de paquetes que sirve como patrón conceptual.

### FND-012 — el mapeo regla → gate sobreafirma algunas garantías

Hay reglas históricas o de proceso que un gate de estado final no puede probar
por sí solo:

- TDD no se deduce de tener coverage o mutation score al final.
- Buscar antes de crear una abstracción no se deduce de un DRY verde.
- El orden mutación → Gherkin → CRAP → DRY requiere evidencia de trayectoria.
- Separar autor y verificador requiere identidad y provenance de la ejecución.
- Reportar honestamente un gate fallido es una conducta, no una propiedad del
  árbol.

Estas reglas siguen siendo valiosas, pero deben etiquetarse como evidencia de
proceso o revisión humana, no como enforcement automático completo.

### FND-013 — la mutación diferencial es más gruesa que su nombre sugiere

El manifiesto identifica funciones cambiadas para decidir si hay trabajo y para
el presupuesto de sitios, pero la ejecución posterior de mutmut no se limita de
forma observable a esas funciones. Cambios de módulo fuera de una función pueden
tener semántica distinta. Límites declarados de workers, timeout y sobrevivientes
no aparecen integrados de manera uniforme.

### FND-014 — “full” y “full hardening” no cubren la misma superficie

El tier `full` no contiene `G-MUT` ni `G-ACCEPT-MUT`. Otros comandos o workflows
encadenan subconjuntos diferentes. La tarea semanal observada ejecuta full,
mutación de aceptación y red team, pero no mutación del código fuente. Los
nombres deben describir un perfil versionado, no una expectativa implícita.

### FND-015 — el gate de orden aleatorio no está disponible

`G-TEST-RANDOM` está registrado como opcional y fuera del tier principal. En el
entorno auditado, pytest rechazó `--randomly-seed=last`. La regla TEST-006 no
tiene por tanto evidencia automática en esta fotografía.

## Matriz de los gates por tier

La columna “fuerza” describe la promesa observada, no la utilidad general de la
herramienta.

### Fast

| Gate | Fuerza | Observación y oportunidad |
|---|---|---|
| `G-META-2` | M | valida restricciones puntuales; no demuestra que `profile` o `mode` alteren la ejecución |
| `G-RULES-DRIFT` | E | compara artefactos generados; añadir provenance de generador y digest |
| `G-SUPPRESS` | E/M | ratchet de supresiones; reportar scope, baseline y clases encontradas |
| `G-DEBT` | E/M | controla marcadores con owner/issue; separar sintaxis de existencia real del issue |
| `G-LINT` | E | Ruff es la ruta ejecutable; hacer explícito el perfil efectivo |
| `G-FMT` | E | verificación determinista de formato |
| `G-TYPE` | E | mypy estricto en el scope configurado; publicar scope y versión |

### Commit

| Gate | Fuerza | Observación y oportunidad |
|---|---|---|
| `G-META-1` | E/P | detecta cambios protegidos en el diff; no prueba quién autorizó la modificación |
| `G-TEST` | E | suite pasa; complementar con collection manifest y clasificación de suites |
| `G-ARCH` | E | dependency rules sobre roots configurados; hoy el foco observado es el ejemplo |
| `G-ARCHMETRICS` | M/H | mide A/I/D con baseline; el resumen “healthy” puede ocultar zonas de dolor toleradas |
| `G-DEPS` | E | dependencias declaradas/usadas según la herramienta; conservar excepciones explícitas |
| `G-DEAD` | E/H | tolerancia cero de findings; documentar confianza, scope y falsos positivos |
| `G-SAST-BANDIT` | E/H | análisis sobre `src`; el núcleo del harness requiere decisión explícita de scope |
| `G-SECRET` | E/H | escanea rutas seleccionadas; documentar exclusiones como decisión, no como implícito |
| `G-MUT-SITES` | E/M | presupuesto sobre archivos cambiados; depende del manifiesto y granularidad de funciones |
| `G-ACCEPT` | E para sintaxis | parsea e inspecciona IR; no prueba ejecución ni cobertura del corpus |
| `G-SIZE` | E | ratchet de tamaño; reportar deuda tolerada y archivos nuevos por separado |
| `G-COGNITIVE` | E | umbral en código fuente configurado; alinear con el scope del producto real |
| `G-WIRE` | E/H | verifica wiring y límites conocidos; sumar fixtures de ensamblaje real |

Las primeras siete entradas de `fast` también forman parte de `commit` y no se
repiten en la tabla.

### PR

| Gate adicional | Fuerza | Observación y oportunidad |
|---|---|---|
| `G-HOOKS-WIRED` | M | doctor confirma instalación/configuración; añadir smoke del evento real |
| `G-COV-TOTAL` | U para ratchet | produce LCOV y corre tests, pero no aplica el baseline y solo mide el ejemplo |
| `G-COV-DIFF` | E/M | bloquea al 90 % hardcoded; conectar umbral y verificar artefacto fresco/scope |
| `G-PROP` | E parcial | corre property tests, pero no garantiza su exclusión de otras métricas |
| `G-ACCEPT-MUT` | U parcial | default a una feature y puede tener cero mutaciones |
| `G-REDTEAM` | H/U | reconocedores sintéticos; no califica los gates productivos end-to-end |

### Full

| Gate adicional | Fuerza | Observación y oportunidad |
|---|---|---|
| `G-CRAP` | E parcial | umbral 6 sobre `src`, herramienta opcional; conectar config y cobertura válida |
| `G-CC` | E parcial | grades hardcoded sobre `src`; publicar equivalencia con CC ≤ 10 por función |
| `G-DRY` | H | análisis estructural útil, pero scope observado no cubre todo el harness |
| `G-DRY-TOK` | H | ausente en la corrida; un `SKIP` debe reducir completitud del perfil |
| `G-DRY-TPL` | H/M | ratchet de templates; distinguir matriz de test legítima de clon productivo |
| `G-INTROVERT` | H/M | heurística y ratchet; no sustituye aserción semántica sobre el SUT |
| `G-LCOM` | H/M | métrica cohesiva; documentar qué clases quedan fuera y por qué |
| `G-SAST-SEMGREP` | E/H | herramienta opcional; perfil certificado requiere disponibilidad fijada |
| `G-AUDIT` / `G-CVE` | E | audita dependencias desplegables; persistir lock y advisory snapshot |
| `G-SBOM` | M | genera inventario; no decide compatibilidad de licencias |
| `G-DOC` | E parcial | cobertura de docstrings, sin consistencia de firmas observada |
| `G-REDTEAM` | H/U | misma limitación end-to-end descrita en PR |

### Gates standalone o aliases relevantes

| Gate | Fuerza | Observación y oportunidad |
|---|---|---|
| `G-MUT` | E parcial | mutmut sobre `src/example`; no pertenece a `full` y no califica el harness |
| `G-COMMIT-MSG` | E contextual | solo tiene sentido con un mensaje real; registrar cuándo no aplica |
| `G-TEST-RANDOM` | U en esta corrida | herramienta ausente y omisión opcional |
| `G-ARCH-CYCLE`, `G-IMPORT-ORDER`, `G-SAST`, `G-TEST-FAST`, `G-TODO`, `G-RULES-SYNC` | alias | evitar contarlos como mediciones independientes en estadísticas de cobertura |

## Oportunidades transversales de hardening

### Contrato mínimo por resultado

Todo gate debería poder declarar:

| Campo | Pregunta que responde |
|---|---|
| `claim_id` y versión | ¿qué afirmación exacta se evaluó? |
| estado y completitud | ¿falló, omitió o ejecutó toda la capacidad? |
| valor, unidad y operador | ¿qué se midió y cómo se compara? |
| umbral y baseline | ¿contra qué criterio pasó? |
| scope y exclusiones | ¿qué archivos, tests y dependencias entraron? |
| herramienta y versión | ¿qué implementación produjo el resultado? |
| digest de configuración | ¿qué política efectiva se usó? |
| artefactos y hashes | ¿puede auditarse la evidencia? |
| duración y presupuesto | ¿cumplió el anillo temporal prometido? |
| provenance | ¿qué revisión, entorno y actor lo ejecutaron? |

### Calificación, no solo tests unitarios

Cada gate necesita una matriz de fixtures:

1. control sano que debe pasar;
2. defecto inequívoco que debe fallar;
3. valores justo debajo, en y encima del umbral;
4. herramienta ausente;
5. herramienta que crashea o excede tiempo;
6. artefacto stale o de otro commit;
7. configuración modificada;
8. intento de bypass;
9. alternativa válida que no debe producir falso positivo;
10. ejecución por el CLI/entrypoint real.

El resultado agregado debe publicar sensibilidad, especificidad, precision,
false-positive rate, false-negative rate y casos no calificables. Estas métricas
se definen en [SPEC-002](specs/SPEC-002-metricas-y-estadistica.md).

### Meta-gate de conformidad de configuración

Antes de añadir otro umbral, el producto necesita demostrar para cada clave
pública una cadena completa:

`clave → parser → consumidor → resultado observable → fixture de frontera → documentación`.

Una clave sin consumidor es deuda de interfaz. Un valor hardcoded que duplica
una clave es shadow configuration. Ambos deben aparecer en el reporte, aunque la
remediación final pueda ser retirar la clave en vez de implementarla.

## Criterio de salida de la fase de calificación

WCT solo debería usar un gate como evidencia cuantitativa en el benchmark de
modelos cuando:

- su claim esté versionado y sea más estrecho que la regla humana si corresponde;
- su ruta real tenga controles positivos, negativos y de frontera;
- su scope y exclusiones sean explícitos;
- `SKIP`, error y herramienta ausente tengan semántica probada;
- el artefacto esté ligado al commit y configuración de la ejecución;
- su tasa de escapes y falsos positivos sea conocida en el corpus de
  calificación;
- y no se cuente dos veces un alias como señal independiente.

Hasta entonces, el gate sigue siendo útil como control de ingeniería, pero no
debe presentarse como instrumento calibrado de investigación.
