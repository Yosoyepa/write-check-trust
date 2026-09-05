# Plan PR-C — Red team productivo: los adversarios cazan con los gates reales

Estado: **escenarios aprobados por humano (2026-09-05)** — PROC-003 satisfecho;
ejecución sobre `fix/redteam-productive`.
Corte de código: `97a9282` (main, post PR-B/#30). Cierra el Horizonte 1.

## Objetivo de la fase

Hoy `wct selftest redteam` verifica 26/30 casos con **reconocedores paralelos**
(regex propias que imitan el juicio del gate — `redteam.py:18-69`); solo 4
(F14/F15) llaman código productivo (`pre_tool_use`). Un "30/30 adversarios
rechazados" no prueba que los gates rechacen nada: prueba que los imitadores
dicen que sí. El dossier lo clasificó (O-002) y la verificación inicial lo
midió: 87% reconocedores.

PR-C convierte el red team en **calificación real del instrumento**: cada caso
planta su defecto en un fixture aislado y el **gate o engine productivo** debe
cazarlo por su ruta real. Lo que no puede convertirse hoy queda **residuo
declarado** — nunca disfrazado.

## Clasificación de los 30 casos (verificada contra `97a9282`)

| Arnés | Casos | Qué ejecuta |
|---|---|---|
| **gate-engine** (10) | F1-a, F3-a/b, F4-a, F5-a, F6-b, F7-a/b, F13-a/b | Engine interno productivo (dry, introvert, suppressions, mutation-sites, archmetrics, cycles) sobre fixture — siempre disponible |
| **gate-tool** (12) | F1-b, F6-a, F8-a/b, F9-a/b, F10-a/b, F11-a/b, F12-a/b | Función de gate productivo (vulture, import-linter, semgrep, deptry, detect-secrets) sobre fixture — herramienta ausente = SKIP visible |
| **hook** (4) | F14-a/b, F15-a/b | `pre_tool_use` productivo (ya productivos hoy — sin cambios de fondo) |
| **heuristic** (4) | F2-a, F2-b, F4-b, F5-b | Residuo declarado: semánticas de mutación/cobertura-diff/test-hardcoded que exigirían corridas de mutmut o diff-cover con git-fixture — ver ADR-C-02 |

## Documentos

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Evidencia archivo:línea, factibilidad por caso, riesgos (runtime, aislamiento), rollback |
| [DoD.md](DoD.md) | DoD por feature, workstream, commit, revisión y merge |
| [decisions/ADR-C-01](decisions/ADR-C-01-modelo-de-ejecucion.md) | Arnés por caso, fixtures aislados, archivos por arnés, SKIP visible |
| [decisions/ADR-C-02](decisions/ADR-C-02-residuos-declarados.md) | Por qué 4 casos quedan heurísticos y qué los redime |
| [specs/SPEC-C-01](specs/SPEC-C-01-conversion.md) | Spec archivo-por-archivo con tests TDD nombrados y frontera R1/R2 |
| [GHERKIN-C.md](GHERKIN-C.md) | **Escenarios para aprobación humana** |
| [VERIFICATION.md](VERIFICATION.md) | DoD de merge, matriz, presupuesto de runtime, secuencia humana |

## Dentro / fuera

**Dentro**: framework de arneses + 22 conversiones (10 engine + 12 tool) +
relabeling de residuos + resumen por arnés + SKIP visible + tests.

**Resultado de la ejecución** (addendum de ADR-C-02): 30 casos = 12
gate-engine · 8 gate-tool · 4 hook · 6 heuristic (declarados). F8-a/b
migraron a engine (el catcher real del framework-leak por import es
archmetrics, no semgrep); F9-b y F11-b son escapes reales del repo
declarados como residuos con redención de 1 línea pendiente de
autorización humana.

**Fuera**: convertir los 4 residuos (exigen corridas de mutmut/diff-cover —
pertenecen al PR de mutación del harness y a O-004); añadir casos nuevos a
F1–F15; tocar los 4 casos hook (ya productivos); paralelizar la ejecución.
