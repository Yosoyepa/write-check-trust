# Addenda E11 — cuatro precisiones previas a la autorización de merge (2026-09-17)

Addenda de `REVISION-E11-PR53-2026-09-17.md`. Cierra TEST-006 con ejecución,
corrige la interpretación contractual de AC1, fija el criterio de identidad
post-merge y re-cuenta la tabla de obligaciones. No repite la auditoría, no
reabre equivalencias ratificadas, no cambia producto, tests, dependencias ni
gobernanza, y no ejecuta bless, salida de borrador, aprobación GitHub, merge,
bump, tag ni release. Conserva la historia: las conclusiones previas del
informe se corrigen por nota sucesora, no se borran.

## 0. Identidades

| Elemento | Valor |
|---|---|
| Candidato técnico auditado por E11 | `32d3491b3a98543d7b13c933482d3ced4ac49a4b` |
| SHA documental revisado por E11 y base de esta addenda | `7402f643e10c4f285e2015257384b88d19942f49` = HEAD = `origin` = headRefOid (sin avance; base `932c835` = merge-base) |
| Árbol de las corridas TEST-006 | copia aislada con raíz Git propia @ `7402f64` (`build/tmp/test006-precision/audit/`, limpia); código idéntico al candidato técnico (delta `32d3491..7402f64` exclusivamente documental, sin `.py`) |
| CI al iniciar | run `35270112933` success sobre `7402f64` |
| Índice | limpio; único sin seguimiento el documento ajeno `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, preservado |

## 1. Frente A — TEST-006: exigible, y satisfecho por ejecución

**Obligación normativa.** `governance/rules/10-testing.yaml:69-77` (regla
TEST-006, **severity: hard**): «Los tests deben pasar en orden aleatorio. Si
fallan con `-p randomly`, hay estado compartido entre tests»;
`verified_by: [G-TEST-RANDOM]`. Implementación/configuración del gate:
`docs/gates.md:164` — G-TEST-RANDOM «sin flujo automático: exige el plugin
`pytest-randomly` (decisión pendiente)», comando documentado
`pytest --randomly-seed=last`; no pertenece a los tiers fast/commit ni a los
checks requeridos de la PR. **La ausencia de cableado automático no es una
dispensa**: la única «decisión pendiente» registrada es sobre el flujo
automático del gate. **No se localizó disposición humana que cubra la omisión
de TEST-006 para este candidato** → la obligación era exigible y se ejecutó.

**Evidencia histórica y su identidad.** Única corrida previa:
`RESULTADO-AC1-R2-REANUDACION-2026-09-13.md` (2026-09-13), pytest-randomly
5.0.0, 4 semillas, sobre la suite de entonces (639 tests). No cubría la
suite final (694/696 con el fixture autouse `git_isolation`).

**Entorno y procedencia (sin instalar nada).** Plugin **pytest-randomly
5.0.0** ya disponible en la caché local de uv
(`~/.cache/uv/archive-v0/grPZpdr9fjaqm_RE`, dist-info verificado; misma
versión que la evidencia histórica), cargado por `PYTHONPATH` en procesos
aislados. Cero instalaciones, cero cambios al runtime compartido, al lock o
a dependencias. Runtime acreditado: `.venv` del worktree (Python 3.13),
`PATH` completo del venv; cwd: raíz de la copia aislada. **Interfaz real
comprobada**: `--randomly-seed=<int|last>`; `-p no:randomly` deshabilita;
la cabecera imprime `Using --randomly-seed=N`.

**Receta y resultados.** Selección canónica del gate G-TEST
(`tools/wct/gate/registry_static.py:43`: `pytest -q tests/unit
tests/integration -m "not property"`; la CI `quality.yml:45` usa el mismo
marcado `-m "not property"` sobre el árbol completo, con cobertura):
`pytest -q tests/unit tests/integration -m "not property"`. TEST-008
respetado (property excluido por marcador). **Exclusión contractual
declarada**: `tests/acceptance/generated/test_acceptance.py` — el único test
no-property fuera de unit/integration — es el artefacto generado por
herramienta cuyo ámbito es G-ACCEPT/la campaña de aceptación
(CONTRATO-AC1: «solo regenerado por herramienta»); ningún caso se retiró
para obtener verde.

| Corrida | Argumentos | Resultado | Duración |
|---|---|---|---|
| Baseline | `-p no:randomly` | **694 passed**, 0 failed/skipped/xfailed, exit 0 | 124 s (+1 s collect) |
| Semilla 42 | `--randomly-seed=42` | **694 passed**, 0 failed/skipped/xfailed, exit 0 | 116 s (+2 s) |
| Semilla 1234 | `--randomly-seed=1234` | **694 passed**, 0 failed/skipped/xfailed, exit 0 | 114 s (+2 s) |
| Semilla 987654321 | `--randomly-seed=987654321` | **694 passed**, 0 failed/skipped/xfailed, exit 0 | 116 s (+1 s) |

- **Misma selección y conjunto de nodeids en las cuatro**: 694 nodeids,
  conjuntos ordenados idénticos por comparación byte a byte.
- **Aleatorización efectiva y órdenes distintos**: las colecciones
  reorganizadas difieren entre las cuatro corridas (base ≠ s42 ≠ s1234 ≠
  s987654321); los archivos de colección se conservan como registro del
  orden efectivo (`collect-*.txt`).
- **Semilla acreditada, no supuesta**: cabecera `Using --randomly-seed=42`
  capturada; determinismo verificado re-colectando con semilla 42 → orden
  byte-idéntico.
- **Presupuesto**: ≈490 s de 900 (4 corridas + colecciones + comprobaciones
  de conjuntos/determinismo). Sin fallos: nada que registrar en PROC-013.
- **Reproducción independiente**: el verifier de esta addenda re-ejecutó una
  corrida completa con `--randomly-seed=1234` (113 s; exit 0; «694 passed»;
  colección byte-idéntica en orden a la del autor) — dictamen FIEL en sus
  cinco secciones, con tres desviaciones menores de artefactos de trabajo
  (línea de log de semilla no impresa bajo `-q`; gloss de CI precisado arriba;
  comparables `ns-*.sorted` con líneas de tiempos) que no afectan los
  resultados publicados aquí.

**Alcance del crédito**: acredita este runtime y los órdenes medidos sobre
`7402f64` (idéntico en código al candidato técnico); no independencia
universal del orden ni futuras suites. Evidencia en
`build/tmp/test006-precision/` (temporal; lo durable es esta addenda).

**Estado**: OBL-10 **SATISFECHA POR EJECUCIÓN**.

## 2. Frente B — AC1: sustentado por las obligaciones y decisiones vigentes

Se corrige la afirmación de E11 §4.B («Falta una campaña killed=planned o
una decisión humana de mantener el cierre por adjudicación como terminal»):
**la decisión existe y está registrada**; no se solicita de nuevo (sin
invalidante). Trazabilidad separada por ámbito:

**A. Mutación de fuentes** (obligación: TEST-002 sobre las fuentes nuevas,
precisada por el procedimiento):
- Brutos históricos inmutables por capas: r2 498=468+30; r2b 486=462+24;
  r3 497=450+47; GS-1 282=280+2; GS-2 102+16 (+sucesiva 118); GS-3
  108=74+34; fase E 27+4 (+micro 4; recampaña 31+0); cleanup 8=6+2; SAST
  74=69+5.
- Disposiciones humanas por ID: 14 equivalencias r3 ratificadas (A1/A2/
  A4–A11, A12, A13, execute__28/29); **excepción puntual TEST-002** para
  B1–B5 y terminate__7 — texto registrado en `ACTA-DECISIONES-FINALES-Y-
  QACCMUT-2026-09-16.md` §3.1: «Para B1–B5 y terminate__7 autorizo una
  excepción humana puntual a TEST-002 para la salida incremental de PR #53,
  únicamente para los IDs que satisfagan las condiciones anteriores…»;
  defectos con regresión permanente (A14, terminate__6, C2, A3, C3);
  comprobación alternativa de los 2 hooks aceptada (§2.3); **928 IDs
  delimitados** por identidad/diff (aprobación §2.4); 5 sucesoras SAST
  ratificadas D-A' (2026-09-17).
- **Decisión de cierre de la puerta**: `CALIFICACION-COBERTURA-CRAP-DRY-
  2026-09-16.md` §2.1: «La obligación que el procedimiento exige para
  continuar es **resolver la mutación de fuentes** (adjudicación), no
  "ejecutar y pasar el gate G-MUT"»; §2.4: «Resultado: **1.
  PUERTA-CONFORME-POR-CIERRE-ADJUDICADO**», con verifier independiente
  APROBAR CON RESERVAS NO BLOQUEANTES. Invalidantes: los registrados por
  cada acta (cambio de fuente/runtime/precondiciones por ID).

**B. Mutación de aceptación** (contrato de campaña):
- `CONTRATO-AC1.md:101-102`: «Solo baseline sano, trabajo >0,
  **killed=planned** y cero survived/errors/not_run permite aprobar» —
  cláusula del **veredicto de campaña de aceptación** (qué permite aprobar
  una campaña `run_mutations`), no de las fuentes.
- **Q-ACCMUT: 47/47 killed + 0 errores + 0 not_run** (ACTA §8) sobre el
  feature `wct-acceptance-evidence-001` (47 celdas = 40+7) = killed=planned
  satisfecho en su ámbito. Vigencia sobre el candidato: repetición fresca
  tras cada cambio de `process.py`; 8/8 anclajes re-medidos en HEAD por el
  revisor B de E11.

**Determinación.** `killed=planned` corresponde a la campaña de aceptación
(satisfecho); **no** es una obligación separada de fuentes — esa fue
precisada por decisión humana vigente (cierre adjudicado). No se traslada
la regla entre campañas por compartir la palabra «mutación»: las cláusulas
citadas son distintas y están en documentos distintos.

**Conclusión (opción 1)**: AC1 queda **sustentado por las obligaciones y
decisiones vigentes** — cadena completa: fuentes resueltas por adjudicación
autorizada → Q-ACCMUT 47/47 → cobertura/CRAP/DRY → full PRE-BLESS (único
rojo G-META-1, resuelto por el bless) → POST-BLESS + CI verde. Lo único que
no existe es una **declaración humana formal posterior** «AC1 acreditado»:
ninguna fuente normativa localizada la exige como condición separada tras
el cierre adjudicado; queda como etiqueta disponible para el humano, no
como evidencia faltante. Hechos separados que se conservan: G-MUT de
fuentes **no ejecutado (sin PASS)**; las ratificaciones no convierten
`survived` en `killed`. **AC1 no es condición de merge** según el plan
(PLAN-EJECUTABLE §1 separa «AC1 no acreditado» de «integración/publicación
bloqueadas por pendientes técnicos, revisión protegida, bless y CI» — estos
últimos, ya resueltos).

## 3. Frente C — identidad post-merge: procedimiento (sin ejecutar)

Se corrige el criterio «M debe resolver al SHA técnico»: con
`required_linear_history=true` en la protección de main, el merge será
rebase o squash y **M tendrá otro SHA por construcción**. La vigencia del
dictamen depende del **árbol integrado**, no del parentesco de commits.

Procedimiento futuro (a ejecutar tras el merge, en un encargo propio):

1. Registrar SHA de cabeza de la PR, base efectiva y **M** (commit
   integrado), con padres y estrategia efectiva (rebase/squash).
2. Comparar el **árbol** de M con el candidato revisado:
   `git diff --stat <candidato> M` y, idealmente, igualdad de tree hash
   (`git rev-parse M^{tree}` vs el del candidato). Si los árboles son
   idénticos, **registrar esa igualdad** con el comando y el hash — no
   asumirla por parentesco ni exigir igualdad de SHA.
3. Clasificar toda diferencia: documental vs producto/configuración.
4. Si main avanzó desde `932c835`: revisar el delta de integración (qué
   entró de main y qué toca del incremento).
5. Verificar sobre M: `wct integrity check` y la CI asociada a ese SHA.
6. Recalificar lo afectado por diferencias materiales; **no trasladar
   evidencia automáticamente ante cambios relevantes** (fuente, runtime,
   precondiciones o config).
7. Identidades siempre separadas: candidato técnico `4217253…`; commit de
   bless `1fc7915…`; documentales sucesivos (…`32d3491`, `7402f64`, esta
   addenda); futuro **M**; futuro **tag V** (requiere decisión D3 sobre SHA
   verificado). `lock.commit` conserva `903f961…`: no se edita; su
   semántica es referir el candidato aprobado en el momento del bless.

## 4. Frente D — contabilidad corregida (16 filas, sin doble conteo)

El informe E11 §3 contiene **16 filas reales**: 8 SATISFECHA POR EJECUCIÓN +
4 SATISFECHA POR ADJUDICACIÓN AUTORIZADA + 1 FUERA DEL INCREMENTO +
3 PENDIENTE. El «11 por ejecución + 4 + 1» de la entrega fue un **error de
resumen** (la tabla del informe nunca lo dijo); los 3 pendientes **son filas
adicionales** (OBL-10, OBL-15, OBL-16), no sub-obligaciones ni estados
superpuestos. Tras esta addenda: OBL-10 pasa a ejecución (§1) y OBL-15 pasa
a adjudicación (§2). Totales corregidos: **9 ejecución + 5 adjudicación +
1 fuera + 1 pendiente = 16**.

| ID | Obligación | Estado principal | Alcance / evidencia | Pendiente subordinado | Efecto |
|---|---|---|---|---|---|
| OBL-01 | Mutación de fuentes AC1 (brutos r2/r2b/r3) | ADJUDICACIÓN | actas por capa; brutos intactos | — | merge: none; AC1: base |
| OBL-02 | Equivalencias y excepciones por ID | ADJUDICACIÓN | 14+excepción puntual+casts+5 sucesoras D-A' | nota de re-anclaje A12/A13/terminate__7 (H2, documental) | merge: none |
| OBL-03 | 928 IDs no ejecutados | FUERA, CON FUNDAMENTO | ACTA §2.4 delimitación por identidad/diff | — | — |
| OBL-04 | Partición TEST-007 | EJECUCIÓN | 17 archivos ≤100 sitios; revisor A más allá del AST | — | merge: none |
| OBL-05 | Hooks no instrumentados | ADJUDICACIÓN | comprobación alternativa aceptada (ACTA §2.3) | — | — |
| OBL-06 | Q-ACCMUT (killed=planned de aceptación) | EJECUCIÓN | 47/47; 8/8 anclajes re-medidos en HEAD | — | AC1: cadena |
| OBL-07 | Cobertura de rama TEST-004 | EJECUCIÓN | 314/348 = 90,23 %; denominador probado | — | merge: none |
| OBL-08 | CRAP | EJECUCIÓN | canónico+focal; suplementario delimitado (66 preexistente/trasladada) | frontera 12 como deuda registrada | — |
| OBL-09 | DRY | EJECUCIÓN | 0/17 = 17/0; jscpd 0 | — | — |
| OBL-10 | Orden aleatorio TEST-006 | **EJECUCIÓN (esta addenda §1)** | 4 corridas, 694 passed, semillas 42/1234/987654321 | corrida futura si cambia la suite | merge: none |
| OBL-11 | Full PRE-BLESS | EJECUCIÓN | 34 = 33 PASS + G-META-1 (4217253) | — | — |
| OBL-12 | POST-BLESS + CI | EJECUCIÓN | integrity 0; tier 21/21; commit-gates PASS | — | merge: satisfecho |
| OBL-13 | Desviación de secuencia | ADJUDICACIÓN | D-B' puntual; no conforme, sin permiso general | — | — |
| OBL-14 | E9 + bless humano | EJECUCIÓN | delta +30/0, 7+log; verifier favorable | — | merge: satisfecho |
| OBL-15 | Acreditación AC1 | **ADJUDICACIÓN (corrección §2)** | cadena completa sustentada; PUERTA-CONFORME-POR-CIERRE-ADJUDICADO | etiqueta formal humana opcional | merge: no es condición |
| OBL-16 | Full POST-BLESS | PENDIENTE (no bloqueante) | insumos de los 33 gates verdes sin cambio por identidad desde 4217253 | correr `--tier full` sobre M si se desea | beta.3: candidato |

## 5. Dictamen reiterado

**APTO PARA MERGE.** Sin bloqueantes confirmados ni obligaciones exigibles
pendientes para integrar. TEST-006, exigible por regla severity hard, quedó
**satisfecho por ejecución** (§1). AC1 está sustentado y **no es condición
de merge** según el plan (§2). Quedan como pendientes exclusivos de
beta.3/release: OBL-16 (opcional sobre M), E10 (bump/lock/tag sin
autorizar), identificación de M y recalificación post-merge (§3), custodia/
SBOM/smokes y el resto de fases B3-P2…P6. Decisiones humanas pendientes:
aprobar la PR, sacarla de borrador y fusionar (procedimiento §3). Mejoras no
bloqueantes de E11: sin cambios (H1, H2, verdict.py:42-43, fila G-DEAD,
banda pytest, cosméticos — con sus recetas).
