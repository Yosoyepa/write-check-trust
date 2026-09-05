# ADR-F-01 — F4-b corre productivo: fixture git mínimo + lcov sembrado, gate real

Fecha: 2026-09-05 · Estado: aceptado · Autor: arquitecto (delegación permanente)

## Contexto

F4-b (producción cambiada sin tests, `production=true;tests=false`) es el
último residuo heurístico del red team (ADR-C-02). El catcher real es
`gate_coverage_diff` → diff-cover, que exige tres cosas que solo viven en un
repo real: la herramienta en PATH, una rama base resoluble por `remote_base`,
y `build/coverage/lcov.info`. Por eso se declaró heurístico en PR-C.

## Decisión

Redimirlo como `gate-tool` con un fixture git mínimo en tempdir de sistema
(el mismo aislamiento que ya usa `_run_tool`, `redteam.py:209`):

1. `git init -b main` + gobernanza mínima commiteada (`policy.yaml` con
   `schema_version: 1` + `thresholds.yaml` con `coverage.diff_min: 90`,
   réplica del valor productivo) con identidad `-c user.email/-c user.name`
   y `commit.gpgsign=false` — el commit base es innegociable: sin él `main`
   no resuelve en `rev-parse --verify` y `remote_base` devuelve None.
2. Víctima `src/victim/ops.py` **untracked** — producción nueva, cero tests.
3. `build/coverage/lcov.info` sembrado con las líneas de la víctima a
   `DA:n,0` (cero ejecuciones): el artefacto que G-COV-TOTAL produciría si
   la suite no ejercita el archivo.
4. El gate productivo corre diff-cover real contra ese fixture; caza =
   `GateResult.status == FAIL` (contrato universal gate-tool, sin `expect`).

## Por qué el lcov sembrado es legítimo (y no "fixture ajustado")

ADR-C-01 §5 prohíbe ajustar el fixture para que el motor caze. Aquí el
fixture autoriza la ENTRADA (el artefacto de cobertura), no el veredicto:
diff-cover — el motor calificado — computa la intersección diff × cobertura
y decide. Es el mismo convenio de PR-C: los fixtures de mutmut autoraban
pyproject/código/tests y mutmut decidía. La alternativa honesta (correr
pytest real dentro del fixture para GENERAR el lcov) añade un entorno Python
completo al fixture y acopla el caso a la disponibilidad de pytest+coverage
en el entorno — fragilidad sin veredicto adicional.

## Alternativas rechazadas

- **Variante B (víctima commiteada en rama `feature`)** — medida en la sonda:
  también caza, pero exige 3 comandos git más y una segunda rama para
  representar el mismo defecto. La variante A además ejercita
  `--include-untracked` — flag productivo cuyo propósito es exactamente
  "archivo nuevo sin commitear".
- **Declarar el residuo permanente** — el costo de la redención resultó una
  sonda de 10 líneas y un builder de ~35; "frágil" (la razón original de
  ADR-C-02) no se sostuvo contra la medición.
- **Esperar demanda (PR-C2 pequeño)** — la demanda existe: cada corrida del
  red team imprime "1 heuristic (declarados)" y el feature residual existe
  solo para acomodarlo.
