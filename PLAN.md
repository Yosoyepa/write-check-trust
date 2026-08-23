# PLAN — Hardening Harness para código generado por agentes

> **Objetivo**: convertir este repositorio en la plantilla base de cualquier proyecto, de modo que se pueda afirmar con seguridad media-alta que el código producido por **cualquier** agente (Claude Code, Codex, Copilot, Cursor, Gemini, Grok, o un humano apurado) es correcto, sin boilerplate, con sentido, y respeta arquitectura, reglas y dependencias.
>
> **Nombre del proyecto**: `well_code_template` · **CLI**: `wct`
> **Evidencia de esta investigación**: [`RESEARCH.md`](RESEARCH.md)
> **Estado (v0.4.0)**: implementado y verificado — fases 0–4 completas,
> full tier 30/30 en CI. El estado real y verificable vive en
> [`docs/STATUS.md`](docs/STATUS.md); este documento es el registro de
> decisiones y diseño, no una lista de pendientes.

---

## Índice

1. [Tesis central: los dos planos](#1-tesis-central-los-dos-planos)
2. [Taxonomía de modos de fallo (F1–F15)](#2-taxonomía-de-modos-de-fallo-f1f15)
3. [Arquitectura: seis anillos de defensa](#3-arquitectura-seis-anillos-de-defensa)
4. [Separación autor/verificador](#4-separación-autorverificador)
5. [La cadena de gates](#5-la-cadena-de-gates)
6. [Especificación de hooks](#6-especificación-de-hooks)
7. [Decisión sobre ponytail](#7-decisión-sobre-ponytail)
8. [Mapeo Uncle Bob → Python](#8-mapeo-uncle-bob--python)
9. [Herramientas a construir](#9-herramientas-a-construir)
10. [Catálogo de skills](#10-catálogo-de-skills)
11. [Subagentes](#11-subagentes)
12. [Estructura del repositorio](#12-estructura-del-repositorio)
13. [El harness se testea a sí mismo](#13-el-harness-se-testea-a-sí-mismo)
14. [Portabilidad multi-proveedor](#14-portabilidad-multi-proveedor)
15. [Roadmap por fases](#15-roadmap-por-fases)
16. [Límites honestos](#16-límites-honestos)

---

## 1. Tesis central: los dos planos

Todo lo que un harness puede hacer cae en uno de dos planos, y confundirlos es el error de diseño más común.

### Plano de la Persuasión

`CLAUDE.md`, `AGENTS.md`, reglas, skills, prompts de sistema, `additionalContext` inyectado por hooks.

- **Naturaleza**: probabilística. Sube la probabilidad de buen comportamiento.
- **Portabilidad**: alta en concepto, baja en mecánica (cada proveedor lee un archivo distinto).
- **Garantía**: **ninguna**. Un agente puede ignorarlo, o simplemente no verlo tras una compactación de contexto.

### Plano de la Prueba

Comandos que retornan exit code distinto de cero.

- **Naturaleza**: determinista. Es indiferente al proveedor, al modelo, a la temperatura, y a si el agente "entendió" la regla.
- **Portabilidad**: total. `ruff check` falla igual sin importar quién escribió el código.
- **Garantía**: **binaria**.

### La regla de oro del proyecto

> **Toda regla que importe debe existir en el Plano de la Prueba. El Plano de la Persuasión solo sirve para que el agente acierte en el primer intento en vez del quinto.**

Esta regla se aplica literalmente: si al escribir una regla en `CLAUDE.md` no puedes nombrar el comando que la verifica, la regla no está implementada — es una aspiración. El plan incluye por eso un lint sobre el propio `governance/` (§5.7, gate `G-META-2`) que exige que cada regla declare su `verified_by`.

### Corolario: la seguridad "media-alta" es medible

Nada de esto es "el código es bueno". Es: *el código pasó N verificaciones independientes, cada una con un umbral declarado, y las que no se pueden automatizar están explícitamente listadas como no cubiertas.* El `wct report` (§5.8) emite exactamente ese documento, y es el entregable real del harness.

---

## 2. Taxonomía de modos de fallo (F1–F15)

No se puede diseñar defensa sin enumerar el ataque. Estos son los modos de fallo reales del código generado por agentes, con la contramedida que los cubre. Cada uno tiene un id que se usa después en los gates y en el red team suite.

| id | Modo de fallo | Síntoma observable | Contramedida | Anillo |
|---|---|---|---|---|
| **F1** | **Boilerplate / sobre-construcción** | Se pidió un helper, llegaron 3 clases, una factory, una interfaz y un `config.py` | Escalera ponytail (bias) + `dry4py` + `vulture` + revisión de diff-size + gate de nuevos archivos | 1, 5 |
| **F2** | **Reimplementar lo que ya existe** | Función nueva que duplica una existente con otro nombre | `dry4py` (estructural, no por tokens) + skill `reuse-scan` | 1, 5 |
| **F3** | **Tests decorativos** | Tests que pasan siempre; `assert True`, mocks que se aseveran a sí mismos | **Mutation testing** (`mutmut`) + `pytest-introvert` | 5, 6 |
| **F4** | **Tests que no ejercitan el SUT** | El test importa el módulo pero aseveran sobre un mock | `pytest-introvert` (port de `deintroverter4clj`) | 5 |
| **F5** | **Cobertura sin verificación** | 95 % de coverage, 0 aserciones significativas | CRAP (`crap4py`) + mutación diferencial | 5 |
| **F6** | **Violación del Dependency Rule** | `domain/` importa `sqlalchemy`, `requests`, o `fastapi` | `import-linter` con contratos `layers`/`forbidden` | 3, 5 |
| **F7** | **Ciclos de dependencia** | A → B → A | `import-linter` `acyclic_siblings` + `pydeps`/`grimp` | 5 |
| **F8** | **Filtración de detalles por los límites** | El caso de uso retorna un `Row` de SQLAlchemy o un `Request` de FastAPI | Contratos `forbidden` sobre tipos + revisión del subagente `architect` | 5, 6 |
| **F9** | **Complejidad no gestionada** | Función de 80 líneas con 6 niveles de anidamiento | `xenon` + `crap4py` + límite de mutation sites | 5 |
| **F10** | **Dependencias fantasma o innecesarias** | Se instaló `pandas` para hacer un `sum()` | `deptry` + `creosote` + peldaño 3/5 de la escalera | 5 |
| **F11** | **Código muerto** | Funciones y ramas nunca alcanzadas | `vulture` + `knip` (JS) + `coverage` | 5 |
| **F12** | **Aceptación decorativa** | El Gherkin pasa pero los valores de ejemplo no están conectados | **Gherkin mutation** (APS) | 5 |
| **F13** | **Erosión por supresión** ⚠ | El agente añade `# noqa`, `# type: ignore`, `# pragma: no cover`, `@pytest.mark.skip` para pasar el gate | **Suppression ratchet**: el conteo de supresiones solo puede bajar | 5 (meta) |
| **F14** | **Manipulación del gate** ⚠ | El agente edita `pyproject.toml`, `.importlinter`, el baseline o el manifest de mutación | **Gate integrity**: cambios a archivos de gobernanza requieren aprobación humana; `PreToolUse` los bloquea | 3, 5 (meta) |
| **F15** | **Deriva semántica** | Todo pasa, pero no resuelve lo que se pidió | Gherkin derivado de la especificación + aprobación explícita del usuario antes de codificar | 1, 6 |

⚠ **F13 y F14 son los que casi nadie implementa y los que rompen todo el resto.** Un gate que el agente puede desactivar no es un gate. La evidencia de que esto es real está en el propio `engineering.prompt` de Uncle Bob: *"Do not edit mutation testing or Gherkin acceptance mutation manifests by hand"* — él ya se topó con el problema. Nosotros lo movemos del Plano de la Persuasión al Plano de la Prueba.

### Los que no se cubren (honestidad)

- **F15 solo se mitiga**, no se resuelve. Ninguna herramienta sabe si el código hace lo correcto; solo si hace consistentemente lo que la especificación dice. El eslabón humano es la aprobación del Gherkin.
- **Correctitud algorítmica profunda** (un off-by-one en una fórmula de negocio que los tests replican con el mismo error) queda fuera. Property tests con `hypothesis` la reducen, no la eliminan.
- **Calidad de diseño subjetiva** (¿es esta la abstracción correcta?) queda en el subagente `architect` y en el humano.

---

## 3. Arquitectura: seis anillos de defensa

Los anillos van de más temprano/más barato/menos fiable a más tardío/más caro/más fiable. La idea es que un problema atrapado en el anillo 1 cuesta un token y uno atrapado en el anillo 6 cuesta un ciclo de CI.

```
┌─ Anillo 1 — INTENCIÓN ────────────────────────────────────────────┐
│  SessionStart / UserPromptSubmit                                  │
│  Inyecta: reglas de arquitectura del proyecto, escalera ponytail, │
│  presupuesto de complejidad, deuda abierta.                       │
│  Naturaleza: persuasión. No bloquea (salvo prompts vacíos).       │
├─ Anillo 2 — SESGO ────────────────────────────────────────────────┤
│  Skills + CLAUDE.md + AGENTS.md + generated/*                     │
│  El agente sabe qué comando correr y qué umbral debe alcanzar      │
│  ANTES de escribir. Reduce iteraciones, no garantiza nada.        │
├─ Anillo 3 — INTERCEPCIÓN ─────────────────────────────────────────┤
│  PreToolUse  → bloquea la escritura antes de que ocurra           │
│                (secretos, archivos de gobernanza, rutas prohibidas,│
│                 imports prohibidos en el payload del Edit)         │
│  PostToolUse → lint/format/typecheck del archivo tocado, al vuelo  │
│  Latencia objetivo: < 2 s. Solo checks por archivo.               │
├─ Anillo 4 — GATE DE TURNO ────────────────────────────────────────┤
│  Stop / SubagentStop / PostToolBatch                              │
│  El agente NO puede terminar el turno con el árbol en rojo.       │
│  Corre `wct gate --tier fast` sobre el diff. Bloquea con exit 2   │
│  y devuelve el fallo por stderr para que el agente lo arregle.    │
├─ Anillo 5 — GATE DE COMMIT ───────────────────────────────────────┤
│  pre-commit + PreToolUse sobre `Bash(git commit *)`               │
│  `wct gate --tier commit`: la suite completa sobre el diff.       │
│  Mismos comandos que CI → el agente nunca "descubre" el fallo     │
│  en CI. Latencia aceptable: 30–120 s.                             │
├─ Anillo 6 — GATE DE CI + VERIFICACIÓN ADVERSARIA ─────────────────┤
│  GitHub Actions / GitLab CI                                       │
│  `wct gate --tier full` (mutación, Gherkin mutation, archmetrics) │
│  + subagente `verifier` que NO escribió el código                 │
│  + red team suite del propio harness                              │
│  Latencia: minutos. Es la única capa que un agente no puede saltar.│
└───────────────────────────────────────────────────────────────────┘
```

### Reglas de diseño transversales de los anillos

1. **Un anillo nunca es la única defensa de un modo de fallo relevante.** F6 (dependency rule) se chequea en el anillo 3 (heurístico sobre el payload) *y* en el 5 (`import-linter` real). Si el anillo 3 falla abierto, el 5 aún atrapa.
2. **Los anillos 3 y 4 fallan cerrado.** Cualquier excepción interna del guard → `sys.exit(2)`. Ver §6.4.
3. **El anillo 5 y el 6 corren exactamente el mismo comando.** Cero divergencia entre local y CI. Si `wct gate --tier commit` pasa localmente y CI falla, es un bug del harness, no del código.
4. **El anillo 6 es el único autorizado para escribir baselines.** Los ratchets se actualizan solo desde `main`, no desde el turno de un agente.

---

## 4. Separación autor/verificador

El hallazgo estructural de `swarm-forge`: **cada rol tiene una sección `## Does Not Own`, y el autor nunca verifica su propio trabajo.**

Uncle Bob lo implementa con tmux + git worktrees + un daemon de handoffs. Eso es válido pero pesado. La versión mínima que preserva la propiedad esencial:

| Rol | Owns | Does Not Own | Implementación |
|---|---|---|---|
| **specifier** | Convertir la petición en Gherkin, obtener aprobación humana | Escribir código de producción | Skill `spec-first` + subagente `specifier` |
| **coder** | TDD, implementación mínima, tests unitarios | Mutación, CRAP, DRY, arquitectura | Sesión principal + skill `tdd-loop` |
| **cleaner** | CRAP ≤ umbral, DRY, splits que preserven comportamiento | Introducir comportamiento nuevo; correr mutación | Subagente `cleaner` |
| **architect** | Las 4 fases (§8), añadir checks automáticos de arquitectura | La suite QA end-to-end del specifier | Subagente `architect` |
| **hardener** | Mutación, Gherkin mutation, matar survivors | Cambiar diseño | Subagente `hardener` |
| **verifier / QA** | Adversarial: intentar refutar que el trabajo está hecho | Arreglarlo | Subagente `verifier` |

### La regla no negociable

> **El subagente que ejecuta un gate no puede ser el mismo que escribió el código que el gate evalúa, y no tiene permiso de escritura sobre el código, los tests, ni los archivos de gobernanza.**

Se implementa con `tools`/`disallowedTools` en la definición del agente. Un `verifier` con `tools: [Read, Grep, Glob, Bash]` y sin `Edit`/`Write` no puede "arreglar" el gate haciéndolo laxo — solo puede reportar.

### Modos de operación

Tres niveles, para no imponer una orquestación de 6 agentes a quien quiere arreglar un typo:

- **`solo`** (default): sesión única, anillos 1–5 activos, `verifier` corre en el anillo 6 (CI).
- **`pair`**: sesión principal codea, subagente `verifier` corre en el anillo 4 antes de cada `Stop`. Modela el `two-pack`.
- **`swarm`**: pipeline completa specifier → coder → cleaner → architect → hardener → verifier, cada uno en su worktree (`isolation: "worktree"`). Modela el `six-pack`. Opt-in explícito, coste alto.

El modo se declara en `governance/policy.yaml` y se puede subir/bajar por sesión.

---

## 5. La cadena de gates

Un solo comando, tres tiers. `wct gate --tier {fast|commit|full}`.

Todo gate: (a) tiene un **id estable** (`G-…`), (b) declara su **umbral**, (c) declara si es **duro** (bloquea) o **ratchet** (solo puede mejorar), (d) opera sobre el **diff** por defecto y sobre todo el repo con `--all`.

### 5.1 Tier `fast` — anillos 3 y 4 (objetivo < 10 s)

| id | Gate | Comando | Umbral | Tipo |
|---|---|---|---|---|
| `G-FMT` | Formato | `ruff format --check <diff>` | 0 diferencias | duro |
| `G-LINT` | Lint | `ruff check <diff>` | 0 findings | duro |
| `G-IMPORT-ORDER` | Orden de imports | `ruff check --select I <diff>` | 0 | duro |
| `G-TYPE` | Tipos | `mypy <diff-modules>` | 0 errores | duro |
| `G-TEST-FAST` | Tests afectados | `pytest --testmon -q` | 0 fallos | duro |
| `G-SECRET` | Secretos | `detect-secrets-hook --baseline .secrets.baseline` | 0 nuevos | duro |
| `G-SUPPRESS` | Supresiones | `wct ratchet suppressions` | ≤ baseline | ratchet |
| `G-TODO` | Marcadores | `wct check markers` | `ponytail:`/`TODO` con owner+issue | duro |

`G-IMPORT-ORDER` es explícitamente el reemplazo de `isort` que el usuario nombró — ver §5.9.

### 5.2 Tier `commit` — anillo 5 (objetivo < 120 s)

Todo lo de `fast`, más:

| id | Gate | Comando | Umbral | Tipo |
|---|---|---|---|---|
| `G-TEST` | Suite completa | `pytest -q -p no:randomly --cov --cov-branch --cov-report=lcov:lcov.info` | 0 fallos | duro |
| `G-TEST-RANDOM` | Independencia de tests | `pytest -q -p randomly` | 0 fallos | duro |
| `G-COV-DIFF` | Cobertura del diff | `diff-cover coverage.xml --fail-under=90` | ≥ 90 % líneas nuevas | duro |
| `G-COV-TOTAL` | Cobertura total | `coverage report --fail-under=<baseline>` | ≥ baseline | ratchet |
| `G-CRAP` | CRAP por función | `crap4py src/ --lcov lcov.info --max-crap <T>` | ≤ T (§5.3) | duro |
| `G-CC` | Complejidad | `xenon --max-absolute B --max-modules A --max-average A src/` | grado | duro |
| `G-DRY` | Duplicación estructural | `wct dry src/ --threshold 0.82 --min-lines 4` | 0 clusters nuevos | ratchet |
| `G-DRY-TOK` | Duplicación por tokens | `jscpd src/ --min-lines 5 --threshold 0` | 0 nuevos | ratchet |
| `G-ARCH` | Contratos de arquitectura | `lint-imports --config .importlinter` | 0 violaciones | duro |
| `G-ARCH-CYCLE` | Ciclos | contrato `acyclic_siblings` | 0 | duro |
| `G-DEPS` | Dependencias | `deptry src/` | 0 unused/missing/transitive | duro |
| `G-DEAD` | Código muerto | `vulture src/ --min-confidence 80` | ≤ baseline | ratchet |
| `G-INTROVERT` | Honestidad de tests | `wct introvert tests/` | 0 `:introverted` nuevos | ratchet |
| `G-SAST` | SAST | `bandit -q -r src/` + `semgrep --config governance/semgrep/` | 0 high/medium | duro |
| `G-CVE` | Vulnerabilidades | `pip-audit` | 0 críticas/altas | duro |
| `G-DOC` | Docstrings públicos | `interrogate -f <baseline> src/` + `pydoclint src/` | ≥ baseline | ratchet |
| `G-COMMIT-MSG` | Mensaje de commit | `cz check` / `gitlint` | conventional | duro |
| `G-META-1` | Integridad de gates | `wct verify-integrity` | hash match | duro |
| `G-META-2` | Reglas verificables | `wct verify-governance` | toda regla con `verified_by` | duro |

### 5.3 Tier `full` — anillo 6 (minutos)

Todo lo de `commit`, más:

| id | Gate | Comando | Umbral | Tipo |
|---|---|---|---|---|
| `G-MUT` | Mutación (diferencial) | `wct mutate --diff --max-workers 8` | 0 survivors en código cambiado | duro |
| `G-MUT-SITES` | Tamaño de archivo | `wct mutate --count` | ≤ 100 mutation sites/archivo | duro |
| `G-ACCEPT` | Aceptación Gherkin | `wct accept run` | 0 fallos | duro |
| `G-ACCEPT-MUT` | Mutación de Gherkin | `wct accept mutate --level soft` | 0 mutantes sobrevivientes | duro |
| `G-GHERKIN-DRY` | DRY del IR de Gherkin | `wct accept ir-dry` | 0 duplicados exactos | ratchet |
| `G-ARCHMETRICS` | Métricas A/I/D | `wct archmetrics --healthy-threshold 0.3` | 0 paquetes en pain/useless nuevos | ratchet |
| `G-PROP` | Property tests | `pytest -m property` | 0 fallos | duro |
| `G-SBOM` | SBOM + licencias | `cyclonedx-py` + `licensecheck` | licencias permitidas | duro |
| `G-REDTEAM` | El harness funciona | `wct selftest redteam` | 100 % de diffs malos rechazados | duro |
| `G-HOOKS-WIRED` | Hooks cableados | `wct doctor --ci` | todos presentes | duro |

### El umbral de CRAP: la decisión abierta

Los datos en conflicto:

- Las herramientas de Uncle Bob publican **30+ = "crappy"**.
- Su `cleaner.prompt` exige **CRAP ≤ 6**.
- `crap4py` no trae default; exige `--max-crap N` explícito.

CRAP ≤ 6 con la fórmula `CC² × (1−cov)³ + CC` implica, en la práctica: si `CC = 6` necesitas coverage 100 % exacto (porque `36 × (1−cov)³` debe ser ≈ 0); con `CC = 10` necesitas coverage ≥ ~96 %. Es un umbral que fuerza *simultáneamente* funciones pequeñas y cobertura por rama casi total. Es exigente pero es precisamente el punto: es el umbral que hace imposible F5 y F9 a la vez.

**Propuesta**: escalera de adopción, declarada en `governance/thresholds.yaml`.

| Perfil | `--max-crap` | Para |
|---|---|---|
| `strict` | **6** | Nuevo código en greenfield. Es el default de la plantilla. |
| `standard` | **15** | Migración de un proyecto existente |
| `legacy` | **30** | Punto de entrada; solo con ratchet activo bajando |

Con una regla adicional: **el umbral aplica al código cambiado siempre en `strict`, independientemente del perfil del repo.** Un repo `legacy` no autoriza escribir código nuevo malo. Esto es lo mismo que hace `diff-cover`, aplicado a CRAP.

### 5.4 Baselines y ratchets

Un ratchet es un gate cuyo umbral es "el valor de la última vez, o mejor". Es el mecanismo que permite adoptar el harness en un repo existente sin bloquearlo el primer día.

`governance/baselines/*.json` — un archivo por métrica, versionado, con:
```json
{
  "metric": "suppressions",
  "value": 47,
  "recorded_at": "2026-08-11T00:00:00Z",
  "commit": "<sha>",
  "recorded_by": "ci",
  "breakdown": {"noqa": 31, "type-ignore": 12, "no-cover": 4, "skip": 0}
}
```

Reglas:
- Solo CI en `main` puede escribir baselines (`wct ratchet --update`). Nunca un agente en su turno.
- Un ratchet **nunca** sube salvo con `wct ratchet --raise --reason "<texto>" --approved-by "<humano>"`, que deja registro en `governance/ratchet-log.md`.
- Todo ratchet aparece en `wct report` con su trayectoria, para que el estancamiento sea visible.

### 5.5 Cobertura vs. mutación: por qué ambas

`G-COV-DIFF ≥ 90 %` es cheap y atrapa el 80 % de F3. Pero coverage no verifica aserciones: un test que llama a la función y no asevera nada da 100 % de cobertura. `G-MUT` es la única prueba de que los tests **detectan cambios de comportamiento**. Y `G-INTROVERT` es la única prueba de que las aserciones tocan el SUT y no un mock.

Los tres miden cosas distintas y ninguna implica a las otras:

| | ¿Se ejecuta el código? | ¿Se asevera algo? | ¿Se asevera sobre el SUT? |
|---|---|---|---|
| `coverage` | ✅ | ❌ | ❌ |
| `mutation` | ✅ | ✅ | ❌ (un mock bien configurado mata mutantes) |
| `introvert` | ❌ | ✅ | ✅ |

### 5.6 Meta-gates: proteger los gates de sus usuarios

**`G-META-1` — Gate integrity.** El conjunto de archivos que definen los gates (`governance/**`, `pyproject.toml` secciones de tooling, `.importlinter`, `.pre-commit-config.yaml`, `.github/workflows/**`, `.claude/settings.json`) tiene un manifest de hashes en `governance/integrity.lock`.

- `PreToolUse` bloquea `Edit`/`Write` sobre esas rutas cuando la sesión no tiene la marca de autorización humana (§6.2).
- `wct verify-integrity` recalcula y compara. En CI, un mismatch sin el commit de autorización correspondiente **falla el build**.
- Actualizar la lock requiere `wct integrity --bless --reason "<texto>"`, que escribe también en `governance/integrity-log.md`.

**`G-SUPPRESS` — Suppression ratchet.** Cuenta `# noqa`, `# type: ignore`, `# pragma: no cover`, `@pytest.mark.skip`, `@pytest.mark.xfail`, `--disable` en configs, y entradas en allowlists de `detect-secrets`/`vulture`/`semgrep`. El conteo total solo puede bajar. Además, cada supresión nueva debe llevar código de regla y justificación en la misma línea:
```python
x = frobnicate()  # noqa: E501 — URL literal de la API, no se puede partir
```
Sin justificación → `G-LINT` la rechaza (regla propia de `ruff`/`flake8` custom o un check de `wct`).

**`G-META-2` — Reglas verificables.** Cada regla en `governance/rules/*.yaml` debe declarar `verified_by:` con el id de un gate existente o el literal `human`. Reglas con `verified_by: human` aparecen listadas en `wct report` bajo "no automatizado". Esto convierte la regla de oro (§1) en un gate.

**`G-HOOKS-WIRED`.** `wct doctor --ci` parsea `.claude/settings.json` (más los settings de plugin) y afirma que cada hook del spec §6 está presente, con el comando esperado. Sin esto, borrar un hook desactiva silenciosamente un anillo entero.

### 5.7 Gate de aceptación: cómo se ve concretamente

Adaptación del Acceptance Pipeline Specification a Python, con `pytest-bdd` como runner:

```
features/*.feature
   │  wct accept parse           (port del gherkin-parser a Python, o bb si está)
   ▼
build/accept/ir.json             (IR JSON canónico)
   │  wct accept ir-dry          → G-GHERKIN-DRY
   │  wct accept generate        (genera entrypoints pytest-bdd)
   ▼
build/accept/test_*.py
   │  pytest build/accept        → G-ACCEPT
   ▼
   │  wct accept mutate --level soft
   │     muta valores de ejemplo en el IR, re-evalúa con el runner adapter caliente
   ▼
build/accept/mutation-report.json → G-ACCEPT-MUT
```

Lo que el proyecto debe escribir (según el spec): generador de entrypoints, runtime de aceptación, step handlers, runner adapter. Lo que la plantilla provee: los tres primeros como plantilla genérica, y el runner adapter como proceso persistente que lee jobs por stdin.

Regla de autoría del Gherkin (del `specifier.prompt`): **usar parámetros de Gherkin para todo campo que pueda variar**, porque son exactamente los que el mutador puede mutar. Un `Scenario` con valores hardcodeados es inmune a la mutación y por tanto no verificable.

### 5.8 `wct report` — el entregable

Un único comando que produce el documento de aseguramiento:

```
$ wct report --format md > QUALITY.md
```

Contenido: por cada gate, su estado, su umbral, su valor actual, su trayectoria si es ratchet; la lista explícita de modos de fallo F1–F15 con qué gate los cubre; la lista de reglas con `verified_by: human`; y las supresiones activas con su justificación. Es el documento que responde a "¿con qué seguridad puedo afirmar que este código está bien?" sin exagerar.

### 5.9 flake8 e isort (lo que el usuario pidió explícitamente)

El usuario nombró `flake8` e `isort`. Recomendación: **`ruff` como motor único**, con los dos disponibles como perfil de compatibilidad.

Razones: `ruff` implementa las reglas de pycodestyle/pyflakes (`E`,`W`,`F`), isort (`I`), bugbear (`B`), comprehensions (`C4`), pyupgrade (`UP`), y un subconjunto de bandit (`S`) — en un binario, órdenes de magnitud más rápido, con un solo config. En un harness donde el gate corre en `PostToolUse` (anillo 3, presupuesto < 2 s por archivo) y en cada `Stop`, la latencia del linter deja de ser un detalle de comodidad y pasa a ser una decisión arquitectónica: `flake8` + `isort` + `black` como tres procesos separados en cada edición es inviable.

Provisión concreta:
- `governance/lint/ruff.toml` — perfil canónico, con la tabla de equivalencia documentada regla-por-regla contra flake8/isort.
- `governance/lint/legacy/` — `.flake8`, `.isort.cfg`, config de `black`, activables con `wct config --lint-profile legacy` para repos que ya los tienen o cuyo equipo los exige. El gate `G-LINT` cambia de comando, no de umbral.
- `pylint` se mantiene aparte y opt-in: se usa por sus reglas de **diseño** (`too-many-arguments`, `too-many-instance-attributes`, `duplicate-code`) que `ruff` no cubre, no por su lint de estilo.

---

## 6. Especificación de hooks

Todo en `.claude/settings.json` del proyecto (no en agentes de plugin — §RESEARCH 4.5: los agentes de plugin no pueden declarar `hooks`).

### 6.1 Tabla completa

| Evento | Matcher | Script | Función | Bloquea | Timeout |
|---|---|---|---|---|---|
| `SessionStart` | `startup\|resume\|clear\|compact` | `wct hook session-start` | Inyecta reglas de arquitectura, umbrales vigentes, escalera, deuda abierta, estado de ratchets | no | 10 s |
| `Setup` | — | `wct hook setup` | Verifica toolchain, instala pre-commit, avisa de lo que falta | no | 60 s |
| `UserPromptSubmit` | — | `wct hook prompt` | Detecta petición de gran alcance → inyecta recordatorio de spec-first (F15) | no | 10 s |
| `PreToolUse` | `^(Edit\|Write\|MultiEdit\|NotebookEdit)$` | `wct hook pre-edit` | **Bloquea**: rutas de gobernanza (F14), secretos en el payload, imports prohibidos según capa (F6), archivos generados | **sí** | 10 s |
| `PreToolUse` | `^Bash$` | `wct hook pre-bash` | **Bloquea**: `git commit --no-verify`, `pytest -k` que salte la suite en el gate, `--no-strict`, edición de manifests por sed, `pip install` de deps no declaradas | **sí** | 10 s |
| `PostToolUse` | `^(Edit\|Write\|MultiEdit)$` | `wct hook post-edit` | `ruff format` + `ruff check --fix` + `mypy` del archivo; reporta a Claude por `decision: block` si queda rojo | reporta | 30 s |
| `PostToolUse` | `^Bash$` | `wct hook post-bash` | Si el comando fue un `git commit`, valida byline y mensaje | reporta | 10 s |
| `PostToolBatch` | — | `wct hook batch` | Cada N edits, corre `--tier fast` y detiene el loop si hay rojo acumulado | **sí** | 60 s |
| `Stop` | — | `wct gate --tier fast --hook` | **El gate de turno.** Exit 2 + stderr con el fallo | **sí** | 120 s |
| `SubagentStop` | — | `wct gate --tier fast --hook --role $agent_type` | Igual, con los gates que ese rol *owns* | **sí** | 120 s |
| `SubagentStart` | — | `wct hook subagent-start` | Inyecta el `Owns` / `Does Not Own` del rol | no | 10 s |
| `TaskCompleted` | — | `wct hook task-complete` | Impide cerrar una task con gates en rojo | **sí** | 60 s |
| `ConfigChange` | — | `wct hook config-change` | **Bloquea** cambios no autorizados a settings de hooks/permisos (F14) | **sí** | 10 s |
| `FileChanged` | `governance/**` | `wct hook governance-changed` | Marca la sesión como "requiere blessing" | no | 5 s |
| `PreCompact` | — | `wct hook pre-compact` | Persiste el estado de gates para que sobreviva la compactación | no | 10 s |
| `PostCompact` | — | `wct hook post-compact` | Re-inyecta reglas y umbrales (contrarresta el olvido post-compactación) | no | 10 s |
| `SessionEnd` | — | `wct hook session-end` | Escribe el resumen de la sesión en `governance/session-log/` | no | 1 s |

### 6.2 El mecanismo de "blessing"

Los archivos de gobernanza no son inmutables — serían inútiles. El diseño:

1. `PreToolUse` sobre `governance/**` y afines → `permissionDecision: "ask"` con una razón explícita que nombra el archivo y por qué está protegido. No `deny`: el humano puede autorizar.
2. Cuando el humano autoriza, `PermissionRequest`/`PostToolUse` registra la autorización en `.claude/.wct-session-blessing` (gitignored) con timestamp y archivo.
3. Al commitear, `G-META-1` exige que el cambio venga acompañado de una entrada en `governance/integrity-log.md` **firmada por un humano** (campo `approved_by`), no por el agente. Un agente que escribe `approved_by: claude` es rechazado.
4. En CI, el diff de `governance/**` sin entrada correspondiente en el log → build rojo.

Esto no es criptográficamente seguro y no pretende serlo (§16). Es suficiente para que la manipulación sea **visible y deliberada** en vez de silenciosa y accidental, que es el modo de fallo real.

### 6.3 Uso de `async` y `asyncRewake`

Los gates lentos (mutación, Gherkin mutation) no pueden correr en `Stop` — 120 s de timeout no alcanzan y frenar el loop del agente por minutos es inaceptable. Diseño:

- `PostToolBatch` con `async: true, asyncRewake: true` lanza `wct mutate --diff` en background.
- Si encuentra survivors, sale con 2 → **despierta a Claude** con el reporte como system reminder, en medio de su trabajo.
- El agente arregla los tests sin que nadie haya esperado.
- El gate duro (`--tier full`) sigue existiendo en CI: el async es una optimización de latencia, no un reemplazo.

### 6.4 Fail-closed: el requisito no negociable

De `RESEARCH.md` §4.2: **exit codes distintos de 0 y 2 son NO bloqueantes.** Un guard que crashea deja pasar todo.

Contramedidas obligatorias en cada hook de enforcement:

```python
def main() -> int:
    try:
        return run_guard()
    except Exception as exc:  # deliberadamente amplio
        print(
            f"wct guard internal error: {exc!r}\n"
            f"Blocking as a precaution. Run `wct doctor` to diagnose.",
            file=sys.stderr,
        )
        return 2  # fail CLOSED, no abierto
```

Más:
- **`wct doctor`** — self-test que verifica cada dependencia, cada config, y que cada hook de enforcement responde con exit 2 ante un input deliberadamente inválido.
- **`G-HOOKS-WIRED`** — CI afirma que los hooks están en el settings.
- **Sin dependencias pesadas en el path del hook.** Los guards del anillo 3 se importan de la stdlib + lo mínimo. Un `ImportError` en un guard es un anillo caído.

### 6.5 Detalles de implementación que hay que respetar

Consecuencias directas de la mecánica documentada en `RESEARCH.md` §4.4:

- Matchers como **regex JS sin anclar**: usar `^Edit$`, no `Edit` (que también matchea `NotebookEdit` y `MultiEdit` cuando no se quiere).
- El campo **`if` falla abierto** ante comandos Bash no parseables → nunca es la única capa. Los guards de `Bash` parsean el comando ellos mismos.
- **Límite de 10 000 caracteres** en `additionalContext`/stderr → los reportes de gate son resúmenes (top-N fallos + path al reporte completo), nunca dumps.
- **`additionalContext` se re-inyecta en `--continue`/`--resume`** → no inyectar estado volátil sin timestamp. El hook de `SessionStart` inyecta umbrales (estables), no conteos actuales (volátiles).
- Redactar el contexto inyectado como **afirmaciones factuales**, no como órdenes tipo "system command" (activa defensas anti-prompt-injection).
- Los hooks corren **sin `/dev/tty`** → toda comunicación por `systemMessage`/stderr.
- Los hooks corren **también dentro de subagentes** → los guards leen `agent_type` del input para aplicar los gates del rol.

---

## 7. Decisión sobre ponytail

### Veredicto

> **Adoptar la escalera de 7 peldaños como capa de sesgo (anillo 1–2). Versionar el texto en este repo (vendoring, MIT + atribución). NO instalar el plugin.**

### Por qué la escalera sí

F1 (boilerplate) y F2 (reimplementación) son los dos modos de fallo más frecuentes de los agentes y los **más difíciles de atrapar con gates**. `dry4py` atrapa la duplicación *después* de escrita; `vulture` atrapa el código muerto *después*. La escalera es la única contramedida que actúa *antes*, y hay evidencia medida (−54 % LOC, n=4, metodología publicada) de que funciona. Su coste en tokens es ~2.5 KB de contexto.

### Por qué no el plugin

| Motivo | Detalle |
|---|---|
| Enforcement cero | Sus 3 hooks solo inyectan contexto; ninguno bloquea. No aporta nada al Plano de la Prueba. |
| Dependencia de Node | Requiere `node` en el PATH no-interactivo. Si falta, la activación enmudece **en silencio** — exactamente el modo de fallo que §6.4 prohíbe. |
| Escribe fuera del proyecto | Inserta `statusLine` en `~/.claude/settings.json`. Una plantilla base no debe tocar la config global del usuario. |
| Footgun de desinstalación | Hay que correr `node scripts/uninstall.js` **antes** de quitar el plugin, porque el script vive dentro del plugin. |
| Superficie de mantenimiento | 52 issues y 72 PRs abiertos, 210 commits, 100k stars. Riesgo de supply chain no trivial para una plantilla que aspira a ser la base de todo. |
| Conflicto de hooks | El propio repo documenta que Gemini no puede llevar `hooks/hooks.json` en la raíz porque los nombres de evento son de Claude → la portabilidad de sus hooks es frágil. |

El texto de la regla es MIT y son 2.5 KB. Vendorizarlo cuesta un archivo y elimina las seis filas de arriba.

### Los cuatro overrides obligatorios

Sin estos, ponytail y Clean Architecture se contradicen (`RESEARCH.md` §1.5):

**Override 1 — Peldaño 5 está subordinado al Dependency Rule.**
> "¿Dependencia ya instalada? Úsala" **no aplica dentro de `domain/` ni `application/`.** En esas capas, usar una dependencia externa es la violación que `G-ARCH` rechaza. El peldaño 5 se lee: *úsala en la capa de adaptadores, detrás de un puerto.*

**Override 2 — La cláusula de testing de ponytail queda anulada.**
> "one runnable check… no frameworks, no fixtures" **no rige.** Rige `coder.prompt`: tests que *"fallarían ante una implementación plausiblemente incorrecta"*, verificado por `G-MUT` (0 survivors) y `G-COV-DIFF` (≥ 90 %). Un self-check con `assert` no sobrevive mutation testing. Esta anulación se escribe explícitamente en el archivo vendorizado, no se deja implícita.

**Override 3 — Los marcadores `ponytail:` son deuda rastreada, no comentarios.**
> Un `ponytail:` sin `owner=` y sin link a issue es rechazado por `G-TODO`. El conteo total tiene ratchet (`G-SUPPRESS` extendido). Sin esto, "diferido" se convierte en un basurero.

**Override 4 — `ultra` no está permitido.**
> Solo `off | lite | full`. `ultra` es incompatible con una plantilla de propósito general.

### Lo que se roba además de la escalera

`scripts/check-rule-copies.js` → **`wct rules check`**: falla si las copias de las reglas en los directorios por proveedor divergen del canon. Es el mecanismo que hace confiable cualquier regla multi-proveedor, y es la base de §14.

### Registro del caveat

En `governance/decisions/ADR-001-ponytail.md` queda escrito el caveat que ponytail mismo publica: **en modelos de razonamiento, deliberar la escalera puede empeorar coste y latencia.** El modo default de la plantilla es `lite` y se documenta cómo medir si conviene subirlo.

---

## 8. Mapeo Uncle Bob → Python

| Herramienta original | Lenguaje | Equivalente Python | ¿Existe? | Gate |
|---|---|---|---|---|
| `crap4go` / `crap4java` / `crap4clj` | Go/Java/Clj | **`crap4py` 0.1.1** — port declarado, mismo fórmula, `--max-crap` con exit no-cero | ✅ **Sí** | `G-CRAP` |
| `mutate4go` / `mutate4java` / `clj-mutate` | Go/Java/Clj | `mutmut` 3.7.0 (dev loop) + `cosmic-ray` 8.7.0 (CI distribuido) | ✅ Sí, distinto mecanismo | `G-MUT` |
| — *(manifest embebido + modo diferencial)* | — | **No existe.** Hay que construir `wct mutate --diff` sobre mutmut: mapa de hashes por función en `governance/mutation-manifest.json`, filtrado por diff de git | ⚠ **Construir** | `G-MUT` |
| `dry4go` / `dry4java` / `dry4clj` | Go/Java/Clj | **No existe equivalente estructural.** `jscpd` y `pylint --duplicate-code` son por tokens | ❌ **Construir `wct dry`** | `G-DRY` |
| `dependency-checker` | Clojure | `import-linter` 2.13 cubre los *contratos*; las *métricas* A/I/D no existen | ⚠ Parcial → **construir `wct archmetrics`** sobre `grimp` 3.15 | `G-ARCH`, `G-ARCHMETRICS` |
| `arch-view` | Clojure | `pydeps`, `madge` (JS), `grimp` para el grafo. Visualización: generar Mermaid desde `grimp` | ⚠ Parcial | informativo |
| `deintroverter4clj` | Clojure | **No existe** | ❌ **Construir `wct introvert`** | `G-INTROVERT` |
| `scrap` (CRAP de tests) | Clojure | **No existe.** `crap4py` excluye tests por diseño | ⚠ Fase 4 — reusar su *capa de decisión* (`remediation-mode`, `ai-actionability`) | ratchet |
| `speclj-structure-check` | Clojure | `pytest --collect-only -q` valida colección; `pytest-deadfixtures` las fixtures huérfanas | ✅ Aproximado | `G-TEST` |
| `Acceptance-Pipeline-Specification` | Go/bb | `pytest-bdd` 8.1.0 como runner; **parser/mutator/generator a construir** o usar los binarios bb/Go del spec | ⚠ **Construir** `wct accept` | `G-ACCEPT*` |
| `swarm-forge` | Clojure/tmux | Subagentes de Claude Code con `isolation: "worktree"` + `Task`/`SendMessage` | ✅ Equivalente nativo | §4 |
| — *(engineering/workflow prompts)* | — | `governance/rules/` + skills + defs de subagente | ✅ | §10, §11 |

### Los umbrales heredados, en un solo lugar

`governance/thresholds.yaml`, con la cita de origen en un comentario para que no se pierda la procedencia:

```yaml
# Fuente: unclebob/swarm-forge branch six-pack, roles/cleaner.prompt
crap:
  max: 6              # "reduce CRAP to 6 or below"
  profile: strict
mutation:
  max_sites_per_file: 100   # "more than 100 mutation sites → split before handoff"
  max_workers: 8            # hardender.prompt
  differential: true        # "Always use differential mutation against the manifest"
  max_survivors: 0
dry:
  threshold: 0.82     # default de dry4go
  min_lines: 4
  min_nodes: 20
architecture:
  healthy_threshold: 0.3    # default de dependency-checker
coverage:
  diff_min: 90
acceptance:
  mutation_level: soft      # hardender.prompt
```

### El orden de ejecución también se hereda

`hardender.prompt` es explícito: **mutación → Gherkin soft mutation → CRAP → DRY**, arreglando lo que cada herramienta encuentre *antes* de correr la siguiente. No es arbitrario: arreglar survivors de mutación añade tests, lo que cambia el coverage, lo que cambia el CRAP. Correr CRAP primero significa recalcularlo después. `wct gate --tier full` respeta ese orden, y falla rápido en el primero que rompa.

---

## 9. Herramientas a construir

Tres huecos reales, en orden de dificultad ascendente.

### 9.1 `wct archmetrics` — el más fácil

**Qué**: fan-in, fan-out, Instability, Abstractness, Distance, y clasificación en zonas, por paquete.

**Cómo**: `grimp` 3.15 ya construye el grafo de imports y ya está instalado como dependencia de `import-linter`. Las fórmulas son las de *Clean Architecture*:

```
I = fan_out / (fan_in + fan_out)
A = abstract_symbols / total_symbols
D = |A + I − 1|

healthy  cuando |A + I − 1| ≤ threshold
pain     cuando A + I < 1 − threshold      (concreto y estable)
useless  cuando A + I > 1 + threshold      (abstracto e inestable)
```

**El detalle que importa**, tomado de `dependency-checker`: un símbolo cuenta como abstracto solo si es indirección real. En Python: `typing.Protocol`, `abc.ABC`/`abstractmethod`, `typing.TypeVar` con bound, `functools.singledispatch`. **Declararlo en config no cuenta.** Sin esa regla, `A` es un número que el agente puede inflar editando un YAML.

**Salida**: JSON + tabla + diagrama Mermaid del grafo con las zonas coloreadas (reemplaza `arch-view`). Gate: ratchet — ningún paquete entra a `pain`/`useless` que no estuviera ya.

**Esfuerzo**: bajo. `grimp` hace el trabajo duro.

### 9.2 `wct dry` — el de mayor retorno

**Qué**: detección de duplicación **estructural fuzzy** en Python. Es el hueco más importante porque es exactamente el patrón que produce un agente: *misma forma, nombres y literales distintos.* `jscpd` y `pylint --duplicate-code` trabajan sobre tokens y no lo ven.

**Cómo** — port directo del algoritmo de `dry4go`:

1. Parsear con `ast`.
2. **Normalizar**: borrar identificadores, nombres locales, atributos y literales. **Preservar**: forma de función, estructura de tipos de parámetros y retorno, bloques, orden de sentencias, `if`/`for`/`while`/`with`/`try`/`match`, asignaciones, `return`, llamadas, atributos, indexado, slicing, literales compuestos (dict/list/set/tuple), operadores.
3. Fingerprint por nodo + fingerprint por función.
4. Similitud de Jaccard entre pares:
   ```
   score = |shared| / |union|
   ```
5. Clustering por umbral. Defaults heredados: `--threshold 0.82`, `--min-lines 4`, `--min-nodes 20`.

**La lección de `scrap` que hay que incorporar desde el día 1**: no reportar duplicación cruda. Convertir cada match en un **candidato de extracción** y estimar si extraer paga:

```
D_before = 0                                    si F ≤ 3 o V > 4
D_before = (max(0, F−3) × (I−1)^1.5) / (V+1)   en otro caso
extraction_pressure = max(0, D_before − D_after − H)
```
`F` = formas compartidas, `I` = instancias en el cluster, `V` = puntos variables, `H` = coste estimado del helper.

Por qué importa: sin esto, el agente "deduplica" tablas de test (muchos casos pequeños que son en realidad una matriz de cobertura) y **destruye cobertura creyendo que mejora**. `scrap` distingue explícitamente "duplicación dañina" de "matriz de cobertura"; `wct dry` debe hacerlo también. Y debe cobrar la complejidad escondida en helpers (`helper-hidden`), para que extraer no parezca gratis.

**Salida**: clusters con `remediation-mode` (`STABLE`/`LOCAL`/`SPLIT`) y `ai-actionability` (`LEAVE_ALONE`/`AUTO_TABLE_DRIVE`/`AUTO_REFACTOR`/`MANUAL_SPLIT`/`REVIEW_FIRST`) — esa capa de decisión es lo que hace la herramienta usable por un agente en vez de solo por un humano.

**Esfuerzo**: medio. El algoritmo está publicado; la parte delicada es calibrar el umbral en Python (comprehensions y decoradores generan más forma compartida que Go).

### 9.3 `wct introvert` — el más difícil

**Qué**: port de `deintroverter4clj`. Clasificar cada test según si sus aserciones **realmente trazan al System Under Test**.

**Cómo**:
1. Inferir el SUT desde los imports del archivo de test (y desde la convención `tests/test_foo.py → src/**/foo.py`).
2. Para cada `assert`, construir el árbol de procedencia de la expresión aseverada: ¿viene de una llamada al SUT? ¿de una variable ligada a una llamada al SUT? ¿de un atributo de un objeto construido por el SUT?
3. Clasificar con los mismos veredictos: `extroverted`, `likely-extroverted`, `conditional-assertion`, `cloistered`, `introverted`, `questionable`.
4. Detectar el caso específico de Python: **aserciones sobre mocks**. `mock.assert_called_once_with(...)` sin ninguna aserción sobre el valor de retorno del SUT es el equivalente Python de `:introverted` — y es dolorosamente frecuente en código generado.

**La advertencia del original hay que respetarla.** `deintroverter4clj` dice literalmente: *"It is not meant to be wired into CI gates… Verdicts are heuristic; treat them as guidance for human judgment, not pass/fail criteria."*

Por tanto `G-INTROVERT` es **ratchet, no gate duro**: el conteo de `introverted` no puede subir. Eso evita falsos positivos bloqueando trabajo legítimo y a la vez impide la degradación. Y `questionable` no cuenta para el ratchet en absoluto.

**Esfuerzo**: alto. Análisis de flujo de datos en Python es intrínsecamente difícil (duck typing, `getattr`, fixtures de pytest que inyectan por nombre de parámetro). La estrategia es empezar con el subconjunto de alta confianza (mocks aseverados sin aserción de retorno) y crecer.

### 9.4 `wct accept` — la pipeline de aceptación

Componentes según el spec: `parse` (Gherkin → IR JSON), `ir-dry`, `generate` (IR → entrypoints `pytest-bdd`), `run`, `mutate` (mutar valores de ejemplo en el IR y re-evaluar).

Decisión de build vs. reuse: el spec provee `gherkin-parser` y `gherkin-mutator` en Babashka con fallback a binarios Go, y su `engineering.prompt` dice explícitamente *"install or build those commands from that repository instead of reimplementing them"*. **Fase 1: usar los binarios upstream si `bb` o Go están disponibles.** Fase 4: port Python nativo para eliminar la dependencia de otro runtime, que es inaceptable en una plantilla de propósito general a largo plazo.

Requisito operativo del spec que hay que cumplir: **las corridas de mutación deben reportar progreso periódico** para que un agente distinga trabajo largo de un cuelgue.

### 9.5 Lo que NO se construye

- `scrap` completo (CRAP de tests) — fase 4, y solo su capa de decisión.
- Visualizador interactivo tipo `arch-view` — se reemplaza por Mermaid estático, suficiente para el propósito.
- Orquestador tmux tipo `swarm-forge` — los subagentes con `isolation: "worktree"` son el equivalente nativo y no requieren tmux.

---

## 10. Catálogo de skills

Las skills son el anillo 2: hacen que el agente sepa **qué comando correr y qué umbral alcanzar** antes de escribir. Cada una es un directorio con `SKILL.md`.

Principio de diseño heredado de las skills de Uncle Bob (`crap4go-SKILL.md`, `mutate4go-SKILL.md`): la skill dice **el comando exacto, la tabla de interpretación del resultado, y qué hacer con cada clasificación**. No explica la teoría.

| Skill | Cuándo se invoca | Qué hace |
|---|---|---|
| `wct:spec-first` | Petición de feature no trivial | Convierte la petición en Gherkin con parámetros, pide aprobación humana explícita antes de codear. Contramedida de F15. |
| `wct:tdd-loop` | Antes de escribir código de producción | El loop del `coder.prompt`: test que falla ante implementación plausiblemente incorrecta → implementación mínima → refactor |
| `wct:reuse-scan` | Antes de crear cualquier función/módulo nuevo | Recorre la escalera de 7 peldaños con comandos reales: `grep` del codebase, `wct dry` contra lo propuesto, chequeo de stdlib, `deptry` de deps instaladas |
| `wct:crap` | "reduce complejidad", CRAP alto | `crap4py` + tabla de interpretación + guía de remediación (¿partir la función o añadir tests?) |
| `wct:dry` | Duplicación sospechada | `wct dry` + cómo leer `extraction_pressure` + **la advertencia de no destruir matrices de cobertura** |
| `wct:mutate` | Tests escritos, antes del handoff | `wct mutate --diff` + qué hacer con Killed/Survived/Timeout/Uncovered (Uncovered → cubrir primero, no mutar) |
| `wct:introvert` | Tests que parecen débiles | `wct introvert` + los 6 veredictos + cómo convertir un test introvertido en extrovertido |
| `wct:arch-check` | Se tocó estructura de módulos | `lint-imports` + `wct archmetrics` + las 4 fases del `architect.prompt` |
| `wct:accept` | Feature con Gherkin | Pipeline completa `parse → ir-dry → generate → run → mutate` |
| `wct:gate` | Antes de cerrar el turno | `wct gate --tier <t>` y cómo leer el reporte |
| `wct:ratchet` | Un ratchet bloquea | Cómo leer el baseline, qué mejorar, y por qué NO se sube el umbral |
| `wct:debt` | Se difirió algo | Registra `ponytail:`/`TODO` con owner + issue, actualiza el ledger |
| `wct:adopt` | Repo existente | Wizard de adopción: mide todo, escribe baselines, elige perfil, genera configs |
| `wct:harden-review` | Rol de verificador | Checklist adversaria: intenta refutar que el trabajo está hecho |

---

## 11. Subagentes

Definiciones en `.claude/agents/`. Restricción de plataforma a respetar (`RESEARCH.md` §4.5): **un agente no puede declarar `hooks`, `mcpServers` ni `permissionMode`** — el enforcement vive en el settings del proyecto. Lo que sí se controla por agente es `tools`/`disallowedTools`, y eso es suficiente para la separación de roles.

| Agente | `tools` | `isolation` | Owns | Does Not Own |
|---|---|---|---|---|
| `specifier` | Read, Grep, Glob, Write(`features/**`) | — | Gherkin, aprobación humana | Código de producción |
| `cleaner` | Read, Edit, Bash, Grep | worktree | CRAP ≤ umbral, DRY, splits | Comportamiento nuevo; mutación |
| `architect` | Read, Grep, Glob, Edit, Bash | worktree | Las 4 fases; añadir checks de arquitectura | Suite QA del specifier |
| `hardener` | Read, Edit, Bash | worktree | Mutación, Gherkin mutation, matar survivors | Cambios de diseño |
| `verifier` | **Read, Grep, Glob, Bash** (sin Edit/Write) | — | Verificación adversaria, reporte | **Arreglar nada** |

La ausencia de `Edit` y `Write` en `verifier` es el mecanismo, no una convención: un verificador sin permiso de escritura **no puede** hacer laxo el gate que ejecuta.

Cada definición de agente lleva, textualmente y en la primera sección, su bloque `## Owns` y `## Does Not Own`, y el hook `SubagentStart` lo re-inyecta — porque tras una compactación el agente olvida su rol, y un `cleaner` que empieza a añadir features es un modo de fallo silencioso.

---

## 12. Estructura del repositorio

```
well_code_template/
├── README.md                      Qué es, cómo se usa, cómo se adopta
├── PLAN.md                        Este documento
├── RESEARCH.md                    La evidencia
├── QUALITY.md                     Generado por `wct report` — el entregable de aseguramiento
├── CLAUDE.md                      Generado desde governance/ — NO editar a mano
├── AGENTS.md                      Generado desde governance/ — NO editar a mano
│
├── governance/                    ★ FUENTE ÚNICA DE VERDAD
│   ├── policy.yaml                modo (solo|pair|swarm), perfil, flags
│   ├── thresholds.yaml            todos los números, con cita de procedencia
│   ├── rules/
│   │   ├── 00-architecture.yaml   capas, dependency rule, límites
│   │   ├── 10-testing.yaml        TDD, mutación, honestidad de tests
│   │   ├── 20-minimalism.yaml     escalera ponytail vendorizada + 4 overrides
│   │   ├── 30-style.yaml          lint, formato, naming
│   │   ├── 40-security.yaml       secretos, SAST, deps
│   │   └── 50-process.yaml        commits, deuda, handoffs
│   │       # cada regla: id, texto, rationale, verified_by (gate id | human)
│   ├── lint/
│   │   ├── ruff.toml              perfil canónico + tabla de equivalencia
│   │   └── legacy/                .flake8, .isort.cfg, black — perfil compat
│   ├── semgrep/                   reglas propias (leak de framework en el core, etc.)
│   ├── baselines/*.json           ratchets
│   ├── decisions/
│   │   ├── ADR-001-ponytail.md    veredicto + 4 overrides + caveat de coste
│   │   ├── ADR-002-ruff-vs-flake8.md
│   │   └── ADR-003-crap-threshold.md
│   ├── integrity.lock             hashes de los archivos de gobernanza
│   ├── integrity-log.md           blessings, firmadas por humanos
│   ├── ratchet-log.md             cada subida de umbral, con razón y aprobador
│   └── generated/                 ★ derivados — verificados por `wct rules check`
│       ├── CLAUDE.md
│       ├── AGENTS.md
│       ├── cursor.mdc
│       ├── windsurf.md
│       ├── copilot-instructions.md
│       └── GEMINI.md
│
├── .claude/
│   ├── settings.json              ★ los hooks (§6). El enforcement vive aquí.
│   ├── agents/                    specifier, cleaner, architect, hardener, verifier
│   └── skills/wct-*/SKILL.md      las 14 skills (§10)
│
├── tools/wct/                     el CLI
│   ├── cli.py                     `wct`
│   ├── gate/                      runner de tiers, registro de gates
│   ├── hooks/                     un módulo por hook, todos fail-closed
│   ├── dry/                       ★ a construir (§9.2)
│   ├── introvert/                 ★ a construir (§9.3)
│   ├── archmetrics/               ★ a construir (§9.1)
│   ├── mutate/                    wrapper diferencial sobre mutmut (§8)
│   ├── accept/                    pipeline de aceptación (§9.4)
│   ├── ratchet/                   baselines
│   ├── integrity/                 meta-gates
│   ├── report/                    `wct report`
│   └── doctor/                    self-test (§6.4)
│
├── quality/
│   └── redteam/                   ★ §13 — diffs deliberadamente malos
│       ├── F01-boilerplate/
│       ├── F03-fake-test/
│       ├── F06-layer-violation/
│       ├── F13-noqa-spam/
│       ├── F14-config-tamper/
│       └── ...                    uno por modo de fallo
│
├── src/example/                   proyecto ejemplo con la arquitectura de capas
│   ├── domain/                    cero dependencias externas
│   ├── application/               depende solo de domain
│   ├── adapters/                  implementa los puertos
│   └── entrypoints/               CLI, HTTP
├── tests/{unit,integration,property,acceptance}/
├── features/*.feature
│
├── .importlinter                  contratos derivados de governance/rules/00
├── .pre-commit-config.yaml        anillo 5
├── .secrets.baseline
├── pyproject.toml                 el toolchain
└── .github/workflows/
    ├── gate.yml                   anillo 6 — tier full
    └── selftest.yml               el red team suite
```

### Por qué `governance/` como fuente única

El problema multi-proveedor real: cada agente lee un archivo distinto (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`, `.github/copilot-instructions.md`, `GEMINI.md`…). Mantenerlos a mano garantiza deriva. Ponytail resolvió esto y su solución es la correcta: **un canon, N generados, y un test que falla si divergen**.

`wct rules build` genera; `wct rules check` verifica (gate en `commit`). El header de cada archivo generado dice explícitamente que es generado, y `PreToolUse` bloquea escrituras directas sobre `governance/generated/**` — es F14 aplicado a las reglas mismas.

---

## 13. El harness se testea a sí mismo

Un harness de calidad sin tests es la ironía más caro de este proyecto. Y hay un modo de fallo específico y silencioso: **un gate que dejó de funcionar se ve exactamente igual que un gate que pasa.**

### El red team suite

`quality/redteam/` — un directorio por modo de fallo, cada uno con un diff deliberadamente malo y el id del gate que debe rechazarlo:

```
quality/redteam/F03-fake-test/
├── manifest.yaml       expects: G-MUT, exit: nonzero
├── patch.diff          añade una función y un test con `assert True`
└── README.md           por qué esto debe ser rechazado
```

`wct selftest redteam` aplica cada patch en un worktree temporal, corre el gate esperado, y **falla si el gate pasa**. Gate `G-REDTEAM` en CI.

Cobertura mínima: ~30 casos, al menos dos por cada F1–F15. Casos adversarios obligatorios:

| Caso | Qué prueba |
|---|---|
| `F13-noqa-spam` | Añadir `# noqa` a 5 líneas para pasar el lint → `G-SUPPRESS` |
| `F14-config-tamper` | Subir `--max-crap` de 6 a 30 en `thresholds.yaml` → `G-META-1` |
| `F14-baseline-tamper` | Editar `governance/baselines/suppressions.json` a mano → `G-META-1` |
| `F14-manifest-edit` | Editar el manifest de mutación por sed → `pre-bash` + `G-META-1` |
| `F03-mock-only` | Test que solo asevera `mock.assert_called_once()` → `G-INTROVERT` |
| `F12-hardcoded-gherkin` | Scenario sin parámetros → `G-ACCEPT-MUT` no puede mutar nada → detectado |
| `guard-crash` | Romper deliberadamente un guard → debe salir 2 (fail-closed), no 1 |
| `hook-removed` | Borrar un hook del settings → `G-HOOKS-WIRED` |
| `no-verify` | `git commit --no-verify` → `pre-bash` |

Ese último grupo es el más importante: son los que verifican que **el harness resiste a un agente que quiere pasar el gate en vez de arreglar el código**.

### Tests del propio CLI

`wct` es código de producción y se somete a sus propios gates: `G-CRAP` con perfil `strict`, `G-MUT` con 0 survivors, `G-ARCH` con sus propias capas. Si el harness no puede pasar su propio harness, el umbral está mal calibrado y esa es información valiosa.

---

## 14. Portabilidad multi-proveedor

El requisito del usuario es explícito: *"que no importe su proveedor"*. Se cumple en tres niveles, con honestidad sobre cuánto cubre cada uno.

### Nivel 1 — Reglas (cobertura amplia, garantía nula)

`governance/generated/` produce el archivo que cada proveedor lee. `wct rules check` impide la deriva. **Garantía: ninguna** — es el Plano de la Persuasión.

### Nivel 2 — Git hooks (cobertura total, garantía media)

`pre-commit` es agnóstico: corre igual sin importar quién hizo el edit. **Esta es la capa portable de enforcement.** Su límite: `--no-verify` la salta, y algunos agentes commitean por API.

### Nivel 3 — CI (cobertura total, garantía alta)

`wct gate --tier full` en CI es la única capa que **ningún** agente puede saltar, de ningún proveedor. Es la garantía real del sistema. Todo lo demás es optimización de latencia: mueve el descubrimiento del fallo más cerca del momento de escribirlo.

### Los hooks de Claude Code son un extra, no la base

Los anillos 3 y 4 (`PreToolUse`, `Stop`) son específicos de Claude Code. Aportan **velocidad de feedback**, no garantía. Un agente de otro proveedor sobre el mismo repo obtiene los niveles 1, 2 y 3 — es decir, la garantía completa, con feedback más lento.

Diseño derivado: **ningún gate existe solo como hook de Claude Code.** Todo gate es un subcomando de `wct` invocable desde cualquier parte. Los hooks solo lo llaman antes.

Para otros proveedores con mecanismos equivalentes (Codex `AGENTS.md`, Cursor rules, hooks de Copilot cuando existan), `governance/adapters/` documenta el mapeo. Con la lección de ponytail registrada: **no colocar `hooks/hooks.json` en la raíz** — Gemini lo auto-carga y los nombres de evento de Claude lo rompen.

---

## 15. Roadmap por fases

> **Estado (v0.4.0): Fases 0–4 implementadas y verificadas** (v0.2.0–v0.4.0;
> full tier 30/30 en CI, red team 30/30). Lo que sigue abajo es el roadmap
> histórico, conservado como registro — **no** es una lista de pendientes.
> El estado real, con comandos para verificarlo por tu cuenta, vive en
> [docs/STATUS.md](docs/STATUS.md).

Cada fase entrega valor por sí sola y tiene criterio de aceptación verificable.

### Fase 0 — Fundación (el andamio)

- `governance/` con `policy.yaml`, `thresholds.yaml`, `rules/*.yaml` (todas con `verified_by`)
- `wct` con: `gate`, `rules build|check`, `doctor`, `report` (esqueleto)
- `pyproject.toml` con el toolchain de §3.2 verificado
- `.claude/settings.json` con **solo** los hooks fail-closed de anillo 3 + el `Stop` de anillo 4
- `pre-commit` + workflow de CI corriendo `--tier commit`

**Aceptación**: `wct doctor` verde. Un `# noqa` gratuito es rechazado. Un `Stop` con el árbol rojo es bloqueado. `wct rules check` falla si edito `CLAUDE.md` a mano.

### Fase 1 — Los gates que ya existen

Cablear todo lo que **no requiere construir nada**: `ruff`, `mypy`, `pytest`, `coverage`, `diff-cover`, `crap4py`, `xenon`, `import-linter`, `deptry`, `vulture`, `bandit`, `semgrep`, `pip-audit`, `detect-secrets`, `mutmut`, `jscpd`, `commitizen`.

Más: los meta-gates (`G-META-1`, `G-META-2`, `G-SUPPRESS`, `G-HOOKS-WIRED`) y el wizard `wct adopt`.

**Aceptación**: `wct gate --tier commit` corre entero en < 120 s en el proyecto ejemplo. `G-CRAP` con `--max-crap 6` pasa sobre `src/example/`. Los 4 casos adversarios de §13 (`noqa-spam`, `config-tamper`, `no-verify`, `hook-removed`) son rechazados.

### Fase 2 — Mutación diferencial y arquitectura

- `wct mutate --diff` con manifest de hashes por función (§8)
- `wct archmetrics` sobre `grimp` (§9.1)
- `PostToolBatch` con `asyncRewake` para mutación en background (§6.3)
- Subagentes `cleaner`, `hardener`, `verifier` + modo `pair`

**Aceptación**: mutación sobre el diff en < 60 s en el ejemplo. `G-MUT` con 0 survivors. `wct archmetrics` clasifica `domain/` como saludable y detecta una violación inyectada.

### Fase 3 — DRY estructural y aceptación

> **Estado: implementada (pre-0.2.0).** `wct accept` tiene `parse / ir-dry /
> generate / run / mutate` en Python puro — no existe dependencia de un
> upstream `bb`/Go; esa referencia era el diseño original, y el port nativo
> ya reemplazó cualquier fallback. Ambos criterios de aceptación se cumplen
> y corren en CI (G-DRY, G-ACCEPT-MUT).

- `wct dry` (§9.2) con la capa de decisión de `scrap`
- `wct accept` con parser/generator/mutator (upstream `bb`/Go en esta fase)
- Skills `wct:dry`, `wct:accept`, `wct:spec-first`
- Subagentes `specifier`, `architect` + modo `swarm`

**Aceptación**: `wct dry` detecta dos funciones estructuralmente idénticas con nombres y literales distintos que `jscpd` no ve. `G-ACCEPT-MUT` rechaza un Gherkin con valores hardcodeados.

### Fase 4 — Honestidad de tests y pulido

- `wct introvert` (§9.3), empezando por el subconjunto de alta confianza
- Capa de decisión de `scrap` sobre código de test
- Port Python nativo del parser/mutator de Gherkin (elimina la dependencia de `bb`/Go)
- Empaquetado como plugin de Claude Code + marketplace
- Variante polyglot (JS/TS con `jscpd`, `dependency-cruiser`, `knip`, `biome`)

**Aceptación**: `wct introvert` detecta un test que solo asevera sobre mocks. El red team suite cubre ≥ 2 casos por cada F1–F15 y pasa al 100 %. `claude plugin validate --strict` limpio.

---

## 16. Límites honestos

Un plan que promete más de lo que puede es peor que no tener plan. Esto es lo que este diseño **no** logra.

### Lo que no se puede garantizar

1. **Correctitud semántica (F15).** Ningún gate sabe si el código resuelve el problema correcto. La mitigación es Gherkin aprobado por un humano antes de codear. **Si la especificación está mal, todo el harness verifica con precisión el error equivocado.** El eslabón humano no es opcional.

2. **Bugs algorítmicos replicados en los tests.** Si el agente escribe la fórmula mal y el test la replica mal, mutación, CRAP y coverage pasan todos. `hypothesis` reduce esto (los property tests encuentran contraejemplos que los ejemplos elegidos por el autor no), no lo elimina.

3. **Calidad de diseño.** "¿Es esta la abstracción correcta?" no es computable. `archmetrics` mide propiedades del grafo, no si el grafo es una buena idea. El subagente `architect` da una segunda opinión, no una prueba.

4. **Protección criptográfica de los gates.** El mecanismo de integridad (§6.2) hace la manipulación **visible**, no **imposible**. Un agente con permiso de escritura sobre el repo y sobre CI puede, en principio, desmontar todo. La defensa real es que un humano revise el diff de `governance/**`, y el harness solo se asegura de que ese diff sea imposible de pasar desapercibido.

5. **Fail-open residual.** §6.4 mitiga el crash del guard, pero si `.claude/settings.json` no se carga en absoluto (bug de la plataforma, `disableAllHooks`, política managed), los anillos 3 y 4 desaparecen sin señal. **Por eso los anillos 5 y 6 no dependen de hooks.** El sistema degrada a "pre-commit + CI", que sigue siendo enforcement real.

### Los costes reales

| Coste | Magnitud | Mitigación |
|---|---|---|
| **Latencia de turno** | El `Stop` gate añade segundos a cada turno | Tier `fast` < 10 s; lo caro va async o a CI |
| **Latencia de CI** | Mutación + Gherkin mutation son minutos | Diferencial por defecto; `--max-workers 8`; `cosmic-ray` distribuido |
| **Tokens** | Reglas inyectadas en cada sesión | `governance/generated/` compacto; escalera en 2.5 KB; solo umbrales estables, no estado |
| **Falsos positivos** | `dry`, `introvert` y `archmetrics` son heurísticos | Los tres son **ratchets**, no gates duros. `introvert` respeta la advertencia del original. |
| **Fricción de adopción** | `--max-crap 6` es duro en un repo existente | Perfiles `legacy`/`standard`/`strict` + `strict` solo sobre código nuevo |
| **Coste de ponytail en modelos de razonamiento** | Documentado por ponytail mismo: puede empeorar coste/latencia | Default `lite`; ADR-001 documenta cómo medirlo |

### La afirmación que sí se puede hacer

Con este harness completo, la afirmación defendible no es "el código es correcto". Es:

> *Este diff pasó N verificaciones independientes con umbrales declarados: formato, lint, tipos, tests, cobertura de líneas nuevas ≥ 90 %, CRAP ≤ 6 por función, complejidad acotada, cero duplicación estructural nueva, contratos de arquitectura sin violación, cero ciclos, dependencias declaradas y sin CVEs conocidos, cero survivors de mutación en el código cambiado, y los ejemplos de la especificación demostradamente conectados a la implementación. Las supresiones activas son N y están justificadas. Lo que NO está verificado automáticamente es: [lista explícita].*

Eso es "seguridad media-alta" medida en vez de afirmada. Y es, exactamente, lo que `wct report` emite.

---

## Apéndice — Decisiones que quedan abiertas

Cinco puntos donde hay evidencia en ambas direcciones y la decisión debería tomarse con datos del proyecto real:

| # | Decisión | Opciones | Inclinación |
|---|---|---|---|
| A1 | Umbral de CRAP | 6 (cleaner.prompt) vs 30 (tabla publicada) | **6 para código nuevo**, perfiles para lo existente (§5.3) |
| A2 | Motor de mutación | `mutmut` (rápido) vs `cosmic-ray` (distribuible, filtros) | `mutmut` en el dev loop, `cosmic-ray` en CI si la suite crece |
| A3 | Gherkin | Binarios upstream (`bb`/Go) vs port Python | Upstream en fase 3, port en fase 4 — una plantilla de propósito general no debe exigir otro runtime |
| A4 | `import-linter` vs `tach` | Contratos declarativos vs módulos con interfaz explícita | `import-linter` como base (más contratos, motor `grimp` reutilizable); `tach` opt-in |
| A5 | Distribución | Plantilla `git clone` vs plugin de Claude Code vs ambos | Ambos: la plantilla trae `governance/` + `wct` + CI; el plugin trae skills y agentes. El enforcement no puede venir del plugin (§RESEARCH 4.5). |
