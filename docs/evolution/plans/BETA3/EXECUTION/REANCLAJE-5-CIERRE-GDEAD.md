# Registro REANCLAJE-5 — cierre de G-DEAD: eliminación de estado muerto y aceptación explícita del alcance de la whitelist (2026-09-18)

Estado: **cierre ejecutivo de G-DEAD**. Eliminación del campo privado muerto
`_ScanState.expectation` (clasificación B de REANCLAJE-4 §3) y aceptación
humana explícita del alcance global por nombre de las 17 entradas aplicadas
en REANCLAJE-3 más tres entradas nuevas (`utc`, `distribution`, `qualified`).
Base verificada:
`2dbc5097e0498be7b7a5787d96b1c4f64829a610` (= remoto `codex/reanclaje-p03a-fase1`
= headRefOid PR #56 antes de publicar; main `8a379d64…` y tag
`v1.0.0b3.dev1` intactos). Expediente antecedente verificado antes de usar su
evidencia: manifiesto REANCLAJE-4 `18c6c975…` (digest del archivo
`MANIFIESTO-REANCLAJE4.sha256` + 4/4 miembros verificados). Copia aislada:
`build/tmp/reanclaje5-20260918/repo` (raíz Git propia).

## 1. Autorización humana aplicada (transcripción resumida)

El encargo REANCLAJE-5 autoriza expresamente: (1) conservar las 17 entradas
de whitelist examinadas en REANCLAJE-4, aceptando que vulture 2.16 silencia
esos nombres globalmente dentro de su alcance de análisis, no por módulo ni
clase; (2) añadir las tres entradas mínimas `utc`, `distribution` y
`qualified` para los cuatro hallazgos contractuales; (3) eliminar el campo
privado `_ScanState.expectation` y su escritura, condicionado a las premisas
verificadas en REANCLAJE-4; (4) publicar el incremento en PR #56, que
permanece en borrador. La aceptación reconoce el riesgo de ocultar futuros
símbolos muertos homónimos y no afirma ausencia universal de ese riesgo. La
whitelist no declara equivalencia de mutantes, no acredita calificación y no
convierte en consumidores productivos las referencias de tests.

## 2. Revalidación de premisas (antes de editar)

- **Reproducción**: receta canónica (cwd=candidato, vulture 2.16,
  Python 3.13.14, exit 3)
  `vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60`
  → **5 hallazgos idénticos byte a byte** a REANCLAJE-4 §1: `utc` ×2
  (`pytest_payload_classes.py:54` ExecutionStart, `:77` ExecutionEnd),
  `distribution` (`:97` PluginClaim), `qualified` (`:100` PluginClaim),
  `expectation` (`pytest_scan_state.py:47` _ScanState).
- **Whitelist previa**: hash `8c2f819b3e5431b509cc7bca19cbe44f0693f87ca6b36b5d428e24e5de3ca5fb`
  (= sello R3) con exactamente las 17 entradas auditadas (R4 §2), sin drift.
- **Campos contractuales revalidados**: PROPUESTA-P03.md (hash
  `47429b88…`, versión congelada en main) §3 exige `utc:S` en
  ExecutionStart y ExecutionEnd (líneas 209/211), `distribution:S no vacío o N`
  y `qualified:B` en PluginClaim (línea 213). Cadena productiva verificada:
  validación del valor crudo en `pytest_payload_validate.py` (`_is_utc`,
  `_optional(_is_text)`, `_is_bool`) → construcción vía kwargs en
  `pytest_builders.py:53/71` (`utc=_utc(…)`) y `:114/:117`
  (`distribution=_opt_s(…)`, `qualified=_b(…)`) → cero lecturas de campo en
  src/tools tras la construcción. Conservación obligatoria confirmada.
- **Premisas de `expectation` revalidadas**: declaración única
  (`pytest_scan_state.py:47`); **única escritura**
  (`pytest_observation.py:165`, kwarg `expectation=item`); **cero lecturas**
  de `.expectation` en src+tools+tests; **única construcción** de `_ScanState`
  en todo el árbol; sin construcción por kwargs en otros sitios, sin
  introspección (cero `getattr`/`setattr`/`asdict`/`__dict__`/`fields()`/
  `signature()` sobre el tipo), sin serialización, sin dependencias de la
  firma del tipo privado; `_ScanState` ausente de la tabla de tipos §2 de
  PROPUESTA-P03 (las validaciones de expectativas originales viven en
  `pytest_api_args.py`/`pytest_observation_validate.py` sobre la tupla, no
  sobre el campo). Las funciones `_validate_expectation` de api_args son
  validación de entrada pública — no consumidoras del campo interno.
  Ninguna premisa cambió desde R4: la autorización condicional aplica.

## 3. Eliminación de `expectation` (clasificación B)

Cambios exactos (diff `logs/04-diff-expectation.patch` + colapso de formato):

| Archivo | Hash anterior | Hash nuevo | Cambio |
|---|---|---|---|
| `tools/wct/evidence/pytest_scan_state.py` | `dbbbef52539139440a4386b3880679d57344acce49ae5aa2746cac9fec6797e7` (= sello R8) | `0c995e77cda9aa5b8bc1c3d47442f621782ca20512acc41c059a6b00632d16d7` | − declaración `expectation: ExecutionExpectation`; − `ExecutionExpectation` del import (sin uso restante) |
| `tools/wct/evidence/pytest_observation.py` | `3ec593ba9e49da27bafe00bea9d273832b5ed7b4d92fa670ec8ad24cfd23dbc1` (= sello R8) | `46309fc84bcd99a2ede5e148047617a086e7a29a27a127a753c51b18f49197fc` | − kwarg `expectation=item` en la única construcción; la línea restante colapsa a una sola por `ruff format` (motor único de formato, STYLE-001) |

Motivo: peso interno muerto (escrito una vez, jamás leído) fuera de todo
contrato. Contrato preservado: la expectativa del API público
(`ExecutionExpectation`, validada en frontera por `pytest_api_args.py` y
`pytest_observation_validate.py`) queda intacta; `execution_id`, `role`, la
FSM, los modelos públicos y el formato wire no cambian. No se añaden tests
cosméticos de ausencia de atributo: la evidencia es la suite de
caracterización idéntica (§6). **Control intermedio 5→4 exacto**: tras la
eliminación, vulture reporta exactamente los cuatro hallazgos contractuales
restantes (`logs/03-gdead-5a4.log`); nada más cambió de salida.

## 4. Whitelist: +3 entradas bajo autorización expresa

`governance/lint/vulture_whitelist.py`:
`8c2f819b3e5431b509cc7bca19cbe44f0693f87ca6b36b5d428e24e5de3ca5fb` →
`a2877ee8deba9ed28ceff1e1a2d93a4c35f1800c12ee436bd47ce5f0fd6b24ef`.

- **Entradas añadidas (exactamente tres, nombres sueltos canónicos ADR-D-02)**:
  `utc`, `distribution`, `qualified`, cada una con `noqa` puntual y
  justificación inline.
- **Las 17 entradas previas se conservan sin ampliar nombres ni patrones**;
  el docstring histórico R3 queda intacto y se añade la sección REANCLAJE-5
  que documenta: símbolos y rutas que motivan cada entrada (payload_classes
  :54/:77/:97/:100); obligación contractual (PROPUESTA-P03 §3, validación en
  frontera + construcción kwargs + cero lecturas: claims del emisor
  conservados que la API retorna al caller); autorización humana actual;
  **alcance global real por nombre** (silencia el nombre en todo su alcance
  de análisis src+tools, no por módulo ni clase; vulture 2.16 no ofrece
  formulación acotada — demostrado en R3 S1–S3 con cuatro formulaciones);
  riesgo de homónimos futuros reconocido y aceptado; y la nota expresa de
  que la whitelist no declara equivalencia de mutantes, no acredita
  calificación y no convierte referencias de tests en consumidores
  productivos. **No se presenta notación cualificada como protección por
  módulo** porque vulture no la proporciona.
- **Control 4→0 exacto**: la receta canónica reporta cero hallazgos,
  exit 0 (`logs/05-gdead-4a0.log`); G-DEAD del tier commit en PASS (§6).

## 5. Controles en copia desechable (fuera del candidato)

Sonda `build/tmp/reanclaje5-20260918/sonda/` con homónimos muertos ajenos
(`ForeignDead.utc/.distribution/.qualified`) y control de nombre distinto
(`zzz_dead_control`); log consolidado `logs/06-controles-ABCD.log`:

- **A ✔** Con la whitelist candidata, los cuatro hallazgos contractuales
  desaparecen (exit 0, salida vacía).
- **B ✔** Un símbolo muerto de nombre distinto (`zzz_dead_control`) sigue
  detectándose — el detector conserva capacidad.
- **C ✔** Los homónimos muertos ajenos `utc`/`distribution`/`qualified`
  quedan OCULTOS con las entradas nuevas (la clase contenedora ajena sí se
  reporta). **Evidencia del riesgo aceptado por el humano, no un PASS de
  capacidad del detector.**
- **D ✔** Sin las tres entradas nuevas, los cuatro hallazgos contractuales
  originales reaparecen exactos y los homónimos vuelven a ser visibles.

Sin lecturas artificiales añadidas al producto para satisfacer G-DEAD.

## 6. Batería del candidato sucesor (runtime íntegro de la copia)

Runtime: venv propio de la copia (`uv sync --all-groups`), Python 3.13.14,
pytest 9.1.1, vulture 2.16, semgrep presente, wct instalado editable
(`1.0.0b3.dev1`, `tools.wct` resuelve dentro de la copia — control negativo
de import por `__file__`; PATH con el bin del venv para subprocesos).
Primer intento de suite con el venv compartido sh-p01 (wct 1.0.0b2
instalado, sin semgrep en PATH): 8 fallos ambientales (subprocesos ruff/git/
which sin PATH; test de versión leyendo metadatos instalados 1.0.0b2 vs
pyproject 1.0.0b3.dev1) — **intento inválido registrado, no cuenta como
evidencia**; sustituido por la corrida canónica con venv de la copia.

| # | Comprobación | Resultado | Log |
|---|---|---|---|
| 1 | Colección completa `pytest --collect-only -q` | **1183 colectados, exit 0**; nodeids ordenados **idénticos** a la colección R3 (diff vacío) | 07, 19 |
| 2 | Focal R8 (`test_pytest_{observation,schema,phases}.py`) | **426 passed**, exit 0 | 08, 20 |
| 3 | Focal operador (`test_accept_typed_operator.py`) | **61 passed**, exit 0 | 09, 21 |
| 4 | AC1 (5 `test_accept_*`) + ratchets (`test_ratchet_check.py`) | **252 passed** (238+14), exit 0 — ningún ratchet relajado | 10-11, 22 |
| 5 | Suite normativa `-m "not property"` | **1182 passed · 0 failed · 1 deselected**, exit 0, 142 s | 23 |
| 6 | Property separada (`tests/property/`) | **1 passed**, exit 0 | 12, 24 |
| 7 | `ruff check --config governance/lint/ruff.toml .` / `ruff format --check` / `mypy tools/wct src` | **PASS / PASS (526 archivos) / PASS (135 archivos)** | 15-17 |
| 8 | `wct gate --tier fast` | **7 PASS · 0 FAIL**, exit 0 | 25 |
| 9 | `wct gate --tier commit` | **21 gates = 20 PASS · 1 FAIL**; el único rojo es **G-META-1** (drift protegido, resumen: `modificado: governance/lint/vulture_whitelist.py`); **G-DEAD PASS**; G-TEST PASS (148.6 s); G-MUT-SITES/G-SIZE/G-COGNITIVE PASS | 26 |

Conciliación de conteos: 1183 colectados = 1182 normativos + 1 property.
La cifra «1181 passed» del registro R3 §5 no es reproducible contra su
propia colección de 1183 nodeids (idéntica a esta); la conciliación de este
encargo es por nodeids (diff vacío contra `05-collect.txt` de R3), no por
conteo histórico. Presupuesto agregado de ejecución ≈ 470 s de 1200 s
(incluye el intento inválido documentado), sin mutación, Q-ACCMUT,
aceptación mutada ni full — prohibidos y no ejecutados.

## 7. Inventario sucesor y sellos

- **Snapshot histórico R8** (`build/tmp/p03a-hardening-c2-zct30u3n/candidate-r8.sha256`):
  digest del archivo verificado = `93acd1a5…` (sello íntegro, no
  sobrescrito; sigue verificando 37/37 contra su snapshot de origen). El
  manifiesto R8 **no se modifica** y este candidato **no declara identidad
  completa** con él.
- **Eliminación anterior de `InstanceReport`** (R3, `e75f96e`):
  `pytest_phases.py` `36844347…` → `ea95730c…` — sin cambios en R5.
- **Reparación anterior de O6** (fase 1, `757cb53`):
  `test_accept_typed_operator.py` diverge del sello `c23d7273…` (digest del
  archivo re-verificado) — sin cambios en R5; las otras 5 rutas de producto
  del sello fase 1 coinciden.
- **Eliminación actual de `expectation`** (R5): `pytest_scan_state.py`
  `dbbbef52…` → `0c995e77…`; `pytest_observation.py` `3ec593ba…` →
  `46309fc8…` (ambas rutas del sello R8; verificación actual del manifiesto
  R8 contra el candidato: **34/37 coinciden, 3 divergen** — phases (R3),
  scan_state y observation (R5)).
- **Whitelist**: `90e52d7f…` → (R3 `356a995`) `8c2f819b…` → (R5)
  `a2877ee8…`; 20 entradas REANCLAJE (17 R3 + 3 R5) + 7 preexistentes
  ADR-D-02.
- **Drift protegido re-medido** (`wct integrity check`): **36 rutas =
  2 modificadas** (`governance/lint/vulture_whitelist.py`,
  `tools/wct/accept/mutation_cases.py`) **+ 34 nuevas** — lista de rutas
  **byte-idéntica** a la de R3: los cambios de hash de R5 (whitelist,
  scan_state, observation) ocurren en rutas ya presentes del conjunto y no
  añaden ninguna. La cardinalidad se midió, no se asumió.

## 8. Dictamen del verifier independiente

**FAVORABLE, sin discrepancias** (agente distinto del autor, sin escritura
sobre el candidato; reejecución en copia desechable propia
`verifier/probe`). Puntos verificados: (1) DOCUMENTAL — cobertura de la
autorización sobre exactamente las 20 entradas de scope REANCLAJE (27
entradas totales = 7 ADR-D-02 + 17 R3 conservadas 1:1 contra la tabla §2 de
R4 + 3 nuevas en formato canónico; diff de whitelist solo aditivo, sin
patrones ni notación cualificada); (2) DOCUMENTAL — eliminación de
`expectation` exacta (declaración + kwarg + import + colapso de formato),
validaciones públicas intactas (`pytest_api_args.py`/`pytest_observation_validate.py`
sin cambios), cero cambios en tests/, `grep \.expectation` = 0; (3)
REEJECUCIÓN — controles 5→4→0 exactos y controles C (homónimos ocultos,
detector vivo con `zzz_dead_control`) y D (4 hallazgos reaparecen sin las 3
entradas); (4) REEJECUCIÓN — colección 1183, focales R8 426, operador 61,
ratchets 14; (5) DOCUMENTAL — solo las 3 rutas M + 1 doc nuevo, sin cambios
en thresholds/lock/log/pyproject/workflows/baselines, confianza vulture
60 intacta, ningún ratchet relajado; (6) REEJECUCIÓN — hashes de las 3
rutas coinciden con §3/§4, sello R8 digest íntegro y 34/37 contra el
candidato (divergen observation/phases/scan_state, como §7 declara), drift
36 rutas byte-idéntico a R3. Observaciones no bloqueantes: la clase
contenedora ajena del control C también se reporta (ya documentado en §5);
la publicación quedaba pendiente al dictaminar (ejecutada después, §9);
`mutation_cases.py` es drift heredado de fase 1, no de este encargo. El
dictamen acredita este cierre de G-DEAD, no la calificación integral de
P03a.

## 9. Publicación

Commits convencionales con byline, separando producto, gobernanza y
registro; push normal a PR #56 (permanece en borrador). Sin bless,
update-manifest, merge, bump, tag ni release. CI observada con seguimiento
acotado; pasos bloqueados por integridad se registran como NO EJECUTADOS.

## 10. Estado de las puertas tras este encargo

G-DEAD queda resuelto en el candidato del PR #56 (pendiente de fusión). La
secuencia posterior permanece: **G-DEAD resuelto → calificación exigible del
código incorporado (mutación/aceptación/cobertura/CRAP/DRY/full, en encargos
propios) → revisión protegida E9 del drift (36 rutas) → bless humano**. El
binding PA01–PA12 sigue pausado; P03a y beta.3 no están completos.
