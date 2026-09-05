# PR-F — Redención de F4-b: el red team queda sin residuos

## Objetivo

Convertir el último caso heurístico declarado (F4-b, ADR-C-02) en un caso
`gate-tool` productivo: la cobertura-diff (`G-COV-DIFF` → diff-cover 10.5.1)
reprobará un fixture git con producción nueva y cero tests. Tras esta PR el
resumen del red team reporta **0 heuristic (declarados)** — todo lo que el
instrumento exige, lo ejecuta un motor productivo.

## Alcance

Dentro:

- Fixture git mínimo para F4-b (builder en `fixtures_tools.py`): repo con rama
  `main` (gobernanza mínima commiteada), víctima untracked, `lcov.info`
  sembrado con las líneas cambiadas a cero.
- Migración del caso `cases.yaml` → `cases-tool.yaml` (arnés `gate-tool`,
  `tool: diff-cover`).
- Retiro del reconocedor residual `testless` (queda sin usuarios) y
  re-enfoque de los tests sintéticos del despachador hacia checkers reales.
- Inversión del feature `wct-redteam-residual-001`: de "los residuos están
  declarados" a "no hay residuos declarados" — ratchet que pone en rojo una
  declaración heurística futura.
- Este dossier.

Fuera (backlog documentado en la PR #34):

- Dedup de plantillas (G-DRY-TPL, baseline 17) — PR propia.
- Mutación diferencial del harness (condiciones en ADR-E-01).
- G-MUT en tier pr; issues upstream (mutmut exit-code, ruff extend).

## Rama y PR

- Rama: `fix/redteam-diffcover` (desde `main` @ 6c0e449).
- PR única → CI → squash merge. Título: `PR-F: el último residuo corre productivo — F4-b vía diff-cover real (O-002)`.

## Plan de commits

1. `docs: PR-F dossier — redención de F4-b` (este dossier, arquitecto).
2. `feat(redteam): F4-b corre gate-tool con fixture git; queda cero residuos`
   (coder, TDD).

## Bless

Un solo paso humano al final (tras CI verde):

```bash
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: redención F4-b, red team sin residuos"
```

`update-manifest` regenera el manifiesto de mutación Y bendice el lock
atómicamente (rutas protegidas tocadas: `tools/wct/selftest/*`). Después,
commit + push del bless; el push final de la rama queda listo para CI.
