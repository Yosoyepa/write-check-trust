# RESEARCH — PR-A1: prior art que soporta las decisiones

Notas de investigación enfocada. Las afirmaciones de herramienta describen
comportamiento documentado y estable (sin clavar versiones); las fuentes
externas del diagnóstico general viven en el
[dossier](../SOURCES.md). Esta investigación se hizo para A1 en esta sesión.

## R1 — Aislamiento de property tests: marker + deselección

- **pytest**: el mecanismo documentado para subconjuntos de tests es el
  sistema de markers con `-m` (selección negativa `-m "not x"` soportada).
  `--strict-markers` (ya activo en este repo, `pyproject.toml:54`) rechaza
  markers no declarados — el marker `property` ya está declarado, solo falta
  usarlo.
- **hypothesis**: los property tests son multiplicadores de casos: cada test
  `@given` ejecuta decenas/cientos de ejemplos generados. Bajo mutmut eso
  multiplica el tiempo por mutante (cada mutante re-corre el property test
  completo con shrinking ante fallo). Aislar property de mutación es práctica
  estándar de eficiencia además de corrección metodológica: el oráculo
  property no debe participar del presupuesto que califica la suite unitaria.
- **coverage.py**: `omit` excluye *archivos como fuente medida*; no impide que
  la *ejecución* de un test cuente líneas. Por eso `omit=["tests/*"]` no
  aislaba nada: la corrección correcta es a nivel de colección (`-m`), no de
  medición. Confirmado empíricamente en este repo: el omit existe y sin
  embargo property contaba (ANALYSIS §1.1).
- **Precedente en el propio repo**: G-PROP ya ejecuta `tests/property` aparte
  (`runner.py:400`) — el diseño de "ejecución dedicada separada" ya estaba
  decidido; A1 solo cierra el hueco de las otras superficies.

## R2 — Dogfooding de cobertura: medir el instrumento

- El principio de que una herramienta de verificación debe medirse a sí misma
  ("quien verifica debe ser verificado") es el mismo que WCT aplica a sus
  adoptantes; su ausencia fue clasificada como deuda por el dossier
  (O-003) y confirmada localmente: `source=["src/example"]` deja fuera
  2 496 statements reales del harness.
- Prior art relevante: suites de herramientas de testing maduras (pytest
  mismo, coverage.py) mantienen suites de tests sobre su propio código fuente
  con cobertura medida sobre el paquete de la herramienta. La separación
  "código del producto vs código del ejemplo" no existe en esos proyectos;
  aquí existe por diseño de plantilla, y por eso el scope debe ser *explícito*
  (eso es PR-A2; A1 solo garantiza que la cifra no esté inflada por property).
- **Lo que A1 fija para A2**: la cifra base 73 % ya medida bajo exclusión de
  property (idéntica con/sin: el property test no aporta líneas únicas).
  Registrar baselines bajo semántica estable es la práctica de ratchet que el
  repo ya usa para docstrings y tamaños de archivo.

## R3 — Pases vacíos en verificación

- **Mutación**: un veredicto de suite basado en "0 mutantes sobrevivieron"
  cuando se ejecutaron 0 mutantes es el caso degenerado clásico de la
  disciplina de mutation testing: la métrica (survival rate) solo significa
  algo con población no vacía. Los reportes serios de mutación reportan
  "covered/killed/survived/timeout" y tratan population=0 como
  sin-datos, no como éxito.
- **Aceptación parametrizada**: TEST-010 ya exige parámetros para todo campo
  variable del escenario; un escenario sin Examples es exactamente el caso
  que esa regla prohíbe. El veredicto actual lo recompensa (pasa "limpio").
  Análogo conceptual: un test sin aserciones — la literatura de calidad de
  tests lo clasifica como test vacío (falso verde), y los linters de tests
  (p.ej. detectores de `assert`-less tests) lo marcan.
- **Decisión de semántica**: fail agregado (0 mutaciones en toda la corrida →
  FAIL) + advertencia por escenario sin Examples. Endurecer a fail por
  escenario se difiere a O-004 porque puede exigir re-parametrizar corpus
  completo — un análisis de corpus, no un fix de veredicto.

## R4 — Visibilidad de SKIP en reportes de CI

- Los sistemas de CI maduros separan explícitamente skipped del conteo de
  éxito (p.ej. GitHub Actions marca `skipped` en su propio estado por job;
  JUnit XML tiene elemento `skipped` distinto de `passed`/`failure`; pytest
  `-ra` reporta skips con razón en el summary corto). La razón: un skip
  codifica "no se evaluó", que es información distinta de "se evaluó y pasó".
- El modelo interno de WCT ya tiene el estado (`Status.SKIP` en `model.py`)
  y la razón (`"herramienta ausente"`, `"desactivado por policy.yaml"`); el
  defecto es solo el agregado del render que los funde con PASS.
- Restricción respetada: no cambiar `blocking` (model.py:28-30) en A1.
  Convertir SKIP en bloqueante por tier es una decisión de perfiles
  (Horizonte 0: perfil local vs completo) con costo operacional conocido
  (entornos sin herramientas opcionales quedarían rojos) — se documenta en
  ADR-A1-03 como alternativa rechazada por ahora.

## R5 — Interacción mutmut × selección de tests

- `pytest_add_cli_args_test_selection` es el punto documentado de mutmut para
  acotar qué tests corren por mutante. Incluir ahí un property test con
  hypothesis multiplica el costo por mutante (generación + shrinking) y
  contamina la calificación con un oráculo que TEST-008 excluye. La lista ya
  mezcla unit/integration/acceptance-generated; retirar solo la entrada
  property es el cambio mínimo con la semántica correcta.
