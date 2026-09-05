# ADR-C-02 — Residuos declarados: 4 casos heurísticos con redención trazada

Estado: propuesto (se ejecuta al aprobarse GHERKIN-C.md).

## Contexto

Cuatro casos no pueden convertirse a ejecución productiva sin costo
desproporcionado o semántica imposible hoy. La opción deshonesta es
disfrazarlos ("parecen gates"); la opción cínica es eliminarlos. Este ADR
elige la tercera: **declararlos** con etiqueta, razón y ruta de redención.

## Decisión

Los casos quedan en `cases.yaml` con `harness: heuristic` y comentario de
razón in situ; el resumen los cuenta como `heuristic (declarados)`. Sus
redenciones:

| Caso | Por qué no puede ser productivo hoy | Redención |
|---|---|---|
| F2-a (G-MUT testless) | Exige corrida real de mutmut en fixture con src y sin tests: minutos por caso, y la selección de tests (pyproject del fixture) acopla el caso a config | PR de mutación del harness (backlog A2): cuando mutmut corra la suite unit del propio WCT, el caso planta src sin tests y mide sobrevivientes reales |
| F5-b (G-MUT survivor) | Ídem: "survived=1" es el OUTPUT de una corrida que hoy no existe | Ídem |
| F2-b (G-TEST hardcoded) | Un test con valor hardcodeado **pasa** pytest por diseño — ningún gate de suite puede cazarlo; solo la mutación lo expone (el mutante cambia el valor y el test sigue verde) | Ídem — es EL caso demostración de por qué la mutación existe |
| F4-b (G-COV-DIFF testless) | diff-cover exige fixture git con rama base y diff real; factible pero frágil (estado git, compare-branch) | Candidato a PR-C2 pequeño si la demanda lo justifica; hoy la cobertura-diff ya se califica de facto en cada PR del repo |

Los heurísticos residuales mantienen sus reconocedores actuales — con la
diferencia de que ahora el reporte **dice qué son**.

## Alternativas consideradas

- **(a) Eliminar los 4 casos**: rechazada — los modos de fallo F2/F4/F5
  siguen siendo requisitos del invariario (≥2 por modo) y el riesgo que
  representan es real aunque hoy se mida con imitación.
- **(b) Convertir F2-a/F5-b corriendo mutmut de verdad**: rechazada por
  runtime (minutos en cada `selftest redteam`, que corre en tier pr) y por
  acoplamiento a la selección de tests del fixture — el costo no compra la
  señal hasta que la mutación del harness exista (dependencia documentada).
- **(c) Moverlos a una suite "slow" fuera del selftest**: rechazada —
  fragmenta el invariario de modos y el inventorio; el etiquetado en el
  mismo YAML mantiene la vista única.

## Consecuencias

- El reporte del red team queda dividido en "productivo" (26) y "declarado"
  (4) — honesto y auditable, alineado con la separación PASS/SKIP de A1.
- La deuda tiene dueño y ruta (PR de mutación del harness); no es un TODO
  anónimo.
