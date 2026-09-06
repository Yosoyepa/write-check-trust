# Changelog

Todos los cambios notables de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto se adhiere a [SemVer](https://semver.org/lang/es/): la serie
`0.x` fue alpha (todo puede cambiar); desde `1.0.0-beta.1` el contrato del
CLI/gates se congela salvo rupturas anunciadas con bump de versión.

## [Unreleased]

## [1.0.0-beta.2] — 2026-09-06

Endurecimiento del propio harness tras declarar la beta: los controles que
antes podían salir verdes sin verificar pasan a medir de verdad. **Un árbol
que estaba verde en beta.1 puede quedar rojo en beta.2** — eso es lo que
esta versión corrige; la guía de actualización dice qué hacer al respecto.

### Changed

- **La mutación se vuelve real (PR #34)**: `G-MUT` verifica sobrevivientes
  contra el manifiesto diferencial y deja de aceptar redenciones — antes
  un escape podía salir verde sin ejecutar la verificación pesada.
- **Veredicto de mutación completo (#37)**: `wct mutate run` clasifica todo
  el inventario del motor (exit 0 PASS · 1 FAIL · 2 ERROR con diagnóstico);
  la salida vacía del motor ya no se interpreta como éxito.
- **Diff-cover con base real (PR #36)**: el 90 % sobre líneas cambiadas se
  mide contra la rama base real, no contra una copia local divergente.
- **Red team productivo (PR #31)**: los adversarios F1–F15 son cazados por
  los motores reales (mutmut, jscpd, semgrep…) en vez de réplicas
  heurísticas — 30/30 sin heurísticas.
- **Conformidad configuración → runtime (PR #30)**: lo declarado en
  `policy.yaml`/`thresholds.yaml` se verifica contra lo que los gates
  ejecutan de verdad.
- **Honestidad del reporte del instrumento (PR #28)** y **scope/baseline
  de cobertura propia (PR #29)**: el harness se mide a sí mismo —
  perfiles de verificación y completitud de lo que un verde significa
  (PR #32).
- **La CI del template exige ratchets medidos (#39, #40)**:
  `quality.yml` produce el LCOV sin property (TEST-008) y el paso
  `Require measured ratchets` consume ese mismo artefacto en el mismo
  job; property conserva ejecución propia. Para adoptantes que copian el
  workflow: ausencia de medición exigible = fallo, nunca salto.
- **G-INTROVERT promovido al tier commit (#39)**: la honestidad de tests
  (aserciones que trazan al SUT) se verifica en cada commit, no solo en
  full.

### Added

- **Ratchets exigibles (#39)**: `wct ratchet check --require
  coverage-total,docstring-coverage` (o `--require all`) — las métricas
  dependientes de artefacto/herramienta bloquean cuando no pueden medirse,
  nombrando la causa y el comando que produce la medición. Aditivo: el
  modo tolerante conserva byte a byte su salida histórica.
- Regresión repo-pineada del escape de tests introvertidos (#39): la
  suite que CI ejecuta sostiene el invariario, con control negativo
  emparejado.
- Suite de contrato del workflow de CI (#40): 11 tests pinean receta
  productiva, comando completo del consumidor, allowlist `{name, run}`
  por paso, adyacencia productor→consumidor y ejecución incondicional
  del job — sellados tras 5 rondas de revisión (12 sondas de
  neutralización rechazadas).

### Fixed

- `adoption-smoke` ejecuta el quickstart real del README (`make
  bootstrap`) y cita el paso con presupuesto correctamente (#25, #26).
- Escape introvertido del test del CLI de mutación: las aserciones traza
  al veredicto del SUT, no solo a su andamiaje (#38).

### Guía de actualización (beta.1 → beta.2)

1. **Acoplamiento por hash, no por versión**: tu repo decide cuándo
   moverse. Corre `wct adopt check` para ver el drift contra este SHA y
   `wct adopt sync` para obtener el parche propuesto — revísalo con
   diff-review antes de aplicarlo; nunca se ejecuta solo.
2. **Espera más rojos honestos**: G-MUT ahora falla con sobrevivientes
   reales, los ratchets exigibles fallan si no pueden medir (corre la
   cobertura antes: `pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property"`), y G-INTROVERT en
   commit exige aserciones que tracen al SUT. Un rojo nuevo de beta.2
   señala algo que beta.1 no veía: **diagnostícalo antes de actuar**.
   El endurecimiento tiene limitaciones y falsos positivos conocidos
   (p. ej. G-INTROVERT no traza tests que ejecutan el SUT por subprocess
   — su limitación está documentada); si el hallazgo es real, arréglalo;
   si es un falso positivo del instrumento, repórtalo con la evidencia —
   en ningún caso lo suprimas sin diagnóstico.
3. **Property tests separados**: si copias la cadena de CI del template,
   property queda fuera de la corrida de cobertura (TEST-008) y necesita
   su paso propio — sin él deja de correr en CI.
4. **Presupuesto del smoke sin cambios**: el límite de 120 s aplica al
   tier commit del adoptador (clon limpio → verde), no al job completo
   de CI del template.

## [1.0.0-beta.1] — 2026-08-24

### Changed

- **Declaración de beta** con política de madurez publicada
  ([RELEASES.md](RELEASES.md)) y acoplamiento de adoptadores por hash de
  commit (`wct adopt lock/check/sync`).

### Added

- `wct adopt lock/check/sync`: ciclo de vida del harness vendido (patrón
  cruft — lock por SHA exacto, drift/behind/conflict-candidates, patch
  propuesto sin ejecutar). Incluye fix de artefactos `__pycache__`.
- Smoke-test de adopción en CI (`adoption-smoke.yml`): clon limpio →
  `wct doctor` + tiers fast y commit en verde, sin intervención.
- [ADOPTERS.md](ADOPTERS.md): evidencia de adopción real.

## [0.5.0] — 2026-08-23

### Added

- **G-WIRE** (tier commit, hard): anti-patrones de inyección de dependencias
  por AST con resolución de alias — instanciación de adapters/frameworks en
  domain/application, llamadas a nivel de módulo en domain, star-imports.
- **G-LCOM** (tier full, ratchet): cohesión LCOM4 advisory con exclusiones
  declarativas (dataclass, Protocol, Enum, excepciones, <3 métodos).
- **G-DRY-TPL** (tier full, ratchet): clones de plantilla — segunda pasada
  DRY anonimizando nombres/literales (patrón PMD CPD), Jaccard ≥ 0.90.

## [0.4.0] — 2026-08-23

### Added

- Válvulas anti-deadlock del Stop hook: `WCT_HOOK_ROLE=observer` (roles de
  solo lectura advierten en vez de bloquear) y cortacircuito global (la
  tercera bloqueada consecutiva pasa con advertencia `DEADLOCK GUARD` que
  obliga a declarar el árbol rojo). PROC-001 actualizado. Hallado en el
  piloto (personalAssistant) durante la integración de 0.3.0.

## [0.3.0] — 2026-08-23

### Added

- `wct hotspots` (churn × complejidad cognitiva, advisory — Tornhill).
- **G-SIZE** (500 LOC tokenize) y **G-COGNITIVE** (≤15, Campbell/S3776).
- Auditoría de `per-file-ignores` como ratchet con justificación obligatoria.
- **G-DRY-TOK con diente**: `--exit-code 1` en jscpd y wiring al tier full
  (antes: gate vacío — salía 0 con clones). En su primera corrida real en CI
  cazó duplicación genuina en el propio harness (PR #16).
- Partición fachada de `gate/runner.py` (bajo el techo de 500 LOC).
- Ratchet de cobertura de docstrings; pip-audit por PR; jscpd en CI.

## [0.2.0] — 2026-08-22

### Added

- Tier `pr` con paridad exacta de la CI de PR.
- Integración del feedback del piloto fases 22–24: `wct split-plan`
  (partición fachada propuesta, nunca ejecutada), diagnóstico de manifiestos
  de mutación legacy/ausentes en G-MUT-SITES, Definition of done del coder.
- `gate_coverage_diff` hard con base fiel a CI (90 % en líneas cambiadas).
- Endurecimiento de workflows para contribuyentes externos.

[Unreleased]: https://github.com/Yosoyepa/write-check-trust/compare/v1.0.0-beta.2...HEAD
[1.0.0-beta.2]: https://github.com/Yosoyepa/write-check-trust/compare/v1.0.0-beta.1...v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/Yosoyepa/write-check-trust/compare/v0.5.0...v1.0.0-beta.1
[0.5.0]: https://github.com/Yosoyepa/write-check-trust/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Yosoyepa/write-check-trust/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Yosoyepa/write-check-trust/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Yosoyepa/write-check-trust/releases/tag/v0.2.0
