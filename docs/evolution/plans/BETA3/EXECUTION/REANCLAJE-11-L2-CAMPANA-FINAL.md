# Registro REANCLAJE-11 — campaña final completa de L2 con selección congelada de 141 nodeids (2026-09-18)

Estado: **L2 CONFORME POR RESULTADO MEDIDO Y ADJUDICACIÓN EXPLÍCITA.** La
campaña nueva (árbol instrumentado fresco, 278 mutantes, ejecución serial
con IDs explícitos) midió **266 killed + 12 survived = 278**; los 12
sobrevivientes corresponden EXACTAMENTE a las disposiciones autorizadas por
el humano en el acta REANCLAJE-11-L2-DECISIONES.md (10 equivalencias
ratificadas D-A + 2 excepciones puntuales D-B), sin otros residuos ni
anomalías. **No** se emite «todos killed» ni PASS de G-MUT; el dictamen se
limita a L2 y no cierra P03a ni beta.3. Sin cambios de producto, tests,
contratos ni configuración versionada; sin otros lotes, 928 IDs, binding
PA01–PA12, Q-ACCMUT, cobertura/CRAP/DRY/full, bless, update-manifest, merge,
bump, tag ni release.

## 1. Base, identidades y aislamiento

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base autorizada (técnica y documental) | `96e304393c83fc78e730c00133bb0bc6b49fbb27` = headRefOid PR #56 (OPEN, borrador) = origin `codex/reanclaje-p03a-fase1`; main `8a379d64…` = baseRefOid = merge-base; sin avance remoto posterior | `gh pr view 56` + `git ls-remote` + `git merge-base` al iniciar |
| Árbol del candidato | tree `0d19c269db10a34dc1a668be659cbe853a9dea47`; copia Git NUEVA con raíz propia `build/tmp/reanclaje11-20260918/repo/`, checkout detached, árbol limpio (al cierre: solo las dos docs de este encargo como untracked, previo a su publicación) | `git clone` + `git rev-parse HEAD^{tree}` + `git status` |
| Manifiesto REANCLAJE-10 | digest exacto `3d965a5271066cf8d32d47eecb52109304babdd56a3cd15c43b65e566ae6bbb5`, 24/24 miembros OK | `sha256sum -c` |
| Selección congelada | `logs/03-seleccion-futura-L2.nodeids` de R10, digest exacto `e8dcdff18e4ba85d742f401a3f88ec5454188e721cbcd63da3de80d1b5c65c17`, **141 nodeids únicos** (112 schema = 98 históricos + 12 R9 + 2 R10; 28 PA02/PA03; PA01-unicode) | `sha256sum` + conteo por prefijo |
| Fuentes wire | 4 archivos byte-idénticos al sello R8 (`63e25807…`, `35e74471…`, `8977f5b4…`, `a6261613…`) al abrir y al cerrar | `sha256sum` apertura/cierre |
| Tests de la selección | `test_pytest_schema.py` `e7d82c99…`, `test_pytest_observation.py` `5d3d30a6…` (hashes R10), sin cambios | `sha256sum` |
| Runtime | venv propio (`uv sync --all-groups`, caché): Python 3.13.14, pytest 9.1.1, mutmut 3.7.0; bin `wct` presente | `--version` |
| Checkout principal del usuario | rama `codex/plan-beta3-moldes-evals` con trabajo ajeno sin commit — **intacto** (solo lectura) | `git status` del principal |
| Decisión previa obligatoria | acta D-A/D-B escrita y sellada ANTES de la generación y la campaña (mtime 23:39 < generación 23:40) | verificador preflight |

Copias: `repo/` (Git, ancla de identidad y destino documental) y `run/`
(ejecución, extraída de `git archive` del HEAD; pyproject original
`f27de519…` sellado aparte, experimental `a229a686…` con
`source_paths` = las 4 wire, `also_copy=["tools","features","src"]` y la
selección de 141 nodeids como `pytest_add_cli_args_test_selection`, cada
nodeid escrito como cadena TOML completa por código — sin split ni
concatenación; uno contiene un espacio literal, línea 85). Lanzador
fail-closed: cwd=`run/mutants`, `PYTHONPATH` absoluto a `mutants`,
`MUTANT_UNDER_TEST` re-asignado y verificado por sonda ambiental con el
mismo entorno del hijo + identidad de imports (`tools.wct` resuelve DENTRO
de mutants/).

## 2. Generación nueva y custodia (pre-campaña)

- **Generación pura** (firma heredera R7, centinela `ZZ_GENERACION_R11_NO_MATCH`):
  «4 files mutated, 0 ignored, 0 unmodified» (381 ms) + assert
  «Filtered for specific mutants, but nothing matches» ANTES de todo test;
  0 «Listing all tests»; 278 claves en `.meta` todas `None` (cero mutantes
  ejecutados). Wall 14.69 s. `logs/04-generacion.log`.
- **Inventario AST del instrumentado**: 278 = values 66 + fields 0 +
  composites 85 + framing 127, sobre 23 funciones; **conjuntos idénticos al
  histórico R7 (0 nuevos, 0 ausentes)** y las 4 fuentes instrumentadas
  **byte-idénticas** al árbol R7 conservado in situ → identidad total, sin
  renombrados ni diferencias que explicar. `custodia/inventario-nuevo-ids.json`.
- **Diffs por ID**: 278 diffs extraídos en proceso con la propia lógica de
  `mutmut show` (`find_mutant`+`get_diff_for_mutant`), digest del archivo
  `b919df53…`; los 12 IDs decididos coinciden hunko a hunko con el artefacto
  original sellado R7 logs/16. `custodia/diffs-por-id-nuevo.txt`.
- **Asociaciones** (stats inicial): 23/23 funciones con tests asociados no
  vacíos. `logs/05-asociaciones-iniciales.json`.
- **Custodia sellada** (`custodia/sello-estatico.sha256`, 13 miembros, sin
  auto-hash): acta de decisiones, selección 141, fuentes originales
  (implícitas en repositorio + hashes) e instrumentadas, inventario, diffs
  por ID, pyproject original y experimental, tests utilizados, stats
  inicial. **Estados inicial y final como snapshots separados**
  (`meta-inicial.json` / `meta-final.json`, `mutmut-stats-inicial.json` /
  `mutmut-stats-final.json`); ningún miembro sellado se reescribió.
  Distinción estático/estado declarada: mutmut modifica `.meta`/stats, no
  las fuentes instrumentadas (verificado byte-idénticas al cierre).
- No se usó `print-time-estimates`; no se reutilizó ningún veredicto ni el
  árbol histórico como árbol de ejecución.

## 3. Preflight y controles del lanzador (sobre A)

Colección real de la selección: **141 collected, exit 0**, 0 duplicados,
todos existen (`logs/02`). Baseline sobre originales: **141 passed, exit 0,
sin skips/xfails/errores; property fuera** (2.93 s, `logs/03`).

Negativos (bloquean ANTES de pytest, `logs/06-*.log`): N1 ID desconocido →
exit 2; N2 selección vacía → exit 2; N3 hash adulterado de fuente → exit 2
(fuente restaurada y revalidada `a6261613…`); N4 activación ausente → sonda
ambiental exacta del lanzador rc 3; N5 imports incorrectos (resolución al
árbol original, el riesgo real de R8 §4) → rc 3.

Positivos: **ORIGINAL 141 passed** sobre el árbol instrumentado (exit 0) y
**canario `x__u__mutmut_1`** resuelto por ID y diff en el inventario nuevo:
rojo con **causa contractual** — `AssertionError: assert 'invalid_field' ==
'limit_exceeded'` (línea 931 del log; 62 failed + 5 passed de sus 67 tests
asociados bajo la selección de 141; en R7 con selección de 126 la asociación
era 38 — el crecimiento es efecto de la selección mayor, no una anomalía).

**Verificador independiente de solo lectura (preflight): DICTAMEN
FAVORABLE, 0 bloqueantes** — fidelidad del acta 12/12 (IDs, diffs, hashes,
clases, sin extras; mangling `ǁ` U+01C1 verificado), preflight reproducido
en copia propia (negativo rc 2; canario rc 1 con la misma causa en la misma
línea; ORIGINAL 141 passed; digests selección/acta recalculados; trampolines
3/3 presentes y ausentes en fields), sello estático 13/13, ledger sin
transferencias. Hallazgos menores: H-1 resumen de controles desactualizado
→ **regenerado** (`logs/07-resumen-controles.json` documenta la corrección);
H-2/H-3 cosméticos (re-serialización del stats; denominación del sello del
pyproject original). Re-ejecuciones del verifier: 13.40 s de su sobre de
240 s. Informe:
`build/tmp/reanclaje11-20260918-verifier/INFORME-PREFLIGHT.md`.

## 4. Campaña completa (sobre B)

`mutmut run --max-children 1 <278 IDs explícitos del inventario aprobado>`
en `run/`, serial, bajo guardián monotónico (timeout limitado al saldo).
**Wall 103.51 s, exit 0, sin timeout del guardián** (`logs/08-campana.log`).
Sin reutilización de estados históricos; sin adaptar selección, tests ni
producto durante la corrida.

Reconciliación por conjuntos (cruda, por claves de `.meta`):
generados = autorizados = resultados = **278**; **0 duplicados, 0 ajenos,
0 faltantes, un solo estado final por ID**; el log corrobora: 266 IDs
únicos con veredicto killed + 12 únicos con survived, sin solapes ni
duplicados, sin timeouts/skipped/suspicious. Estados anómalos: **0**.

## 5. Bruto nuevo medido y transiciones

**Bruto nuevo (campaña R11, selección 141): 266 killed + 12 survived = 278.**
Este es el resultado medido de ESTA campaña; no se reconstruye sumando kills
de campañas distintas.

Métricas separadas e inviolables:

| Corrida | Resultado | Rol |
|---|---|---|
| A. Histórico R7 (selección 126) | 278 = 233 killed + 45 survived | referencia inmutable |
| B. Sensibilidad sucesora R9 (111) | 33/33 rojos atribuidos por ID | evidencia previa de transición |
| C. **Campaña nueva R11 (141)** | **266 killed + 12 survived** | **resultado medido propio** |

Transiciones (análisis, no suma):

- **33 survived→killed (PREVISTOS)**: exactamente los 33 IDs con hueco de
  oráculo adjudicados en R8 §5.1 y sensibilizados en R9. Contrastados por
  ID, test y causa contra la microcampaña R9 (`logs/10-transiciones-33.json`):
  33/33 con dictamen ROJO en R9 y killed en R11, con tests causales
  identificadas (p. ej. `test_wire_constant_literals_are_invalid_json` ×10,
  `test_wire_digest_field_rejects_non_lowerhex` ×8,
  `test_wire_plugin_claim_optionals…` ×6,
  `test_wire_depth_at_eight_is_not_invalid_json` ×6,
  `test_wire_canonical_utf8…` ×5, `test_wire_phase_make…` ×4, argv ×2,
  cwd ×2, control_char ×1 — PA01-unicode adicional para cb_8/cb_12).
  Exit 1 por sí solo no se tomó como kill: la cadena de causalidad es
  campaña + asociaciones no vacías + canario con causa + ORIGINAL verde +
  sonda R9 por ID con test y causa, sobre un árbol instrumentado
  byte-idéntico al históricamente usado.
- **killed→survived: 0** (ningún killed histórico sobrevive).
- **survived→survived (12)**: exactamente los IDs con disposición autorizada
  (abajo). Ninguna mutación ratificada o exceptuada cambió de resultado.

## 6. Estado final de las disposiciones autorizadas

Los 12 sobrevivientes del bruto nuevo corresponden EXACTAMENTE (igualdad de
conjuntos, sin extra ni faltante) a:

| Disposición | IDs (resultado R11) |
|---|---|
| **Equivalencias ratificadas D-A** (10) | composites `x__cwd__mutmut_5`, `x__utc__mutmut_5`, `x__utc__mutmut_6`; framing `x_canonical_bytes__mutmut_3`, `_6`, `_11`, `_16`, `_18`, `x__parse_line__mutmut_4`, `x__line_defect__mutmut_7` — todos **survived** |
| **Excepciones puntuales TEST-002 D-B** (2) | framing `xǁ_DefectErrorǁ__init____mutmut_1`, `xǁ_DefectErrorǁ__init____mutmut_3` — **survived** (no kills, no equivalentes; permanecen en el bruto con el resultado observado) |

Los textos de ratificación, fundamento, precondiciones e invalidantes por
ID están en el acta `REANCLAJE-11-L2-DECISIONES.md` (publicada junto a este
registro). Ningún ID se convirtió en killed ni se eliminó del bruto.

## 7. Estado de WIRE_FIELDS

`pytest_wire_fields.py` es tabla pura (sin funciones): **0 mutantes
generados por mutmut** — límite instrumental declarado desde R7 (los 60
sitios de módulo no son instrumentables por mutmut 3.7). Los controles de
WIRE_FIELDS de REANCLAJE-10 forman parte de la selección congelada como
**evidencia alternativa del contenido de tablas**
(`test_wire_fields_table_is_the_contract_transcription` — literal
transcrito del contrato, independencia acreditada — y
`test_wire_decoder_binds_payload_positions_to_contract_fields`):
ambos pasaron en la colección, el baseline y el ORIGINAL del preflight, y
formaron parte del conjunto asociado durante la campaña. **No cuentan como
mutantes generados ni kills.** Los 5 docstrings de módulo siguen
documentados como contenido sin efecto conductual identificado (limitación
declarada, sin dispensa).

## 8. Presupuesto real (guardián monotónico, `logs/00-ledger-guardian.csv`)

| Sobre | Techo | Real | Estado |
|---|---:|---:|---|
| A — preflight + generación + baseline + asociaciones + controles | 300 s | 33.82 s | ✔ |
| B — campaña completa | 1200 s | 103.51 s | ✔ |
| C — sondas causales y anomalías | 600 s | 0 s | ✔ (sin anomalías que sondear; logs completos bastaron) |
| D — reejecuciones del verifier | 240 s | 13.40 s (preflight; ledger propio del verifier) | ✔ |
| **Experimental total** | **2340 s** | **150.73 s** | ✔ |
| PUB — fast y comprobaciones ejecutables de publicación | 180 s | ver §11 | aparte |

Intentos inválidos contabilizados y declarados: 2 × resolución de symlink
del venv (0.02 s c/u, corregido con ruta absoluta sin resolve); 1 × primer
lote de controles con dos bugs del arnés (exigencia de trampolines en
wire_fields con 0 mutantes legítimos; N5 con cwd incorrecto — 3 controles
rechazados por el propio lanzador fail-closed, ~0.2 s, corregido y rehecho;
hito H-1 del verifier resuelto regenerando el resumen). Sin transferencias
entre sobres; timeouts por hijo limitados al saldo; solo procesos propios;
nada dependió del buffering de stdout (archivos con flush explícito).

## 9. Revisión final del verifier independiente — DICTAMEN FAVORABLE

Agente distinto del autor, sin escritura en el workspace del autor; reprodujo
en copia propia (`build/tmp/reanclaje11-20260918-verifier-final/`). **DICTAMEN:
FAVORABLE al cierre de L2** — 10/10 puntos conformes (documental + recálculo +
reejecución): custodia 13/13 y manifiesto 43/43 verificados desde su copia;
recalculó el bruto desde `meta-final.json` (266+12 exactos, surviving set ==
12 IDs decididos); transiciones completas 233 k→k + 33 sv→k + 12 sv→sv con
0 no previstas; reejecuciones frescas: sonda de un killed de los 33
(`x__loads__mutmut_17` → exit 1 con `ValueError: Out of range float values
are not JSON compliant: inf` y ORIGINAL verde), sonda de un survived de los
12 (`x_canonical_bytes__mutmut_18` → exit 0: supervivencia real del alias de
codec, no inactivación), ORIGINAL 141 passed, réplicas de N4/N5 (rc 3).
Re-ejecuciones: 14.33 s de su sobre (1 intento inválido propio declarado).
Hallazgos: **0 bloqueantes**; 4 menores (evidencia N4/N5 de 0 bytes mitigada
con réplicas; timestamps truncados en una fila del ledger y un paso del
estado — corregidos antes de re-sellar; imprecisión de redacción §1 —
corregida; formato de diffs-por-id — hunks exactos 12/12). El dictamen se
limita a L2: no cierra P03a ni beta.3, no otorga ratificaciones. Informe:
`build/tmp/reanclaje11-20260918-verifier-final/INFORME-FINAL.md`.

## 10. Pasos reales del workflow NO ejecutados

La CI del PR #56 (commit de este registro) falla por diseño ante el drift
protegido preexistente del propio PR (34 «nuevo protegido» + 2 «modificado»,
R10 §2.C): los pasos mecánicos posteriores a «Verify generated policy and
control-plane integrity» quedan SKIPPED por ese fallo. **Bless**
(actualizar integrity.lock) y **merge** son operaciones humanas fuera del
job y siguen pendientes de puerta propia. No se ejecutaron bless, merge,
bump, tag, release ni update-manifest.

## 11. Sellado y publicación

Expediente `build/tmp/reanclaje11-20260918/`: `MANIFIESTO-REANCLAJE11.sha256`
(43 miembros: 17 logs + 17 custodia + 2 docs + 7 scripts/estado; sin
auto-hash; digest y verificación fuera de sus miembros). Publicación en PR
#56 (borrador): diff exacto = el acta de decisiones + este registro; commit
convencional con byline; hooks sin bypass; push normal; fast ejecutado bajo
el sobre PUB; CI observada con seguimiento acotado.

## 12. Siguiente lote mínimo propuesto — NO EJECUTAR SIN AUTORIZACIÓN

**PROPUESTO**: encargo del **lote L4 (decoder)** siguiendo el plan
REANCLAJE-6 §4 — campaña de mutación sobre `pytest_decode_events.py` y
consumidores del paquete kernel, con la misma mecánica probada aquí
(selección congelada por digest, generación pura, lanzador fail-closed,
sobres cerrados): el decoder es el siguiente módulo del contrato wire tras
las 4 fuentes L2 y concentra las rutas de findings que R10 §5 dejó
documentadas (`_execution_index`, atribución, catchers). Alternativa:
regularización del drift del integrity lock (bless) como puerta humana
separada. Nada de esto se ejecutó en este encargo.
