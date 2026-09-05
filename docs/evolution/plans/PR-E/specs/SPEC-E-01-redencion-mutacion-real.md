# SPEC-E-01 — Las 3 redenciones con corridas reales (Coder-E1)

ADRs: [E-01](../decisions/ADR-E-01-alcance-mutacion.md),
[E-02](../decisions/ADR-E-02-gmut-full-tier.md) §2.
Escenarios: [GHERKIN-E.md](../GHERKIN-E.md) (wct-mutation-real-001).

## Paso 0 (documentar en handoff — OBLIGATORIO antes de escribir código)

1. **Matriz exit-code de `mutmut run` SIN PIPES** (redirige a archivo,
   lee `$?` después): fixture cazado (todos los mutantes mueren) → ¿?;
   fixture con sobreviviente → ¿?; fixture con tests que NO pueden correr
   (import roto) → ¿?. Documenta las tres. Si runner-roto → exit 0,
   REPÓRTALO de inmediato como hallazgo (G-MUT aprueba en falso sobre
   fixtures rotos) y propón el cierre barato antes de seguir.
2. **Convención de fixture funcional**: fija cómo resuelven imports los
   tests del fixture bajo mutmut (conftest con sys.path, o el layout del
   probe con `[project]` instalable). Documenta la receta elegida — es lo
   que los builders replican.
3. Verifica el despachador: un caso `gate-tool` con `tool: mutmut` ya
   despacha por REGISTRY["G-MUT"] con SKIP visible si mutmut falta
   (PR-C) — confirma que NO hay que tocar el runner para los casos.

## Cambios

### 1. `quality/redteam/cases.yaml` (cirugía)

Elimina F2-a, F2-b, F5-b con sus comentarios (quedan 4 hook + F4-b
heuristic con el suyo). Los reconocedores `hardcoded` y `survivor` mueren
en `_reject` (`testless` SOBREVIVE: F4-b lo usa).

### 2. `quality/redteam/cases-tool.yaml` (+3)

`{id: F2-a, failure_mode: F2, harness: gate-tool, gate: G-MUT, tool:
mutmut}` + comentario del adversario; ídem F2-b y F5-b. Sin campo
`expect` (contrato universal status==FAIL, ruling PR-C).

### 3. `tools/wct/selftest/fixtures_tools.py` (+3 builders, patrón f1_b)

Cada builder crea en su tmpdir: `pyproject.toml` con `[project] name` +
`[tool.mutmut]` (source_paths + selección de tests del fixture, según la
receta del paso 0.2), src diminuto, y tests según el adversario:
- `f2_a`: src real (p. ej. 2 funciones puras) y **NINGÚN test** — todos
  los mutantes sobreviven.
- `f2_b`: producción con un camino no ejercido (p. ej. `def total(items):
  return sum(items) * 1.0`) y test que asierte constante SOLO sobre el
  camino vacío (`assert total([]) == 0`) — el mutante del camino no
  ejercido sobrevive. Es EL caso demostración: el test pasa, la mutación
  expone que no protege nada.
- `f5_b`: test débil que deje ≥1 sobreviviente distinto de f2_b.
Los mutantes por fixture: 2-6 (runtime). El gate corre con cwd=fixture;
verifica que mutmut no deje cache escapando al repo del runner.

### 4. `tools/wct/selftest/redteam.py`

Solo la eliminación de los reconocedores muertos (`hardcoded`,
`survivor`) y su entrada en la tabla si aplica. NADA más.

### 5. `tests/unit/test_redteam_tools.py`

Parametrizado ×9 → **×12** (rojo primero: los builders no existen).
skip-if-absent honesto por herramienta sigue siendo el patrón — pero
mutmut está en quality (el suite local con quality los corren todos).

## No hacer

- No tocar `tools/wct/gate/runner.py`, `pyproject.toml`, TIERS, docs/
  (frontera E2/arquitecto).
- No convertir F4-b.
- No cambiar el alcance (`source_paths`) del repo.
- Si mutmut exit-code resulta insuficiente para el contrato status==FAIL
  del caso (p. ej. runner-roto → 0), NO maquilles el caso: repórtalo y
  espera ruling.

## Commits

1. `feat(selftest): F2-a/F2-b/F5-b cazan con corridas reales de mutmut`
2. `refactor(selftest): cases.yaml queda con hook + el residuo F4-b`

Byline `By coder.` en ambos. Suite verde en cada commit.
