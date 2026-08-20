# WCT — Write, Check, Trust

Base de hardening agnóstica al proveedor para código generado por agentes.
Combina instrucciones de desarrollo con verificadores ejecutables, hooks
fail-closed, ratchets, tests adversariales y separación entre autor y verificador.

No promete demostrar que un programa es correcto. Sí hace difícil entregar
código sin formato, sin tests útiles, con dependencias ilegales, arquitectura
erosionada, secretos, supresiones gratuitas o controles manipulados.

## Modelo de confianza

El template separa dos planos:

- **Persuasión:** `CLAUDE.md`, `AGENTS.md`, reglas de Cursor, Copilot, Gemini,
  Windsurf, skills y agentes especializados. Orientan al agente, pero no prueban nada.
- **Prueba:** `wct`, Ruff, mypy, pytest, import-linter, mutation testing,
  CRAP, Semgrep, Bandit, deptry, pre-commit y CI. Sus códigos de salida son la ley.

`governance/` es la única fuente de verdad. Las reglas específicas de cada
proveedor se generan; `wct rules check` rechaza drift manual.

## Inicio rápido

Requiere Python 3.11–3.14, `uv` y Git.

```bash
make bootstrap
uv run wct doctor
uv run wct gate --tier commit
```

`make bootstrap` instala grupos dev/quality, genera reglas, crea el lock de
integridad e instala pre-commit. Después de editar archivos protegidos con
aprobación humana, usa (en UNA sola línea; los backslashes de continuación
no sobreviven al copy-paste):

```bash
uv run wct integrity bless --approved-by "nombre" --reason "aprobado en PR #N: explicación concreta"
```

El `--reason` debe citar la evidencia de aprobación (URL de PR/comentario o
referencia `#N`): una frase en prosa no prueba nada y el comando la rechaza.
`bless` (y `ratchet record`, y `mutate update-manifest --approved-by`) es
exclusivamente humano: el hook PreToolUse bloquea al agente que lo intente,
incluido en su forma `python -m tools.wct ...`.

## Tiers

| Tier | Uso | Presupuesto |
|---|---|---:|
| `fast` | feedback durante edición y PostToolUse | 10 s |
| `commit` | pre-commit, Stop y handoff | 120 s |
| `full` | release, hardener y CI programada | 30 min |

```bash
uv run wct gate --tier fast
uv run wct gate --tier commit
uv run wct gate --tier full
```

El tier completo añade branch coverage, CRAP <= 6, complejidad, DRY
estructural, honestidad de tests, Semgrep, auditoría de dependencias
desplegables y el corpus adversarial.

## Comandos propios

```bash
uv run wct rules build|check
uv run wct doctor
uv run wct report
uv run wct ratchet check
uv run wct archmetrics --json
uv run wct dry --json
uv run wct introvert --json
uv run wct mutate scan|run|update-manifest
uv run wct accept parse|ir-dry|generate|run|mutate [feature]
uv run wct selftest redteam
uv run wct adopt /ruta/a/repositorio
```

### Formateo acotado al changeset

`wct fmt` formatea SOLO el changeset (diff contra main/master más el árbol de
trabajo); `wct fmt --staged` se limita a lo staged. En proyectos con G-FMT
desactivado para adopción gradual, es el único formateo permitido para
agentes: un `ruff format` global re-formatea archivos legacy intactos y
detona G-MUT-SITES en archivos ajenos a la tarea.

```bash
uv run wct fmt            # changeset completo
uv run wct fmt --staged   # solo lo staged
```

### Manifiesto de mutación y bless atómico

`wct mutate update-manifest` regenera el manifiesto diferencial (las
funciones se identifican por fingerprint semántico `archivo::qualname`, no
por línea: insertar un import ya no invalida medio archivo). Con aprobación
humana explícita regenera también el lock en el mismo paso, así G-META-1
nunca observa un manifiesto fresco con un lock desfasado:

```bash
uv run wct mutate update-manifest --approved-by "nombre" --reason "aprobado en PR #N: motivo"
```

### Webhooks

`wct webhook` emite un envelope JSON v1 firmado con HMAC-SHA256. La URL y el
secreto solo se leen del entorno; HTTP se rechaza salvo localhost.

```bash
export WCT_WEBHOOK_URL=https://quality.example/hooks/wct
export WCT_WEBHOOK_SECRET='obtenido-desde-el-secret-store'
uv run wct webhook gate.completed --data '{"tier":"commit","status":"PASS"}'
```

El contrato está en `governance/adapters/webhook.schema.json`. El harness no
envía webhooks automáticamente hasta que el proyecto configure un receptor.

## Arquitectura de ejemplo

```text
entrypoints -> adapters -> application -> domain
```

`domain` no conoce IO ni frameworks. `application` define los puertos que usa;
los adaptadores los implementan. `.importlinter` hace cumplir la dirección y
`wct archmetrics` calcula fan-in, fan-out, `I`, `A`, `D` y ciclos. Los imports
bajo `if TYPE_CHECKING:` no cuentan como dependencia (se borran en runtime);
`importlib.import_module`/`__import__` que oculten módulos del proyecto se
reportan como violación. Las excepciones documentadas de wiring diferido
viven en `governance/thresholds.yaml` → `architecture.cycle_allowlist`.

## Ponytail

La escalera minimalista se vendorizó como una capa de sesgo, sin instalar los
hooks Node del plugin original. Tiene cuatro overrides obligatorios:

1. Una dependencia instalada no se usa dentro de domain/application si viola
   la Dependency Rule.
2. La cláusula de “un solo self-check, sin frameworks” queda anulada; mandan
   pytest, cobertura y mutation testing.
3. Todo marcador `ponytail:` requiere owner e issue y está sujeto a ratchet.
4. El modo `ultra` está prohibido.

Consulta `governance/decisions/ADR-001-ponytail.md`.

## Skills y agentes

Las 14 skills canónicas viven en `skills/`; `.claude/skills/` contiene la
copia para Claude y `plugins/write-check-trust/skills/` la distribución Codex.
Se validan con las herramientas oficiales de creación de skills/plugins.

Los roles de `.claude/agents/` son `specifier`, `coder`, `cleaner`,
`architect`, `hardener` y `verifier`. El verificador carece de Edit/Write:
quien produjo el cambio no modifica la evidencia de aprobación.

## Adopción en un repositorio existente

Primero ejecuta un inventario read-only:

```bash
uv run wct adopt ../mi-proyecto
```

Después configura capas y rutas, mide baselines reales y conserva dos reglas:

- código cambiado usa el perfil estricto;
- deuda legacy solo puede mejorar mediante ratchets.

No copies los baselines verdes de este ejemplo a un sistema legacy: medir una
ficción equivale a desactivar los gates.

## CI y bypasses

- `.pre-commit-config.yaml` ejecuta fast tier y valida Conventional Commits.
- `.github/workflows/quality.yml` corre `uv run wct integrity check` tras el
  `uv sync --frozen`: una PR que toque rutas protegidas sin bless falla en CI,
  no solo en local. El paso depende de la semántica de avisos de integridad:
  una ruta protegida ausente y NO versionada (instalaciones locales) se
  reporta como `aviso` y no falsifica un fallo en un runner limpio; una ruta
  versionada eliminada sigue siendo bloqueante; sin git, fail-closed.
- `.github/workflows/quality.yml` también ejecuta commit tier, aceptación
  mutada y red-team; `full-hardening.yml` ejecuta el tier completo
  semanalmente y bajo demanda.
- Claude Code aplica PreToolUse, PostToolUse, PostToolBatch, Stop,
  SubagentStart/Stop, ConfigChange y PostCompact.
- `git commit --no-verify`, ediciones directas de archivos protegidos y
  comandos indirectos contra el control plane se bloquean.

Un hook que crashea retorna exit 2. Nunca se interpreta como permiso.

### Runbook del mantenedor

- **Bless con baseline incluido:** el hook de pre-commit regenera
  `.secrets.baseline` (su `generated_at` cambia) a mitad del commit y aborta
  si no está staged. Inclúyelo desde el inicio: `git add .secrets.baseline
  governance/ && uv run wct integrity bless --approved-by "..." --reason
  "aprobado en PR #N: ..."`.
- **Dependabot en bloque:** para un grupo de PRs de dependencias atascadas,
  una sola rama con los cambios + `uv lock` + un único bless resuelve todas
  con el coste de una. Cierra las PRs individuales haciendo referencia a la
  consolidada.
- **Tests flaky:** registra cada flake (test, job, fecha, si pasó al rerun)
  en cuanto aparezca; la decisión de reintentos acotados o aislamiento se
  toma con datos, no en caliente.

## Versiones

La versión vive SOLO en `pyproject.toml`: `__version__` (de `example` y de
`tools.wct`) se deriva de `importlib.metadata` con fallback `0.0.0+local`
cuando el paquete no está instalado. Un bump de release no se sincroniza a
mano en dos sitios.

## Verificación del harness

```bash
uv run pytest -q
uv run wct selftest redteam   # 30 adversarios, F1–F15
uv run wct gate --tier full
```

La investigación fuente está en [RESEARCH.md](RESEARCH.md) y las decisiones,
fases, límites y catálogo de gates en [PLAN.md](PLAN.md).

## Límites honestos

Ningún linter prueba requisitos omitidos, decisiones de producto, usabilidad,
ética, rendimiento real, calibración de hardware o seguridad completa. Los
análisis DRY, A/I/D e introvert son heurísticos; por eso combinan evidencia
automática, ratchets y revisión independiente. Los gates reducen el riesgo y
la superficie de autoengaño, no sustituyen la responsabilidad humana.

