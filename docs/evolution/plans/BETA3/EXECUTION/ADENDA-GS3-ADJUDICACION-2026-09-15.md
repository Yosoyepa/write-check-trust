# Adenda GS-3 — adjudicación de los 34 supervivientes (2026-09-15)

Adjudicación documental y experimental de los 34 supervivientes del lote GS-3
sobre `tools/wct/gate/semgrep.py` (corte medido
`eec71fb1a1dc502b3ab7d557893fcdae4a33be2b`). **No implementa reparaciones, no
repite la campaña de 108 mutantes, no ratifica equivalencias y no convierte
demostraciones posteriores en resultados históricos.** El bruto de campaña
permanece: **108 = 74 killed + 34 survived**. La PR #53 sigue en borrador.

Antecedentes: `GS3-SEMGREP-RESULTADO-2026-09-15.md` (§7 agrupaciones
candidatas), `ANEXO-PREPARACION-GS3-2026-09-15.md`,
`GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15.md` (lanzador fail-closed e
instrumento) y `MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md`.

## 0. Expedientes y custodia

- Original sellado (intacto, verificado 259/259): `build/tmp/gs3.PDSK9G`;
  manifiesto `gs3.sha256`, digest
  `63c83bd2db9af58f4044957bd3a3b4c94cc87bfc94afdfb1ced258fb5b03b990`.
- Expediente sucesor (local, temporal): `build/tmp/gs3-adj.y9i6Rh` (ADJ) con
  copia privada `ADJ/checkout` (HEAD eec71fb; generado
  `mutants/tools/wct/gate/semgrep.py` sha256 `6dcf432d…`), los 5 tests de sonda
  bajo `ADJ/tests-exp/` y `ADJ/evidence/`.
- El sello del original cubre scripts, `evidence/` y `probes/` (259 miembros),
  no `checkout/`; la integridad del árbol medido se corrobora con
  `corte.sha256` (9/9) y la igualdad de hashes entre GS3/ADJ/worktree.
- **Custodia durable: este documento**; la evidencia bajo `build/tmp/` es
  local y temporal.

## 1. Congelación y conciliación

- Los 34 IDs de `ADJ/evidence/supervivientes.tsv` son únicos (0 duplicados),
  pertenecen al inventario sellado de 108 y coinciden 34/34 con los `survived`
  de `results-post.txt` (74 killed + 34 survived = 108).
- No se reabrió ninguno de los 74 atribuidos: no apareció contradicción
  concreta; la adjudicación se limita a los 34.

## 2. Método y sondas

Arnés `ADJ/sonda-exp.sh` (`70b57196…`) + `instrumento.py` (`26e44b52…`): ID
exacto del inventario, modo explícito, entorno saneado antes de asignar
`MUTANT_UNDER_TEST`, cwd/PYTHONPATH dentro de la copia privada, timeout 120 s,
autochequeo `selftest-esperado == selftest-leido` y activación in-process
`INST-GS3` (ID, fuente bajo `ADJ/checkout/mutants`, `variante_en_tabla`).

| Familia | Test (sha256) | IDs | Mutantes | Controles originales |
|---|---|---|---|---|
| E1 skip | `test_skip_branch.py` (`d6ef490c…`) | gate 6–13 | 8/8 exit 1 | exit 0 |
| E2 git | `test_git_failure.py` (`af8ae384…`) | top 6,11,20 | 2 exit 0, 1 exit 1 | exit 0 |
| E5a error | `test_error_branch.py` (`41b62bc4…`) | gate 43,46,50,53,54,55 | 6/6 exit 1 | exit 0 |
| E5b final | `test_success_branch.py` (`4bfdb689…`) | gate 56,59,60,61,65,66,67,69,70,71,74 | 11/11 exit 1 | exit 0 |
| E4 bytes | `test_bytes_text.py` (`f6fbad97…`) | gate 24,29,33 | 3/3 exit 0 | exit 0 |
| E6 policy | `test_policy_message.py` (`d846659c…`) | policy 8 | 1/1 exit 1 | exit 0 |

- Activación acreditada **32/32**; 0 ImportError/INTERNALERROR/errores de
  colección; únicos exits observados: 0/1.
- E2 produce un **fallo Git real** (directorio sin repositorio +
  `GIT_CEILING_DIRECTORIES`; `CalledProcessError 128` con `check=True`), no un
  doble. E5a/E5b usan reloj controlado por sustitución del punto existente
  (`semgrep.time`) con valores fijos 1000.0 → 1002.5 (esperado 2500 ms), sin
  sleeps ni tolerancias. E4 usa un doble de frontera fiel a `text`.
- Tres controles originales iniciales fueron invalidados por un payload
  incompleto (`{"results": []}` sin `errors`, schema «esquema incompleto»),
  corregidos y re-ejecutados; quedan contabilizados (R5).
- Los tests de sonda son experimentos del expediente; **no** son regresiones
  permanentes ni entran al producto.

## 3. Tabla por ID

Resultado original uniforme: control de la familia verde (exit 0). La columna
Mutante muestra el comportamiento público observado con activación acreditada.

| ID completo | Fn | Diff (sha256 12) | Precondición | Contrato | Consumidor | Mutante | Sonda (exit) | Clase |
|---|---|---|---|---|---|---|---|---|
| `tools.wct.gate.semgrep.x__topology__mutmut_6` | `_topology` | git subprocess.run(..., check=None) (ded42f407660…) | git rev-parse falla (no-repo + GIT_CEILING_DIRECTORIES) | subprocess.run: `if check and retcode` (falsy idéntico) | gate_sast_semgrep (preflight) | idéntico al original | E2 git (0) | **C** |
| `tools.wct.gate.semgrep.x__topology__mutmut_11` | `_topology` | git subprocess.run(..., check omitido → default False) (e77b20499ccf…) | git rev-parse falla (no-repo + GIT_CEILING_DIRECTORIES) | subprocess.run: `if check and retcode` (falsy idéntico) | gate_sast_semgrep (preflight) | idéntico al original | E2 git (0) | **C** |
| `tools.wct.gate.semgrep.x__topology__mutmut_20` | `_topology` | git subprocess.run(..., check=True) (b1171064ea40…) | git rev-parse falla (no-repo + GIT_CEILING_DIRECTORIES) | conducta del preflight (returncode != 0 → return) no formalizada | gate_sast_semgrep → runner (guard crash) | CalledProcessError 128 (no devuelve GateResult) | E2 git (1) | **B** |
| `tools.wct.gate.semgrep.x__policy__mutmut_8` | `_policy` | SemgrepScopeError(None) (mensaje del raise) (0053a4e6d4d6…) | governance/policy.yaml ilegible (ConfigError) | feature «Los errores de alcance identifican la causa del rechazo» (ejemplos de forma de policy; sin prefijo aprobado para policy ilegible) | gate_sast_semgrep → summary ERROR | summary='None' | E6 policy (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_6` | `gate_sast_semgrep` | GateResult(None, SKIP, 'herramienta ausente: semgrep') (c49a3bc99356…) | shutil.which('semgrep') → None | model.py::GateResult.gate_id: str + gates.md G-SAST-SEMGREP | report/render.py (identidad) + runner run_gates | gate_id=None | E1 skip (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_7` | `gate_sast_semgrep` | GateResult(GATE_ID, None, 'herramienta ausente: semgrep') (1671a6af8e1f…) | shutil.which('semgrep') → None | model.py Status + docstring semgrep.py «Semgrep ausente es SKIP visible» | report/render.py (agregado PASS/SKIP) | status=None | E1 skip (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_8` | `gate_sast_semgrep` | GateResult(GATE_ID, SKIP, None) (fa1a51d62c16…) | shutil.which('semgrep') → None | model.py::GateResult.summary: str + visibilidad SKIP | report/render.py (diagnóstico) | summary=None | E1 skip (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_9` | `gate_sast_semgrep` | GateResult(Status.SKIP, 'herramienta ausente: semgrep') (fb056d7f2aba…) | shutil.which('semgrep') → None | model.py::GateResult campos requeridos | cualquier consumidor de GateResult | TypeError (falta summary) | E1 skip (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_10` | `gate_sast_semgrep` | GateResult(GATE_ID, 'herramienta ausente: semgrep') (03571c84db03…) | shutil.which('semgrep') → None | model.py::GateResult campos requeridos | cualquier consumidor de GateResult | TypeError (falta status) | E1 skip (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_11` | `gate_sast_semgrep` | GateResult(GATE_ID, Status.SKIP) (ba1776cfe8d6…) | shutil.which('semgrep') → None | model.py::GateResult campos requeridos | cualquier consumidor de GateResult | TypeError (falta summary) | E1 skip (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_12` | `gate_sast_semgrep` | summary 'XXherramienta ausente: semgrepXX' (c9ba15242c97…) | shutil.which('semgrep') → None | grafía no contratada (convención en test_gate_mutation.py:193) | humano (diagnóstico) | summary con XX | E1 skip (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_13` | `gate_sast_semgrep` | summary 'HERRAMIENTA AUSENTE: SEMGREP' (5d9471cf8581…) | shutil.which('semgrep') → None | grafía no contratada | humano (diagnóstico) | summary en mayúsculas | E1 skip (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_24` | `gate_sast_semgrep` | subprocess.run(..., text=None) (f8f5d9d76273…) | semgrep real o sustituido con salida válida/ilegible | semgrep_schema.response: json.loads acepta str y bytes (equivalencia en runtime; las firmas anotan str) | classify → verdict público | idéntico al original (PASS y 'salida ilegible') | E4 bytes (0) | **C** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_26` | `gate_sast_semgrep` | subprocess.run(COMMAND, ..., check=None) (b61cad75767a…) | semgrep con exit no-cero o cero | subprocess.run: `if check and retcode` (falsy idéntico) | gate_sast_semgrep → classify | idéntico al original | estructural + campaña (n/a) | **C** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_29` | `gate_sast_semgrep` | subprocess.run(..., text omitido → bytes) (9b3bf1745d58…) | semgrep real o sustituido con salida válida/ilegible | semgrep_schema.response: json.loads acepta str y bytes (equivalencia en runtime; las firmas anotan str) | classify → verdict público | idéntico al original (PASS y 'salida ilegible') | E4 bytes (0) | **C** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_31` | `gate_sast_semgrep` | subprocess.run(COMMAND, ..., check omitido) (a51169fa65fb…) | semgrep con exit no-cero o cero | subprocess.run: `if check and retcode` (falsy idéntico) | gate_sast_semgrep → classify | idéntico al original | estructural + campaña (n/a) | **C** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_33` | `gate_sast_semgrep` | subprocess.run(..., text=False) (0de92a818385…) | semgrep real o sustituido con salida válida/ilegible | semgrep_schema.response: json.loads acepta str y bytes (equivalencia en runtime; las firmas anotan str) | classify → verdict público | idéntico al original (PASS y 'salida ilegible') | E4 bytes (0) | **C** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_43` | `gate_sast_semgrep` | GateResult(None, ERROR, str(exc), duración) (53e6da563913…) | OSError del instrumento (rama ERROR) | model.py::GateResult.gate_id: str | report/render.py + runner | gate_id=None | E5a error (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_46` | `gate_sast_semgrep` | GateResult(GATE_ID, ERROR, str(exc), None) (4cd994c8d5cd…) | OSError del instrumento (rama ERROR) | model.py::GateResult.duration_ms: int | report/render.py (columna MS) | duration_ms=None | E5a error (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_50` | `gate_sast_semgrep` | GateResult(GATE_ID, ERROR, str(exc)) (duración omitida → 0) (7a1e2cf48991…) | OSError del instrumento (rama ERROR) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=0 | E5a error (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_53` | `gate_sast_semgrep` | duración / 1000 (f8841c71b430…) | OSError del instrumento (rama ERROR) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=0 | E5a error (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_54` | `gate_sast_semgrep` | duración + started (fb2ad00d611a…) | OSError del instrumento (rama ERROR) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=2002500 | E5a error (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_55` | `gate_sast_semgrep` | duración * 1001 (c2fee9c23730…) | OSError del instrumento (rama ERROR) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=2502 | E5a error (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_56` | `gate_sast_semgrep` | GateResult(None, PASS/FAIL, ...) (13d35a19b66b…) | semgrep exitoso (rama final) | model.py::GateResult.gate_id: str | report/render.py + runner | gate_id=None | E5b final (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_59` | `gate_sast_semgrep` | GateResult(..., duration_ms=None, ...) (3590e86933b0…) | semgrep exitoso (rama final) | model.py::GateResult.duration_ms: int | report/render.py (columna MS) | duration_ms=None | E5b final (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_60` | `gate_sast_semgrep` | GateResult(..., details=None, ...) (3b664bea8d9b…) | semgrep exitoso (rama final) | model.py::GateResult.details: list[str] | as_dict()/json_report | details=None | E5b final (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_61` | `gate_sast_semgrep` | GateResult(..., command=None) (da3bf4cf4ab3…) | semgrep exitoso (rama final) | command opcional (str \| None); sin literal para este gate | as_dict()/json_report | command=None | E5b final (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_65` | `gate_sast_semgrep` | desplazamiento: duration_ms=details, details=command, command=None (4d5144bc227a…) | semgrep exitoso (rama final) | model.py::GateResult tipos por campo | report/render.py (formato de list) + as_dict | tipos inválidos por campo | E5b final (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_66` | `gate_sast_semgrep` | desplazamiento: details=command (str) (ce5811d138bc…) | semgrep exitoso (rama final) | model.py::GateResult.details: list[str] | as_dict()/json_report | details=str | E5b final (1) | **A** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_67` | `gate_sast_semgrep` | command omitido (→ None) (5605592255a7…) | semgrep exitoso (rama final) | command opcional (str \| None); sin literal para este gate | as_dict()/json_report | command=None | E5b final (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_69` | `gate_sast_semgrep` | duración / 1000 (f10232b9e575…) | semgrep exitoso (rama final) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=0 | E5b final (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_70` | `gate_sast_semgrep` | duración + started (da0247d1b8ee…) | semgrep exitoso (rama final) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=2002500 | E5b final (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_71` | `gate_sast_semgrep` | duración * 1001 (0c614821d6b8…) | semgrep exitoso (rama final) | semántica de duration_ms no formalizada | report/render.py (columna MS) | duration_ms=2502 | E5b final (1) | **B** |
| `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_74` | `gate_sast_semgrep` | 'XX XX'.join(COMMAND) (098f3b4cd460…) | semgrep exitoso (rama final) | representación de command no contratada para este gate | as_dict()/json_report | command con separador 'XX XX' | E5b final (1) | **B** |

Recuento conciliado: **A = 13**, **B = 14**, **C = 7** (13+14+7 = 34).

## 4. Fundamentos y correcciones de hipótesis

- **Rama SKIP (E1)**: la no-ejercitación en campaña era ambiental, no código
  muerto: se sustituyó el punto existente `shutil.which` y se observó el
  resultado público. Los campos `None`/desplazados violan el contrato de
  `GateResult` y/o la política documentada («Semgrep ausente es SKIP visible»)
  → A; las variantes de grafía no tienen obligación → B (decisión D1).
- **Git y `check` (E2)**: el fallo Git real (exit 128, sin repositorio) con
  `check=False`/`None`/omitido se tolera igual (early return del preflight);
  con `check=True` el gate **no devuelve `GateResult`** (CalledProcessError no
  capturada) → B (decisión D2). **Corrección de la hipótesis de calibración**:
  «`check=None` ≡ `check=False`» queda sustentada para `top_6`/`top_11`
  (estructura `if check and retcode` + sonda verde) y para `gate_26`/`gate_31`
  (estructura; sin input discriminante, campaña verde con activación); **no**
  se extiende a `check=True`.
- **Campos de `GateResult` (E5a/E5b)**: `gate_id`/`status`/`summary`/`details`
  y la duración con valor `None` son violaciones de tipo/identidad → A; la
  **semántica** de `duration_ms` (0, /1000, +started, *1001) y la
  representación de `command` no están formalizadas → B (decisiones D3/D4).
  El reloj controlado produjo valores distinguibles (2500 esperado; 0,
  2002500, 2502 observados) sin sleeps.
- **Bytes/str (E4)**: `semgrep_schema.response` usa `json.loads`, que acepta
  `str` y `bytes`; con doble fiel a `text`, el resultado público es idéntico
  (PASS válido y «salida ilegible» malformado) → C **en runtime** (las firmas
  anotan `str`; mypy estricto no aceptaría bytes). Invalidaría la conclusión
  cualquier operación de cadena sobre `payload` o un chequeo de tipo.
- **Mensaje de `_policy` (E6)**: el contrato de la feature cubre prefijos de
  errores de forma de policy, no el texto de `policy.yaml` ilegible; la
  observabilidad (summary) existe pero la grafía no está contratada → B
  (decisión D5). La mutación reduce el summary a `'None'`.

## 5. Sensibilidad medida frente a expectativas

- **Medida**: los 27 IDs A+B fueron **matados** por los oráculos propuestos en
  las sondas (13 A + 14 B, exit 1 con activación acreditada y causa en el log).
- **Medida (equivalencia)**: `top_6`, `top_11`, `gate_24`, `gate_29`,
  `gate_33` sobrevivieron a sus sondas con comportamiento público idéntico.
- **Expectativa no ejecutada**: `gate_26`/`gate_31` (C estructural) no tienen
  input discriminante; su equivalencia descansa en `subprocess.run` y en la
  campaña con activación, y queda pendiente de ratificación humana.

## 6. Propuesta mínima de reparación (no ejecutada)

| Familia | IDs | Contrato | Entrada | Resultado esperado | Test propuesto |
|---|---|---|---|---|---|
| F1 SKIP visible | gate 6–11 | `GateResult` + docstring SKIP | `which` → None | `GateResult(G-SAST-SEMGREP, SKIP, "herramienta ausente: semgrep")`, `details=[]`, `command=None` | `test_herramienta_ausente_es_skip_con_identidad` |
| F2 tolerancia Git | top 20 | preflight (returncode ≠ 0 → return) | no-repo + `GIT_CEILING_DIRECTORIES` | sin excepción; `GateResult` normal | `test_preflight_tolera_fallo_de_git` |
| F3 rama ERROR | gate 43, 46 | tipos de `GateResult` | OSError + reloj fijo | `gate_id` correcto y `duration_ms == 2500` | `test_rama_error_campos_publicos` |
| F4 retorno final | gate 56, 59, 60, 65, 66 | tipos de `GateResult` | semgrep limpio + reloj fijo | `gate_id`, duración 2500, `details=[]` | `test_retorno_final_campos_publicos` |
| F5 duración | gate 50, 53–55, 69–71 | semántica a decidir (D3) | reloj fijo | `duration_ms` = milisegundos transcurridos | aserción en F3/F4 |
| F6 command | gate 61, 67, 74 | representación a decidir (D4) | semgrep limpio | `command == " ".join(COMMAND)` | aserción en F4 |
| F7 grafía SKIP | gate 12, 13 | decisión D1 | `which` → None | summary exacto o contrato de prefijo | `test_herramienta_ausente_summary_contratado` |
| F8 mensaje policy | policy 8 | decisión D5 | policy ilegible | `summary.startswith("governance/policy.yaml ilegible:")` | `test_policy_ilegible_nombra_causa` |

- **Allowlist exacta propuesta** para el incremento de reparación:
  `tests/unit/test_sast_targets.py` (F1–F4, F7, F8 bajo contrato existente o
  decisiones aprobadas); si D1/D3/D4/D5 se aprueban como contrato nuevo,
  documentarlo en la feature/`docs/gates.md` antes de tocar producto. Sin
  cambios de gobernanza.
- **Gherkin necesario** solo si hay decisión contractual nueva: escenarios para
  «herramienta ausente → SKIP visible con identidad y diagnóstico», «fallo Git
  no rompe el preflight» y «policy ilegible nombra la causa» (los tres hoy sin
  escenario).
- **Sensibilidad**: 27/27 medidas (A+B); no se afirma sensibilidad de los 7 C.
- **Presupuesto sugerido del incremento siguiente**: ≤ 900 s de ejecución
  (13 A medidos ≈ 30 s; 14 B ≈ 60 s si se aprueban sus decisiones; autoría y
  verificación aparte).

## 7. Decisiones humanas pendientes

- **D1** grafía del summary SKIP (`gate_12`, `gate_13`).
- **D2** tolerancia a fallo Git en el preflight (`top_20`).
- **D3** semántica de `duration_ms` (`gate_50`, `gate_53–55`, `gate_69–71`).
- **D4** campo `command` para este gate (`gate_61`, `gate_67`, `gate_74`).
- **D5** prefijo del mensaje de policy ilegible (`policy_8`).
- **D6** ratificación de las equivalencias C (`top_6`, `top_11`, `gate_24`,
  `gate_26`, `gate_29`, `gate_31`, `gate_33`).

## 8. Presupuesto

- Sondas de adjudicación: **41 corridas / 63.764 s** (incluye 3 originales
  invalidados por payload; re-ejecutados). `ADJ/evidence/presupuesto-adj.tsv`.
- Verifier: ~13 s (sello, micro-verificaciones y 2 reejecuciones puntuales).
- **Total ≈ 76.8 s de 900 s**. Sin `mutmut run` ni repetición de campaña.
- R5: los 3 intentos invalidados solo constan en el ledger presupuestario; sus
  artefactos fueron sobrescritos por la re-ejecución válida.

## 9. Dictamen independiente

**Verifier independiente de solo lectura** (PROC-005): revisó sellos, los 34
IDs congelados, hashes de diff recomputados 34/34, 38 artefactos de sonda,
activación 32/32, citas contractuales y presupuestos; reejecutó `gate_24` y
`gate_9` (~2.8 s). **Dictamen: CONFORME CON RESERVAS (R1–R6, menores, ninguna
bloqueante)**, atendidas en esta adenda: R1 corregida la celda `2502` de
`gate_55`/`gate_71`; R2 acotada la equivalencia de bytes a runtime; R3 cita de
`policy_8` ajustada (se mantiene B); R4 borde `gate_12/13` pendiente de
ratificación repo-wide (D1); R5 intentos invalidados declarados; R6 alcance del
sello (no cubre `checkout/`; integridad por `corte.sha256` y hashes cruzados).
Modalidad: documental + re-derivación programática y 2 reejecuciones.

## 10. Estado real

- **Adjudicación completa**: 34/34 IDs con diff, contrato, consumidor,
  resultado observado, evidencia y clase; 13 A, 14 B, 7 C.
- Sin reparaciones, sin ratificación de equivalencias, sin PASS de G-MUT, AC1
  ni beta.3; el bruto histórico 108 = 74 killed + 34 survived no cambia.
- Publicable con las decisiones D1–D6 pendientes; el siguiente incremento
  mínimo es la reparación F1–F8 bajo aprobación humana.
