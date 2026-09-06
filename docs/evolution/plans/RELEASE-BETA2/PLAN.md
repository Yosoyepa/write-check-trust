# PLAN beta.2 — ejecución de la salida v1.0.0-beta.2

Estado: propuesta EN EJECUCIÓN (fase 2). Companion de
[READINESS.md](READINESS.md) (decisión y hallazgos R01–R11). Este plan NO
autoriza nada: cada puerta requiere aprobación humana explícita y separada
(SEC-005). Puerta 1 cerrada: G3a-2 fusionada en `7f2fa04` (PR #40, bless y
CI verde, 2026-09-06). Corte actual de main: `7f2fa04`.

## Secuencia

| Fase | Contenido | Autorización requerida |
|---|---|---|
| 0 | Aprobación del diff G3a-2 + Gherkin (SPEC-G3a-2, GHERKIN-G3a-2) | **Puerta 1** (humana) — **APROBADA 2026-09-05** |
| 1 | Implementación G3a-2: TDD, feature, diff YAML; verifier ×5 rondas; PR; **bless**; CI; squash merge | **FUSIONADA** — PR #40 → `7f2fa04`; bless citando #40; CI verde a la primera (job 184 s; pasos nuevos ≈1 s); suite 345 · commit 21/21 post-merge |
| 2 | PR de release: CHANGELOG (beta.1→beta.2 con los 14 commits), STATUS, guía de actualización, bump de versión + lock; **bless** (pyproject protegido) | **Puerta 2 AUTORIZADA (2026-09-06)** — bump + lock + docs EJECUTADOS en working tree; staging pendiente de bless |
| 3 | Matriz de release sobre el SHA final de main (post-fase 2) — tabla de abajo, evidencias conservadas | ninguna nueva (solo ejecutar) |
| 4 | Publicación: tag inmutable + GitHub prerelease (`--prerelease`, NO `--latest`), assets (SBOM), verificación del smoke disparado por tag | **Puerta 3**: publicación (humana) |

El candidato es el SHA final de main tras la fase 2 — no se publica
retrospectivamente ningún SHA intermedio como si incluyera algo posterior
a su fusión.

## Matriz de release (fase 3 — sobre el SHA candidato)

| # | Control | Comando / dónde | Criterio | Evidencia conservada |
|---|---|---|---|---|
| M1 | CI quality | push del merge de fase 2 (y del PR de fase 1) | verde, incluido el paso exigible con LCOV nuevo | URL del run |
| M2 | Suite completa | `uv run pytest -q` (checkout aislado del SHA) | 334+ passed, 0 failed | salida íntegra en `docs/evolution/plans/RELEASE-BETA2/evidence/` |
| M3 | Ratchets con LCOV recién producido | borrar `build/coverage/lcov.info` → receta productiva → `uv run wct ratchet check --require coverage-total,docstring-coverage` | `medidas N de N exigibles`, exit 0 | salida + SHA del checkout |
| M4 | full-hardening | `gh workflow run full-hardening.yml --ref main` (tras el merge); jscpd lo instala el propio workflow | `headSha` del run == SHA candidato; tier full sin FAIL/ERROR; inventario completo de SKIP; G-DRY-TOK ejecutado (jscpd presente) — el fallo histórico de `82d686d` se reproduce o se refuta | JSON del run + intento de descarga de `quality-reports`; si no existe, ausencia REGISTRADA con diagnóstico + log completo (nota M4) |
| M5 | Orden PROC-004 | secuencia LOCAL en el checkout aislado, en orden canónico: `uv run wct mutate run` → `uv run wct accept mutate` → `uv run wct gate --tier full` | PROC-004 es regla por incremento y el workflow NO la demuestra: G-ACCEPT-MUT vive en el tier pr y full-hardening lo corre DESPUÉS del tier completo. La secuencia local sí recorre mutación → mutación de Gherkin → CRAP/DRY (el tier re-ejecuta G-MUT antes de CRAP/DRY: repetición, no reordenamiento) | tres salidas íntegras en `evidence/` con exit codes |
| M6 | Adoption smoke (pre-tag) | `gh workflow run adoption-smoke.yml --ref main` | clon limpio → bootstrap → doctor → fast → commit ≤ 120 s | URL + `time-to-green(commit)` del log |
| M7 | Orden aleatorio (TEST-006) | checkout aislado: `uv run --with pytest-randomly==5.0.0 pytest -q tests/unit tests/integration -m "not property" --randomly-seed=S` para S ∈ {1, 2, 3} + 1 corrida sin semilla (registrar la semilla que reporta) | verde en todas; si falla → registro PROC-013 (test, corrida, reintento) y decisión humana — JAMÁS reintento silencioso ni baja de umbral | salidas + entorno registrado (nota M7) |
| M8 | SBOM (R08) | checkout aislado sincronizado como CI (`uv sync --frozen --group dev --group quality`) → `uv run cyclonedx-py environment --output-file build/sbom.json` | SBOM real del candidato; alcance documentado: entorno completo con tooling; el subconjunto desplegable es `uv export --frozen --no-dev` (frontera del pip-audit de CI) | `build/sbom.json` renombrado con SHA → asset de la release |
| M9 | Integridad y coherencia de versión | `uv run wct integrity check`; `uv run wct --version` muestra `1.0.0b2`; `git diff` del lock toca solo el bloque de versión del proyecto | todo consistente; lock sin actualización incidental de dependencias | salidas |
| M10 | Smoke disparado por tag (post-puerta 3) | push del tag `v1.0.0-beta.2` | adoption-smoke verde sobre el tag antes de declarar cerrada la release | URL |

Notas de método:

- **Presupuesto del smoke (aclaración 2026-09-06)**: el límite de 120 s
  aplica al PASO `tier commit` dentro del smoke del adoptador, no al job
  `commit-gates` completo del template. Medido en la CI de `7f2fa04`:
  paso "Run commit tier" = 77 s (≤ 120); el job completo (checkout, sync,
  pip-audit, cobertura, exigible, property) = 184 s — cifra informativa,
  no presupuesto. El smoke del candidato sigue SIN medirse: M6 lo exige
  sobre el SHA final.

- **Regla de SHA candidato**: todo run remoto citado como evidencia (M1,
  M4, M6, M10) se verifica con `gh run view <id> --json headSha` igualado
  contra el SHA candidato aprobado; si difiere (hubo un push durante la
  calificación), el ítem queda NULO y se re-ejecuta sobre el SHA nuevo —
  nunca se cita un run de otro SHA como evidencia del candidato.
- M4: la conservación de evidencia NO puede asumir el artefacto
  `quality-reports` — el run histórico no encontró archivos que subir.
  Tras el run: guardar `gh run view <id> --json headSha,conclusion,jobs`,
  intentar `gh run download <id> -n quality-reports`; si el artefacto no
  existe, la AUSENCIA se registra como hallazgo con diagnóstico (qué se
  esperaba que poblara `quality/reports/` y por qué no ocurrió) y la
  evidencia es el `gh run view <id> --log` completo conservado en
  `evidence/`. Una ausencia sin explicar no es evidencia.
- M7 usa dependencia efímera con versión FIJADA (`pytest-randomly==5.0.0`,
  resuelta 2026-09-05): cero cambios en `pyproject.toml` (R10 — cualquier
  dependencia declarada requiere aprobación aparte; dejarla en dev es
  decisión futura, no bloqueante). Alcance honesto: aleatoriza SOLO
  unit+integration — la batería del tier commit (333 tests); property
  queda fuera (1 test: barajarlo es vacío) y la aceptación generada se
  verifica por mutación, no por orden. La efímera no ES un entorno
  reproducible por construcción: se registran python/uv, sha256 de
  `uv.lock`, versión del paquete efímero y semillas, para que cualquiera
  pueda repetir la corrida exacta.
- M4: si G-DRY-TOK falla de nuevo, NO se relaja el presupuesto ni se
  deduplica por conveniencia: se diagnostica, se registra y la puerta
  GO/NO-GO decide con ese rojo visible.
- Los checks de un PR no son evidencia del SHA final (el squash merge
  cambia el SHA): M1 cita el run del push a main.

## Puerta 2 — bump protegido (diff exacto a aprobar)

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -7 +7 @@
-version = "1.0.0-beta.1"
+version = "1.0.0-beta.2"
@@ -85 +85 @@
-version = "1.0.0-beta.1"
+version = "1.0.0-beta.2"
```

Más `uv lock` (sin `--upgrade`) para propagar la versión del proyecto al
lock; verificación: el diff de `uv.lock` toca únicamente el registro del
propio proyecto. Requiere bless (G-META-1 rojo por diseño hasta entonces).

## Puerta 3 — publicación (checklist, ítems de READINESS Etapa C)

- [ ] SHA candidato final y árbol aislado limpio; versión y lock consistentes (M9).
- [ ] quality verde en ese SHA; exigible aplicado con LCOV nuevo (M1, M3).
- [ ] full-hardening sin FAIL/ERROR; SKIP inventariado; SBOM no aceptado como SKIP (M4, M8).
- [ ] Orden PROC-004 documentado sin sobre-atribución al workflow (M5).
- [ ] TEST-006 con semilla/entorno, o excepción humana explícita y registrada (M7).
- [ ] Smoke limpio ≤ 120 s sin cambios al presupuesto (M6; M10 tras el tag).
- [ ] CHANGELOG/migración/limitaciones revisados; beta.1→beta.2 completo (14 commits: #25–#27 fixes CI smoke, PR-A1/A2, PR-B, PR-C+blend, PR-D, PR-E, PR-F, G1a, #38, G3a-1, G3a-2 #40).
- [ ] Autorización humana final de publicación.
- [ ] Tag `v1.0.0-beta.2` inmutable + GitHub release con `--prerelease` (beta.1 quedó `isPrerelease=false` — R07; NO modificar la release histórica); SBOM adjunto; smoke por tag verificado (M10).

Distribución propuesta: tag + prerelease del template. Sin PyPI, sin
marketplace; si alguna vez se quiere wheel/sdist, exige build +
instalación + CLI smoke + revisión de contenido del paquete ANTES de
autorizar ese canal (un tag no prueba el empaquetado).

Compatibilidad probada a declarar: Python 3.12 en CI (pyproject permite
3.11–3.14). No afirmar matriz multiversión verificada.

## GO/NO-GO (plantilla de cierre — se llena con evidencia, no con verde agregado)

| Criterio | Estado | Evidencia |
|---|---|---|
| Matriz M1–M9 completa sin rojos ocultos | ☐ | |
| Rojos/SKIP/faltantes declarados con causa | ☐ | |
| Limitaciones explícitas (G1b, subprocess G-INTROVERT, random no declarado, #12/#35, PR #33) | ☐ | |
| Tres puertas autorizadas con fecha y firma humana | ☐ | |

Un solo criterio en rojo sin decisión humana explícita = NO-GO.

## Fuera de alcance (sin cambio respecto de READINESS)

G1b (identidades, frescura en workspace, symlinks, perturbaciones),
PR #33 (decisión y audit separados), #12/#35, GA 1.0.0 (exige tres
adoptadores, continuidad, 30 días sin cambio de contrato y guía de
migración — R11), deduplicación (prioritaria solo si M4 la señala).
