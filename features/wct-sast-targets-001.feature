Feature: Alcance verificable del analisis SAST

  Scenario Outline: Clasificar una respuesta Semgrep por rutas normalizadas
    Given fuentes Python exigibles "<required>"
    And rutas Python informadas como escaneadas "<scanned>"
    And una respuesta "<payload>" con exit "<exit>"
    When clasifico el resultado SAST por alcance
    Then obtengo estado "<status>" y diagnostico "<diagnostic>"

    Examples:
      | required            | scanned             | payload             | exit | status | diagnostic                  |
      | src/a.py            | src/a.py            | finding-valido      | 1    | FAIL   | regla y archivo             |
      | src/a.py;tools/b.py | src/a.py;tools/b.py | limpio-valido       | 0    | PASS   | 2 fuentes analizadas        |
      | src/a.py            |                     | limpio-valido       | 0    | ERROR  | 0 de 1 fuentes              |
      | src/a.py;tools/b.py | src/a.py            | limpio-valido       | 0    | ERROR  | falta tools/b.py            |
      | src/a.py;tools/b.py | src/a.py;tests/c.py | limpio-valido       | 0    | ERROR  | ruta distinta no compensa   |
      |                     |                     | limpio-valido       | 0    | PASS   | sin fuentes aplicables      |
      | src/a.py            |                     | json-malformado     | 0    | ERROR  | salida ilegible             |
      | src/a.py            |                     | esquema-incompleto  | 0    | ERROR  | esquema incompleto          |
      | src/a.py            | src/a.py            | errores-instrumento | 0    | ERROR  | error del instrumento       |
      | src/a.py            | src/a.py            | limpio-valido       | 1    | ERROR  | exit sin finding explicativo |

  Scenario: Una fuente ignorada sigue siendo exigible
    Given un modulo Python ignorado dentro de una ruta declarada
    When Semgrep no lo informa entre sus rutas escaneadas
    Then el alcance SAST bloquea por omision de esa ruta

  Scenario: Un temporal fuera de rutas declaradas no infla el denominador
    Given un archivo Python bajo el directorio de construccion
    When se forma el conjunto exigible de seguridad
    Then ese archivo queda fuera del conjunto exigible

  Scenario: Un modulo no testeable sigue sujeto a seguridad
    Given un modulo marcado como unsuitable_for_test bajo una ruta declarada
    When se calcula el alcance SAST
    Then ese modulo pertenece a las fuentes exigibles

  Scenario: El fixture adversarial usa una raiz Git propia
    Given un defecto IO plantado bajo el temporal permitido
    When el fixture inicializa su propio proyecto Git
    Then Semgrep escanea la ruta plantada y rechaza la regla de dominio

  Scenario: El aislamiento Git restaura el entorno en el mismo proceso
    Given valores heredados para ceiling, git-dir y git-work-tree
    When entra y sale el fixture de aislamiento Git
    Then durante el fixture solo queda el ceiling del temporal
    And al terminar se restauran los tres valores originales

  Scenario: La gobernanza del fixture adversarial es cargable por el lector productivo
    Given el fixture adversarial f9_a plantado en un temporal mediante filesystem y Git, sin Semgrep
    When cargo su raiz con el load_config productivo
    Then el proyecto retornado es esa misma raiz
    And policy y thresholds son mapas sin ConfigError

  Scenario Outline: Los resumenes SAST conservan las fuentes omitidas
    Given fuentes Python exigibles para el resumen "<required>"
    And rutas Python informadas como escaneadas para el resumen "<scanned>"
    And una respuesta para el resumen "<payload>" con exit "<exit>"
    When clasifico el resultado SAST para el resumen
    Then obtengo estado "<status>" y resumen exacto "<resumen>"

    Examples:
      | required                       | scanned  | payload        | exit | status | resumen |
      | src/a.py;tools/b.py;tests/c.py | src/a.py | finding-valido | 1    | FAIL   | governance.semgrep.wct-io-in-domain src/a.py:3 (omitidas: tests/c.py, tools/b.py) |
      | src/a.py;tools/b.py;tests/c.py | src/a.py | limpio-valido  | 0    | ERROR  | falta tests/c.py, tools/b.py |

  Scenario Outline: Los errores de alcance identifican la causa del rechazo
    Given una raiz temporal con la politica de alcance "<caso>"
    And la condicion invalida "<invalido>"
    When determino el alcance exigible de la raiz
    Then el rechazo es de tipo "<tipo>" con prefijo "<prefijo>"

    Examples:
      | caso | invalido | tipo | prefijo |
      | paths-no-mapa | policy sin mapa paths | SemgrepScopeError | policy.paths debe ser un mapa para determinar el alcance |
      | source-string | source como string no lista | SemgrepScopeError | policy.paths.source debe ser una lista de rutas string |
      | build-mapa | build como mapa no lista | SemgrepScopeError | policy.paths.build debe ser una ruta string o una lista de rutas string |
      | build-no-normalizable | build que no normaliza bajo la raiz | SemgrepScopeError | ruta de construcción no normalizable bajo la raíz |
      | fuente-escapa | fuente cuyo enlace resuelve fuera de la raiz | SemgrepScopeError | fuente declarada escapa de la raíz |
      | declarada-no-normalizable | declarada con salto de directorio | SemgrepScopeError | ruta de alcance no normalizable bajo la raíz |
      | declarada-escapa | declarada que resuelve fuera de la raiz | SemgrepScopeError | ruta de alcance escapa de la raíz |
      | declarada-ambigua | dos declaradas que resuelven a la misma | SemgrepScopeError | ruta de política ambigua |

  Scenario Outline: La herramienta ausente produce un SKIP visible del gate
    Given una raiz de proyecto con politica de alcance valida
    And la deteccion de "semgrep" no encuentra la herramienta
    When ejecuto el gate SAST sobre la raiz sin herramienta
    Then obtengo estado "<status>" con gate "<gate>" y resumen "<resumen>"

    Examples:
      | status | gate           | resumen                      |
      | SKIP   | G-SAST-SEMGREP | herramienta ausente: semgrep |

  Scenario Outline: El preflight tolera un Git no cero acotado y observa el resultado posterior
    Given una raiz privada sin repositorio con frontera Git "<frontera>"
    And una politica de alcance valida con fuente declarada
    And un instrumento acotado que responde "<payload>" con exit "<exit>"
    When ejecuto el gate SAST sobre la raiz privada
    Then obtengo estado "<status>" y resumen "<resumen>"

    Examples:
      | frontera | payload       | exit | status | resumen                           |
      | ceiling  | limpio-valido | 0    | PASS   | 1 fuentes analizadas, 0 hallazgos |
      | ceiling  | limpio-valido | 2    | ERROR  | exit fuera de contrato            |

  Scenario Outline: La rama de error expone la causa y la duracion medida
    Given una raiz de proyecto con politica de alcance ilegible
    And la deteccion de "semgrep" encuentra la herramienta
    And un reloj controlado para la rama de error "<inicio>" seguido de "<fin>"
    When ejecuto el gate SAST sobre la raiz con politica ilegible
    Then obtengo estado "<status>" con gate "<gate>" y duracion de error ms "<duracion>"
    And el resumen empieza por "<prefijo>" y conserva la causa "<causa>"

    Examples:
      | inicio | fin     | status | gate           | duracion | prefijo                          | causa                         |
      | 3000.0 | 3001.25 | ERROR  | G-SAST-SEMGREP | 1250     | governance/policy.yaml ilegible: | causa determinista de lectura |

  Scenario Outline: El retorno final expone duracion y comando informativo
    Given una raiz Git propia con politica de alcance valida
    And un instrumento controlado que responde "<payload>" con exit "<exit>"
    And un reloj controlado para el retorno final "<inicio>" seguido de "<fin>"
    When ejecuto el gate SAST sobre la raiz Git propia
    Then obtengo estado "<status>" con gate "<gate>" y duracion final ms "<duracion>"
    And el comando informado es "<comando>"

    Examples:
      | inicio | fin    | payload       | exit | status | gate           | duracion | comando |
      | 1000.0 | 1002.5 | limpio-valido | 0    | PASS   | G-SAST-SEMGREP | 2500     | semgrep --quiet --error --severity ERROR --config governance/semgrep --json |
