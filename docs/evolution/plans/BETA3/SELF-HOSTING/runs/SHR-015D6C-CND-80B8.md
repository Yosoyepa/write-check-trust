# Registro de entrega — SH-P01 (P01-IDENTIDADES), primer candidato

```text
task_id: SH-P01
contract_version: sh-p01/1
run_id: SHR-015D6C            # local opaco: el operador no asignó IDs en el encargo
coder_blind_id: COD-CA7A      # local opaco, ídem
candidate_id: CND-80B8        # local opaco, ídem
parent_candidate_id: none
mode: SH-D
base_sha: 8de9107184288f1aa72c9578a14913686c47ad7c
context_digest: |
  P01-IDENTIDADES.md  sha256=7f0143ae6e6a931735914963e242e83900ca9df2bcf445f041057d1cb9b5ac99
  GHERKIN-P01.md      sha256=6f87f2ae1e0ddd5a65b4c761ced00984b92ab005899b0905d3cf9375c684b5e5
  GOBERNANZA.md       sha256=3206c01b754e60c901ef965382590ec9b895986bd244b350ce7dc47977b72a9f
  MOLDE-WCT.md        sha256=70cef562bf7e75db6bbff24331cd11c6b077e5a80ebc504dc5a478875c4f4db6
  REGISTROS.md        sha256=fece961f0005c4432f096b1f1dd55f9df4f9f37d64b1209bc3e74b1d6479d500
candidate_manifest_digest: de207e0dc06a995918d5a8f34917744e53aae9e17c97c2aad483a7ee797e86b4
  # fórmula: sha256 de las 4 líneas "sha256  ruta" del changed_files, en ese orden
started_at: 2026-09-07T15:47:57-05:00
ended_at: 2026-09-07T16:20:21-05:00
timezone: UTC-05:00 (local del host)
```

## implementation_path

Worktree exclusivo nuevo (creado por este run, no preexistente):

- `/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8`
- rama `codex/beta3-sh-p01-identidades` creada desde `8de9107`.
- El árbol compartido (`codex/plan-beta3-moldes-evals`) no recibió checkout,
  stash, reset ni edición de archivos trackeados; los documentos sin commit
  ajenos (BETA3, G1, POST-PR36, REVIEW-G1) quedan como estaban.
- Dossier leído desde su ruta original
  `docs/evolution/plans/BETA3/SELF-HOSTING/`.
- Evidencia de corridas: `build/tmp/sh-p01-CND-80B8-evidence/` (gitignored).

## changed_files

```text
d89be6c7fa40a8f6ed21953414140c223a335a9477fdeb8145595e5c80829e5e  tools/wct/evidence/__init__.py
e27b0aa992d4ce4dc4832d8fc57c53ddaa84216f75f51eedc52d20a387473953  tools/wct/evidence/identities.py
e02cd1427420c8a6a5e2089813ad5513dae2d3def02f1b6e220edeb62ac658e6  tests/unit/test_evidence_identities.py
d3d64140477e5b67e6ee1f6967fe9cb0c4c285365b562b953043a0056b251b0e  features/wct-evidence-identities-001.feature
```

4 archivos nuevos, +589 líneas, 0 modificados, 0 borrados. Los 4 están en la
allowlist de P01 §2. Registro: este archivo (`runs/SHR-015D6C-CND-80B8.md`,
nuevo) en el árbol compartido junto al dossier.

## attempts

1. **Bootstrap red (esperada):** test escrito primero; `pytest
   tests/unit/test_evidence_identities.py` → 1 error de colección,
   `ModuleNotFoundError: No module named 'tools.wct.evidence'`. Clasificada
   bootstrap por import ausente: NO es prueba de sensibilidad semántica.
2. **Implementación del módulo:** `identities.py` + `__init__.py` (solo
   docstring). Re-ejecución: 53 passed, 1 failed — el binding falla con
   `FileNotFoundError` del feature aún inexistente (rojo análogo a bootstrap,
   por artefacto ausente, no por lógica del SUT).
3. **Feature verbatim:** bloque extraído programáticamente (awk entre fences)
   de `GHERKIN-P01.md` → `features/wct-evidence-identities-001.feature` (27
   líneas). `wct accept parse` exit 0; `wct accept ir-dry` exit 0,
   `{"findings": [], "count": 0}`. Re-ejecución focal: **54 passed**.
4. **Variante plausible local (sensibilidad, se revierte):** deduplicar antes
   de validar (`tuple(dict.fromkeys(...))` por inventario) → **5 failed**
   exactamente en `I08, I09, I10, I17, test_i21_immutable_deterministic_canonical`,
   49 passed. Revertida: 54 passed. Es calibración local del coder, no G-MUT
   y no sustituye el challenge del verifier.
5. **Gate fast 1.ª corrida:** 3 FAIL en archivos nuevos. Correcciones:
   - G-SUPPRESS: eliminé 4 supresiones `# type: ignore[...]` del test
     (innecesarias: mypy no corre sobre tests; STYLE-007 exige regla+justificación).
   - G-LINT: I001, import multi-línea colapsado a una línea (98 chars).
   - G-FMT: `ruff format` solo sobre los 3 archivos python nuevos.
6. **Gate fast 2.ª corrida:** 7/7 PASS, exit 0.
7. **Gate commit 1.ª corrida:** 19/21; G-META-1 FAIL (drift pre-bless
   esperado) y G-DEAD FAIL (`identities.py:139 unused function
   'compare_identities' (60% confidence)`).
8. **Resolución G-DEAD sin tocar gobernanza:** vulture 2.16 respeta `__all__`
   (sonda apartada de build/tmp lo confirmó: módulo con `__all__` → exit 0).
   Añadí `__all__` con exactamente los 3 nombres públicos de §3. Vulture con
   el comando exacto del gate (incluida la whitelist ADR-D-02) → exit 0.
   Nota: una corrida manual mía sin la whitelist mostró el FP preexistente
   `archmetrics/analyzer.py:24 abstract_symbols`; con la whitelist, ese FP
   está cubierto y la base 8de9107 tiene G-DEAD verde.
9. **Gate commit 2.ª corrida (final):** 20/21 PASS; único FAIL G-META-1
   (ítem 10 de checks abajo). `git diff --check` exit 0 (con intent-to-add).

## checks

| # | argv (cwd=worktree) | exit | resultado |
|---|---|---|---|
| 1 | `uv sync` (inicial) / `uv sync --all-groups` (tras incidente) | 0 | entorno |
| 2 | `uv run pytest tests/unit/test_evidence_identities.py -q` | 1→1→0 | rojos 1–2, luego 54 passed |
| 3 | `uv run wct accept parse features/wct-evidence-identities-001.feature` | 0 | IR correcto, 18 examples |
| 4 | `uv run wct accept ir-dry features/wct-evidence-identities-001.feature` | 0 | findings: [], count: 0 |
| 5 | `uv run pytest tests/unit/test_evidence_identities.py --cov=tools.wct.evidence --cov-branch --cov-report=term-missing -q` | 0 | **100%** (53 stmts, 20 branches, 0 miss, 0 partial) — medido sobre el módulo nuevo, no inferido de src/example |
| 6 | `uv run pytest --collect-only -q` | 0 | 401 tests collected |
| 7 | `uv run pytest -q` (suite completa) | 0 ×4 corridas | 401 passed (87.4s, 11.8s→con entorno parcial, 90.3s, y dentro de G-TEST ×2) |
| 8 | `uv run wct gate --tier fast` | 1→0 | final: 7/7 PASS |
| 9 | `uv run wct gate --tier commit` | 1→1 | final: 20/21 PASS, único FAIL = G-META-1 |
| 10 | `uv run wct integrity check` | 1 | drift = EXACTAMENTE `tools/wct/evidence/__init__.py` + `tools/wct/evidence/identities.py` (allowlist); pre-bless esperado, no se toca el lock |
| 11 | `git diff --check` (tras `git add -N`) | 0 | sin errores de blancos |
| 12 | `uv run vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60` | 0 | comando exacto del gate |

Outputs completos: `build/tmp/sh-p01-CND-80B8-evidence/{focal-run-final.txt,
gate-fast.txt, gate-commit.txt, full-suite.txt, accept-parse.json,
accept-ir-dry.json}`.

## case_bindings

| Caso | nodeid (todos con prefijo `tests/unit/test_evidence_identities.py::`) | Resultado |
|---|---|---|
| I01–I18 (18 filas) | `test_identity_table_row[Ixx]` | PASSED, 1 corrida pytest por fila (parametrizada) |
| I19 (7 contenedores × 3 argumentos) | `test_i19_non_tuple_container_raises[<field>-<container>]` (21 ids) | PASSED; TypeError esperado |
| I20 (4 elementos × 3 argumentos) | `test_i20_non_string_element_raises[<field>-<element>]` (12 ids) | PASSED; TypeError esperado |
| I21 | `test_i21_immutable_deterministic_canonical` | PASSED (inmutabilidad, entradas intactas, determinismo, orden canónico literal) |
| I22 | `test_i22_identity_opacity` | PASSED (nodeids `[a b]`/`[a]`, Unicode NFC/NFD, controles match) |
| binding feature↔tabla | `test_feature_rows_bind_to_literal_table` | PASSED: las 18 filas del feature (parseadas con `parse_feature` real) equivalen fila a fila a la tabla literal (estado + hallazgos + contrato `sh-p01/1`) |

Nodeids completos con resultado: `evidence/focal-run-final.txt`. El expected
de la tabla es literal del contrato §5 (transcrito como datos); el renderizado
a notación abreviada del binding es formato puro de esos literales, no llama
ni replica el algoritmo del SUT.

## red_evidence

- Bootstrap: `ModuleNotFoundError` (import ausente) — transcript attempt 1.
- Binding: `FileNotFoundError` del feature ausente — attempt 2.
- Semántica (local, no-verifier): variante deduplicadora → 5 failed
  (I08/I09/I10/I17/I21) — attempt 4. Rechazar-todo NO es el caso de I01/I02:
  mi implementación válida los pasa (controles positivos verdes).

## deviations

1. `__all__` en `identities.py` con los 3 nombres de §3: no está enumerado en
   la §2 del contrato (que define contenido mínimo de los archivos); lo añadí
   para que vulture@60 no marque la API contratada como muerta (su único
   caller pre-P06 son los tests, fuera del alcance de scan). Declara
   exactamente la superficie §3, sin nombres extra ni comportamiento.
   Alternativa (whitelist en governance) estaba prohibida para este encargo.
2. `git add -N` (intent-to-add) sobre los 4 archivos, para que `git diff`/
   `git diff --check` vean los nuevos. No es commit; índice local del
   worktree del candidato.
3. IDs de run/coder/candidato generados localmente y opacos: el encargo no
   traía IDs del operador. Metadatos del proveedor: no existen aquí.
4. El venv del worktree se creó nuevo con `uv sync` (y `--all-groups` tras el
   incidente): instala solo lo declarado en pyproject/uv.lock; no se añadió
   ni actualizó ninguna dependencia.

## unverified

- Tiers `full` y `pr` (G-COV-TOTAL, G-MUT, G-CRAP, G-CC, G-DRY*, G-LCOM,
  G-SAST-SEMGREP, G-AUDIT, G-SBOM, G-COV-DIFF, G-PROP, G-ACCEPT-MUT,
  G-REDTEAM, G-HOOKS-WIRED): no corridos. Motivo: el encargo pide fast +
  commit; G-MUT histórico apunta a src/example y P01 §7 prohíbe sumar tools a
  paths.source solo para verdes.
- G-TEST-RANDOM: no existe en ningún tier corriible local; no corrido.
- Ejecución de aceptación con handlers de estos steps: fuera de pieza
  (handlers llegan con P06); el binding se hace con tests de contrato.
- Coste/tokens: unavailable — recibos y telemetría del proveedor los custodia
  el operador; esta sesión no los emite ni los conoce.

## incidents

1. Primera suite completa: 1 failed (`test_gate_secrets...scans_src`) + 24
   skipped por herramientas ausentes — causa raíz: venv nuevo sin el grupo
   `quality` declarado. Resuelto con `uv sync --all-groups` (deps ya
   declaradas en pyproject/uv.lock). Repetida: 401 passed. No fue flake ni
   defecto del diff.
2. Ningún timeout, cancelación ni reintentos de tests.

## scope y límites

- Solo P01: tipos + `compare_identities` puros, stdlib. Sin IO, reloj,
  random, red, procesos, stdout, imports de WCT/pytest en el módulo.
- Sin GateResult, sin CLI, sin engine, sin puertos de una sola implementación
  (MIN-007), sin esqueletos de P02+.
- `classify_inventory` NO fue modificado ni reutilizado (consume texto mutmut
  → GateResult; dominio distinto), conforme al contrato §1.
- `match` no significa ejecución ni PASS; los strings son opacos; `""` es el
  único string inválido en esta capa.
- Ambigüedad menor declarada (interpretación, no defecto del contrato):
  subclases de `tuple` (p. ej. NamedTuple) se aceptan por `isinstance`; el
  contrato exige «tuplas de strings» y no dice si la aceptación es exacta.

## custody / assistance / git

```text
usage_custody: recibos privados con el operador; telemetría unavailable
assistance: ninguna
git_actions: no commit / no push / no PR / no bless (solo git add -N local en el worktree)
next_action: revisión independiente (REVISION-Y-FEEDBACK) sobre este diff congelado; sin autoaprobación
```
