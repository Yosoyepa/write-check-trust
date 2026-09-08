# Revisión ciega R1 — SH-P01 / CND-74E0

**Dictamen: CONFORME_AL_CONTRATO en el alcance técnico de SH-P01.**

Recomiendo aceptar técnicamente esta reparación, completar la trazabilidad
documental indicada abajo y pasar a la revisión humana del diff. No se exige
otro refactor. No es bless, autorización de PR/publicación ni cierre de beta.3.
No se encontraron defectos HIGH/MEDIUM en el código del candidato examinado.
Quedan aclaraciones de expediente y un seguimiento LOW del binding.

## 1. Identidad, autoridad y cegamiento

| Campo | Valor |
|---|---|
| review_id | SHP01-REVIEW-CND-74E0 |
| task / contract / mode | SH-P01 / `sh-p01/1` / SH-D |
| run / coder / candidate | SHR-27687E / COD-CA7A / CND-74E0 |
| parent_candidate_id | CND-80B8; conserva su dictamen REQUIERE_CORRECCION |
| base | `8de9107184288f1aa72c9578a14913686c47ad7c` |
| candidate_manifest_digest | `909e58a71e9477ccc25822823f8b3615225b68fec713cf03e22be4ccabc09cb4` |
| calidad congelada | 2026-09-07T23:01:32Z, antes de revelar modelo o coste |
| reviewer | arquitecto de esta tarea, distinto del autor del candidato |
| independencia | mismo host; arquitecto autor de la SPEC y del feedback R1; no hubo otro reviewer humano/agente en esta corrida |
| asistencia al coder | diagnóstico previo; el arquitecto no escribió el fix ni cambió tests/producto |
| coste/modelo | unavailable / oculto por decisión del custodio |

Worktree: `/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-74E0`,
rama `codex/beta3-sh-p01-identidades-r1`. El diff sigue limitado a cuatro
archivos nuevos, 787 inserciones. El padre conserva sus cuatro hashes y el
árbol documental compartido conserva su diff trackeado previo. Sin cambios
del reviewer a producto, tests, feature, gobernanza o registros del coder.

Se leyeron el [handoff R1](../runs/SHR-27687E-CND-74E0.md), el
[dictamen del padre](REVIEW-CND-80B8.md), el
[encargo R1](PROMPT-CND-80B8-R1.md), P01/Gherkin y las reglas vigentes.
Los digests normativos siguen coincidiendo. Las guías locales WCT de review,
test-honesty, CRAP, DRY, ratchets y arquitectura determinaron comprobar el
scope del motor y la sensibilidad de tests, no solo sumar gates verdes.

La revisión es cooperativa, sin aislamiento hostil acreditado. Los hashes
identifican bytes, no autentican su origen ni sustituyen custodia externa.
No se consultaron settings, cuentas, identidad, tarifas o telemetría del modelo.

## 2. Resultado de R01–R05

| Hallazgo anterior | Resultado de esta revisión | Motivo y evidencia |
|---|---|---|
| R01 — CRAP | **Resuelto** | motor real 0.1.1, LCOV focal nuevo: 9 funciones, máximo 5.0; las antiguas funciones de 10/7 quedan en 2/4 |
| R02 — orden sin protección | **Resuelto** | variante de duplicados descendentes: 1 failed/57 passed, precisamente I21b; invertir gaps: 2 failed/56 passed; original pasa |
| R03 — filas/escenarios extra | **Resuelto para los escapes encargados** | binding legacy en memoria: los 3 negativos fallan, positivo pasa; cardinalidad, unicidad y escenario extra quedan discriminados |
| R04 — identidad/conteos | **Identidad y selección actuales resueltas** | manifest actual reproducible; conteos distinguidos; causa histórica del digest anterior no acreditada, aclaración LOW L01 |
| R05 — cobertura/ratchets | **Verificación completada** | LCOV global entregado coincide con su hash; el reviewer corrió `--require all`: exit 0, 10/10; el coder solo había reportado 1/1 |

### Diseño de la reparación

`identities.py:89–210` divide conteo, vacíos, duplicados, diferencias y resolución
de estado en responsabilidades reconocibles. `_STATUS_PRECEDENCE` contiene
tres reglas explícitas de §4, no un registry extensible ni una tabla opaca para
evitar el analizador. Se conservan API, tipos inmutables, todos los diagnósticos,
orden y pureza stdlib. No se añadió IO, CLI, dependencias o esqueletos de P02.

No penalizar por sí solo el paso de 4 a 9 funciones: se pidió cumplir CRAP sin
debilitar criterios, y los helpers describen operaciones del contrato. Tampoco
afirmar que toda la complejidad desapareció: la suma de CC de las funciones
medidas es 26 en ambos candidatos. La mejora acreditada es el cumplimiento del
límite por función y una descomposición revisable, no una reducción universal
del riesgo. El módulo pasa de 54 a 59 statements medidos y de 20 a 18 ramas.

`__all__` sigue conteniendo exactamente los tres símbolos contratados; es
legítimo. La tabla parametrizada sigue siendo matriz de cobertura, no un
objetivo de deduplicación. Los nombres y dependencias internos se inspeccionaron
manualmente: los contratos arquitectónicos de `src/example` no cubren tools
por inferencia.

## 3. Evidencia reproducida por el arquitecto

Se usó el venv ya preparado del padre con `UV_PROJECT_ENVIRONMENT`,
`PYTHONPATH` al hijo y `uv run --no-sync`, sin instalar ni sincronizar paquetes.
Una sonda comprobó que `identities`, `tools.wct.cli` y `gate.runner` se cargan
desde **CND-74E0**. Python 3.13.14, pytest 9.1.1, crap4py 0.1.1. Esto acredita
resolución del árbol en la revisión, no aislamiento ni un filesystem readonly
forzado para el venv compartido.

| Comando/control | Resultado propio | Alcance |
|---|---|---|
| `pytest --collect-only -q` | **405 collected** | selección completa actual |
| `pytest -q` | **405 passed, 83.21 s** | nueva corrida completa, no el log del coder |
| Focal con branch coverage | **58 passed; 59 statements/18 ramas; 100 %** | módulo nuevo, LCOV de revisión separado |
| `crap4py tools/wct/evidence --lcov <review>/focal.lcov --max-crap 6` | **exit 0; máximo 5.0** | nueve funciones del módulo real |
| `wct dry --json <dos archivos de evidence>` | **0 candidatos, 9 unidades** | duplicación interna de la pieza |
| Motor DRY con archivos de src + tools/wct | **71 archivos, 272 unidades, 0 errores; ningún candidato involucra evidence/** | 19 pares en el resto; no se afirma cero duplicación global |
| `wct dry --json` | 0 candidatos, 3 unidades | scope histórico de src, no prueba de la pieza |
| `wct gate --tier fast` | **7 PASS, 0 SKIP** | tier completo |
| `wct gate --tier commit` | **20 PASS, 1 FAIL** | único rojo de este tier: G-META-1; G-TEST 89.025 s |
| `wct integrity check` | **exit 1, exactamente dos rutas** | `tools/wct/evidence/__init__.py` e `identities.py`, nuevas y protegidas |
| `wct ratchet check --require all` | **exit 0, medidas 10 de 10** | completa el comando omitido por el coder; ver procedencia del LCOV abajo |
| `wct introvert --json <test de identities>` | 7 extroverted, 3 questionable | los negativos se revisaron manualmente y se sometieron a variante legacy |
| `lint-imports` / archmetrics | 4 kept, 0 broken; sin ciclos/violaciones | src/example, zonas legacy dentro del baseline |
| `mutation_sites(identities.py)` | **79**, frente a límite 100 | proxy AST explícito de tools; no mutantes ejecutados |
| `git diff --check` | exit 0 | incluye los archivos nuevos por intent-to-add |

Los tres `questionable` son los negativos de binding con `pytest.raises`
alrededor del helper local; el detector no reconoce una aserción trazada.
No se clasifican como tests malos por esa heurística: el cambio legacy hace
fallar realmente los tres. No se necesita añadir aserciones artificiales para
complacer al detector ni modificar su ratchet.

### Procedencia de cobertura, sin sobreafirmar frescura

El LCOV focal recién producido por el reviewer es byte-idéntico al focal del
coder: SHA-256 `15adcdb0479cfc7c424004fe8d156f2dc33ddddc988d9de904069f62bb78246f`.

El LCOV global consumido por `--require all` es **el entregado por el coder**,
SHA-256 `cdccbe33f605aae94ca052d56f355c4effc3e19f80d6a12f56d1d75363ae45e0`,
igual antes y después de esta revisión. Su log registra receta global sin
property: 404 passed, 1 deselected, 113.61 s. Esa corrida no se atribuye al
reviewer, que no reemplazó ni regeneró el LCOV global. El baseline vigente es
74.5, `higher_is_better`; no cambió. El 10/10 verifica presencia/validación y
umbrales con ese artefacto, no procedencia criptográficamente autenticada.

Para CI sobre un futuro SHA, producir nuevamente el LCOV global y consumirlo
en el mismo job conforme al workflow vigente. No trasladar automáticamente el
10/10 de este worktree a un commit diferente.

## 4. Calibración manual y control válido

Las variantes se cargan en memoria, en procesos separados; se ejecuta el
archivo focal real del hijo sin editarlo. El script comprueba antes el hash
del módulo. Los temporales de las sondas están en build/tmp. No son mutmut,
G-MUT, G-ACCEPT-MUT ni una certificación de G1b.

| Variante | Resultado |
|---|---|
| Original | 58 passed |
| Duplicados descendentes | 1 failed / 57 passed |
| Gaps descendentes | 2 failed / 56 passed |
| Binding legacy sin validaciones | 3 failed / 55 passed |
| Comparar solo tamaños | 6 failed / 52 passed |
| Deduplicar antes de validar | 6 failed / 52 passed |
| Ignorar executed | 25 failed / 33 passed |
| Vacío como match | 2 failed / 56 passed |
| Strip de identidades | 2 failed / 56 passed |
| Solo primera causa | 9 failed / 49 passed |
| Rechazar todo | 12 failed / 46 passed |
| Implementación alternativa diagnóstica | 58 passed |

Se escribió una alternativa **solo en la sonda de revisión**, usando conteos
por tupla, predicados de pertenencia, ordenación final y decisión de estado
desde las entradas, sin llamar los helpers ni el algoritmo del candidato.
Usa los tipos públicos de salida para poder correr los mismos tests literales.
No es un fix facilitado al coder ni un juez externo independiente.

Además se contrastaron ambos algoritmos en **64 000 combinaciones**: todas las
tuplas de longitudes 0–3 sobre el alfabeto `{vacío, A, B}` en los tres argumentos;
cero diferencias. Es un dominio finito declarado, no prueba exhaustiva para
cualquier string/tamaño ni 64 000 tareas de un benchmark. Los tests literales
de opacidad/Unicode siguen siendo controles adicionales.

## 5. Aclaraciones y seguimiento, sin otro refactor obligatorio

### SHP01-R1-L01 — LOW: la causa histórica del digest no se reproduce

El nuevo manifest `909e58a7…` **sí es correcto**. La explicación añadida por el
coder para `de207e0d…` del padre dice que provino de rutas absolutas. Al repetir
la tubería con las cuatro rutas absolutas del padre, en el orden declarado y
LF final, se obtiene:
`01a1c071ed5f7e8f904c8a9adce381352126cfbaaf3ff1846ed30397cf618070`.
Sin LF final resulta:
`fae236bba34330bbeb6c9d25f81b3b174d6506ef04f8172430d6283bfb674c62`.
Ninguno es el digest histórico declarado.

**Decisión:** en una addenda nueva, aportar el comando/bytes originales que
expliquen el hash o marcar la causa como no confirmada. No inventar otra causa
ni editar el registro anterior. Owner: coder para la aclaración; arquitecto
para el cotejo. No es evidencia de alteración del candidato actual ni motivo
para cambiar su código. La corrección de la identificación actual está probada;
la afirmación causal histórica es lo que no debe darse por resuelto.

### SHP01-R1-L02 — LOW: binding de filas no equivale a identidad completa del feature

En `tests/unit/test_evidence_identities.py:430–480`, el helper valida cantidad
de escenarios/filas, unicidad y pertenencia de casos; el positivo verifica
nombres y celdas. No comprueba el flag `outline` ni el contenido de los pasos.
Dos sondas de texto leído por el parser real lo muestran: cambiar
`Scenario Outline:` a `Scenario:`, o sustituir el paso When por otro texto,
deja **58 tests verdes**.

**Por qué no reabre R03 ni bloquea este candidato:** la entrega actual conserva
el feature aprobado verbatim, comprobado por lectura y hash; R03 encargó
cerrar duplicados y escenarios extra, y ambos escapes quedaron discriminados.
No se exige retrospectivamente automatizar toda la auditoría textual como
condición nueva de esta reparación. Sí queda prohibido describir el binding
como prueba completa de semántica, verbatim o ejecución de esos pasos.

**Seguimiento propuesto:** arquitecto, ampliar el contrato del binding/ensamblaje
en un incremento separado: clase de escenario, pasos/parametrización y campos
contratados, con negativos nuevos y positivos válidos. P06 conserva la puerta
de ejecución real. No añadir aquí un handler ficticio ni generar tests que
solo aprueben datos autorreferenciales. Estado: propuesta, sin issue remoto
creado ni autorización de implementación.

### SHP01-R1-L03 — INFO: atribuir el 10/10 a quien lo ejecutó

El encargo pidió `--require all`; el coder ejecutó y reportó solo
`--require coverage-total`. La omisión queda subsanada por el comando del
reviewer, no por reescribir su historial. Añadir la referencia a esta acta en
el expediente basta; no pedir otra inferencia de código ni inventar una
corrida propia del coder. Registrar su omisión alimenta la mejora de recibos
y matrices de obligaciones del harness.

## 6. Qué enseña R0 → R1 sobre el caso de uso

| Señal | Padre CND-80B8 | Hijo CND-74E0 |
|---|---|---|
| Dictamen técnico | REQUIERE_CORRECCION | CONFORME_AL_CONTRATO, alcance P01 |
| Máximo CRAP medido de la pieza | 10.0 | 5.0 |
| Funciones por encima de 6 | 2 | 0 |
| Cobertura focal | 100 %, 54 statements/20 ramas | 100 %, 59 statements/18 ramas |
| Casos focales | 54 | 58 |
| Orden descendente de duplicados | no detectado | detectado por I21b |
| Inventario extra del feature | escape de binding | negativos discriminantes de cardinalidad/unicidad/escenarios |
| Identidad agregada actual | no reproducible según fórmula declarada | reproducible |
| Ratchet global requerido | LCOV ausente | LCOV entregado y consumo verificado; 10/10 por reviewer |

Este es **un caso de desarrollo asistido, con una reparación y dos revisiones
del arquitecto**, no una comparación causal de modelos/harnesses. Los tiempos
83.21/89.21/96.27 s no son un presupuesto emparejado ni demuestran aceleración.
No comparar tasas de detección con denominadores distintos de variantes/tests.
El resultado del padre no se borra porque el hijo pase.

Se acredita una mejora concreta de conformidad y sensibilidad tras feedback.
No se acredita todavía ahorro económico, autonomía, calidad universal ni
superioridad del modelo secreto. Cuando el custodio entregue recibos, imputar
coder R0/R1, revisión, diagnóstico y coordinación al workflow completo, sin
presentar solo el coste de la última respuesta exitosa.

Prioridades de aprendizaje: F01 (scope efectivo sobre tools), F03 (recibos y
matriz completa), F04 (sensibilidad por cláusula) del acta anterior; añadir a
F04 el límite L02. F01–F06 siguen siendo propuestas separadas, no código
implementado en P01 ni reglas nuevas aplicadas retroactivamente a este lote.

## 7. Artefactos, límites y siguiente puerta

Directorio de revisión:
`/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-r1-review.dbuKI7/`.
Contiene `r1full.txt`, `r1collect.txt`, `r1cov.txt`, `r1crap.txt`, `r1commit.txt`,
`r1fast.txt`, `r1check-ratchets-all.txt`, controles de DRY/arquitectura,
`challenge-*.txt`, `focal.lcov` y el snapshot del diff.

- `challenge.py`: SHA-256 `3a2a85e2cfcde77a7a4260b529f0dda14b3c52401d72d089ec2a99b91b0a52a4`.
- `candidate-CND-74E0.patch`: SHA-256 `635adce19c4c03c33cb509f5a3237cc47500c06061f44c5c69ee96d0c5072c87`.
- Los cuatro hashes de archivos son los del handoff R1 y se volvieron a
  verificar al final; agregado `909e58a7…` sin drift.

Incidentes del **reviewer**, no del coder: dos invocaciones DRY con directorios
devolvieron exit 2 porque esta CLI espera archivos; se conservan sus outputs y
se corrigió la invocación. Una llamada de orquestación tuvo un error de sintaxis
antes de ejecutar comandos; se corrigió. Ninguno se convirtió en PASS ni se
atribuyó a un defecto del candidato. No se observó un flake en las pruebas
completadas; no se ejecutó orden aleatorio para afirmarlo en general.

No ejecutados por el reviewer: tiers full/pr completos, mutmut, aceptación
ensamblada/mutada P06, orden aleatorio, SBOM, release, ni productor global de
coverage repetido. Las exclusiones de P01 no cierran G1b o las demás piezas.
Los artefactos build/tmp son locales y gitignored; conservarlos antes de
limpieza. Este fichero no crea custodia inmutable por sí mismo.

**Siguiente puerta:** [cierre documental de P01](PROMPT-CIERRE-CND-74E0.md),
lectura humana/separada del diff y decisión explícita del usuario sobre PR y
bless. No dar bless por analogía con aprobaciones de PRs anteriores, ni abrir
una PR o publicar beta.3 como consecuencia automática de este dictamen.
