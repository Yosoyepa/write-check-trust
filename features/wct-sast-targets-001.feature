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
