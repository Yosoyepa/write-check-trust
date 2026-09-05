# ADR-D-03 — `ruff check` desnudo usa el perfil del repo

Estado: aceptado (arquitecto con autoría delegada, 2026-09-05; hallazgo
del coder de PR-C).
Contexto: [ANALYSIS.md](../ANALYSIS.md) §1 "ruff desnudo".

## Decisión

Añadir a `pyproject.toml`:

```toml
[tool.ruff]
extend = "governance/lint/ruff.toml"
```

`ruff` invocado sin `--config` extiende el perfil viviente del repo. El
comando autoritativo (`ruff check --config governance/lint/ruff.toml`,
G-LINT, STYLE-001) queda intacto: `extend` solo aporta configuración base
cuando no se pasa `--config` explícito.

## Evidencia que decide

Repro documentado en el handoff de PR-C: `uv run ruff check
tools/wct/gate/checks.py` (archivo intacto desde main) reporta I001 —
ruleset distinto con orden de imports mutuamente excluyente
(`force-sort-within-sections`). Todo agente (humano o subagente) que
corra ruff desnudo recibe hallazgos falsos o formatea con settings
ajenos. Es un footgun del propio harness, detectado por el harness.

## Alternativas consideradas

- **(a) Documentar "siempre usa --config" en skills/runbook**: rechazada
  — la documentación no cambia el comportamiento del comando y el
  incidente ya ocurrió CON documentación vigente.
- **(b) Mover toda la configuración de ruff a pyproject**: rechazada —
  `governance/lint/ruff.toml` es ruta protegida con semántica de
  gobernanza (perfiles legacy/strict); moverla es otra discusión.

## Consecuencias

- Test de equivalencia: el check con `--config` y el desnudo deben pasar
  ambos sobre el repo (el desnudo hoy falla → TDD rojo primero).
- pyproject.toml es ruta protegida: viaja en el bless de esta PR (el
  humano autorizó la decisión por delegación 2026-09-05).

## Addendum — el extend es parcial (root-cause de PR-E, 2026-09-05)

El fix cierra el ruleset pero NO los `per-file-ignores`: en modo extend,
ruff resuelve los paths de un config relativos al DIRECTORIO del archivo
que lo declara (`governance/lint/tests/**` — no existe), mientras que
`--config` los resuelve relativos al cwd (matchea). `ruff check .`
desnudo reporta 622 (S101/PLR2004/etc. en tests); con `--config` pasa.
Descartado como estructural: patrones `../../` rompen el comando
autoritativo, y duplicar la tabla en pyproject duplica gobernanza
inauditable (el ratchet audita solo governance/lint/ruff.toml). Vigente:
el comando autoritativo del repo SIEMPRE lleva `--config`; el desnudo
queda como aproximado por-archivo. Candidato a issue upstream.
