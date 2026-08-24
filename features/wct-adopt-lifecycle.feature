# wct-adopt-lifecycle-001
Feature: Adopt lifecycle

  Scenario Outline: El lock acopla el vendido al commit exacto del upstream
    Given un clon upstream en <sha> con tools/wct
    When corro adopt lock con ese source
    Then .wct-upstream.json registra <sha> y la URL del origin
    And re-lockear sin --force falla

    Examples:
      | sha   |
      | HEAD  |
      | (tag) |

  Scenario: Check clasifica drift, behind y candidatos a conflicto
    Given un lock sobre el commit A con el archivo X idéntico
    And X divergido localmente
    And el upstream cambia X en el commit B
    When corro adopt check --ref B
    Then X aparece como diverged, changed y conflict candidate

  Scenario: Sync propone sin ejecutar
    Given lock en A y ref B con cambios en paths
    When corro adopt sync --ref B
    Then existe el patch bajo build/
    And ningún archivo fuera de build/ cambió
