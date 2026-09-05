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

## Addendum — lo que destapó la ejecución (2026-09-05)

La conversión productiva corrigió la tabla original en tres puntos:

- **F8-a/F8-b no eran falsos negativos**: el catcher productivo del
  framework-leak por IMPORT es `archmetrics.analyzer.analyze`
  (`forbidden_external` por capa, `analyzer.py:169-173`) — G-ARCHMETRICS,
  no G-SAST-SEMGREP (cuyas reglas cubren filtración de tipos y uso, no
  imports). Migrados a gate-engine con policy espejo de la real
  (sqlalchemy/fastapi están en las listas del repo). El reconocedor
  paralelo los tenía mal atribuidos desde el inicio.
- **F9-b es un escape real del repo**: `application:tkinter.Tk()` hoy pasa
  todos los gates — import-linter no ve externos sin
  `include_external_packages`, semgrep no tiene regla tkinter y la policy
  no lo lista en `forbidden_external.application`. Residuo declarado;
  redención: 1 línea en `governance/policy.yaml` (autorización humana) y
  convertir a gate-engine.
- **F11-b es un escape real del repo**: vulture reporta constante muerta a
  confianza 60, pero el umbral declarado es 80
  (`thresholds.yaml → dead_code.vulture_min_confidence`). Residuo
  declarado; redención: decisión humana del umbral (bajar a 60 acepta el
  ruido, o whitelist) y convertir a gate-tool.

El conteo pasa de 4 a 6 residuos: 30 casos = **12 gate-engine · 8 gate-tool
· 4 hook · 6 heuristic (declarados)**. Los dos escapes nuevos son cambios
de 1 línea en `governance/**` que requieren autorización humana explícita
(SEC-005) y pueden ir en el mismo bless.
