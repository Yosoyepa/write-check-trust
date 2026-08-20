# reserve-stock-001
Feature: Reserve stock

  Scenario Outline: Reserve available units
    Given inventory contains "<stock>" units
    When I reserve "<quantity>" units
    Then "<remaining>" units remain

    Examples:
      | stock | quantity | remaining |
      | 10    | 3        | 7         |
      | 5     | 5        | 0         |

