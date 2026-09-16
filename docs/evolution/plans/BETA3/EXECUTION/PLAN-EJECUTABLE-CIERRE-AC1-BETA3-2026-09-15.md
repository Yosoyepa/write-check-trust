# Plan ejecutable — cierre AC1 y salida beta.3 (2026-09-15)

Consolida los pendientes reales de AC1 y beta.3 tras el cierre acotado GS-3
(`ACTA-CIERRE-ACOTADO-GS3-2026-09-15.md`) y propone un orden ejecutable por
oleadas. **Este documento es un plan: no autoriza nada.** No ejecuta campañas,
no cambia producto, tests, features, gobernanza, dependencias ni umbrales, y
no habilita bless, `update-manifest`, merge, bump, tag ni release. Nada aquí
sustituye una decisión humana explícita.

Estado de partida verificado (2026-09-15):

- Rama `codex/beta3-ac1-r2-integration`, HEAD `5d9ea2d`, igual a
  `origin`; PR #53 `OPEN`, **borrador**, `mergeStateStatus: BLOCKED`, única
  check `commit-gates` en FAILURE (run `35034583947`), detenida en
  `wct integrity check` por el drift de rutas protegidas (G-META-1/E9).
- Drift protegido real re-verificado con `wct integrity check` en HEAD:
  **23 rutas = 7 modificadas + 16 nuevas** (medido en esta consolidación; no
  se hereda de documentos previos).
- Los pasos posteriores a integridad en CI **no se ejecutaron** (tier commit,
  `pip-audit`, cobertura, ratchets, property, diff-cover, aceptación y
  redteam): no hay resultado de CI para ellos.
- La reparación G-DEPS/G-DEAD ya está integrada (`b4403c5`); el tier commit
  quedó en 20 PASS + 1 FAIL (solo G-META-1) según los registros de
  `REPARACION-INTEGRACION-GDEPS-GDEAD` §6 y `GS3-CONTRATOS…` §6 (corrida del
  coder; no re-ejecutada por el verifier de este plan). Las filas de
  documentos previos que describían esa reparación como pendiente quedan
  supersedidas por la medición actual, sin reescribir actas históricas.
- Expediente `build/tmp/gs3-dominio.2512829890` (checkout principal) presente
  y conforme (`sha256sum -c`); digest del manifiesto `c2c97d1e…`. La evidencia
  durable, en todo caso, es el registro versionado.

Fuentes principales: `MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md`
(§A–E y E1–E11), los registros GS-1/2/3 de esta rama,
`CALIFICACION-AC1.md`, `CONTRATO-AC1.md`, `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`
(local, no seguido), `BETA3/PLAN.md`, `docs/gates.md`, `governance/rules/` y
`governance/thresholds.yaml`, y el documento local
`DECISION-INTEGRACION-Y-SIGUIENTE-INCREMENTO-2026-09-13.md` (checkout
principal, solo lectura).

## 1. Tres cierres distintos (no intercambiables)

| Cierre | Qué exige | Estado actual |
|---|---|---|
| **Acreditación AC1** | Invariante del `CONTRATO-AC1.md` (baseline válida, `killed=planned`, cero survived/errors/not_run) sobre la cadena E8 (aceptación mutada → cobertura/CRAP → DRY → tier full), con decisiones D-A/D-B/D-C/D-D, E1/E2 (928), E4-PASS, E6 y E7 resueltas | **No acreditado**; E8 «no iniciado»; decisión de operador/tabla de aceptación pendiente |
| **Integración / salida incremental (PR #53)** | Calificación pre-merge del candidato + revisión del diff protegido + bless humano único + CI verde + merge; después custodia, SBOM, smokes, tag/prerelease y D3 | **Bloqueada**: borrador, BLOCKED, CI roja en integridad; sin bless |
| **beta.3 completa** | `BETA3/PLAN.md` §1 (B3-P0…P6) y §5 (contrato de salida), incluida la decisión G1b si se exige ese claim | **No completa ni publicada**; P02–P10 no implementadas según `BETA3/README.md` |

**El merge de PR #53 no cierra beta.3 completa.** Cierre AC1, salida
incremental y beta.3 integral son alcances separados y así se reportan.

## 2. Inventario único de pendientes

Una fila por pendiente real. «Tipo»: D = decisión humana, I = implementación,
V = verificación/ejecución. Los presupuestos marcados **(est.)** son
estimaciones, no mediciones; los que citan umbral los toman de
`governance/thresholds.yaml` o `docs/gates.md`.

| ID | Obligación / contrato | Estado actual | Fuente y evidencia | Qué falta exactamente | Tipo | Dependencias | Criterio de cierre | Allowlist propuesta | Presupuesto (estimación) |
|---|---|---|---|---|---|---|---|---|---|
| `R3-DA-10` | Ratificar/rechazar 10 equivalencias r3: A1, A2, A4–A11 | Pendiente; arquitectura recomienda ratificar (runtime) | MATRIZ §A; `ADJUDICACION-SUPERVIVIENTES-AC1-R3`; `DECISION-INTEGRACION…` §5 | Decisión humana por ID bajo bytes, runtime y precondiciones de la matriz; sin tests cosméticos nuevos | D | `R3-CAST` | Decisión registrada; si ratifica, equivalencia acotada (no convierte `survived`→`killed`) | — (sin código) | — |
| `R3-DA-4` | Ratificar/rechazar A3, A12, A13, A14 (justificaciones bajo revisión) | Pendiente; **no ratificar con las justificaciones actuales** | MATRIZ §A; r3 md:50,64-66; `DECISION-INTEGRACION…` §4 | Decisión con IDs y mutaciones **corregidos** (A13 `_14` = `remaining+1→remaining+2`; A14 `_17` = `continue→break`; `select 0.05→1.05` es `_2`, ya con regresión); revisión causal acotada si se pide | D (+I/V acotada) | — | Decisión registrada; rechazo deja hueco abierto para incremento propio | `tests/unit/test_accept_campaign.py` si la revisión acotada añade pruebas | revisión acotada ≤300 s (est.) si se autoriza |
| `R3-DB` | Decidir B1–B5 (15 IDs no contratados) | Pendiente | MATRIZ §B; r3 md:35-45,72-78 | Contrato observable (aserción normativa) vs presentación (sin test); prohibido equivalencia por omisión o exclusión silenciosa | D (+I si contrato) | — (recomendado antes de D-A) | Decisión por familia registrada | `tests/unit/test_accept_campaign.py`, `tests/unit/test_accept_pytest.py` | ≤120 s (est.) si contrato |
| `R3-DC` | Decidir C1–C3 (7 IDs, límites instrumentales) | Pendiente | MATRIZ §C; r3 md:48-52,62,69-70 | ¿Límite = contrato operativo? Si sí: dobles por puntos de sustitución existentes (sin cambio de producto) en incremento TDD propio; si no: sin ratificar | D (+I) | — | Decisión registrada; si contrato, incremento con TDD y verifier | `tests/unit/test_accept_campaign.py` (transporte) | ≤300 s (est.) |
| `R3-DD` | Autorizar comprobación alternativa de 2 hooks decorados | Especificada, no ejecutada | MATRIZ §D; `ADENDA-AC1-R3…` §6; r3 json | Decisión; si autoriza, ejecutar control + sembrados HOOK-MR-01/HOOK-SF-01 con semillas/expectativas fijas, 30 s, grupo propio y limpieza en `finally` | D (+V) | — | Decisión registrada; si autoriza, dictamen con evidencia | expediente `build/tmp/ac1-r2-qualification/r3-hook-alternative/<run>/` (no producto) | ≤120 s (est.) |
| `R3-CAST` | Efecto del descomillado de casts sobre referencias históricas | `process.py` cambió de bytes (`bdbb5646…`→`84b9340f…`); la evidencia r3/GS no se traslada sola | `REPARACION-INTEGRACION-GDEPS-GDEAD` §2.3 y §5 | Registrar análisis de impacto y transferencia (delta = 2 líneas; `typing.cast` identidad runtime; 213 tests de transporte verdes) o exigir re-verificación afectada; sin recampaña automática | D/V documental | Insumo para `R3-DA-10` | Transferencia registrada o verificación programada | — | — |
| `PX-928` | Destino de los 928 IDs no ejecutados (959 generados; subconjunto de 31 ejecutado) | Fuera del subconjunto aprobado; ni exclusión aceptada ni campaña autorizada | `RECETA-FASE-G`; `ADJUDICACION-FASE-E`; MATRIZ E1/E2; `PREPARACION-LOTE-GATE-SELFTEST…` §6 | Decisión de alcance: opción A (excluir los 3 archivos con limitación registrada), opción B (archivos completos con sobre-alcance medido y frontera ≤100 autorizada) o diferir. No es deuda automática ni exclusión automática | D (+V si B) | `PX-T007` (frontera compartida) | Decisión registrada; si B, preflight y autorización propios | — | si B: recalibrar en preflight; orden de magnitud 928 × ~4-5 s ≈ 4.000–5.000 s (est.) |
| `PX-REG` | Comprobación conductual del despacho SAST (`REGISTRY["G-SAST-SEMGREP"]`) | Pendiente (GS-4/E6); huecos (a)(b)(c) | MATRIZ E6; `ADENDA-PREPARACION…` §5 | Decidir si los huecos son contrato; si sí: test de despacho extremo a extremo, rama SKIP con `which`→None y comando según contrato existente | D (+I) | — | Tests verdes con allowlist respetada; sin cambio de producto | `tests/unit/test_sast_targets.py` | ≤120 s (est.) |
| `PX-T007` | TEST-007: archivos cambiados >100 sitios WCT | Abierta; G-MUT-SITES en PASS por lectura diferencial (funciones cambiadas ≤100) | `governance/rules/10-testing.yaml`; `ADENDA-PREPARACION…` §3; `DECISION-INTEGRACION…` §5 | checks.py **258**, runner.py **442**, fixtures_tools.py **191**. Decidir partición fachada (cada módulo ≤100, tests intactos) o excepción humana acotada por ruta/diff (procedimiento no existente; requiere aprobación explícita y, si toca gobernanza, autorización separada). Sin excepción, rige la partición | D (+I si partición) | `PX-928`; SEC-005 si gobernanza | Decisión registrada; partición entregada o excepción inequívoca | módulos nuevos de la partición (≤100 sitios c/u) | partición: 3 incrementos (est.); excepción: 0 |
| `Q-DESIGN-ACC` | Diseño del operador/tabla de aceptación AC1 (48 celdas; tokens fuera de vocabulario; ≥1 fila no discriminante) | No resuelto; P03a no se incorpora implícitamente a #53 | `CALIFICACION-AC1.md`; `DECISION-INTEGRACION…` §6 | Cerrar operador/tabla por contrato y aprobación **antes** de ejecutar aceptación mutada | D + I (incremento propio) | — | Contrato del operador/tabla aprobado | según su incremento (features/tests) | por definir en su incremento |
| `Q-ACCMUT` | Mutación de aceptación (G-ACCEPT-MUT) sobre la feature AC1 | No iniciada | MATRIZ E8; `CONTRATO-AC1.md` (baseline válida; `killed=planned`; 0 survived/errors/not_run) | Ejecutar sobre candidato congelado con operador resuelto y contrato del recibo | V | `Q-DESIGN-ACC`; decisiones de lotes | Resultado conforme al invariante AC1, con evidencia y verifier | features/tests del incremento de aceptación si aplica | ≤900 s (est.) |
| `Q-COVCRAP` | LCOV nuevo + cobertura de diff ≥90 % + CRAP ≤6 en cambiado; ratchet total | No iniciada | MATRIZ E8; thresholds (90 %, CRAP 6); PROC-004 | Ejecutar tras aceptación mutada sobre el candidato | V | `Q-ACCMUT` | Puertas verdes con el LCOV del candidato | `build/coverage/lcov.info` | ≤600 s (est.) |
| `Q-DRY` | DRY estructural/tokens/plantillas | No iniciada | MATRIZ E8; `wct dry`; jscpd; PROC-004 | Ejecutar tras cobertura/CRAP | V | `Q-COVCRAP` | Cero duplicación nueva; findings resueltos | — | ≤600 s (est.) |
| `Q-FULL` | Tier full (34 gates) | No iniciado | MATRIZ E8; `docs/gates.md` (30 min) | Ejecutar tras DRY; incluye G-SAST-SEMGREP y el resto del tier | V | `Q-DRY`; `Q-PRE-EQ` | 34/34 sin ERROR/FAIL bloqueante | — | 1800 s (tope vigente) |
| `Q-RANDOM` | Orden aleatorio y obligaciones vigentes (TEST-006/008/011) | No iniciado | MATRIZ E8; `governance/rules/`; `BETA3/PLAN.md` §4 | Correr suite en orden aleatorio, property separado y colección | V | — | Sin dependencias de orden; property fuera de gates | — | ≤600 s (est.) |
| `Q-PRE-EQ` | Precondiciones de 24/29/33 en el SHA final | Definida en el acta; no ejecutada | `ACTA-CIERRE-ACOTADO-GS3` §5 | Ejecutar y conservar evidencia (productor 1.174.0, hash de `semgrep.py`, COMMAND, encoding UTF-8 efectivo, stdout sin BOM) | V | candidato congelado | Evidencia conservada; si falla, la ratificación no se traslada | — | ≤120 s (est.) |
| `E4-PASS` | Decisión humana sobre el PASS del lote GS-2 | Pendiente; cierre acotado de atribución ya registrado | MATRIZ E4; `GS2-REVALIDACION…` §5.1 | Decidir PASS del lote o mantener NO PASS | D | — | Decisión registrada | — | — |
| `INT-DIFF` | Revisión del diff protegido acumulado | Drift real de **23 rutas (7 + 16)** re-verificado en `5d9ea2d`; sin lista itemizada en documentos | MATRIZ E9; `REPARACION-INTEGRACION…` §8; `wct integrity check` | Lista itemizada y revisión humana del diff protegido completo (incluida versión/lock si se autoriza). G-META-1 pertenece al incremento acumulado, no es «ajeno» a la entrega global | D (revisión humana) | candidato final congelado | Revisión registrada | — | — |
| `INT-BLESS` | Bless humano único del diff protegido final | No ejecutado; G-META-1 es el único rojo del tier commit | MATRIZ E9; `docs/runbook.md`; SEC-005 (agentes bloqueados) | Humano ejecuta bless con `--approved-by` y motivo; registro en `governance/integrity-log.md` | D (acción humana) | `INT-DIFF`; pendientes técnicos y versión resueltos | G-META-1 verde; la CI continúa | diff protegido final | — |
| `INT-CI` | CI completa de la PR | Detenida en integridad (run `35034583947`); pasos posteriores no ejecutados | PR #53; `.github/workflows/quality.yml` | Tras el bless: correr y dejar verdes tier commit, pip-audit, cobertura, ratchets, property, diff-cover, aceptación y redteam | V | `INT-BLESS` | CI verde en el HEAD de la PR | — | — |
| `INT-REVIEW` | Revisión integral, salida de borrador y merge (E11) | Pendiente; E1–E9 no conformes | MATRIZ E11; `PREPARACION-SALIDA…` §2 | Revisión humana del diff completo; salir de borrador y merge solo con autorización explícita | D | `INT-CI` y decisiones previas | Merge autorizado y ejecutado | — | — |
| `REL-SCOPE` | Alcance entregado de beta.3 frente al planificado | PR #53 es integración AC1/R2; B3-P0…P6 no implementadas | `BETA3/README.md`; `BETA3/PLAN.md` §1/§5; `EXECUTION/README.md` | Decisión de alcance y notas beta.2→beta.3 que separen entregado/experimental/diferido | D | — | Alcance declarado con límites explícitos | — | — |
| `REL-VERSION` | Convención de versión/tag (E10) | Pendiente; vigente `1.0.0-beta.2`; propuestas `v1.0.0-beta.3` (PLAN §5) y `1.0.0b3.dev1`/`v1.0.0b3.dev1` (PREPARACION §6) | MATRIZ E10; `pyproject.toml`; `BETA3/PLAN.md` §5 | Decisión humana de la convención; bump/lock/notas en commit propio antes del congelamiento final | D (+I) | `REL-SCOPE` | Convención aprobada y aplicada antes de la revisión protegida | `pyproject.toml`, `uv.lock`, notas | — |
| `REL-CUSTODY` | Custodia y recuperación de evidencia | `local-only`; sin copia durable ni prueba de recuperación | `PREPARACION-SALIDA…` §5 (5.1–5.3) | Decidir destino/owner durable; manifiesto no circular; prueba de recuperación en host limpio. No depende de la release | D + V | — | Recuperación verificada desde el destino antes de D3 | `CUSTODIA-BETA3.1.json` + `.sha256`; bundle + `SHA256SUMS` | ≤600 s (est.) la prueba |
| `REL-PUB` | SHA final, SBOM, smokes, tag y verificación remota (D3) | No iniciado | `BETA3/PLAN.md` §5; `PREPARACION-SALIDA…` §2/§8; `RELEASES.md` | Congelar SHA tras bump; SBOM; full hardening; smoke pre/post-tag; tag inmutable; prerelease; verificar `isPrerelease/isDraft/tag→SHA/assets/Latest`; verificación post-merge del SHA real; cualquier bloqueo = NO-GO | V + D (D3) | `INT-REVIEW`; `REL-CUSTODY`; `REL-VERSION` | Prerelease verificado al SHA aprobado, o NO-GO declarado | `build/sbom.json`; artefactos del tag | 1800 s full + smokes (tope vigente) |

## 3. Priorización (sin ampliar el proyecto)

**1. Bloqueante para calificar AC1**: `R3-DA-10`, `R3-DA-4`, `R3-DB`,
`R3-DC`, `R3-DD`, `R3-CAST`, `PX-928`, `PX-REG`, `PX-T007`, `Q-DESIGN-ACC`,
`Q-ACCMUT`, `Q-COVCRAP`, `Q-DRY`, `Q-FULL`, `Q-RANDOM`, `Q-PRE-EQ`,
`E4-PASS`.

**2. Bloqueante para integrar/publicar el alcance elegido**: `INT-DIFF`,
`INT-BLESS`, `INT-CI`, `INT-REVIEW`, `REL-SCOPE`, `REL-VERSION`,
`REL-CUSTODY`, `REL-PUB`.

**3. Mejora opcional o trabajo futuro** (requiere fundamento y decisión; no
se usa para eludir obligaciones):

- Convertir el decode error en `ERROR` estructurado «salida ilegible»: **hoy
  no autorizado** (D2); solo con encargo propio que justifique el cambio de
  producto. No es un pendiente de este cierre.
- Reabrir la presentación de O5 (`mutmut_8/25` de `semgrep_verdict`) si se
  retirase el contrato de presentación aprobado; no es el caso hoy.
- Resto de beta.3 fuera de este alcance (`B3-P4` contratos de contexto,
  `B3-P5` piloto, `G1b` si no se exige su claim): backlog de `BETA3/PLAN.md`
  §1/§6, no de esta salida.

Los grupos D-B/D-C/D-D se deciden juntos (una sesión) para no fragmentar en
encargos de una corrección; sus implementaciones, si se aprueban, van en
incrementos separados con límites de autorización propios.

## 4. Plan por oleadas

### O0 — Publicación de este cierre (este encargo)

- Precondiciones: decisiones D1–D3 recibidas; fuentes leídas; comprobaciones
  ligeras de identidad/hash hechas.
- Tareas: este plan + `ACTA-CIERRE-ACOTADO-GS3-2026-09-15.md` + actualización
  acotada de la matriz; verifier independiente; `git diff --check`; fast;
  commit y push a la rama de PR #53 (PR sigue en borrador).
- Parada: publicar solo con revisión independiente favorable y fast verde.
- Ya ejecutado al publicar este documento.

### O1 — Decisiones humanas agrupadas (sin trabajo técnico pesado)

- **Precondiciones**: O0 publicada.
- **Paralelizable** (solo lectura, directorios independientes bajo
  `build/tmp/`, sin tocar la rama): dossier R3 (`R3-DA-10/4`, `R3-CAST`),
  dossier preexistente (`PX-928`, `PX-T007`), dossier aceptación/release
  (`Q-DESIGN-ACC`, `REL-SCOPE`, `REL-VERSION`, `REL-CUSTODY`).
- **Dependiente**: ninguna entre sí; todas confluyen en una única sesión de
  decisión.
- **Puerta de verifier**: verifier de solo lectura comprueba que cada
  decisión no inventa autorizaciones, que las citas existen y que no se
  convierte en cierre lo que es propuesta.
- **Criterio de parada**: decisiones registradas en un acta de decisiones
  (con ratificaciones/rechazos explícitos por ID y alcance).
- **Commit/push**: commit documental con el acta; no mezclar con otros
  cambios.

### O2 — Incrementos aprobados (implementación/verificación acotada)

- **Precondiciones**: O1 con decisiones registradas.
- **Paralelizable** en worktrees separados, cada uno con su rama: `PX-REG`
  (tests); `R3-DD` (comprobación de hooks, si autorizada); `R3-DB`/`R3-DC`
  (tests si sus contratos se aprueban); `PX-T007` partición (si se aprueba;
  3 sub-incrementos seriados dentro de su worktree); `Q-DESIGN-ACC`
  (candidato separado, nunca incorporado implícitamente a #53);
  `REL-VERSION` bump/lock/notas (si se aprueba; commit propio y entra al
  candidato final).
- **Dependiente**: no compartir índices ni árboles mutables; cada incremento
  su verifier y su fast.
- **Puerta de verifier**: por incremento (PROC-005).
- **Criterio de parada**: cada incremento aprobado con evidencia y dictamen;
  no se arrastra alcance no aprobado.
- **Commit/push**: por incremento, en su rama.

### O3 — Calificación AC1 sobre candidato congelado

- **Precondiciones**: O2 cerrado en lo que afecte a AC1; versión/lock
  aplicados si el alcance es la salida incremental; operador/tabla de
  aceptación resuelto; candidato congelado (hashes de fuentes/tests/
  configuración/runtime, `git status --porcelain` limpio) en checkout
  aislado.
- **Orden obligatorio** (PROC-004 + `CALIFICACION-AC1.md` §4):
  `Q-ACCMUT` → `Q-COVCRAP` → `Q-DRY` → `Q-FULL`. `Q-RANDOM` y `Q-PRE-EQ`
  corren junto a la cadena sin compartir árbol mutable.
- **Puerta de verifier**: al terminar la cadena, sobre toda la evidencia.
- **Criterio de parada**: cualquier superviviente, timeout, `not_run`, fallo
  instrumental o puerta roja detiene la calificación: se registra y **no se
  declara PASS**; presupuesto agotado = parar y reautorizar.
- **Commit/push**: acta de calificación con evidencia referenciada.

### O4 — Revisión protegida, bless, CI y merge

- **Precondiciones**: O3 verde sobre el **SHA final** (código + docs + bump si
  corresponde; `git status --porcelain` limpio); `REL-VERSION` ya aplicada si
  el alcance es la salida incremental; diff protegido congelado. El SHA
  calificado en O3 es el final: no se califica un SHA y se bendice o etiqueta
  otro.
- **Tareas**: `INT-DIFF` (lista itemizada de las 23 rutas y revisión humana
  del diff completo), `INT-BLESS` (humano; los agentes están bloqueados),
  `INT-CI` (pasos que hoy no corren), `INT-REVIEW` (salida de borrador y
  merge solo con autorización explícita).
- **Dependiente**: CI después del bless; merge después de CI verde.
- **Puerta de verifier**: revisión independiente del diff protegido antes del
  bless.
- **Criterio de parada**: CI roja o revisión no conforme → no hay merge.
- **Commit/push**: el merge preserva el SHA calificado; no se rebasa sin CI
  verde.

### O5 — Post-merge y publicación

- **Precondiciones**: merge en `main`; `REL-CUSTODY` decidida y ejecutada.
- **Tareas**: verificación post-merge del SHA real que se etiquetaría;
  `REL-PUB`: SBOM, full hardening, smoke pre/post-tag, tag inmutable,
  prerelease y verificación remota (`isPrerelease`, `isDraft`, tag→SHA,
  assets, sin promoción a Latest); decisión D3 explícita.
- **Criterio de parada (NO-GO)**: cualquier bloqueo post-merge —quality,
  integridad, full, smoke, SBOM, custodia, versión, asset o metadata remota—
  detiene la publicación; no se etiqueta, no se publica y la reparación vuelve
  a un incremento revisable.
- **Commit/push**: tag solo tras autorización; la verificación remota se
  conserva como evidencia.

**Orden relativo y una dependencia circular evitada**: la custodia
(`REL-CUSTODY`) no necesita la release para existir: se decide destino/owner y
se prueba la recuperación en host limpio **antes** de D3; un asset de
prerelease no satisface la custodia. La versión (`REL-VERSION`) precede al
congelamiento final; el bless se aplica sobre el diff protegido final; la CI
corre después del bless; el merge después de la CI; la verificación
post-merge no repara bloqueos ni cambia el candidato. Este orden sigue
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1…` §2 y `BETA3/PLAN.md` §5.

## 5. Presupuestos de ejecuciones pesadas y agotamiento

| Ejecución | Tope/estimación | Fuente | Si se agota |
|---|---:|---|---|
| `Q-ACCMUT` | ≤900 s (est.) | estimación sobre el contrato; recalibrar | Parar, registrar consumo y resultado parcial; no declarar PASS |
| `Q-COVCRAP` | ≤600 s (est.) | estimación | Parar y reautorizar |
| `Q-DRY` | ≤600 s (est.) | estimación | Parar y reautorizar |
| `Q-FULL` | 1800 s (vigente) | `thresholds.yaml` / `docs/gates.md` | Parar; no hay PASS parcial |
| `Q-RANDOM` | ≤600 s (est.) | estimación | Parar y registrar |
| `Q-PRE-EQ` | ≤120 s (est.) | estimación | Si falla o no puede correrse, la ratificación no se traslada |
| `PX-928` opción B | 4.000–5.000 s (orden de magnitud, est.) | 108 IDs/479 s de GS-3 extrapolado | Recalibrar en preflight; no lanzar sin autorización |
| `REL-CUSTODY` prueba | ≤600 s (est.) | estimación | Sin recuperación verificada no hay D3 |

Ninguna de estas ejecuciones está autorizada por este plan; cada una requiere
su encargo.

## 6. Decisiones humanas agrupadas (una sola sesión, cuando se quiera)

1. `R3-DA-10` + `R3-CAST`: ratificar/rechazar las 10 con transferencia
   registrada tras el descomillado.
2. `R3-DA-4`: decisión con IDs corregidos; pedir o no revisión acotada.
3. `R3-DB`, `R3-DC`, `R3-DD`: contrato vs presentación; límites; hooks.
4. `PX-928`: opción A, opción B o diferir (con la regla citada).
5. `PX-T007`: partición fachada o excepción acotada explícita (o mantener la
   obligación abierta); ninguna se concede aquí.
6. `Q-DESIGN-ACC`: aprobar el contrato del operador/tabla y el incremento.
7. `E4-PASS`: PASS del lote GS-2 o mantener NO PASS.
8. `REL-SCOPE` y `REL-VERSION`: alcance declarado y convención de versión.
9. `REL-CUSTODY`: destino/owner durable y prueba de recuperación.
10. `INT-DIFF`/`INT-BLESS`: revisión y bless (acción humana), tras lo
    técnico.
11. D3 y publicación: solo al final, después de la custodia.

## 7. Próxima oleada recomendada y prompt autosuficiente

**Recomendada: O1** — dossier de decisiones agrupadas, solo documentación y
lectura. No hay trabajo técnico que hacer antes de las decisiones, y forzarlo
reabriría alcance no autorizado. El prompt siguiente es autosuficiente y **no
se ejecuta en este encargo**:

```text
ENCARGO — Oleada 1: dossier de decisiones agrupadas AC1 (solo documentación)

Repositorio: /home/jandradeu/Documents/well_code_template
Worktree de partida: /home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration
Rama base: codex/beta3-ac1-r2-integration (PR #53, borrador)
Runtime: /home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8/.venv

OBJETIVO
Preparar, sin ejecutar campañas ni cambiar producto, los expedientes de decisión
para que un humano resuelva en una sola sesión: R3-DA-10, R3-DA-4, R3-CAST,
R3-DB, R3-DC, R3-DD, PX-928, PX-T007, Q-DESIGN-ACC, E4-PASS, REL-SCOPE,
REL-VERSION y REL-CUSTODY, según PLAN-EJECUTABLE-CIERRE-AC1-BETA3-2026-09-15.md.

REGLAS
- Solo lectura de fuentes; se permite crear un worktree de documentación nuevo
  desde el SHA publicado de la rama (por ejemplo codex/beta3-decisiones-ac1-r3),
  o trabajar en un directorio bajo build/tmp sin tocar la rama.
- Prohibido: campañas de mutación, sondas de mutantes, cambios de producto,
  tests, features, gobernanza, dependencias o umbrales; bless, merge, bump,
  tag o release; crear issues externos.
- Los documentos locales ajenos se leen pero no se copian ni se stagean.
- Usa build/tmp/ para temporales (PROC-007).

ENTREGABLE
Un acta de decisiones (docs/evolution/plans/BETA3/EXECUTION/ADENDA-DECISIONES-AC1-2026-09-XX.md)
con, por cada pendiente: evidencia citada, alcance exacto de la decisión,
opciones con consecuencias, campos de decisión vacíos y presupuesto del
incremento derivado si se aprueba. Los IDs de equivalencias citan el diff
autoritativo del lote r3 (correcciones de _14/_17 incluidas) y el hash vigente
de process.py tras el descomillado de casts.

VERIFICACIÓN
Verifier independiente de solo lectura: fidelidad de citas, ausencia de cierres
implícitos y de autorizaciones inventadas. Commit documental conventional con
byline si se publica; la PR #53 permanece en borrador.
```

## 8. Qué impediría todavía bless, merge y publicación

- **Bless**: pendientes técnicos sin decidir (`R3-*`, `PX-*`), diff protegido
  sin revisión itemizada y G-META-1 sin revisión humana (23 rutas). El bless
  no puede sustituir una calificación.
- **Merge**: CI detenida en integridad; tras el bless deben correr los pasos
  no ejecutados y quedar verdes. E11 exige revisión integral y autorización
  explícita; la PR sigue en borrador.
- **Publicación**: versión sin convención aprobada, custodia `local-only` sin
  recuperación probada, SBOM/smokes/tag/prerelease no ejecutados y D3 no
  tomada. Cualquier bloqueo post-merge es NO-GO.
- **AC1**: sin la cadena E8 resuelta y el diseño de aceptación aprobado no hay
  acreditación. El cierre acotado de GS-3 y el merge de PR #53 **no** la
  otorgan.
- **beta.3 completa**: requiere `BETA3/PLAN.md` §1/§5 completos y la decisión
  sobre G1b si se exige ese claim; el alcance de esta rama es una parte.
