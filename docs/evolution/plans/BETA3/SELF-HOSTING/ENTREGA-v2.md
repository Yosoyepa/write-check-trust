# sh-delivery/2 — Contrato de entrada, evidencia y entrega

Fecha: 2026-09-07. Consumidores: arquitecto prepara; coder aplica; reviewer
comprueba; humano decide promoción. Se aplica a **nuevos encargos** que lo
referencien. No cambia el dictamen ni el contrato `sh-p01/1` de CND-74E0.
No reemplaza AGENTS, política ni la aprobación de escenarios de cada pieza.

## 1. Antes de escribir: recibo de entendimiento obligatorio

El arquitecto entrega un paquete cerrado. El coder devuelve esta ficha con
valores concretos antes del primer cambio; «leído» no la sustituye:

| Campo | Contenido comprobable |
|---|---|
| Identidad | task/run/candidate/parent ciegos; SHA base; hashes de contrato, feature y calificador; versiones de entrega/molde |
| Producto | Una frase de comportamiento y una de lo que NO acredita |
| Frontera | Lista exacta de rutas editables; salidas temporales aparte; controles y contratos no editables |
| Reutilización | Búsqueda por comportamiento y APIs existentes; por qué hace falta cada módulo nuevo |
| Verificación | Ruta → regla/capacidad → argv real → denominador → artefacto → resultado esperado |
| Tests | Requisito → caso literal bueno → variante mala plausible → aserción que debe fallar |
| Entorno | cwd, ejecutable, versiones, raíz de imports, locks y variables operativas no secretas |
| Paradas | Datos o autoridad faltantes; gates fuera de alcance; discrepancia de herramientas; no improvisar excepciones |

Si falta API, selección, salida, permiso o Gherkin aprobado, el coder entrega
esa discrepancia **sin implementar**. No completa por su cuenta decisiones del
specifier. El humano puede devolver el paquete o aprobar su versión revisada.
No se exige revelar modelo/proveedor/precio para entender el contrato.

## 2. Alcance real de la medición

- Una regla que aplica al código sigue aplicando si un gate no lo escanea.
  Enumerar cada fuente cambiada y mostrar quién la mide; «commit PASS» no
  demuestra CRAP/mutación/arquitectura de `tools/wct` si apuntan al ejemplo.
- Cobertura focal y global son productos distintos, con selecciones, rutas
  y denominadores separados. Cobertura 100% no implica tests discriminantes.
- CRAP mínimo posible es CC cuando la cobertura es completa: CC > 6 no puede
  cumplir CRAP ≤ 6 añadiendo tests. Dividir por responsabilidades coherentes;
  no esconder ramas en datos, supresiones o abstracciones sin consumidor.
- Declarar sitios estimados, mutantes generados y mutantes realmente ejecutados
  como magnitudes distintas. Desafíos manuales no son una campaña exhaustiva
  de mutmut. No ampliar `paths.source` ni editar baselines para completar una
  tabla de comprobaciones.
- Copiar argv de la ayuda/builder vigente y contrastarlo. El texto de una regla
  puede mencionar una opción que el CLI no implementa: reportar el desacuerdo,
  usar solo una alternativa comprobada y no atribuirle el alcance ausente.
  En este corte `wct dry` acepta archivos; no suponer que una carpeta o una
  opción `--against` constituyen un escaneo válido.

## 3. Tests que distinguen implementaciones

1. Expectativas literales aprobadas, independientes del SUT. No generar el
   expected llamando al propio algoritmo que se intenta verificar.
2. Para cada invariante, registrar al menos un caso correcto y un defecto
   plausible. Verificar que el defecto falla por la aserción pertinente y
   que el correcto sigue pasando. Registrar también intentos fallidos de sonda.
3. Ejemplo de orden: un solo duplicado no distingue ascendente de descendente.
   Usar al menos dos identidades repetidas y entrada permutada; comprobar toda
   la salida y precedencia, no solo cantidad o primer hallazgo.
4. Ejemplo de inventario: igual N con sustitución, duplicados con N conservado,
   vacío, faltantes y sobrantes. Una conversión temprana a set/dict puede
   eliminar precisamente el defecto que debe detectarse.
5. Los desafíos se ejecutan en copias aisladas operativamente; no se altera el
   árbol congelado. Un error de sintaxis/import no prueba sensibilidad semántica.
6. Respetar selección por marcas de los productores y coleccionar después de
   editar tests. Guardar nodeids reales; no reconstruirlos suponiendo orden de
   parametrización. Subconjunto focal no se presenta como suite/gate completo.

## 4. Qué demuestra un binding de Gherkin

Antes del código, enumerar los campos exigidos: nombre de feature, inventario
y nombre de escenarios, tipo (`Scenario`/`Scenario Outline`), secuencia/texto
de pasos y parámetros, encabezados, filas, unicidad, IDs y celdas. Para cada
campo declarado protegido debe existir un positivo y una alteración que falle.
No colapsar filas a un diccionario antes de comprobar cardinalidad/unicidad.

Separar expresamente tres niveles:

- **Verbatim/sintaxis:** bytes del bloque aprobado y parseo compatibles.
- **Binding de contrato:** campos concretos cotejados; no ejecución.
- **Aceptación ejecutada:** handlers productivos, invocación y resultado terminal
  de cada caso/filas esperadas; un parser o conteo de funciones no lo sustituye.

El paquete de una pieza puede no prometer los tres niveles, pero debe decirlo
antes de implementarse. El binding actual de P01 cubre inventario/nombres/filas
y celdas; no tipo de escenario, texto de pasos ni ejecución. R1 no se reabre
por esta regla futura. La narrativa del Gherkin de este repo sigue en comentarios
cuando su parser lo requiere; no modificar un bloque aprobado para obtener verde
sin nueva decisión del specifier.

## 5. Recibos, frescura y atribución

Cada corrida conserva ID, actor, propósito, UTC inicio/fin, cwd, argv como lista,
variables relevantes no secretas, ejecutable/versiones, identidad del árbol y
contexto, selección, exit code, stdout/stderr sin resumir, rutas y SHA-256 de
artefactos. Hacer una corrida adicional no borra una que falló o se interrumpió.

El handoff separa: ejecuté / otro actor ejecutó / inspeccioné / infiero / no
verificado. Una hipótesis causal se etiqueta como tal hasta reproducir la
combinación exacta de bytes, cwd y argv que produjo el síntoma.

Para ratchets globales del corte actual, el productor real es:

```bash
uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property"
uv run wct ratchet check --require all
```

La segunda línea solo consume después de que la primera termine con éxito.
Ejecutar secuencialmente, con la misma identidad de código/config/tests, sin
otro productor concurrente y sin copiar LCOV focal encima del global. Registrar
las dos corridas y el hash del LCOV entre ambas. Si cambia un input pertinente,
repetir productor y consumidores; que el archivo exista no acredita frescura.
En CI actual se exigen `coverage-total,docstring-coverage`; no atribuirle 10/10.

El artefacto de otro actor puede inspeccionarse/reconsumirse, pero debe citarse
su productor original y no afirmar «regeneré». El protocolo de misma corrida es
evidencia operativa; no es autenticación frente a procesos hostiles del mismo
usuario. Antes de nuevos comandos confirmar receta y ámbito vigentes.

## 6. Identidad de candidato sin ambigüedad de rutas

El paquete congela la lista ordenada de rutas de producto, pruebas y feature.
No mezclar ese digest con hashes de contexto, logs, LCOV o SBOM. Para nuevos
paquetes, la lista usa rutas POSIX relativas a la raíz del candidato, orden
lexicográfico de bytes UTF-8; declarar cualquier excepción histórica.
No permitir rutas absolutas, `..`, controles, barra inversa ni saltos de línea
en ese formato de manifiesto. Cualquier ruta no representable requiere otro
formato aprobado, no normalizarla silenciosamente.

Serialización: por ruta, hash SHA-256 de los bytes originales, dos espacios
ASCII, ruta exacta, LF; UTF-8 sin BOM y LF final. El agregado es SHA-256 de esos
bytes del manifiesto. Conservar la lista, el manifiesto y el comando, no solo
el agregado. Verificar cada archivo y la igualdad de lista; un hash solo no
certifica procedencia ni que esa sea toda la superficie que debía medirse.

P01 conserva su orden histórico explícito, no el nuevo orden por defecto:

```bash
sha256sum -- tools/wct/evidence/__init__.py tools/wct/evidence/identities.py tests/unit/test_evidence_identities.py features/wct-evidence-identities-001.feature
```

Se ejecuta desde la raíz de CND-74E0. Hashear esa salida exacta produce
`909e58a71e9477ccc25822823f8b3615225b68fec713cf03e22be4ccabc09cb4`.
Cambiar cwd y anteponer `build/tmp/...` cambia la serialización, aunque los
archivos sean idénticos. El error R0 fue ese prefijo relativo, no rutas absolutas.

## 7. Custodia, frontera Git y autoridad

- Separar lista exacta de producto, documentos, evidencia publicable y artefactos
  locales. No usar `git add -A` ni «todo el directorio y lo relacionado».
  Comparar conjunto staged con allowlist antes de commit; revisar también bytes.
- Un archivo bajo `build/tmp` y su hash en Markdown no constituyen custodia
  durable. Antes de limpiar, copiar al destino aprobado, verificar inventario y
  hashes y registrar responsable/retención. Sin esa copia, estado `local-only`;
  no declarar replay asegurado ni borrar la única evidencia.
- Revisar secretos/recibos de proveedor/holdout antes de publicar. La evaluación
  ciega no se rompe para preparar una PR. No subir evidencia privada por defecto.
- Un verificador no puede corregir y autoaprobar los bytes en la misma pasada.
  Registrar autoría del contrato y asistencia; una revisión distinta del coder
  no implica independencia de supuestos ni un experimento controlado.
- Commit/push y PR documentan el candidato. Bless humano refiere PR real y diff
  exacto, y es separado de merge/release. Rojo de integridad esperado se declara;
  ningún otro rojo se convierte en excepción por estar cerca del cierre.

## 8. Checklist que acompaña al handoff

- [ ] Recibo de §1 y contrato de pieza/Gherkin aprobados, sin campos pendientes.
- [ ] Matriz de alcance explícita y controles discriminantes con salidas reales.
- [ ] Colección, suite, focal, property y gates distinguidos; ninguno inventado.
- [ ] Verbatim y niveles de binding/aceptación declarados y comprobados.
- [ ] Manifiesto reproducible, producto/contexto/evidencia separados y sin drift.
- [ ] Ratchets con productor global contemporáneo; atribuciones y límites claros.
- [ ] Lista cerrada de archivos y custody status; secretos/modelo preservados.
- [ ] Revisión sobre bytes finales; sin reutilizar veredicto de otra versión.
- [ ] Puerta siguiente explícita; no convertir un kernel conforme en beta.3 lista.
