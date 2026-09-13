# AC1 — alcance y preflight de calificación

Estado: PAUSADO por petición humana; véase CIERRE-PARCIAL-2026-09-08.md.
No campaña aprobada. Base de implementación:
`932c835ac0eeb75010ec7a1071315b1c51f78eb6`. Cohorte asistida B3-MA-D;
coste y modelo no disponibles. Este documento no es un bless ni un GO.

## Por qué no basta el gate habitual

La política actual declara `paths.source: [src]`. Un gate de mutación verde
sobre ese alcance no califica las nuevas fuentes `tools/wct/accept/`.
La prueba focal debe incluir todas ellas, incluso parser trasladado, fachada,
transporte, validadores y plugin. Separar módulos no reduce este alcance.
La autorización de 54 supervivientes de P02a no se aplica a AC1.

## Riesgo observado en el instrumento

El arquitecto inspeccionó el mutmut 3.7.0 instalado: `run_stats` recoge
`mutmut._stats` en el teardown del proceso pytest padre; el bucle de ejecución
asigna exit 33 si no encuentra tests asociados a una función. El comodín `*`
fuerza reintentos, pero no evita esa condición. Las integraciones que cargan
el plugin únicamente en subprocess no bastan para registrar sus asociaciones.
Esto es un riesgo confirmado por lectura del motor, no un resultado todavía
medido de la campaña AC1.

Decisión: conservar integraciones por subprocess y añadir pruebas directas
del adaptador de hooks, con CallInfo/TestReport reales y aserciones sobre
recibos y eventos emitidos. No fabricar asociaciones ni excluir funciones
para ocultar un `no tests`. Comprobar las asociaciones observadas antes de
atribuir cobertura de mutación al plugin.

## Copia aislada propuesta

Tras congelar el candidato, crear una copia exclusiva bajo `build/tmp`, con
tools, src, tests, features y governance de ese candidato. La configuración
temporal de la copia, nunca la del checkout entregable, delimita:

```toml
[tool.mutmut]
source_paths = ["tools"]
only_mutate = ["tools/wct/accept/*.py"]
also_copy = ["src", "features", "governance"]
pytest_add_cli_args_test_selection = [
  "tests/unit/test_accept_pipeline.py",
  "tests/unit/test_accept_verdict.py",
  "tests/unit/test_accept_campaign.py",
  "tests/unit/test_accept_receipt.py",
  "tests/unit/test_accept_pytest.py",
]
pytest_add_cli_args = ["-m", "not property"]
use_git_change_detection = false

[tool.pytest.ini_options]
addopts = "-ra --strict-config --strict-markers"
testpaths = ["tests"]
markers = [
  "integration: tests crossing process or filesystem boundaries",
  "property: property-based tests",
  "acceptance: generated acceptance tests",
]
```

Usar el ejecutable existente, sin sync ni instalaciones, como
`mutmut run --max-children 1 '*'`. Registrar versiones, comando exacto y exit.
La configuración es receta pendiente de preflight, no garantía de ejecución.
No confundir esta selección focal con una corrida de toda la suite.
Antes de arrancar Python/mutmut, precrear `<copia>/mutants` y `<copia>/mutants/src`:
una ruta PYTHONPATH todavía inexistente puede quedar cacheada como no
importable. No precargar módulos originales ni reutilizar metas anteriores.

En esa copia, el PYTHONPATH de padre e hijos debe contener las rutas absolutas
`<copia>/mutants:<copia>/mutants/src`, nunca rutas relativas ni el candidato
original: mutmut cambia el cwd a mutants al ejecutar pytest. Usar PYTHONSAFEPATH=1,
temporales privados y entorno de protocolo limpio. Verificar en un hijo el
`__file__` del plugin y la propagación de MUTANT_UNDER_TEST; probar que un
mutante discriminante cambia realmente su comportamiento. Un resultado que
ejercita fuentes originales por error no acredita al mutante.

## Evidencia y puertas

1. Congelar hashes de fuentes, tests, configuración y runtime; conservarlos
   antes y después. No reaprovechar metas de una campaña anterior.
2. Preservar árbol generado e inventario de identidades extraído de su AST.
   Comparar conjuntos de IDs con resultados, no solo sus cantidades.
3. Registrar asociaciones, resultados brutos, supervivientes, no-tests,
   timeouts y fallos instrumentales con atribución explícita. El exit global
   del instrumento no sustituye esa reconciliación.
   El cierre exige cero supervivientes, no-tests (33/5), timeout (36/-24),
   suspicious, skipped, segfault, not-checked e instrumentales. Mutmut 3.7.0
   puede salir 0 con supervivientes y clasifica exit 3 como killed; un error
   interno de pytest no acredita por sí solo detección semántica. Conservar
   y revisar esos resultados antes de atribuirles una muerte válida. Esta
   cautela de calificación AC1 no modifica governance/thresholds.yaml.
4. Solo después de resolver mutación de fuentes: mutación de aceptación,
   LCOV nuevo/CRAP, DRY y tier full, en ese orden.
5. Revisar también el feature nuevo: un token mutado fuera del vocabulario
   del runner no demuestra un desacuerdo semántico. No redefinir unknown
   como pass ni traducir errores de lenguaje a SemanticMismatch para pasar.
   El ejemplo histórico y la feature AC1 son alcances distintos y se reportan
   separados. Los 42 handlers P02a siguen fuera de este incremento.

Las mediciones y el dictamen independiente se adjuntarán al expediente al
ejecutarse. Hasta entonces no se afirma cero supervivientes, cobertura focal
completa ni preparación para release.

## Sonda arquitectónica del refactor, previa a congelar candidato

El arquitecto cargó el pipeline de HEAD mediante `git show` y comparó sus
funciones parse_feature/ir_dry con las refactorizadas sobre los 30 archivos
`features/*.feature` presentes en esa corrida. Comparó IR completo y diagnóstico
de duplicación, o tipo/mensaje de excepción: cero diferencias, exit 0. Los
hashes de ambas fuentes permanecieron iguales antes y después de la sonda:

- parsing.py: `d2640e966e1f90d358754dd9bbc96eae11f46d43dc5ba5e6e2f5b601b889e6b5`.
- ir_checks.py: `d40dd19412cd6b71e060c2981b0d8d30fe4ac2268953f1cc2fc2a9a9ba3319d8`.

Es compatibilidad del corpus existente, no prueba exhaustiva del lenguaje,
no TDD retroactivo y no calificación del candidato final. La feature AC1 nueva
todavía no estaba presente. Sigue siendo necesaria la caracterización focal
y la revisión independiente sobre los bytes finalmente entregados.

## Control mínimo del falso verde

Antes de implementar, el arquitecto ejecutó el ejemplo con un runner que
únicamente hace `raise SystemExit(1)`: el motor de HEAD devolvió 6 killed,
0 survived y veredicto aprobatorio. No ejecutaba el SUT.

Repetido por el arquitecto sobre el núcleo congelado en
`build/tmp/b3-ma-ac1-r0/partial-review-1.sha256`, el mismo runner produjo
baseline invalid por recibo ausente, 6 planned, 0 killed, 6 not_run y dictamen
de fallo. No creó directorios mutation-*; la sonda y sus aserciones salieron 0.
Evidencia persistida por el producto en `build/tmp/wct-accept-na_8vlp2/`.
Esta reproducción acredita ese defecto concreto, no toda la campaña AC1.

## Revisión parcial independiente R0

El verifier revisó siete módulos del núcleo contra el manifiesto parcial
`23b7de76c7cfa69fc84fc651ca4be0a0ed6fb79463d401f41b517bcb8bc7bb96`.
Repitió 99 tests focales de recibos/veredicto/campaña: PASS, 2.22 s; los siete
hashes permanecieron intactos. No revisó aún el candidato final completo.

Hallazgos aceptados para reparación: comando vacío propagaba IndexError;
deadline anterior al lanzamiento omitía evidencia del intento; validación
incompleta de exits del baseline; TMPDIR no privado. Solicitó además controles
de límite combinado exacto/+1 byte y exit/logs/reap para timeout y exceso.
El coder preservó ocho rojos anteriores a esas reparaciones en su expediente.

La sugerencia inicial de resolver siempre el root se descartó como corrección
AC1: cambiaría la compatibilidad intencional de la API y runners temporales.
El contrato ahora aclara explícitamente cwd del invocador y la limitación
histórica del CLI. El verifier aceptó esa distinción. Esto no acredita que el
CLI funcione desde cualquier subdirectorio.

Las reparaciones requieren nueva identidad y nueva revisión; este acta parcial
no las da por aprobadas ni sustituye la secuencia de hardening.

## Suite global R0: rojo y atribución

El arquitecto ejecutó `uv run --no-sync pytest -q` con basetemp exclusivo
dentro de build/tmp, PYTHONPATH del candidato y su src, y TMPDIR privado.
Resultado: **552 passed, 6 failed, 156.46 s, exit 1**. Log íntegro:
`build/tmp/b3-ma-ac1-r0/root-suite.txt`. No se hicieron cambios de código
durante la corrida; las 18 entradas de source-review-2 siguieron idénticas.
El tiempo no es presupuesto emparejado, pues hubo revisión paralela.

Una regresión propia: `test_repo_introverted_ratchet_holds_baseline` mide
14 introverted frente a baseline 0. El coder recibió reparación de tests
sin elevar baseline, suprimir ni insertar aserciones vacías para contentar
al analizador. Los 163 focales verdes anteriores no cubrían este ratchet.
El manifiesto R0 se preserva antes de corregir; el siguiente debe ser hijo.

Otros cinco fallos se reprodujeron en el checkout sin AC1, HEAD 7ca0deafc56a,
cuyo árbol Git `d217bcf6a3b499537d0326447c399da836a9a8f1` es idéntico al
árbol base de main 932c835a:

- test_adopt_lifecycle::test_lock_without_git_in_source_raises_error.
- test_gate_config_wiring::test_unreadable_config_fails_naming_the_key.
- test_integrity::test_review_fails_closed_without_git.
- test_ratchet_record::test_record_single_metric_writes_only_that_baseline.
- test_redteam_tools::test_tool_case_catches_planted_defect[F9-a].

La repetición diagnóstica seleccionó esos cinco tests explícitamente: cinco
fallos, exit 1, 5.34 s. No equivale a ejecutar la suite baseline completa.
Evidencia en el checkout `build/tmp/beta3-execution.uW30FJ`, directorio
`build/tmp/ac1-baseline-evidence.EwgZN0/diagnostic.txt`. Una primera repetición
dio los mismos cinco fallos; su tee quedó dentro del basetemp que pytest
recreó, por lo que se repitió con el log fuera de esa carpeta. No atribuir
custodia persistente al primer log; su salida sí quedó en la conversación.

Sonda adicional sobre baseline, con GIT_CEILING_DIRECTORIES limitado al
basetemp: tres pasan y dos fallan (configuración y F9-a), exit 1, 5.35 s.
Evidencia: `build/tmp/ac1-ceiling-evidence.c46mpu/diagnostic.txt` en ese mismo
checkout. Esto confirma descubrimiento Git por ancestros en tres casos.
La lectura de find_root confirma que busca governance en los padres, incluso
si el fixture pretendía no tener configuración. La causa exacta de Semgrep
todavía requiere diagnóstico; no llamarlo una regresión AC1 ni darlo por verde.

Conclusión: existe un problema previo de aislamiento bajo la regla de
temporales build/tmp. No se corrige editando silenciosamente pruebas ajenas,
usando /tmp contra la regla ni reportando una suite global verde. Su resolución
se mantiene separada de la reparación del ratchet nuevo y debe quedar explícita
antes de calificar integración/release.

### Causa de F9-a y reparación de tests R1

El arquitecto ejecutó Semgrep 1.174.0 en el fixture baseline con JSON y verbose.
El comando productivo reportó exit 0, `paths.scanned=[]`, cero hallazgos y
exclusión de governance/src por patrones semgrepignore. La herramienta anunció
explícitamente cero targets. GIT_CEILING_DIRECTORIES no lo corrigió.
La misma sonda añadiendo solamente `--project-root .` escaneó
`src/victim/domain/io.py`, detectó `wct-io-in-domain` y salió 1. No se editaron
reglas ni archivos del fixture. La ayuda local de Semgrep define project-root
como frontera para descubrir ignores. Esto sustenta un incremento separado
de aislamiento y evidencia de targets: éxito del proceso con cero objetivos
no acredita detección del adversario plantado. No se cambió el gate AC1.

El coder reparó la regresión de trazabilidad en dos archivos de tests, sin
fuentes nuevas ni cambio de baseline. Manifiesto hijo R1 de 23 archivos:
`f0a6a119ff29c9d2b76bc8ebce81d046b79d3b3b8158d0511abf8b8d00955f60`.
Su corrida final: 177 passed = 163 AC1 + 14 test_ratchet_check, 24.66 s;
colección global 558; fast 7/7; introverted 0. Una primera corrida R1 falló
porque su expectativa del registro vacío ignoraba que PytestPluginManager
se registra a sí mismo; se corrigió la comparación antes/después y la ausencia
del observer WCT, preservando el control subprocess. No se clasifica como
flake ni defecto productivo. La revisión independiente de R1 está pendiente
al registrar esta sección; no hay suite global verde ni GO de integración.

## Preflight de mutación: primera ejecución detenida

El verifier repitió R1: 177 PASS/27.08 s, 23/23 identidades intactas; declaró
apto para iniciar mutación focal, no para integración. El arquitecto creó
`build/tmp/ac1-mutation-preflight.OVLNA8`, validó allí 23/23 hashes y lanzó
mutmut con la configuración anterior, rutas absolutas y máximo ocho workers.

Generó 14 archivos instrumentados, ignoró 61 fuera de scope y ejecutó los
163 focales durante stats: PASS/40.00 s. Después se detuvo con exit 1 porque
no encontró ninguna asociación test→función. **No ejecutó mutantes.** Log:
`build/tmp/mutmut-run-r0.log` dentro de esa copia. No convertir ese resultado
en cero supervivientes ni pasar a aceptación/CRAP/DRY.

Diagnóstico del arquitecto, en procesos nuevos sin escribir asociaciones:
las importaciones del árbol ya generado apuntan correctamente a mutants; una
llamada directa registra un hit, y PytestRunner.run_stats sobre
test_accept_pipeline registra 19 funciones y 190 asociaciones (26 PASS).
Una sonda separada confirmó que Python cachea como None las rutas PYTHONPATH
inexistentes al arrancar; crearlas después no limpia esa entrada, mientras
invalidate_caches sí lo hace. La primera receta no precreó mutants. Esto
sustenta corregir el bootstrap y verificarlo en una copia nueva; no es defecto
atribuible al coder ni evidencia de ausencia real de tests. El fallo inicial,
su árbol generado y sus metas se conservan, sin editar el runtime instalado.

## Segunda campaña instrumental: interrumpida, no calificable

La copia `build/tmp/ac1-mutation-r1.qGjB9k` preserva R1 (23/23 hashes).
Precrear mutants corrigió el bootstrap del objetivo: el verifier acreditó
60/60 funciones asociadas, 2.336 aristas, 163 tests y 1.481 IDs únicos;
una sonda confirmó importación instrumentada y activación real del mutante.
Sin embargo, mutants/src no existía al arrancar Python: no queda acreditada
la procedencia aislada de las dependencias src, aunque sus bytes coincidían.

Incidente instrumental registrado el 2026-09-08 en esta campaña local:
dos procesos fallaron en pytest_sessionfinish/cleanup_dead_symlinks por
FileNotFoundError sobre el pytest-current compartido. Evidencia:
`build/tmp/mutmut-run-r1.log` dentro de la copia, aproximadamente en los
contadores 447 y 932. No hubo reintento que acreditase esos IDs. Es una
carrera de infraestructura, no un defecto demostrado del producto ni un
test flaky individual identificable con el log intercalado. Mutmut trata
esos exit 1 como kills: el contador no distingue su causa.

El arquitecto interrumpió el proceso de esa copia tras verificar PID y cwd.
El cierre devolvió exit 0 al manejar la interrupción: NO significa éxito.
Inventario parcial conservado: 1.209 exit 1, 148 exit 0 y 124 null = 1.481.
No descontar dos kills ni acreditar los restantes: no hay atribución causal
suficiente. Los supervivientes sirven para orientar tests, no como resultado
calificado; tampoco el throughput parcial acredita presupuesto.

La próxima campaña usará otra copia fresca, precreará TODAS las rutas de
PYTHONPATH (mutants y mutants/src) antes de Python y ejecutará con
`--max-children 1`. No se modifican mutmut, sus metas ni los umbrales.
Se repite el inventario completo, no solo los supervivientes anteriores.
La responsabilidad de esta corrección de receta es del arquitecto.

R2 añade 33 casos de tests sobre fuentes intactas: colección global 591,
focal más ratchets 210 PASS, fast 7/7 e introverted 0, según el coder.
Manifiesto histórico R2:
`78441605767e5f3d20f437ad779624c3de178042f91ba6f676752e43965ea63f`.
Revisión independiente solicitada. Ningún nuevo kill se atribuye todavía
a esos refuerzos. Un refuerzo adicional de transporte PYTEST_PLUGINS se
prepara en un único archivo separado; tendrá manifiesto hijo, no reemplazará R2.

## Candidato R3 y repetición serial

R3 incorpora dos controles de preservación de PYTEST_PLUGINS en baseline y
mutante, con receipt válido y observación del entorno real del hijo. No carga
plugins ficticios ni acredita por ello integración real de esos plugins.
El entorno padre debe permanecer intacto. Todas las 18 fuentes/fixtures del
manifiesto source-review-2 permanecen idénticas.

Manifiesto R3 (23 archivos):
`9774c49f287bb107ba3bbf3caf1ce821dccbaed2db0b710abec8d925ab19f68e`.
Copia exclusiva `build/tmp/ac1-mutation-r2.hObK4N`: 23/23 verificados.
Configuración temporal:
`29cfc3e5864f2ef925a60c5f4e09a5a9f75fac0a2ecb57fa63c3e97397432182`.
Receta run-mutation.sh:
`a47e245c659c84de712fbb92d5c597d8d67b03624ce1658cdd2ce6d56ce4750d`.
La campaña serial comenzó el 2026-09-08 a las 07:24:20 UTC; Python 3.13.14,
mutmut 3.7.0, log build/tmp/mutmut-run-r2.log dentro de esa copia.
La revisión independiente final corre sobre el candidato inalterado; iniciar
la medición no concede GO ni sustituye su dictamen.

El verifier aprobó después R3 para campaña serial, no integración: 23/23
hashes antes/después, 18 rutas fuente/fixtures/feature sin cambios; 212
focales colectados y PASS/27.06 s, fast 7/7 sin SKIP/FAIL/ERROR. Confirmó
que los controles nuevos observan el SUT, no mocks ni coincidencias cosméticas.
En la copia verificó AST = meta = spans: 1.481 IDs únicos, cero diferencias;
60/60 bases asociadas, ninguna vacía, 2.880 aristas, 198 tests con duración
y 197 asociados. La sonda de procedencia resolvió tools y src dentro de la
copia y registró dos trampolines. Esto acredita el preflight, no el resultado
final de todos los mutantes ni la ausencia de futuros fallos instrumentales.

## Revisión concurrente y siguiente candidato, sin alterar R3

Mientras termina la campaña se revisan únicamente módulos cuyos metas ya
no tienen resultados null. Las revisiones parciales VALIDACION, PLUGIN y
PARSER de este directorio conservan fecha, IDs y reservas; no sumarlas como
dictamen global ni convertir variantes de diagnóstico en equivalencias
literales. Las excepciones siguen sin autorización.

Se preparó `build/tmp/ac1-next-tests.fXt7qn` separada del checkout y de la
campaña. Solo admite refuerzos de tests: activación del observer mediante el
hook público, escenario esperado ausente, causa de hash incorrecto y escritura
UTF-8 bajo locale ASCII. Son contratos ya exigidos, no cambios de producto.
El último caso responde a una reproducción independiente: retirar encoding
explícito causa UnicodeEncodeError bajo LC_ALL=C/PYTHONUTF8=0; no se fuerza
un fallo para el alias UTF-8 que conserva comportamiento. El coder no reclama
un rojo TDD propio para esa reproducción ajena. Fuentes y candidato R3 quedan
congelados; la copia siguiente no hereda calificación por contener más tests.

## Riesgo de la próxima puerta de aceptación

Análisis separado del agente de preparación, todavía sin campaña calificada:
la feature AC1 tiene 6 filas por 8 columnas (48 celdas). El operador léxico
actual produce tokens fuera del vocabulario en baseline/mutation/verdict,
18 celdas en total. Esos rechazos no son detección semántica.

Un perfil futuro de operadores tipados podría intercambiar pass/mismatch
para baseline; mismatch/pass y errores/mismatch para mutation; pass/fail
para verdict; y valores 0/1 para cantidades. Es una propuesta, no autorización
para implementar ni un resultado de 48 kills.

Incluso con esos operadores, la segunda fila bloquea en el baseline: cambiar
el modo de un mutante que jamás se ejecuta no cambia el comportamiento. Por
lectura se espera al menos una equivalencia; una supervivencia allí no prueba
un defecto del motor. El umbral vigente tampoco autoriza ignorarla. Se deben
reconocer ambas responsabilidades: el coder implementa el contrato recibido;
el arquitecto aprobó esta tabla y debe resolver su compatibilidad con el
criterio de mutación. No atribuir ese coste de rediseño al modelo implementador.
Se deben
conservar inventarios completos y separados del operador histórico y de todo
operador futuro, con hashes y vínculo a las celdas originales. Resolver esa
puerta exige diseño revisado o adjudicación humana específica sustentada;
nunca trasladar las 54 excepciones de P02a, borrar IDs ni llamar killed a
errores de vocabulario. Esta advertencia impide declarar listo el incremento
para integración solo porque el ejemplo histórico tenga seis kills válidos.
