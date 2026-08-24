# Changelog

Todos los cambios notables de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto se adhiere a [SemVer](https://semver.org/lang/es/): la serie
`0.x` fue alpha (todo puede cambiar); desde `1.0.0-beta.1` el contrato del
CLI/gates se congela salvo rupturas anunciadas con bump de versión.

## [Unreleased]

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

[Unreleased]: https://github.com/Yosoyepa/write-check-trust/compare/v1.0.0-beta.1...HEAD
[1.0.0-beta.1]: https://github.com/Yosoyepa/write-check-trust/compare/v0.5.0...v1.0.0-beta.1
[0.5.0]: https://github.com/Yosoyepa/write-check-trust/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Yosoyepa/write-check-trust/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Yosoyepa/write-check-trust/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Yosoyepa/write-check-trust/releases/tag/v0.2.0
