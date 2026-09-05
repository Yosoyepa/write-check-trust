# wct-bare-ruff-001
Feature: ruff sin --config usa el perfil del repo

# Un agente que corra ruff desnudo no debe recibir el ruleset de nadie.

  Scenario: ruff desnudo extiende el perfil viviente
    Given un archivo fuente del repo que pasa el lint del perfil
    When se corre ruff check sin --config sobre él
    Then no reporta hallazgos
    And el comando con --config sigue pasando igual
