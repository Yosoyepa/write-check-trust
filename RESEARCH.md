# RESEARCH — Evidencia recolectada

> Investigación realizada el 2026-08-11 sobre repositorios reales, no memoria.
> Todo lo citado aquí fue leído en su fuente (`raw.githubusercontent.com`, GitHub API, PyPI JSON API, docs oficiales).
> Este documento es la **evidencia**. El plan que se deriva de él está en [`PLAN.md`](PLAN.md).
>
> **Advertencia para lectores y agentes**: esto es un registro histórico de
> investigación — los "huecos" y "propuestas" que describe fueron CERRADOS en
> v0.2.0–v0.4.0 (cada sección relevante lleva su nota de resolución). El estado
> actual vive en [`docs/STATUS.md`](docs/STATUS.md) y se verifica con comandos,
> no con prosa.

---

## Parte 1 — Evaluación de `DietrichGebert/ponytail`

### 1.1 Qué es

No es una librería. Es un **paquete de reglas + skills + hooks multi-proveedor** cuyo único objetivo es sesgar al agente hacia la implementación mínima. Su mecanismo central es una escalera de 7 peldaños que el agente recorre *después* de entender el problema, deteniéndose en el primero que aplique:

```
1. ¿Necesita existir?            → no: no lo hagas (YAGNI)
2. ¿Ya está en este codebase?    → reúsalo, no lo reescribas
3. ¿La stdlib lo hace?           → úsala
4. ¿Feature nativa de plataforma?→ úsala
5. ¿Dependencia ya instalada?    → úsala
6. ¿Cabe en una línea?           → una línea
7. Solo entonces: el mínimo que funciona
```

Texto completo de la regla: `AGENTS.md` (2 593 bytes) — replicado byte-a-byte en 7 ubicaciones más (`.cursor/rules/ponytail.mdc`, `.windsurf/rules/`, `.clinerules/`, `.qoder/rules/`, `.kiro/steering/`, `.agents/rules/`, `.github/copilot-instructions.md`).

### 1.2 Metadatos verificados

| Campo | Valor |
|---|---|
| Licencia | MIT |
| Versión plugin | 4.9.0 |
| Stars / forks | ~100.6k / 5.5k |
| Commits | 210 |
| Issues abiertos / PRs abiertos | 52 / 72 |
| Blobs en repo | 159 |
| Stack | Node.js (hooks + scripts de build), Markdown/JSON (reglas), `.mjs` (plugin OpenCode), dir `ponytail-mcp` |

### 1.3 Mecanismo de inyección (lo técnicamente valioso)

`hooks/claude-codex-hooks.json` — solo tres hooks, todos de inyección de contexto, ninguno bloqueante:

| Evento | Matcher | Handler | Timeout |
|---|---|---|---|
| `SessionStart` | `startup\|resume\|clear\|compact` | `node hooks/ponytail-activate.js` | 5 s |
| `SubagentStart` | *(todos)* | `node hooks/ponytail-subagent.js` | 5 s |
| `UserPromptSubmit` | — | `node hooks/ponytail-mode-tracker.js` | 5 s |

Detalle relevante: `PONYTAIL_SUBAGENT_MATCHER` acepta una regex contra `agent_type`; si está sin definir, es inválida, o el tipo no se reporta, **inyecta de todas formas** (fail-safe hacia inyectar). El modo por defecto se configura con `PONYTAIL_DEFAULT_MODE` (`lite|full|ultra|off`) o `defaultMode` en `~/.config/ponytail/config.json`.

Comandos: `/ponytail [lite|full|ultra|off]`, `/ponytail-review` (delete-list sobre el diff), `/ponytail-audit` (repo completo), `/ponytail-debt` (recolecta los marcadores `ponytail:` diferidos en un ledger), `/ponytail-gain`, `/ponytail-help`.

### 1.4 Benchmarks (declarados por el propio repo)

Metodología: sesiones headless de Claude Code editando `tiangolo/full-stack-fastapi-template`, 12 tickets, n=4, Haiku 4.5, puntuadas sobre el `git diff` resultante.

| Arm vs. baseline | LOC | tokens | coste | tiempo | safe |
|---|---|---|---|---|---|
| ponytail | −54 % | −22 % | −20 % | −27 % | 100 % |
| caveman (control de prosa terse) | −20 % | +7 % | +3 % | +2 % | 100 % |
| prompt "YAGNI + one-liners" | −33 % | −14 % | −21 % | −30 % | 95 % |

Dos honestidades del propio README que hay que registrar:

1. **Auto-corrección de marketing**: cifras previas de "80–94 % menos código" venían de benchmarks single-shot donde el baseline del modelo desnudo rellenaba con prosa. El issue [#126](https://github.com/DietrichGebert/ponytail/issues/126) lo señaló; ahora 80–94 % se presenta como *techo por tarea*, no como media.
2. **Caveat de coste**: modelos de razonamiento que gastan tokens de thinking deliberando la escalera pueden salir **peores** en coste/latencia. Se reporta explícitamente en GPT-5.5.

Las ganancias se concentran donde existe la trampa de sobre-construcción (date picker: 404 → 23 líneas; color picker: 287 → 23) y tienden a cero en código ya mínimo.

### 1.5 Los tres conflictos con Clean Architecture

Esto es el hallazgo central de la evaluación. Ponytail y Uncle Bob **no son compatibles sin más**; hay tensión real en tres puntos:

| # | Conflicto | Texto de ponytail | Texto contrario |
|---|---|---|---|
| C1 | **Peldaño 5 vs. Dependency Rule** | "¿Dependencia ya instalada? Úsala." | `architect.prompt`: "Identify and correct… framework leakage, low-level data-shape leakage"; "Keep application policy isolated from UI, filesystem, database, network, framework, and device details." → usar la dependencia instalada *en el core* es exactamente la violación que el architect debe corregir. |
| C2 | **Testing deliberadamente débil** | "non-trivial logic leaves ONE runnable check behind, the smallest thing that fails if the logic breaks (an assert-based demo/self-check or one small test file; **no frameworks, no fixtures**). Trivial one-liners need no test." | `coder.prompt`: "use TDD to specify behavior before implementation. First write focused unit tests that express the requested observable behavior **and would fail for a plausible wrong implementation**." + `hardender.prompt`: cero survivors de mutación. Un "self-check" sin framework no sobrevive mutation testing ni coverage por rama. |
| C3 | **Cero enforcement** | Todo el mecanismo es inyección de contexto. Los hooks nunca devuelven `permissionDecision: deny` ni exit 2. | Un harness de hardening necesita al menos una capa que **rechace**, no solo que sugiera. |

Adicionalmente: `/ponytail ultra` ("para cuando el codebase te ha ofendido personalmente") no tiene lugar en una plantilla de propósito general.

### 1.6 Riesgos de supply chain / operativos

- 210 commits, 52 issues y 72 PRs abiertos frente a 100k stars → superficie de mantenimiento desbalanceada.
- Requiere `node` en el **PATH no-interactivo**; si falta, la activación *silenciosamente* deja de funcionar (los skills siguen, la activación always-on enmudece).
- El plugin escribe una entrada `statusLine` en `~/.claude/settings.json` (fuera del proyecto). Desinstalar limpio exige correr `node scripts/uninstall.js` **antes** de quitar el plugin, porque el script es él mismo un archivo del plugin.
- Gemini deliberadamente no lleva `hooks/hooks.json` en la raíz porque Gemini auto-carga esa ruta y los nombres de evento son de Claude/Codex → evidencia de que la portabilidad multi-proveedor es frágil por construcción.

### 1.7 Lo que sí vale la pena robar (además de la escalera)

`node scripts/check-rule-copies.js` + `npm test`: **falla el test suite si las copias de la regla en los 8 directorios de proveedor divergen del texto compacto canónico.** Ese es el mecanismo que hace confiable una regla multi-proveedor. Es, discutiblemente, el activo más valioso del repo después de la escalera, y es trivial de replicar.

### 1.8 Veredicto

**Integrar la escalera, versionar el texto en el repo (vendoring), NO instalar el plugin.** Razonamiento y overrides exactos en `PLAN.md` §7.

---

## Parte 2 — Inventario de `github.com/unclebob` (93 repos)

### 2.1 El hallazgo

Uncle Bob pasó 2026 construyendo, en tres lenguajes en paralelo, **una suite de herramientas cuyo propósito explícito es controlar la calidad del código generado por agentes**. No es teoría de Clean Code: son binarios con umbrales numéricos y skills de Claude Code.

Nótese el patrón: `crap4{go,java,clj}`, `mutate4{go,java}`/`clj-mutate`, `dry4{go,java,clj}` — la misma tríada portada a cada lenguaje. Eso indica una arquitectura deliberada: **CRAP + Mutation + DRY es el núcleo mínimo de verificación**.

### 2.2 Repos relevantes (ordenados por relevancia para este proyecto)

| Repo | Lang | Stars | Último push | Qué es |
|---|---|---|---|---|
| `swarm-forge` | Clojure | 2 149 | 2026-08-10 | Orquestación de swarms de agentes en tmux + git worktrees, con "constitución" por capas y protocolo de handoff |
| `Acceptance-Pipeline-Specification` | Go | 170 | 2026-06-26 | Spec portable: Gherkin → JSON IR → tests generados → **mutación de Gherkin** |
| `crap4java` / `crap4go` / `crap4clj` | — | 279/14/34 | 2026 | Métrica CRAP por función: `CC² × (1−cov)³ + CC` |
| `mutate4java` / `mutate4go` / `clj-mutate` | — | 29/18/28 | 2026 | Mutation testing con manifest embebido y modo diferencial |
| `dry4java` / `dry4go` / `dry4clj` | — | 15/24/29 | 2026 | Detección de duplicación estructural fuzzy (AST normalizado + Jaccard) |
| `dependency-checker` | Clojure | 7 | 2026-06-17 | Verificador de límites de componente: fan-in/out, I, A, D, zonas |
| `deintroverter4clj` | Clojure | 5 | 2026-06-22 | **Detecta tests que pasan sin ejercitar el SUT** |
| `scrap` | Clojure | 21 | 2026-03-17 | CRAP para *test code*: complejidad estructural + presión de extracción |
| `arch-view` | Clojure | 51 | 2026-03-20 | Visor interactivo de arquitectura por capas con detección de ciclos |
| `speclj-structure-check` | Clojure | 5 | 2026-06-03 | Skill que valida estructura/anidamiento de specs antes de correr tests |
| `gospringies` | Go | 13 | 2026-05-23 | Port a Go del runner de specs |
| `FunctionalDesign`, `PPP`, `CC_SMC`, `GoVideoStore`, `BoboliaTaxes` | — | — | 2018–2024 | Código de ejemplo de los libros. Valor pedagógico, no de tooling |

Los ~70 repos restantes son ejercicios, katas, Advent of Code, juegos y material de `cleancoders.com`. **No aportan configuración ni herramientas reutilizables** — revisados y descartados para este propósito.

### 2.3 Las fórmulas y umbrales exactos

**CRAP** (`crap4go/README.md`, `crap4clj/README.md`):
```
CRAP(fn) = CC² × (1 − coverage)³ + CC
```
Tabla de interpretación publicada: 1–5 limpio · 5–30 moderado · 30+ complejo y sub-testeado.

Puntos de decisión que cuentan para CC en Go: `if`, `for`, `range`, cláusulas `case` de `switch`/type-switch, cláusulas de `select`, `&&`, `||`.

**Duplicación** (`dry4go/README.md`): normaliza el AST (identificadores, nombres locales, selectores y literales se borran; se preserva forma de función, estructura de tipos de parámetros/retorno, bloques, orden de sentencias, `if`/`for`/`range`/`switch`/`select`, asignaciones, returns, calls, selectores, indexado, slicing, literales compuestos, operadores), genera un fingerprint por nodo + uno por función, y compara con **similitud de Jaccard**:
```
score = fingerprints compartidos / fingerprints en cualquiera de las dos
```
Defaults: `--threshold 0.82`, `--min-lines 4`, `--min-nodes 20`.

**Mutación** (`mutate4go/README.md`) — 6 categorías de operadores:

| Categoría | Mutaciones |
|---|---|
| Aritmética | `+`→`-`, `-`→`+`, `*`→`/` |
| Comparación | `>`↔`>=`, `<`↔`<=` |
| Igualdad | `==`↔`!=` |
| Booleana | `true`↔`false` |
| Lógica | `&&`↔`\|\|` |
| Constante | `0`↔`1` |

Clasificación de resultados: **Killed** (bien), **Survived** (escribe un test que falle con la mutación), **Timeout** (se cuenta como killed porque el comportamiento cambió), **Uncovered** (no gastes tiempo mutando; primero cubre).

Mecanismo clave: **manifest embebido en el pie del archivo fuente** con fecha del último run + hash del texto normalizado de cada función + su rango de líneas → habilita mutación **diferencial** por defecto. Es lo que hace viable la mutación en un loop de agente.

**Métricas de arquitectura** (`dependency-checker/README.md`) — implementa directamente las métricas de *Clean Architecture*: fan-in, fan-out, Instability (I), Abstractness (A), Distance from main sequence (D), y clasificación en zonas:

- `healthy` cuando `A + I` está dentro del umbral de 1.0
- `pain` cuando `A + I < 1 − threshold` (concreto y estable → difícil de cambiar)
- `useless` cuando `A + I > 1 + threshold` (abstracto e inestable → abstracciones muertas)
- Default `:healthy-threshold 0.3`

Detalle importante: un símbolo cuenta como *abstracto* solo cuando representa indirección real (`defprotocol`, `defmulti`). **Marcarlo en config no cuenta.** Y las dependencias no listadas en `:allowed-dependencies` son violación por defecto (allowlist, no denylist), con `--init` para inferir el mapa inicial de lo observado.

**Honestidad de tests** (`deintroverter4clj/README.md`) — clasifica cada test:

| Veredicto | Significado |
|---|---|
| `:extroverted` | Al menos una aserción traza al SUT (llamada a función, lectura de var, invocación de var privada, o valor derivado de un `let` ligado al SUT) |
| `:likely-extroverted` | Llamada sin cualificar vía `:refer :all` desde namespace del SUT (heurístico) |
| `:conditional-assertion` | Las aserciones están detrás de un condicional que el analizador no pudo aplanar |
| `:cloistered` | No alcanza el SUT, pero el cuerpo llama a otro namespace de la capa de test |
| `:introverted` | No alcanza el SUT ni otros módulos de test → **el test pasa sin ejercitar nada** |
| `:questionable` | El análisis no alcanzó un veredicto confiable |

El propio README advierte: *"It is not meant to be wired into CI gates… Verdicts are heuristic; treat them as guidance for human judgment, not pass/fail criteria."* Se respeta esa advertencia en el plan (§5, tier de ratchet, no gate duro).

**Estructura de specs** (`scrap/README.md`) — CRAP aplicado al código de test. Lo verdaderamente reutilizable es su **capa de decisión para IA**, no las métricas:

- `remediation-mode`: `STABLE` | `LOCAL` | `SPLIT`
- `ai-actionability`: `LEAVE_ALONE` | `AUTO_TABLE_DRIVE` | `AUTO_REFACTOR` | `MANUAL_SPLIT` | `REVIEW_FIRST`

Y una lección de diseño que hay que copiar tal cual: SCRAP **no suma duplicación cruda al score**. Convierte los matches fuzzy en candidatos de extracción, estima si extraer paga, y **solo cobra el beneficio neto positivo**:
```
D_before = 0                                    si F ≤ 3 o V > 4
D_before = (max(0, F−3) × (I−1)^1.5) / (V+1)   en otro caso
extraction_pressure = max(0, D_before − D_after − H)
```
(`F` = formas estructurales compartidas, `I` = ejemplos repetidos en el cluster, `V` = puntos variables, `H` = coste estimado del helper.)

Además: **cobra al ejemplo la complejidad escondida en helpers** (`helper-hidden`), para que extraer no parezca automáticamente una mejora. Y distingue "duplicación dañina" de "matriz de cobertura" (muchos ejemplos pequeños que en realidad son una tabla) — porque un agente lee mal esa diferencia y destruye cobertura "deduplicando".

### 2.4 SwarmForge — la arquitectura de roles

`swarm-forge` (branch `main` es documental; los branches `two-pack`/`four-pack`/`six-pack` son ejecutables) orquesta N agentes, cada uno en su **propio git worktree**, comunicándose por archivos de handoff validados que entrega un daemon (`handoffd.bb`) — los agentes nunca hablan tmux directamente.

Tres topologías:

| Branch | Roles | Flujo |
|---|---|---|
| `two-pack` | coder, cleaner | coder → cleaner → coder |
| `four-pack` | specifier, coder, refactorer, architect | specifier → coder → refactorer → architect → specifier |
| `six-pack` | specifier, coder, cleaner, architect, hardender, QA | specifier → coder → cleaner → architect → hardender → QA → completion |

Backends por rol: `claude`, `codex`, `copilot`, `grok` (configurable línea por línea en `swarmforge.conf`) — **multi-proveedor en la misma pipeline**.

#### El principio arquitectónico

Cada `roles/<role>.prompt` tiene una sección explícita **`## Does Not Own`**. Ejemplos textuales:

- `coder.prompt`: "Do not run language mutation, CRAP, or DRY checks; the cleaner, architect, and hardender own those checks."
- `cleaner.prompt`: "Do not run mutation tests. Do not introduce new behavior."
- `architect.prompt` / `hardender.prompt` / `QA.prompt`: "Ignore the specifier's end-to-end QA suite."

**El autor nunca es su propio verificador.** Ese es el hallazgo estructural más importante de todo el repo, y es replicable sin tmux ni worktrees (§4 del plan).

#### Umbrales numéricos duros que aparecen en los prompts

Estos son los números reales que Uncle Bob usa, no convenciones genéricas:

| Fuente | Regla |
|---|---|
| `cleaner.prompt` | "Run the language CRAP tool first and **reduce CRAP to 6 or below**." |
| `cleaner.prompt` | "If any changed or new source file has **more than 100 mutation sites**, perform a reasonable behavior-preserving split before handoff." |
| `hardender.prompt` | "Use mutation to **cover the uncovered and kill survivors**." · `--max-workers 8` · "Always use differential mutation against the manifest." |
| `hardender.prompt` | Secuencia final de verificación: **mutación → Gherkin soft mutation → CRAP → DRY**, "Fix any issues each tool finds before running the next one." |
| `engineering.prompt` | "**On startup**, procure the latest version of each required CRAP, mutation, and DRY tool… Do not rely on stale cached, vendored, or preinstalled copies." |
| `local-engineering.prompt` | "Every agent except the specifier must run unit tests and acceptance tests before handoff and fix any failures." |
| `workflow.prompt` | "Use `./tmp/` in your assigned worktree for temporary files; do not use `/tmp`." · Byline obligatorio en cada commit: `By <role>.` |

CRAP ≤ 6 es **cinco veces más estricto** que el umbral convencional de 30 que publican sus propias herramientas. Esa brecha es una decisión de diseño a tomar (§5.3 del plan).

#### Reglas de testabilidad (`engineering.prompt`)

Un principio que casi nadie codifica y que resuelve un problema real de agentes:

> "Separate testable modules from environmentally unsuitable modules that open GUIs, depend on external devices, throw environment errors, emit system errors, or hang under automated tests. **Maximize testable code and minimize the unsuitable boundary.** Only testable modules should participate in tools that run tests, including unit tests, acceptance tests, coverage, mutation testing, CRAP analysis, DRY analysis that invokes tests, and property tests."

Y: "Keep property tests separate from normal verification" — los property tests no contaminan las métricas de cobertura/mutación.

#### Guardrails anti-trampa (`engineering.prompt`)

> "**Do not edit mutation testing or Gherkin acceptance mutation manifests by hand**; allow approved mutation tools to update those manifests as part of their normal runs."

Es el reconocimiento explícito de que un agente, presionado por un gate, editará el manifest en vez de arreglar el test. Se generaliza en el plan como **meta-gates** (§5.6).

#### Las 4 fases de revisión arquitectónica (`architect.prompt`)

1. **UI/Core Separation** — ¿se puede testear el comportamiento core sin UI ni IO?
2. **Dependency Rule** — módulos de alto nivel (lejos de IO) no deben depender de bajo nivel (cerca de IO); el bajo nivel depende hacia adentro vía abstracciones estables.
3. **Information Hiding & Encapsulation** — ¿exponen solo lo necesario? ¿ocultan representación e IO? ¿preservan invariantes? ¿evitan filtrar estructuras de framework o persistencia por los límites?
4. **Local Code Quality** — nombres, control de flujo, duplicación, manejo de errores, edge cases.

Más una instrucción directamente accionable para nosotros: *"Add lightweight automated architecture checks when practical, such as dependency-direction checks, forbidden-import checks, import-cycle checks, or adapter-boundary checks."*

### 2.5 Acceptance Pipeline Specification — la idea que nadie más tiene

Pipeline normal:
```
feature file → gherkin parser → JSON IR → [IR-DRY checker] → generador de entrypoints → tests generados → runner del proyecto
```

Pipeline de mutación:
```
feature file → parser → IR base → generador → tests reutilizables → gherkin mutator → runner adapter evalúa IR mutado → reporte
```

> "**Acceptance mutation means mutating Gherkin example values in the specification-derived JSON IR.** It does not mean conventional mutation testing of application source code."

Por qué importa: verifica que **los datos de ejemplo de la especificación estén realmente conectados a la aplicación**. Si cambias el valor esperado en el Gherkin y el test de aceptación sigue pasando, ese ejemplo nunca estuvo conectado a nada. Es el detector directo de "test de aceptación decorativo" — el modo de fallo más caro de los agentes, porque produce evidencia falsa de que el requisito se cumple.

Herramientas portables (Babashka, con binarios Go como fallback):
- `bb gherkin-parser <feature> <json-out>`
- `bb gherkin-ir-dry-checker [--include-exact] <ir> <report-out>` → reporta `duplicate-in-scenario`, `placeholder-variant`, `near-duplicate`, `possible-synonym`
- `bb gherkin-mutator --runner-worker "<cmd>" [opts]`

Componentes que **cada proyecto debe escribir**: generador de entrypoints, runtime de aceptación, step handlers, runner adapter (que se mantiene caliente y acepta trabajos de mutación por stdin/stdout), y scripts de conveniencia.

Advertencia del propio spec sobre el IR-DRY checker: *"Do not blindly merge steps only because they look similar. Some step texts have the same shape but different setup or assertion semantics."*

Del `specifier.prompt`, el workflow de 6 fases y dos reglas que solo tienen sentido si sabes que el Gherkin será mutado:
- "Gherkin will be mutation tested; **use Gherkin parameters for any fields that might vary.**"
- "Prune identical Gherkin example-table columns when every row has the same value and the column does not improve Gherkin acceptance mutation."

---

## Parte 3 — Verificación del ecosistema Python

Todas las versiones consultadas contra la API JSON de PyPI el 2026-08-11.

### 3.1 Existe un port de CRAP a Python

```
crap4py  0.1.1  (2026-06-24)  "CRAP score per function for Python source files"
```
Su propia descripción: *"Python port of Uncle Bob's crap4go and crap4clj."* Repo: `gabadi/crap4py`.

- CC desde el `ast` de Python por `def`/`async def`
- Coverage por **rama** desde registros `BRDA` de LCOV, intersectados con el rango de líneas de cada función
- **`--max-crap N` → exit no-cero** ⇒ es un gate de CI usable directamente
- Salta rutas ignoradas por `.gitignore` y archivos de test (`test_*.py`, `*_test.py`)
- Uso: `pytest --cov --cov-branch --cov-report=lcov:lcov.info` → `crap4py src/ --lcov lcov.info --max-crap 30`

Alternativa in-process: `pytest-crap` 0.3.0 (`pytest --crap`, `--crap-threshold`, `--crap-top-n`; usa radon + coverage + rich). Buena para feedback local; `crap4py` es el que sirve como gate.

### 3.2 Tabla de verificación completa

| Herramienta | Versión | Fecha | Rol en el harness |
|---|---|---|---|
| `ruff` | 0.16.2 | 2026-08-07 | Lint + format + isort + subset bandit, motor único |
| `flake8` | 7.3.0 | 2025-06-20 | Compat (perfil legacy) |
| `isort` | 8.0.1 | 2026-02-28 | Compat (perfil legacy) |
| `black` | 26.5.1 | 2026-05-18 | Compat (perfil legacy) |
| `pylint` | 4.0.7 | 2026-08-09 | `duplicate-code` (symilar) + reglas de diseño |
| `mypy` | 2.3.0 | 2026-07-13 | Tipos, `--strict` |
| `pyright` / `basedpyright` | 1.1.411 / 1.39.9 | 2026-06 | Segundo checker (opcional) |
| `crap4py` | 0.1.1 | 2026-06-24 | **CRAP por función + gate** |
| `pytest-crap` | 0.3.0 | 2025-12-02 | CRAP in-process (dev loop) |
| `radon` | 6.0.1 | 2023-03-26 | CC / MI / Halstead |
| `xenon` | 0.9.3 | 2024-10-21 | **Gate de complejidad** (`--max-absolute/--max-modules/--max-average`) |
| `lizard` | 1.23.0 | 2026-06-02 | CC + **copy-paste detection** multi-lenguaje (`-E duplicate`, `-C`, `-T`, `--checkstyle`) |
| `mutmut` | 3.7.0 | 2026-07-31 | Mutation testing (rápido, buen dev loop) |
| `cosmic-ray` | 8.7.0 | 2026-08-09 | Mutation testing (distribuible, filtros, sesiones) |
| `hypothesis` | 6.165.3 | 2026-08-11 | Property-based testing |
| `coverage` | 7.15.4 | 2026-08-06 | Cobertura, branch, LCOV |
| `pytest-cov` | 7.1.0 | 2026-03-21 | Integración pytest |
| `diff-cover` | 10.5.0 | 2026-08-08 | **Cobertura sobre líneas cambiadas** |
| `slipcover` | 1.0.18 | 2026-03-17 | Cobertura de bajo overhead |
| `pytest-testmon` | 2.2.0 | 2025-12-01 | Selección de tests afectados (dev loop) |
| `pytest-randomly` | 4.1.0 | 2026-04-20 | Orden aleatorio → detecta acoplamiento entre tests |
| `pytest-xdist` | 3.8.0 | 2025-07-01 | Paralelismo |
| `pytest-deadfixtures` | 3.1.0 | — | Fixtures no usadas |
| `import-linter` | 2.13 | 2026-07-03 | **Contratos de arquitectura** |
| `grimp` | 3.15 | — | Motor de grafo de imports de import-linter → **base para archmetrics** |
| `tach` | 0.35.0 | 2026-05-12 | Arquitectura modular (alternativa/complemento) |
| `pytest-archon` | 0.0.7 | 2025-09-19 | Reglas de arquitectura como tests |
| `deptry` | 0.25.1 | 2026-03-18 | Deps no usadas / faltantes / transitivas |
| `creosote` | 5.2.0 | 2026-03-28 | Deps no usadas (segunda opinión) |
| `vulture` | 2.16 | 2026-03-25 | Código muerto |
| `bandit` | 1.9.4 | 2026-02-25 | SAST Python |
| `semgrep` | 1.172.0 | 2026-07-28 | SAST multi-lenguaje con reglas propias |
| `pip-audit` | 2.10.1 | 2026-06-10 | CVEs en dependencias |
| `safety` | 3.8.1 | — | CVEs (alternativa) |
| `detect-secrets` | 1.5.0 | 2024-05-06 | Secretos + baseline |
| `interrogate` | 1.7.0 | 2024-04-07 | Cobertura de docstrings |
| `pydoclint` | 0.9.1 | 2026-07-03 | Consistencia docstring ↔ firma |
| `refurb` | 2.3.1 | 2026-04-03 | Modernización |
| `pyupgrade` | 3.21.2 | 2025-11-19 | Sintaxis moderna |
| `codespell` | 2.4.3 | 2026-07-15 | Typos |
| `pytest-bdd` | 8.1.0 | 2024-12-05 | Gherkin en pytest |
| `behave` | 1.3.3 | 2025-09-04 | Gherkin standalone |
| `pre-commit` | 4.6.2 | — | Framework de hooks de git |
| `commitizen` | 4.17.0 | 2026-07-29 | Conventional commits + versionado |
| `gitlint` | 0.19.1 | — | Lint de mensajes de commit |
| `cyclonedx-bom` | 7.3.1 | — | SBOM |
| `licensecheck` | 2026.0.8 | — | Compatibilidad de licencias |
| `nbqa` | 1.9.1 | — | Aplicar linters a notebooks |

Lado JS/TS (para la variante polyglot):

| Herramienta | Versión | Rol |
|---|---|---|
| `jscpd` | 5.0.14 | **Copy/paste detector multi-lenguaje** (v5 es Rust) |
| `dependency-cruiser` | 18.2.0 | Reglas de dependencia (equivalente a import-linter) |
| `@biomejs/biome` | 2.5.8 | Lint + format (equivalente a ruff) |
| `eslint` | 10.8.1 | Lint |
| `knip` | 6.32.1 | Código/exports/deps no usados |
| `madge` | 8.0.0 | Grafo de dependencias, ciclos |
| `ts-prune` | 0.10.3 | Exports no usados |

### 3.3 Contratos de `import-linter` 2.13

Confirmados en la doc oficial: `forbidden`, `protected`, `layers`, `independence`, `acyclic_siblings`, **más contratos custom definibles por el usuario**. Config en `.importlinter` con `[importlinter]` (`root_package`) + secciones `[importlinter:contract:<id>]`. CLI: `lint-imports`, exit no-cero en violación.

`acyclic_siblings` merece mención aparte: prohíbe ciclos entre hermanos — cubre exactamente lo que `arch-view` visualiza en rojo.

### 3.4 Los tres huecos confirmados

> **Estado (v0.4.0): RESUELTOS — los tres se construyeron en este repo.**
> DRY estructural → `tools/wct/dry/` + G-DRY; honestidad de tests →
> `tools/wct/introvert/` + G-INTROVERT; métricas A/I/D → `tools/wct/archmetrics/`
> + G-ARCHMETRICS. Esta tabla se conserva como registro del hallazgo original.

Verificado en PyPI que **no existen**: `dry4py`, `pytest-introvert`, `testintrospect`, ni equivalente Python de `dependency-checker` con métricas A/I/D.

| Hueco | Equivalente de Uncle Bob | Qué habría que construir |
|---|---|---|
| **DRY estructural fuzzy** | `dry4go` | Normalizador de AST Python → set de fingerprints → Jaccard ≥ 0.82. `jscpd` y `pylint --enable=duplicate-code` son basados en tokens y no detectan el caso "misma estructura, nombres y literales distintos" que es exactamente lo que produce un agente. |
| **Honestidad de tests** | `deintroverter4clj` | Analizador de pytest: inferir SUT de los imports, trazar las expresiones aseveradas hasta llamadas al SUT, clasificar extroverted/introverted/questionable. El más difícil de los tres. |
| **Métricas de arquitectura A/I/D** | `dependency-checker` | Fan-in/out, I, A, D, zonas de pain/uselessness por paquete. **Construible sobre `grimp`**, que ya está instalado como dependencia de import-linter. El más fácil de los tres. |

---

## Parte 4 — Mecánica del harness (Claude Code)

Consultado en `code.claude.com/docs/en/hooks` y `.../plugins-reference` el 2026-08-11.

### 4.1 Eventos disponibles

37 eventos. Los relevantes para gating de calidad:

`SessionStart` · `Setup` · `UserPromptSubmit` · `UserPromptExpansion` · `PreToolUse` · `PermissionRequest` · `PermissionDenied` · `PostToolUse` · `PostToolUseFailure` · `PostToolBatch` · `Stop` · `StopFailure` · `SubagentStart` · `SubagentStop` · `TeammateIdle` · `TaskCreated` · `TaskCompleted` · `Notification` · `MessageDisplay` · `InstructionsLoaded` · `ConfigChange` · `CwdChanged` · `DirectoryAdded` · `FileChanged` · `WorktreeCreate` · `WorktreeRemove` · `PreCompact` · `PostCompact` · `Elicitation` · `ElicitationResult` · `SessionEnd`

### 4.2 Semántica de exit codes — el detalle que decide si el harness funciona

| Exit | Efecto |
|---|---|
| `0` | Éxito. stdout se parsea como JSON. stdout se muestra como contexto **solo** en `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`; en el resto va al debug log. |
| `2` | **Error bloqueante.** stdout/JSON se ignoran; **stderr se entrega a Claude**. El efecto depende del evento. |
| cualquier otro | **Error NO bloqueante.** La acción procede. Excepción: `WorktreeCreate`, donde cualquier no-cero aborta. |

> **Consecuencia crítica de diseño:** un guard que crashea (exit 1, traceback, dependencia faltante) **deja pasar todo silenciosamente**. Cualquier hook de enforcement debe envolverse en try/except y salir 2 ante error interno. Y debe existir un self-test (`wct doctor`) más un check de CI que parsee `.claude/settings.json` y verifique que los hooks esperados están cableados. Sin eso, el harness es teatro. Se aborda en `PLAN.md` §5.6 y §6.

### 4.3 Qué puede bloquear cada evento

| Evento | Exit 2 hace | Campos JSON de decisión |
|---|---|---|
| `PreToolUse` | **Bloquea la tool call** | `hookSpecificOutput.permissionDecision`: `allow`/`deny`/`ask`/`defer` + `permissionDecisionReason`; `updatedInput`; `additionalContext` |
| `PostToolUse` | No bloquea, pero **stderr se muestra a Claude** | `decision: "block"` + `reason`; `updatedToolOutput`; `additionalContext` |
| `PostToolBatch` | **Detiene el loop agéntico** antes de la siguiente llamada al modelo | `decision: "block"` + `reason` |
| `Stop` | **Impide detenerse; continúa la conversación** | `decision: "block"` + `reason`; `additionalContext` |
| `SubagentStop` | **Impide que el subagente termine** | `decision: "block"` + `reason` |
| `UserPromptSubmit` | Bloquea el prompt **y lo borra** | `decision: "block"` + `reason`; `additionalContext` |
| `PermissionRequest` | Deniega el permiso | `hookSpecificOutput.decision.behavior`: `allow`/`deny` + `decision.updatedInput` |
| `TaskCompleted` | **Impide marcar la task como completa** | exit code o `continue: false` |
| `ConfigChange` | **Bloquea el cambio de config** (excepto `policy_settings`) | `decision: "block"` + `reason` |
| `PreCompact` | Bloquea la compactación | `decision: "block"` + `reason` |
| `SessionStart` | No bloquea | `additionalContext`, `initialUserMessage`, `watchPaths`, `sessionTitle`, `reloadSkills` |
| `SubagentStart` | No bloquea | `additionalContext` |

### 4.4 Otros detalles que condicionan el diseño

- **Tipos de handler**: `command` (exit + stdout), `http` (POST, no puede bloquear vía status — debe devolver 2xx + JSON de decisión), `mcp_tool`, `prompt` (evalúa un prompt con un LLM, timeout 30 s), `agent` (**subagente verificador con tools**, timeout 60 s, experimental).
- **Campo `if`**: sintaxis de reglas de permiso (`"Bash(git *)"`, `"Edit(src/**)"`). Solo se evalúa en eventos de tool. Es **best-effort y falla abierto** ante comandos no parseables → no sirve para allow/deny duro. En Bash: se strippean asignaciones `VAR=value` iniciales, y se chequea cada subcomando `&&`/`;` y cada `$()`/backtick. `Edit(src/**)` matchea solo `src` de nivel superior; usa `Edit(**/src/**)` para cualquier profundidad.
- **Matchers**: `*`/`""`/omitido = todos; solo letras/dígitos/`_`/`-`/espacio/`,`/`|` = string exacto o lista separada; cualquier otro carácter = **regex JS sin anclar**. `Edit.*` también matchea `NotebookEdit`; usa `^Edit$`. MCP: `mcp__<server>__<tool>`, y `.*` es **obligatorio** para matchear un servidor entero.
- **Reescritura de contenido**: `PreToolUse` → `hookSpecificOutput.updatedInput` reemplaza los argumentos de la tool. `PostToolUse` → `updatedToolOutput`. `UserPromptSubmit` **no** puede reemplazar el prompt, solo añadir `additionalContext`.
- **Límite de 10 000 caracteres** en `additionalContext`, `systemMessage` y stdout; el exceso se escribe a archivo y se reemplaza por preview + path. → los reportes de gates para el agente deben ser resúmenes, no dumps.
- **`additionalContext` se guarda en el transcript y se re-inyecta en `--continue`/`--resume`** → los valores se vuelven obsoletos. No inyectar estado volátil (p. ej. "hay 3 violaciones ahora mismo") sin marca de tiempo.
- Se recomienda redactar `additionalContext` como **afirmaciones factuales**; el fraseo imperativo tipo "system command" puede activar las defensas anti-prompt-injection.
- **`async: true`** corre en background sin bloquear; **`asyncRewake: true`** implica async y despierta a Claude en exit 2, mostrando stderr como system reminder → útil para gates lentos (mutación) sin frenar el loop.
- Todos los hooks que matchean corren **en paralelo**. Un handler duplicado entre archivos de settings corre una sola vez.
- Los hooks corren **sin terminal controlador** en macOS/Linux — no hay `/dev/tty`; usa `systemMessage` o `terminalSequence`.
- Los hooks **también corren dentro de subagentes**, con `agent_id`/`agent_type` en el input.
- Merge de configuración: `~/.claude/settings.json` → `.claude/settings.json` (committeable) → `.claude/settings.local.json` (gitignored) → managed policy. Las entradas **se fusionan**, no se reemplazan. `allowManagedHooksOnly` bloquea hooks de usuario/proyecto/plugin. `disableAllHooks` no puede desactivar los managed salvo a nivel managed.
- Timeouts por defecto: 600 s (`command`/`http`/`mcp_tool`), 30 s (`prompt`), 60 s (`agent`); `UserPromptSubmit` 30 s, `MessageDisplay` 10 s, `SessionEnd` comparte un presupuesto de 1.5 s.
- `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` disponibles como placeholders y env vars. Preferir **exec form** (con `args`) al usar placeholders.

### 4.5 Empaquetado como plugin

`.claude-plugin/plugin.json` — solo `name` es obligatorio. Campos de rutas de componentes: `skills`, `commands`, `agents`, `workflows`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`, `experimental.themes`, `experimental.monitors`, `userConfig`, `channels`, `dependencies` (con constraints semver).

Restricción decisiva: **los agentes provistos por un plugin NO pueden declarar `hooks`, `mcpServers` ni `permissionMode`** (razones de seguridad). Los agentes de plugin soportan `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation` (solo `"worktree"`).

⇒ **El enforcement tiene que vivir en `.claude/settings.json` del proyecto, no en los agentes del plugin.** El plugin puede distribuir skills, agentes y su propio `hooks/hooks.json`, pero un agente empaquetado no puede armarse sus propios hooks.

Otros: `defaultEnabled: false` para plugins que se opt-in. `claude plugin validate ./plugin --strict` trata warnings como errores (útil en CI). Campos top-level no reconocidos se ignoran → un mismo `plugin.json` puede doblar como manifest de otro ecosistema.

---

## Parte 5 — Longitud, tamaño y principios (DRY / KISS / SOLID / Clean Code)

> Investigación del 2026-08-22. Pregunta disparadora: "wct no está viendo por la longitud del código producido… veo archivos de más de 300 líneas, ¿eso aplica DRY? ¿KISS, SOLID, Clean Code?".
> Método: 6 subagentes de investigación web en paralelo (uno por práctica/métrica) + inventario local del código real + verificación empírica de tools.

### 5.1 Inventario local (qué mide WCT hoy)

Presupuesto de tamaño/complejidad ya activo en `governance/lint/ruff.toml` (reglas PL seleccionadas) y `governance/thresholds.yaml`:

| Límite | Valor WCT | Referencia industria (ruff/pylint default) | Veredicto |
|---|---|---|---|
| Statements por función (PLR0915) | **40** | 50 | WCT más estricto |
| Argumentos (PLR0913) | **5** | 5 | igual |
| Ramas (PLR0912) | **10** | 12 | WCT más estricto |
| Returns (PLR0911) | **4** | 6 | WCT más estricto |
| CC por función (C901 + xenon `--max-absolute B`) | **10** | 10 | igual |
| CRAP cambiado/legacy | **6 / 30** | — | propio |
| Boolean traps (FBT), defaults mutables (B006/B008) | prohibidos | prohibidos | igual |
| Código muerto | vulture `--min-confidence 80` | recomendado 100 | WCT más estricto |
| DRY estructural (G-DRY) | analyzer propio (extraction_pressure de unclebob/scrap) | jscpd/pylint R0801 | más profundo que tokens |
| **Longitud de archivo** | **no existe** | pylint C0302 = 1000; Sonar S104 = 1000 | **hueco** |
| **Complejidad cognitiva** | **no existe** | Sonar S3776 = 15 | **hueco** |
| **Cohesión (LCOM)** | **no existe** | LCOM4 > 1 = clase doble | **hueco** |

Realidad medida del repo (2026-08-22): en `src/` + `tools/` **solo un archivo pasa de 300 líneas** — `tools/wct/gate/runner.py` (593; el siguiente es archmetrics/analyzer.py con 270). El máximo en tests es 203.

### 5.2 Evidencia web — tamaño de archivo y función

- **Ningún estándar respalda fallar a las 300 líneas.** Clean Code (Martin): ~200 típico, ~500 techo. Google Python Style Guide: sin límite duro de archivo; "si una función pasa de ~40 líneas, considera partirla" (y su propio pylintrc desactiva toda la categoría R). Linux kernel: reglas de función (1-2 pantallas, ≤3 niveles de indentación) pero ninguna de archivo. pylint C0302 y SonarSource S104: **1000** por defecto. ESLint `max-lines` (JS): 300.
- **Empírica**: la densidad de defectos por tamaño es en U (mínimo ~161-400 LOC, Malaiya & Hatton); el tamaño predice el *conteo* de fallas, no la densidad (Ostrand/Weyuker/Bell ISSTA'04); y **churn × complejidad supera al tamaño como predictor** (Nagappan & Ball; Tornhill "Code Red": 39 codebases, el código de baja calidad concentra 15× más defectos).
- Función: Sonar S138 falla a **80** líneas; Code Complete sitúa la zona de comfort hasta ~100-200; el estudio de 450 rutinas citado da 41% menos errores ≤32 LOC.

⇒ 300+ líneas es una **bandera de revisión**, no un fallo de CI. El techo defendible para WCT: **500 LOC (sin blancos/comentarios) con ratchet** — coincide con el techo de Clean Code y el borde superior de la banda de mínima densidad.

### 5.3 Evidencia web — por principio

- **DRY**: taxonomía Type-1/2/3/4; los detectores cubren 1-2 y parte de 3; la duplicación semántica (Type-4) sigue sin solución práctica (survey arXiv 2026). Consenso moderno: duplicación de *conocimiento*, no de texto (Sandi Metz: "duplication is cheaper than the wrong abstraction"; regla de tres; AHA). Ruff **no tiene** regla de duplicación (issues #18432/#17724 abiertos). Recetas: pylint R0801 con `min-similarity-lines=10` + ignore imports/docstrings/signatures; jscpd con `min-tokens 70`, presupuesto ~5%, `--exitCode`. WCT ya va mejor por camino propio (G-DRY estructural con LEAVE_ALONE para tablas de test = MIN-008 coincide con el mejor consejo encontrado).
- **KISS/YAGNI**: los proxies medibles ya están todos cableados en WCT (tabla 5.1); nesting no tiene regla en ruff (R1702 es preview; pylint-only) — la vía correcta es complejidad cognitiva (castiga anidamiento). YAGNI se cubre con F401/F841/ARG + vulture; no existe gate de "genericidad especulativa" más allá de MIN-007.
- **SOLID**: S → parcial (próxies: cohesión LCOM4, R0904); O → human-only (consenso); L → nivel firma (mypy estricto ya lo hace); I → human-only con próxy débil (tamaño de Protocol); D → **lo más automatizable** (import-linter + secuencia principal) — WCT ya tiene ambos (G-ARCH + G-ARCHMETRICS), adelantado al ecosistema Python (no hay tool turnkey de C&K). La comunidad conscientemente deja O/I y LSP comportamental a review (Goodhart).
- **Métricas**: cognitiva validada y con umbral publicados (Sonar S3776 = **15**, porque castiga nesting sin recompensar extracción); MI **no gateable** (fórmula contestada, Teamscale la rechaza, inputs redundantes); LCOM4 (>1 componente = dos clases), tool Python `cohesion` (GPL-3.0 — conflicto potencial con licencia MIT para dependencia); coupling Ca/Ce/I ya implementado en archmetrics propio.

### 5.4 Hallazgos concretos (verificados — snapshot 2026-08-22)

> **Estado (v0.4.0): los cuatro hallazgos fueron RESUELTOS en v0.3.0.**
> (1) G-DRY-TOK lleva `--exit-code 1` (PR #15) y corre en el tier full —
> en su primera corrida real en CI cazó duplicación genuina (PR #16).
> (2) per-file-ignores ahora exige justificación por entrada y es ratchet
> que solo baja (`governance/baselines/per-file-ignores.json`, PR #13);
> la deuda restante vive en el issue #12. (3) runner.py se partió (PR #14):
> hoy 488 LOC, dentro del techo. (4) G-SIZE y G-COGNITIVE existen desde
> PR #13; LCOM4 (P6) sigue abierto por diseño. Esta sección se conserva
> como registro del diagnóstico original.

1. **G-DRY-TOK es un gate vacío cuando jscpd está instalado.** Verificado empíricamente (2026-08-22, fixture con 44% de líneas duplicadas): `jscpd <files>` sale **0** aunque encuentre clones; solo con `--exit-code 1` sale no-cero (nota: el flag es kebab-case; `--exitCode` es error de parseo). El wiring actual (`runner.py:460`) no pasa la bandera → siempre PASS. Arreglo: añadir `--exit-code 1` + config `.jscpd.json` (min-tokens 70, ignore tests/generated/`__init__`, reporte a `build/`). Medición del repo al momento del fix: **0 clones** en `src` + `tools` a min-tokens 70.
2. **Las 7 exenciones `per-file-ignores` del harness son deuda invisible.** `governance/lint/ruff.toml:121-127` suprime C901/PLR0911/0912/0915 para accept/pipeline.py, archmetrics/analyzer.py, cli.py, dry/analyzer.py, hooks/guard.py, introvert/analyzer.py, selftest/redteam.py — sin justificación por entrada (STYLE-008 solo audita supresiones inline `# noqa`, no config) y sin ratchet que las cuente. Esta es la deuda real de "boilerplate/complexidad" del harness — no la longitud de archivo.
3. **`tools/wct/gate/runner.py` (593 LOC)** es el único violador de un techo de 500. Contiene registro de gates + funciones gate + TIERS + preflight: candidato natural a partición fachada (mismo patrón que TEST-007 / `wct split-plan`).
4. Falta gate de longitud de archivo, falta complejidad cognitiva, falta métrica de cohesión (ver tabla 5.1).

### 5.5 Propuesta priorizada (RESUELTA: P1–P5 implementadas en v0.3.0; P6 sigue abierta por diseño)

> **Estado por ítem**: P1 → G-SIZE (PR #13). P2 → G-COGNITIVE (PR #13).
> P3 → auditoría per-file-ignores (PR #13). P4 → G-DRY-TOK con diente
> (PR #15, probado en CI en #16). P5 → `wct hotspots` (PR #14). P6 (LCOM4,
> advisory) permanece como candidato futuro. El texto de abajo es la
> propuesta original, conservada como registro.

- **P1 — G-SIZE**: longitud de archivo en LOC real (sin blancos/comentarios), techo **500**, analyzer AST propio (~60 líneas, patrón de dry/analyzer), tier `commit`, arranque como ratchet con baseline actual (=1: runner.py) y regla nueva STYLE-011. Excluye tests/generated (tablas = matriz de cobertura, MIN-008).
- **P2 — G-COGNITIVE**: complejidad cognitiva por función, umbral **15** (Sonar S3776), walker AST propio (algoritmo publicado de Campbell; la dep `cognitive_complexity` está dormida desde 2022 — escalera MIN-001 peldaño 3: stdlib/propio). Es la única métrica que castiga el anidamiento que CC≤10 deja pasar — patrón típico de código generado por agentes. Regla nueva STYLE-012.
- **P3 — Cerrar el agujero de `per-file-ignores`**: extender `wct check suppressions` (G-SUPPRESS) para que audite el bloque `[lint.per-file-ignores]` del perfil ruff: exigir comentario con código de regla + owner/issue (PROC-009) por entrada y contar el total como ratchet que solo baja.
- **P4 — Arreglar G-DRY-TOK** (hallazgo 1): bandera + config; opcional subirlo de `optional_tools` cuando quede demostrado en CI.
- **P5 — `wct hotspots`** (reporte, no gate): churn × CC de los últimos 90 días (Tornhill). El mejor predictor empírico de defectos; encaja con la filosofía de tendencias sobre umbrales.
- **P6 — Cohesión LCOM4** (opcional, después): analyzer propio, clases con >1 componente = bandera. Falsos positivos conocidos (dataclasses, orquestadores) → advisory primero.

**Descartado explícitamente**: MI como gate (fórmula contestada, inputs redundantes); hard-fail a 300 líneas (ninguna evidencia lo respalda); pylint completo (rompe el motor único de ADR-002/STYLE-001); gates de OCP/ISP (no estáticamente verificables — review humano, como hoy); duplicación Type-4 (sin tool práctica).

### 5.6 Fuentes principales (selección)

SonarSource Cognitive Complexity + regla S3776 (default 15) y S104 (1000 líneas); Campbell 2018 (ACM TechDebt); pylint C0302/symilar defaults; ruff issues #18432/#17724 (sin regla de duplicación) y docs PLR091x; Google Python Style Guide §3.18; Linux kernel coding style; Clean Code caps. 3-5; Code Complete §7.4; Malaiya & Denton 2000; Ostrand/Weyuker/Bell ISSTA 2004; Tornhill & Borg "Code Red" 2022; Sandi Metz "The Wrong Abstraction"; jscpd docs (verificación empírica propia del exit code); hynek.me y realpython.com para SOLID-Python; mschwager/cohesion (LCOM, GPL-3.0); radon/xenon/lizard (estado 2026: lizard activo, radon en mantenimiento).
