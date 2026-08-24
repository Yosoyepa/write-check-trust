# wct-wire-001
Feature: Wire gate

  Scenario Outline: Instanciación de infraestructura en capas internas
    Given un archivo en <layer> que instancia <symbol> desde <origin>
    When corre el gate de wiring sobre <layer>
    Then el reporte flaggea <symbol> con origen <origin> en la línea exacta

    Examples:
      | layer       | symbol | origin                    |
      | domain      | Repo   | adapters.persistence.repo |
      | domain      | Client | requests                  |
      | application | S3     | boto3                     |

  Scenario: El composition root en entrypoints queda limpio
    Given entrypoints/wire.py que instancia todos los adapters
    When corre el gate de wiring sobre el composition root
    Then el reporte no tiene flags

  Scenario: Alias no evade el gate
    Given domain/service.py con "from adapters.repo import Repo as R" y "R()"
    When corre el gate de wiring sobre el alias
    Then el reporte flaggea R con origen adapters.repo
