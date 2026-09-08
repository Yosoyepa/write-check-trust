# Revisión ciega SH-P01 — CND-80B8

**Dictamen: REQUIERE_CORRECCION. No recomendar bless ni comenzar P02.**

La lógica inspeccionada satisface los ejemplos públicos y la suite pasa, pero
dos funciones incumplen el límite vigente de CRAP; los tests dejan escapar una
violación del orden contractual y dos alteraciones del inventario del feature.
Además, el digest agregado del handoff no se reproduce y falta la verificación
de ratchets solicitada. No se ha demostrado un fallo semántico del comparador
original con las entradas examinadas: distinguirlo de los fallos de sus tests.

## 1. Identificación y límites de autoridad

| Campo | Valor |
|---|---|
| review_id | SHP01-REVIEW-CND-80B8-R1 |
| task / contrato / modo | SH-P01 / `sh-p01/1` / SH-D, desarrollo |
| run / coder / candidate | SHR-015D6C / COD-CA7A / CND-80B8 |
| base de producto | `8de9107184288f1aa72c9578a14913686c47ad7c` |
| reviewer | arquitecto de esta tarea; no autor del candidato |
| calidad congelada | 2026-09-07T22:02:10Z; dictamen anterior a conocer modelo/coste |
| cegamiento | identidad, proveedor, precio y consumo no consultados |
| independencia | revisión separada del coder, mismo host; el arquitecto participó en la SPEC |
| aislamiento acreditado | revisión cooperativa; no sandbox hostil ni evaluación externa independiente |
| asistencia | diagnóstico y criterios de reparación; no fix de producto escrito por el arquitecto |
| coste de diagnóstico | unavailable; no se convierte duración de comandos en coste de inferencia |

Contrato, Gherkin, gobernanza, molde y registros conservan los cinco hashes
individuales del [handoff original](../runs/SHR-015D6C-CND-80B8.md). No se
modificaron esos documentos, el handoff ni los cuatro archivos candidatos.
Las sondas sustituyen código o texto **solo en procesos de diagnóstico**, no
en el candidato. No hubo commit, push, PR, bless ni instalación de dependencias
por el reviewer. Esto tampoco constituye aprobación de una release beta.3.

Worktree inspeccionado:
`/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8`, rama
`codex/beta3-sh-p01-identidades`. Cuatro archivos nuevos, 589 inserciones, sin
cambios a archivos existentes de producto, tests o gobernanza. El intent-to-add
permite verlos con `git diff`; no es un commit.

## 2. Hallazgos, motivos y condiciones de cierre

Los IDs siguientes pertenecen a esta revisión, **no son issues de GitHub**.
Task, candidato, contrato y fecha son los de §1. HIGH/MEDIUM requieren resolver
el defecto o una decisión explícita de alcance antes de aceptar, conforme a
[REVISION-Y-FEEDBACK](../REVISION-Y-FEEDBACK.md). No se infiere intención del coder.

### SHP01-R01 — HIGH: CRAP 10 y 7 en código nuevo

- **Dónde:** `tools/wct/evidence/identities.py:81` (`_inventory_findings`) y
  `:120` (`_resolved_status`), en el worktree candidato.
- **Regla:** STYLE-002/003; `governance/thresholds.yaml`, `crap.changed_max: 6`.
- **Esperado:** CRAP ≤ 6 en toda función cambiada; no basta CC ≤ 10.
- **Observado:** con LCOV focal recién generado y cobertura 100 %, el motor
  instalado `crap4py` devuelve exit 1: CRAP **10.0** y **7.0**. Las otras
  funciones medidas tienen 5.0 y 4.0. Certeza: reproducción directa.
- **Razón:** `CRAP = CC² × (1 − coverage)³ + CC`; con coverage=1 queda CC.
  Añadir más cobertura no arregla estas dos funciones.
- **Por qué escapó:** fast/commit no ejecutan G-CRAP. Más importante todavía:
  `tools/wct/gate/checks.py:101–117` construye `crap4py src ...` y
  `gate/runner.py:410–417` declara scope `src`. El G-CRAP histórico de full
  **tampoco mide esta pieza de tools**, aunque estuviera verde.
- **Control:** mismo LCOV, dos funciones conformes y dos no conformes;
  cruce adicional con el analizador de CC. No hay un umbral inventado.
- **Primera detección:** revisión del arquitecto, medición explícita de tools.
- **Decisión / owner:** coder reduce complejidad preservando comportamiento,
  con responsabilidades coherentes; no extracción mecánica para engañar al
  contador, supresiones, aumento de umbral ni cambio de runner. Reviewer
  vuelve a medir sobre los bytes finales. Rediseñar el alcance del gate es
  una propuesta separada, no permiso para tocar gobernanza en P01.

### SHP01-R02 — MEDIUM: el test de orden canónico no discrimina duplicados múltiples

- **Dónde:** `tests/unit/test_evidence_identities.py:293–322`, I21; orden
  productivo en `identities.py:105`.
- **Regla:** P01 §§4–6, I21, TEST-001. Debe conservarse el orden lexicográfico
  dentro de cada código e inventario, también al permutar entradas.
- **Observado:** cambiar solo el orden de los duplicados a descendente deja
  **54 tests verdes**. Con E=(B,A,B,A), C=X=(B,A), el original emite los
  duplicados A,B, pero la variante emite B,A. Expected independiente literal.
- **Causa confirmada:** las aserciones actuales no enfrentan dos identidades
  duplicadas distintas dentro del mismo inventario/código. Una lista de varias
  findings de clases distintas no demuestra este eje de ordenación.
- **Control válido:** el candidato original y una estrategia alternativa de
  conteo pasan. **No hay bug de orden observado en el original**; el defecto
  es que su regresión contractual sobrevive al cambio incorrecto.
- **Decisión / owner:** coder añade ejemplos literales con al menos dos IDs
  duplicados en cada inventario y entradas permutadas; coteja salida completa.
  Cubrir también el eje de múltiples missing/unexpected al revisar I21. El
  reviewer repite la variante y el control válido. No exigir nuevas reglas
  semánticas ni reescribir la tabla pública.

### SHP01-R03 — MEDIUM: el binding del feature descarta evidencia duplicada o extra

- **Dónde:** `tests/unit/test_evidence_identities.py:375–386`, especialmente
  el acceso a `scenarios[0]` y el dict por `row['caso']` en :379.
- **Esperado:** acreditar el inventario exacto aprobado, no solo sus claves
  únicas; P01 exige feature verbatim y correspondencia con I01–I18.
- **Observado:** el parser productivo recibe, mediante una sonda de lectura,
  texto con una fila I01 duplicada: 19 filas, `ir_dry_count=0`, **54 passed**.
  Otra sonda duplica el Scenario Outline completo: dos escenarios,
  `ir_dry_count=0`, **54 passed**. No se editaron archivos del candidato.
- **Causa confirmada:** la construcción del dict elimina duplicados y el
  índice `[0]` ignora otros escenarios. Parse/ir-dry tampoco detectaron estas
  dos alteraciones. La primera reproducción por IR se confirmó después
  usando texto alterado y el parser real, sin sustituir su implementación.
- **Control válido:** el feature original sí coincide con el bloque aprobado
  y pasa. No se acusa al coder de entregar un feature duplicado.
- **Decisión / owner:** coder refuerza el test de binding: cardinalidad,
  unicidad antes de indexar y conjunto completo de escenarios contratados.
  Negativos con fila/escenario extra deben fallar; el original debe pasar.
  No modificar el parser ni añadir handlers de P06 en este incremento.

### SHP01-R04 — MEDIUM: identificación agregada y afirmaciones del handoff no reproducibles

- **Dónde:** `candidate_manifest_digest`, fila 7 de checks y case_bindings
  del [registro original](../runs/SHR-015D6C-CND-80B8.md).
- **Regla:** PROC-012 y REGISTROS: evidencia vinculada a bytes, alcance y corrida.
- **Observado:** los cuatro hashes individuales coinciden, pero el digest
  agregado declarado `de207e0d…` no coincide con la fórmula indicada. La
  serialización exacta de §3 produce `e3a64265…`; sin LF final tampoco coincide.
  **No hay evidencia de que los archivos candidatos hayan cambiado.**
- El registro agrupa «401 passed ×4» mezclando una corrida ambiental fallida
  y ejecuciones de G-TEST. Este gate selecciona unit/integration sin property:
  se coleccionaron **399**, no 401. El archivo `full-suite.txt` guardado acredita
  una corrida de 401 en 90.31 s. No se acreditan cuatro completas exitosas con
  esos artefactos; el texto no sustituye los outputs faltantes.
- El resumen de I19/I20 invierte componentes del nodeid: se observa
  `[string-expected]`, no `[expected-string]`. Los IDs completos sí están en
  el log focal; deben extraerse, no reconstruirse a mano.
- El informe de cobertura dice 53 statements; la medición sobre el candidato
  final da **54 statements y 20 ramas, 100 %**. Vincular cada medición a su
  snapshot, especialmente tras añadir `__all__` al final de la secuencia.
- **Certeza:** diferencias de hashes, alcance y colección reproducidas. No se
  conoce la causa de la cifra de digest ni se atribuye fabricación intencional.
- **Decisión / owner:** coder entrega una addenda/registro nuevo append-only,
  con parent_candidate_id y serialización definida, resultados por corrida y
  outputs/digests. Corregir atribuciones sin borrar la primera entrega. El
  reviewer congela y verifica otra vez la siguiente identidad de candidato.

### SHP01-R05 — MEDIUM: ratchets solicitados sin evidencia global de cobertura

- **Regla:** P01 §8.3 y PROMPT-CODER paso 7 requieren ratchets y alcance real.
- **Observado:** el handoff no registra su ejecución. En el candidato no
  existe `build/coverage/lcov.info`. Mi `wct ratchet check` devuelve exit 0,
  pero `wct ratchet check --require coverage-total` devuelve exit 1:
  `coverage-total: exigible no medida (no existe build/coverage/lcov.info)`;
  **medidas 0 de 1 exigibles**.
- **Razón:** el modo tolerante no acredita una métrica ausente. El LCOV focal
  de este review prueba cobertura del módulo, no el ratchet global del repo.
  «Solo G-META rojo» es verdadero **dentro del tier commit corrido**, no para
  toda la verificación requerida de la pieza.
- **Control:** mismo snapshot: tolerante verde y obligación de presencia roja.
  No se ha probado una caída de cobertura; falta medirla con el productor
  correcto y comprobarla. No se reemplazó el LCOV global con datos focales.
- **Decisión / owner:** coder produce cobertura global nueva con la receta
  productiva sin property, y ejecuta ratchets tolerante y exigible con alcance
  declarado. Si aparece un rojo, diagnosticarlo; no elevar baseline ni bless
  para ocultarlo. Reviewer reproduce el resultado posterior.

## 3. Identidad del candidato conservado

Manifiesto: UTF-8, dos espacios entre hash y ruta relativa, orden siguiente,
LF tras **cada** línea incluida la última; sin fences ni líneas en blanco:

```text
d89be6c7fa40a8f6ed21953414140c223a335a9477fdeb8145595e5c80829e5e  tools/wct/evidence/__init__.py
e27b0aa992d4ce4dc4832d8fc57c53ddaa84216f75f51eedc52d20a387473953  tools/wct/evidence/identities.py
e02cd1427420c8a6a5e2089813ad5513dae2d3def02f1b6e220edeb62ac658e6  tests/unit/test_evidence_identities.py
d3d64140477e5b67e6ee1f6967fe9cb0c4c285365b562b953043a0056b251b0e  features/wct-evidence-identities-001.feature
```

SHA-256 reproducido:
`e3a6426553e7b3c00445ad249f0dd8f31fb098d7e5276e11cc97667bfdd77a6a`.
Se obtiene desde el worktree con:

```bash
sha256sum tools/wct/evidence/__init__.py tools/wct/evidence/identities.py tests/unit/test_evidence_identities.py features/wct-evidence-identities-001.feature | sha256sum
```

Declarado por el coder:
`de207e0dc06a995918d5a8f34917744e53aae9e17c97c2aad483a7ee797e86b4`.
Alternativa sin LF final:
`dbd5fcf49168dcf9beae3032b27f444a2f17672f07e6ff45a70d6cb00afb7c7a`.
Este manifiesto de revisión **no** es `governance/mutation-manifest.json` ni
`integrity.lock`; no los modifica ni sustituye un bless humano.

Se conservó además `candidate-CND-80B8.patch` fuera del worktree candidato,
SHA-256 `460ca37f2a420d2aad3f6e05985cadbae2e750a52fe5cbd61d412de0dfa15306`.
Los artefactos bajo `build/tmp/` son locales e ignorados por Git: preservarlos
antes de limpieza y no afirmar custodia inmutable/remota. El siguiente intento
debe mantener el original disponible, no sobreescribir su identidad.

## 4. Verificación efectivamente ejecutada por el arquitecto

Cwd: worktree candidato de §1; invocaciones con `uv run --no-sync`, sin
sincronización/instalación automática. Runtime observado: Python **3.13.14**;
`crap4py` **0.1.1**. No equiparar timings con la línea base documental en
Python 3.12.13 ni derivar regresión de rendimiento de corridas no emparejadas.

| Comprobación | Resultado observado | Alcance / fuente |
|---|---|---|
| `pytest --collect-only -q` | 401 collected | repo completo; transcript de revisión |
| `pytest -q` | **401 passed, 89.21 s** | nueva corrida completa del reviewer, sesión 23701; transcript |
| Focal con coverage/branch | **54 passed; 54 statements, 20 ramas, 100 %** | solo `tools.wct.evidence`; `coverage-focal.txt` y `focal.lcov` |
| `crap4py tools/wct/evidence --lcov … --max-crap 6` | **exit 1, scores 10/7/5/4** | motor real, LCOV focal nuevo; `crap.txt` |
| `wct gate --tier fast` | 7 PASS, 0 FAIL, 0 SKIP | tier real, no inferido de pruebas focales |
| `wct gate --tier commit` | 20 PASS, 1 FAIL: G-META-1 | no declara que CRAP/ratchets estén verdes |
| `wct integrity check` | exit 1, exactamente los dos archivos nuevos de producto | drift pre-bless permitido, no paths ajenos |
| `wct ratchet check` | exit 0, «Todos los ratchets se mantienen.» | tolerante; no acredita presencia de coverage-total |
| `wct ratchet check --require coverage-total` | exit 1, medidas 0 de 1 | falta LCOV global; no es prueba de umbral incumplido |
| `pytest --collect-only -q tests/unit tests/integration -m "not property"` | 399 collected | selección del G-TEST actual |
| `lint-imports` / archmetrics | 4 contratos kept; sin ciclos/violaciones reportados | modelo arquitectónico de `src/example`, no cobertura automática de tools |
| `wct introvert --json tests/unit/test_evidence_identities.py` | 6 funciones extrovertidas | detector de trazabilidad; no garantiza sensibilidad de 54 casos |
| Conteo AST de sitios | 82 en identities.py, por debajo de 100 | **no** son 82 mutantes ejecutados |
| `git diff --check` | exit 0 | cuatro archivos nuevos visibles por intent-to-add |

Cobertura focal producida con `pytest tests/unit/test_evidence_identities.py
-q -m "not property" --cov=tools.wct.evidence --cov-branch`, con
`COVERAGE_FILE` y salida LCOV exclusivos en el directorio de artefactos. El
comando CRAP consume ese LCOV, no uno heredado del repo de ejemplo.

No ejecutados: full/pr completos, mutmut/G1b, aceptación con handlers o su
mutación, orden aleatorio, SBOM, calificación de release, cobertura global
recién producida. **DRY no se ejecutó después del CRAP rojo**: la guía
`wct-crap` exige resolver la causa y PROC-004 detener esa secuencia antes del
siguiente control pesado. No se certifica hardening completo por estos datos.

### Calibración manual de sensibilidad

Cada variante se carga en memoria en un proceso nuevo y se ejecutan los 54
tests focales del candidato. Son ejemplos de diagnóstico, **no una muestra
aleatoria de defectos, un mutation score oficial ni un holdout privado**.

| Variante | Resultado focal | Lectura |
|---|---|---|
| Original | 54 passed | control válido |
| Conteo alternativo válido en lugar de Counter | 54 passed | no se exige una única estrategia de conteo |
| Comparar solo conteos | 6 failed / 48 passed | defecto detectado |
| Deduplicar antes de validar | 5 failed / 49 passed | defecto detectado; reproduce el challenge declarado por el coder |
| Ignorar executed y reutilizar collected | 24 failed / 30 passed | defecto detectado |
| Aceptar expected vacío como match | 2 failed / 52 passed | defecto detectado |
| Aplicar strip a identidades | 2 failed / 52 passed | defecto detectado |
| Devolver solo la primera causa | 8 failed / 46 passed | defecto detectado |
| Rechazar todo | 12 failed / 42 passed | controles positivos discriminan |
| Duplicados en orden descendente | **54 passed** | escape; ejemplo independiente demuestra el orden incorrecto |
| Feature con I01 duplicada, parser real | **54 passed**, 19 filas | escape del binding |
| Feature con Scenario Outline extra, parser real | **54 passed**, 2 escenarios | escape del binding |

La alternativa válida cambia la estrategia de conteo, **no es una segunda
implementación independiente completa del comparador**. Se declara esta
limitación respecto del ideal de calibración de P01. Tras publicar estas
sondas, son regresiones de desarrollo SH-D, nunca examen ciego SH-E reutilizable.

## 5. Rúbrica no compensatoria y decisiones benignas

| Dimensión | Dictamen | Motivo |
|---|---|---|
| Corrección semántica | satisface en el alcance comprobado | tabla y controles válidos; sin prueba de corrección universal |
| Diseño y ensamblaje | satisface | stdlib, núcleo puro, API e inmutabilidad; sin CLI/P02 ni IO |
| Honestidad de tests | defecto | R02 y R03; cobertura no equivale a sensibilidad |
| Compatibilidad | satisface en el alcance comprobado | archivos existentes intactos; suite completa pasa |
| Gobernanza/evidencia | defecto | R04; falta registro exigido de R05 |
| Mantenibilidad | defecto | R01, umbral vigente incumplido |
| Operación y límites | no-evaluable para cierre completo | R05; hardening y frescura global no acreditados |

- `__all__` exporta exactamente los tres símbolos públicos contratados. Es
  una declaración idiomática y coherente para la API sin caller de producto
  hasta P06, **no por sí misma un bypass ilegítimo**. No requiere whitelist
  adicional ni bloquea esta revisión. El coder corrigió explícitamente su
  lectura inicial equivocada de la whitelist existente.
- La tabla parametrizada es una matriz de cobertura; no pedir su eliminación
  por similitud estructural (MIN-008). Mantener expected literal y SUT real.
- Preparar un venv con dependencias ya declaradas resolvió un fallo ambiental,
  no un flake probado. Sin embargo, el prompt decía «no instalar»: registrar
  la desviación y reconciliar preflight/autoridad para la reparación. No
  reinterpretarlo como permiso ilimitado ni exigir entornos nuevos imposibles.
- IDs opacos locales e intent-to-add fueron declarados; no son modelo,
  telemetría ni acción de publicación. Telemetría unavailable no es defecto
  de calidad, pero impide afirmar ahorro o coste por tarea.

## 6. Aprendizajes para mejorar WCT, separados de la reparación

Estado de todas las propuestas: **candidate / investigar**, owner arquitecto,
sin issue remoto creado ni implementación autorizada. Se aplican a futuros
incrementos/lotes Wn/Qn, preservando este resultado del primer candidato.

| Propuesta | Evidencia y motivo | Regla/consumidor propuesto | Calibración y frontera |
|---|---|---|---|
| SHP01-F01 — cobertura de obligaciones por ruta | R01: un gate verde de src no juzga tools | matriz pieza→regla→motor→scope efectivo; impedir «verificado» sin intersección con cambios | positivos src/tools/excluidos; negativos fuera de scope; medir overhead; runner/policy protegidos, autorización aparte |
| SHP01-F02 — inventarios sin pérdida al indexar | R03: dict/set borra anomalías antes de validarlas | conservar lista y validar cardinalidad/unicidad antes del binding, futuro consumidor de P01 | distinguir IDs repetidos de datos repetidos legítimos; escenarios extras y casos nuevos del revisor; no imponer unicidad a todo código |
| SHP01-F03 — recibos reproducibles | R04/R05: digest, selección y artefactos mezclados | generar manifest, argv, runtime, colección real, exits y hashes desde capturas, no prosa manual | medir archivos omitidos, LF, runs fallidos, logs parciales y cambios tras coverage; no prometer autenticidad por hashing local |
| SHP01-F04 — challenge por cláusula contractual | R02: todos los branches cubiertos, orden sin protección | vincular regla observable con negativo plausible y positivo válido; medir qué detecta cada instrumento | nuevos negativos no usados al diseñar tests; coste de revisión y falsos positivos; no entrenar y evaluar sobre el mismo examen |
| SHP01-F05 — preflight reproducible del operador | venv sin quality; runtime distinto de referencia | entorno declarado/fijado antes del coder, comprobar herramientas y selection; aprobación de sync sin upgrades si necesaria | worktree limpio, deps ausentes, intérprete divergente; separar incidentes de defectos del patch |
| SHP01-F06 — coherencia matemática de gobernanza | STYLE-002 rationale dice CC=10 con ~96 % para CRAP≤6; imposible | corregir explicación sin cambiar fórmula ni umbral: CRAP≥CC para coverage en [0,1] | ejemplos CC4/6/7/10 y bordes; revisar también rationale STYLE-003; rules/generated protegidos, no editar en P01 |

No se ha medido presupuesto técnico emparejado de estas propuestas ni coste
de revisión completo; ambos quedan unavailable. Antes de promocionarlas se
exigen controles nuevos y validación separada/humana; no autoaprobar el juez
que el mismo arquitecto acaba de diseñar. F06 es también responsabilidad de la
especificación/gobernanza previa, no solo del coder.

**Conclusión experimental:** este caso revela límites del harness y trabajo
humano necesario para compensarlos. No demuestra todavía que WCT mejore por
sí solo a un modelo barato, ni que falle la estrategia. Se conserva el primer
candidato como resultado no conforme; el coste de una futura reparación y de
esta revisión pertenece al workflow, no desaparece al obtener un verde final.

## 7. Artefactos y siguiente paso

Directorio de sondas y outputs:
`/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-review.UuPr1u/`.
Los outputs de algunas comprobaciones de §4 permanecen solo en el transcript
de herramientas de esta revisión; no se presentan como logs archivados aquí.

| Artefacto local | SHA-256 |
|---|---|
| `challenge.py` | `ead057f7ec7cf75ee22bf8df6eb2825c944610ad4b1469901173d43d3b95a2d0` |
| `focal.lcov` | `000f88959eae9ce83af4838505ef24beef7310c0b0c8460b9ca94af2eaa75de0` |
| `crap.txt` | `04bd145730392cc2e6cc87254b7537a5c469a513bcb1cfea27cd3ac7ad236737` |
| `challenge-reverse-duplicate-order.txt` | `1f93cf5d9a5f472909dc0e04d8ac195228622b6de718af8df7011c90c6cbc002` |
| `challenge-feature-text-duplicate.txt` | `e78c3894f5f42d488694380a0c244bb111cc5ee4d761b14868bb745312213d72` |
| `challenge-feature-text-extra.txt` | `c20df4a35b1d8ed3743f861698cb04d005481f9da592a69a970e7e4efa575854` |

`challenge.py` es el artefacto ejecutable de la calibración local; su hash no
abarca toda la revisión humana ni lo convierte en un evaluador independiente.
Para repetir, desde el worktree original: `uv run --no-sync python
/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-review.UuPr1u/challenge.py
<variante>`, con los nombres de §4 codificados en el script. No correrlo sobre
una reparación fingiendo que conserva los mismos anclajes o candidate hash.

Siguiente acción recomendada: entregar al mismo coder ciego el
[prompt de reparación R1](PROMPT-CND-80B8-R1.md). Su envío por el usuario
autoriza **esa reparación**, no bless ni propuestas F01–F06. Registrar un
candidato hijo y repetir revisión sobre sus bytes; conservar esta acta y el
primer resultado. Pedir después challenge separado/humano antes del GO final,
sin revelar el modelo para elegir reglas más indulgentes o más duras.
