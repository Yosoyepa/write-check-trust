# B3-P1 — Gherkin para D1 y matriz de pruebas

Estado: **propuesto para aprobación humana**. Solo especificación Markdown;
sin tests ejecutables nuevos. Contrato normativo:
[SPEC-P1](specs/SPEC-B3-P1-evidencia.md). Los IDs de casos se conservan en el
manifest de calificación futuro como identidad de fila, no como mero conteo.

## Gherkin del primer incremento

```gherkin
Feature: Evidencia acotada de tests y cobertura
  Scenario Outline: El cierre conserva la identidad y el estado de cada obligacion
    Given el perfil "<perfil>" con expectativas revisadas "<expectativas>"
    And el caso de evidencia "<caso>" tiene condicion "<condicion>"
    When ejecuto la cadena de evidencia por la CLI productiva
    Then el cierre es "<cierre>" y el codigo de salida es "<exit>"
    And el registro conserva la causa "<causa>" y los resultados "<resultados>"
    Examples:
      | perfil | expectativas | caso | condicion | cierre | exit | causa | resultados |
      | beta3-p1 | completas | P1-V01 | tests terminales y LCOV propio sobre inputs estables | accredited | 0 | alcance comprobado | originales |
      | beta3-p1 | completas | P1-V02 | todos los tests terminan y cobertura valida bajo piso | rejected | 1 | umbral no satisfecho | FAIL original |
      | beta3-p1 | completas | P1-V03 | asercion falla y artefacto completo propio | rejected | 1 | test fallido | FAIL original |
      | beta3-p1 | completas | P1-A01 | productor falla y solo hay LCOV historico | invalid | 1 | artefacto ajeno al productor | FAIL original |
      | beta3-p1 | completas | P1-A02 | artefacto de otro run con mismos contadores | invalid | 1 | identidad de run distinta | originales |
      | beta3-p1 | completas | P1-A03 | LCOV truncado con productor que informa exito | invalid | 1 | artefacto malformado | originales |
      | beta3-p1 | completas | P1-A04 | LCOV propio falta tras terminar productor | incomplete | 1 | artefacto requerido ausente | originales |
      | beta3-p1 | completas | P1-I01 | falta un nodeid requerido y el resto pasa | incomplete | 1 | identidad de test faltante | originales |
      | beta3-p1 | completas | P1-I02 | otro nodeid sustituye uno con el mismo conteo | incomplete | 1 | conjuntos de tests distintos | originales |
      | beta3-p1 | completas | P1-I03 | un SF ajeno sustituye uno con el mismo conteo | invalid | 1 | archivos de cobertura distintos | originales |
      | beta3-p1 | vacias | P1-I04 | no hay unidades requeridas | incomplete | 1 | inventario vacio | originales |
      | beta3-p1 | completas | P1-X01 | herramienta requerida ausente | incomplete | 1 | herramienta ausente | ERROR original |
      | beta3-p1 | completas | P1-X02 | test requerido termina en SKIP | incomplete | 1 | obligacion no ejecutada | originales |
      | beta3-p1 | completas | P1-X03 | ejecucion cancelada sin todos los terminales | incomplete | 1 | cancelacion | resultados disponibles |
      | beta3-p1 | completas | P1-X04 | inventario terminal truncado y resumen verde | incomplete | 1 | ejecucion incompleta | originales |
      | beta3-p1 | completas | P1-D01 | fuente unstaged cambia con HEAD conservado | invalid | 1 | inputs distintos | originales |
      | beta3-p1 | completas | P1-D02 | nuevo modulo ignorado en scope tras snapshot | invalid | 1 | inputs distintos | originales |
      | beta3-p1 | completas | P1-D03 | configuracion cambia antes del consumo | invalid | 1 | configuracion distinta | originales |
      | beta3-p1 | completas | P1-D04 | runner difiere del digest fijado por reviewer | invalid | 1 | verificador distinto | resultados disponibles |
      | beta3-p1 | completas | P1-D05 | test falla y fuente cambia durante corrida | invalid | 1 | inputs distintos y test fallido | FAIL original |
      | beta3-p1 | completas | P1-L01 | se solicita ademas mutacion fresca | incomplete | 1 | G1b abierto | originales |
```

```gherkin
Feature: Compatibilidad de la salida anterior
  Scenario Outline: El comando historico conserva formato y semantica
    Given la secuencia fija de GateResult "<secuencia>" y la opcion "<opcion>"
    When renderizo y termino el comando historico "<comando>"
    Then la salida coincide con "<referencia>" y el codigo es "<exit>"
    And los campos de GateResult permanecen "<campos>"
    Examples:
      | secuencia | opcion | comando | referencia | exit | campos |
      | PASS | texto | gate | beta2 byte a byte | 0 | los seis originales |
      | PASS y SKIP | json | gate | beta2 lista JSON byte a byte | 0 | los seis originales |
      | FAIL y ERROR | quiet | gate | beta2 solo bloqueantes | 1 | los seis originales |
      | PASS y SKIP | quiet | gate | beta2 salida vacia | 0 | los seis originales |
```

```gherkin
Feature: Propiedad de archivos de evidencia
  Scenario Outline: La corrida conserva artefactos ajenos y no cruza su frontera
    Given los inputs y destinos tienen condicion "<condicion>"
    When inicio la operacion de evidencia "<operacion>"
    Then la disposicion observable es "<disposicion>"
    And los archivos ajenos permanecen "<preservacion>"
    Examples:
      | condicion | operacion | disposicion | preservacion |
      | dos arboles estables con tests homonimos | dos runs concurrentes | registros y artefactos distintos sin mezcla | identicos |
      | destino ya pertenece a otro run | crear run | rechazo de propiedad | identicos |
      | input symlink interno | inventariar | alcance no soportado | identicos |
      | input symlink externo | inventariar | alcance no soportado | identicos |
      | destino symlink o traversal | crear run | rechazo de frontera | identicos |
      | productor cancelado | cerrar run | incompleto con terminacion visible | identicos |
```

```gherkin
Feature: Presupuesto y limites del perfil
  Scenario Outline: La evidencia declara lo que no puede acreditar
    Given el recurso o capacidad "<elemento>" tiene estado "<estado>"
    When emito el registro del perfil "<perfil>"
    Then la declaracion es "<declaracion>"
    And la consecuencia es "<consecuencia>"
    Examples:
      | elemento | estado | perfil | declaracion | consecuencia |
      | costo monetario | tarifa no acordada | beta3-p1 | unavailable | no afirmar costo cero |
      | tiempo de corrida | techo alcanzado | beta3-p1 | budget_exhausted | cierre incompleto |
      | arquitectura hexagonal | fuera de P1 | beta3-p1 | not-accredited | no acreditar el molde |
      | mutacion fresca y completa | G1b abierto | beta3-p1 | not-accredited | no anunciar validacion completa |
      | calificacion de plataforma | ausente | beta3-p1 | incomplete | no acreditar el perfil |
```

## Matriz de calificación y trazabilidad

Todos los casos exigen control válido pareado. Las variantes de una fila son
ejemplos independientes de cobertura; no colapsarlas por DRY (MIN-008). Las
salidas esperadas se fijan antes de implementar. Ningún ID siguiente afirma que
un test nuevo ya exista o haya pasado.

| ID / requisito | Fixture positivo y negativo/frontera | Observable y evidencia necesaria | PR |
|---|---|---|---|
| P1-C / compatibilidad | PASS/FAIL/ERROR/SKIP, alias y mezcla; texto/JSON/quiet; defaults | Seis campos y bytes de report con duración fija; CLI real mantiene exits y reporte overview anterior | P1a/c |
| P1-I / denominador | Lista manual de módulos/nodeids/filas; sustituir/borrar/duplicar con N constante; colección vacía | expected/collected/executed distintos no cierran; SF ajeno/omitido visible. Manifest nunca se refresca de observed | P1a/b |
| P1-I-branch / límite de coverage | Fixture con if/else conocido, rama no visitada, módulo no importado y `__init__` vacío | SF/DA/BRF/BRH de fixtures contrastados con expected humano; en repo general solo completitud por archivo, límite publicado | P1b |
| P1-I-scenario / aceptación | Dos filas paramétricas con IDs estables; eliminar solo una ejecución y conservar parse verde | fila→nodeid→terminal completa o incomplete; no tomar IR verde como ejecución | P1b/c |
| P1-X / ejecución | Test pasa, falla, skip, xfail/xpass; error setup/teardown; tool ausente; crash/timeout/cancel | Resultados/exit reales y nodeids terminales; estado original conservado; ningún exit 0 vacío acredita | P1b |
| P1-A / artefactos | LCOV propio válido; antiguo, ausente, malformado, contadores imposibles, duplicado, ajeno por run/config/scope | Consumer lee solo path+digest de productor autorizado. Mutar a «último LCOV» rompe el test E2E | P1b |
| P1-D / inputs | Misma HEAD con staged/unstaged/nuevo/ignorado, cuerpo de test y conftest, baseline/lock/plugin/runner alterados | Inputs distintos invalidan; comparar también final. Cambio de runner con ancla externa conocida no acredita | P1a/c |
| P1-S / frontera | Raíz inexistente/vacía, segunda raíz de negocio, namespace no soportado, symlinks internos/externos/rotos y traversal | Rechazo atribuido sin escrituras ajenas; no reducir a primer root | P1a/c |
| P1-R / concurrencia | Dos runs/árboles distintos con IDs homónimos; choque de run ID; uno cancelado | Artefactos propios, pertenencia exacta, sin leer/borrar archivos del vecino; rechazo visible si no puede proceder | P1b/c |
| P1-O / argv | Argumento con espacios y comillas, marcador `not property` como un argumento | Lista argv del proceso conserva fronteras, independiente del string histórico command; logs no son órdenes | P1b |
| P1-E / ejes simultáneos | Fallo semántico junto a cambio de fuente; SKIP junto a otro FAIL | Precedencia invalid/incomplete/rejected y reasons múltiples; el fallo no se borra | P1c |
| P1-L / claims | Verde de cadena; exigir arquitectura o mutación fresca no disponible | Perfil solo acredita tests/LCOV; mutación limitada visible; exigir capacidad sin soporte produce incomplete | P1c |
| P1-B / presupuesto | Run completo, tope alcanzado y tarifa ausente | Medición exacta/estimada/no disponible; 80 runs locales propuestos no son resultados; no seguir por reset de contador | P1c |

Prueba del propio instrumento: un challenger omite una obligación en el
productor/compilador de fixture; el expected independiente sigue exigiéndola y
la calificación debe ponerse roja. Otra implementación válida debe conservar
verde. No usar mocks como única evidencia de la composición.

## Qué debe aprobar el humano

Estos cuatro bloques, la tabla de alcance/limitaciones y los techos técnicos de
SPEC-P1, **para B3-P1 únicamente**. La gramática se comprobará mediante
`accept parse`/`ir-dry` sobre copias efímeras de estos bloques; eso no los conecta
a steps ni equivale a aceptación. El encargo coder debe incluir conectar la
ruta real y coleccionar sus tests. Resultados de comprobación de este turno:
[VERIFICACION-D0](VERIFICACION-D0.md).
