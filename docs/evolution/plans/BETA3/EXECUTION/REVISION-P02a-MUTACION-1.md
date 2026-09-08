# P02a — primera campaña focal, no conformidad todavía

Registro del arquitecto durante desarrollo B3-MA-D. No es cierre de beta.3,
autorización de bless ni dictamen de primera entrega completa. Continúa
[SEGUIMIENTO-P02](SEGUIMIENTO-P02.md), sin reemplazar su historia.

## Identidad y resultados recibidos

El coder congeló las 17 rutas de producto/tests/feature aprobadas con manifiesto
agregado `5a5fe9dc824951fdc3b253c18ff168e34986564124f63be1131f05809d2b226e`.
Los hashes se conservaron durante la campaña y la prerevisión independiente.
El handoff, fuera de ese manifiesto, puede registrar evidencia sin modificar
los bytes medidos. Evidencia local del candidato:
`build/tmp/b3-ma-p02a-r0/candidate-pre-mutation.sha256` y
`mutation-campaign-results.json`.

Resultado comunicado por el coder: **1552 identidades = 1295 killed +
257 survived brutos**, sin otros estados ni resultados ausentes. La salida
0 del comando mutmut no es aprobación. El arquitecto no presenta esa corrida
como ejecutada por él ni como G-MUT productivo: es la calificación focal
aislada autorizada para los doce módulos `tools/`.

La primera colección del instrumento falló por resolución de una instalación
editable previa; ese intento no ejecutó los mutantes. El reintento con árbol
generado e imports comprobados produjo la campaña citada. Preservar ambas
salidas y la receta: no atribuir el fallo de importación a un mutante detectado
ni afirmar que se acreditó una ejecución inicial íntegra sin incidencias.

## Decisiones y motivos

1. **No conforme todavía:** reparar déficits observables de tests/producto
   antes de continuar CRAP/DRY o pedir bless. Ningún resumen global verde
   reemplaza la evidencia focal sobre el harness.
2. **Oráculos independientes:** el serializer necesita un JSON literal
   completo, no solo comprobar que cambia su propio hash. El arquitecto leyó
   y cotejó contra §6 el golden auxiliar propuesto por el coder, SHA
   `829292efcda2cc8f9b7491a701fd1621099129c3ce965d87c3a38669d4c8497b`.
   Incluye todos los campos de spec/context/files/Git, sha de `abc`, size3,
   mode420 y LF final. Aprobado como prueba pura; no sustituye fixtures API
   ni acredita que commits sintéticos existan en Git.
3. **Equivalentes separados:** el coder señaló `ensure_ascii=False → None`
   como posible equivalente. Es una hipótesis pendiente de adjudicación
   independiente, no permiso para filtrarlo. Conservar IDs, cambios y conteos
   brutos. No matar equivalentes mediante mocks de kwargs ni trasladar
   constantes fuera de alcance para mejorar artificialmente la métrica.
4. **Tipos antes de transformación:** el coder detectó que `_typed_fields`
   llama `dataclasses.asdict` antes de validar valores. El arquitecto lo
   reprodujo en memoria: un objeto inválido en `InputSpec.profile_id` cuyo
   `__deepcopy__` lanza RuntimeError propaga esa excepción, en vez del TypeError
   contractual. La validación no debe copiar ni ejecutar comportamiento del
   valor inválido para conocer su tipo. Corrección y test discriminante
   pendientes al registrar este documento.
5. **Límites sin oráculo circular:** entradas usa el literal independiente16;
   file/total/manifest aún obtenían el tamaño esperado del snapshot del SUT.
   Se pidió reforzarlos con bytes conocidos de fixture y el golden revisado.
   Una medición producida por el mismo serializer podría aprobar un artefacto
   erróneamente incompleto.

La prerevisión independiente terminó con dos bloqueantes: confirmó el
deepcopy anterior y reprodujo que `open_directory` deja escapar FileNotFoundError
cuando fallan tanto open como el stat del diagnóstico con ENOENT. Reportó
17/17 hashes intactos, imports de los doce módulos desde el candidato,
177 tests coleccionados y 177 PASS en 4.31s. No aprobó mutación ni el producto.
El arquitecto liberó entonces la congelación para corregir ambos con tests
previos y reforzar los oráculos; la campaña conserva la copia anterior.

Cualquier reparación exige nueva identidad antes de volver a medir. Estas asistencias
son parte del experimento y no deben convertirse en varias tareas exitosas
independientes ni ocultarse para calcular primera aceptación. Telemetría y
coste siguen unavailable; no hay conclusión causal sobre ahorro del modelo.

## Integración documental separada

PR48 fusionada como `34bd572a6f54f6c49f1205fe2ece63acd9e818a3`, únicamente
contratos, sondas y feedback revisados. CI de PR `34182628760` success.
No contiene implementación P02b ni ejecutó bless. La CI de main
`34183257402` se comprobó después: completed/success.

## Adjudicación arquitectónica parcial: no es una excepción autorizada

El arquitecto extrajo y ejecutó mediante AST las funciones `orig` y
`x_canonical_json__mutmut_4` del árbol generado preservado, sin importar ni
modificar el candidato en reparación. Ocho entradas, incluido Unicode anidado
y el golden completo, produjeron bytes idénticos. El digest del golden en
ambas fue `829292efcda2cc8f9b7491a701fd1621099129c3ce965d87c3a38669d4c8497b`.

La razón no es solo la muestra: se leyeron `JSONEncoder.encode` e `iterencode`
del Python3.13.14 instalado. Ambos eligen la codificación de strings mediante
`if self.ensure_ascii`; False y None siguen la misma rama y ese valor no se
transfiere al encoder interno como un dato diferente. Fuente `json/encoder.py`
SHA `bfaf651515edeb7b8c4d4aef5fcd2a650d817e47ec85ac4606e5be2e4dd5bbb4`.
Para los valores JSON del perfil, el cambio no altera los bytes observables.
No es una afirmación sobre cualquier runtime ni sobre mocks que inspeccionen
los argumentos internos de json.dumps.

Conclusión limitada: hay evidencia de al menos un mutante equivalente en la
campaña anterior; **no implica que los otros 256 lo sean**. TEST-002 y la
skill wct-hardening aún exigen cero supervivientes. La delegación de contratos
no autoriza al arquitecto a elevar el umbral o introducir una exclusión tácita.
Si persiste en el candidato final, la política de adjudicación requerirá una
decisión humana explícita antes de aprobar hardening, manteniendo el conteo
bruto y la evidencia por ID. Mientras tanto, corregir los defectos reales no
depende de esa decisión y continúa autorizado.
