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
- **F9-b era un escape real del repo**: `application:tkinter.Tk()` pasaba
  todos los gates — import-linter no ve externos sin
  `include_external_packages`, semgrep no tiene regla tkinter y la policy
  no lo listaba en `forbidden_external.application`. **REDIMIDO
  (2026-09-05, PR #31)**: tkinter prohibido en
  `architecture.forbidden_external.application` con autorización humana
  explícita (línea con procedencia en policy.yaml); el caso hoy corre como
  gate-engine (archmetrics lo caza) y el reconocedor `environment` murió
  con su último usuario.
- **F11-b es un escape real del repo**: vulture reporta constante muerta a
  confianza 60, pero el umbral declarado es 80
  (`thresholds.yaml → dead_code.vulture_min_confidence`). Residuo
  declarado; redención: decisión humana del umbral (bajar a 60 acepta el
  ruido, o whitelist) y convertir a gate-tool.

El conteo pasó de 4 a 6 residuos y la redención de F9-b (PR #31) lo deja
en 5: 30 casos = **13 gate-engine · 8 gate-tool · 4 hook · 5 heuristic
(declarados)**. F11-b sigue pendiente de decisión humana de umbral; todo
cambio de 1 línea en `governance/**` exige autorización humana explícita
(SEC-005).

## Addendum 2 — PR-E redime los tres residuos de mutación (2026-09-05)

F2-a, F2-b y F5-b se convierten a gate-tool con corridas REALES de
mutmut sobre fixtures con su propio `[tool.mutmut]` (plan
docs/evolution/plans/PR-E): el caso caza cuando la corrida mide los
sobrevivientes y el gate productivo FALLA. F2-b cierra su promesa: es EL
caso demostración — el test pasa, la mutación expone que no protege nada.
Queda UN solo residuo declarado: F4-b (diff-cover con fixture git), con
su redención documentada arriba. El wholesale al harness quedó rechazado
con números (4.235 sitios / 16 archivos sobre presupuesto / ≈21h) —
ADR-E-01.
