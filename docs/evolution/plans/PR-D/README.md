# Plan PR-D — Perfiles y completitud: lo que un verde significa (O-006)

Estado: **autorizado por el humano (2026-09-05)** — "toma la decisión como
arquitecto, te doy autoría, sigue autónomamente hasta que necesites mi
bless": decisiones de arquitecto con autoría delegada, escenarios aterrizados
sin pre-aprobación, el bless del PR los sella.
Corte de código: `87c562c` (main, post PR-C/#31).

## Objetivo de la fase

Horizonte 1 tiene un criterio de salida pendiente: "`full` no oculta
capacidades ausentes" y "scopes del core y template son explícitos"
(O-006). Hoy un tier `full` con SKIPs retorna verde y nada agregado dice
QUÉ capacidad no se verificó; `wct report` clasifica reglas pero no dice
qué gate necesita qué herramienta ni qué scope escanea. Además, la
ejecución de PR-C dejó tres redenciones de ergonomía con evidencia fresca.

PR-D entrega: (1) el **perfil de capacidades** — por gate: herramienta
requerida, presencia efectiva, scope y tiers, derivado de la fuente única
del constructor del gate; (2) el resumen del tier con SKIPs declara
"capacidades no verificadas"; (3) tres redenciones: F11-b (vulture a
confianza 60 + whitelist de 1 entrada — la sonda midió 1 falso positivo en
todo el repo), `ruff check` desnudo usa el perfil del repo (footgun
documentado por el coder de PR-C), y el artefacto de aceptación deja de
embeber rutas absolutas (bug que ensució el árbol durante PR-C).

## Documentos

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Evidencia archivo:línea, sonda vulture@60, riesgos, rollback |
| [DoD.md](DoD.md) | DoD por feature, workstream, commit, revisión y merge |
| [decisions/ADR-D-01](decisions/ADR-D-01-perfil-derivado.md) | Perfil derivado del constructor vs declarado en config |
| [decisions/ADR-D-02](decisions/ADR-D-02-f11b-vulture-60-whitelist.md) | F11-b redimido con la sonda como evidencia |
| [decisions/ADR-D-03](decisions/ADR-D-03-ruff-extend.md) | `ruff check` desnudo usa el perfil del repo |
| [decisions/ADR-D-04](decisions/ADR-D-04-artefacto-relativo.md) | Artefacto de aceptación reproducible entre checkouts |
| [specs/SPEC-D-01](specs/SPEC-D-01-perfil-capacidades.md) | Coder-D1: perfil de capacidades + resumen honesto |
| [specs/SPEC-D-02](specs/SPEC-D-02-redenciones-higiene.md) | Coder-D2: F11-b + ruff extend + artefacto relativo |
| [GHERKIN-D.md](GHERKIN-D.md) | Escenarios (autorizados; el bless los sella) |
| [VERIFICATION.md](VERIFICATION.md) | DoD de merge, matriz, secuencia humana |

## Dentro / fuera

**Dentro**: capabilities en `wct report` (JSON, auditable); línea
"capacidades no verificadas" en el resumen de tiers; scopes expuestos por
el constructor de cada gate; `dead_code.vulture_min_confidence` 80→60 +
whitelist (1 entrada) + F11-b convertido a gate-tool; `[tool.ruff]
extend` en pyproject.toml; `wct accept generate` embebe ruta relativa y el
artefacto existente se regenera con la herramienta.

**Fuera**: mutación sobre el harness (PR-E: redime F2-a/F2-b/F5-b);
convertir F4-b (diff-cover con fixture git); scopes configurables desde
policy (hoy se derivan — ver ADR-D-01); tocar gates rojos por otras
razones; nuevo gate de completitud bloqueante (el perfil informa, no
bloquea — MIN-001).

## Secuenciación

PR-E (después): mutación del harness. Su valor se multiplica con estos
contratos: saber qué corre dónde y con qué scope es prerrequisito para
interpretar qué significa mutar el harness.
