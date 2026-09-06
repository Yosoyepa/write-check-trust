# G3a — DoD por unidad (G3a-1 VERIFICADA en árbol, SIN commit; listo para bless)

## Corrección residual pre-bless (3º hallazgo humano) — EJECUTADA y verificada

- [x] KeyError cerrado: `_record_defect` detecta cubiertas-sin-total y
      nombra `LH 1 sin LF en <SF>` / `BRH 1 sin BRF en <SF>` (spot-check
      del arquitecto); con total presente el mensaje es byte-idéntico al
      histórico. Test 0g nació en rojo (traceback KeyError documentado).
- [x] Completitud NO ampliada (LF-sin-LH sigue válido y medido; anclado en
      test). Tolerante intacto (mide, no valida, no lanza).
- [x] Verificador independiente: APROBADO CON HALLAZGOS — H-1 LOW no
      bloqueante: artefacto SOLO-LH-sin-LF (sin diluyente) bloquea con
      causa `LF+BRF == 0` en vez de `sin LF` (el chequeo de totales
      precede al por-registro); conforme al SPEC (0g define el escenario
      con diluyente). Registrado como borde, sin acción.
- [x] Batería: 334 passed · redteam 30/30 sin cambios · fast 7/7 · commit
      21 gates SOLO G-META-1 pre-bless · tolerante idéntico · require-all
      10/10 · ruff limpio. (Proceso honesto del coder: primer fix rompió
      G-LINT PLR0911 — reportado y rehecho como bucle de pares.)
- [x] DoD reconciliado preservando la evidencia histórica: los seguimientos
      LOW del primer verifier quedaron resueltos por 0d (verde N-de-N),
      0b/0e (ramas de causa) y la corrección documental del ADR-G1-01;
      el título ya no dice "pendiente de verifier".

## Corrección FINAL pre-bless (2º hallazgo humano) — EJECUTADA y verificada

- [x] Contadores LCOV negativos/malformados (`LF:-1`, `LF:1.5`, `LF:`
      vacío) RECHAZADOS por la vía exigible: `medición inválida (contador
      LF:-1 en bad.py)` — verificado por el verifier con código productivo
      (y leading zeros `LH:007` aceptados, sin rechazo espurio). Tolerante
      intacto (regex y parsers históricos sin diff).
- [x] Comando productor shell-correcto (`-m "not property"`); test con
      `shlex.split` comparando la LISTA del builder sin aplanar —
      sensibilidad probada por el verifier en ambos ejes (sin comillas →
      falla; builder reordenado → falla).
- [x] Verificación independiente repetida sobre el diff final: APROBADO CON
      HALLAZGOS (todos INFO: leading-zeros sin test ancla; espacios/`+5`
      también tratados como malformados — consistente con el ADR).
      Batería: 333 passed · redteam 30/30 sin cambios · fast 7/7 · commit
      21 gates SOLO G-META-1 pre-bless · tolerante idéntico · require-all
      10/10.
- [x] Caso C: SIN cambio (decisión humana 2026-09-05 — validez obligatoria
      para exigidas, comparaciones históricas para las demás; G3a-2 exigirá
      coverage explícitamente).

- [x] **Hallazgo 1 (bloqueante) corregido**: LCOV imposible (LH>LF, BRH>BRF,
      totales 0, rango) bloquea el modo exigible con "medición inválida" +
      defecto nombrado; bordes 100% verde / 0% rojo-por-umbral. Tolerante
      byte-compat verificado 9/9 artefactos contra HEAD (verifier).
- [x] **Hallazgo 2 corregido**: `--require` es ADITIVO — conserva TODAS las
      comparaciones tolerantes; sin líneas duplicadas; combinaciones
      (rojo + inválida + ambas exigidas) verificadas por el verifier.
- [x] Comando productor alineado (`-q -m not property`), anclado por test
      contra el builder productivo.
- [x] Tests CLI consolidados (aserciones ambas clases en el original; el
      duplicado eliminado; verifier: ninguna aserción huérfana).
- [x] Verde exigible N-de-N probado (0d; ya verde pre-corrección, declarado
      regresión por el coder).
- [x] Rojos de 0a/0b validados INDEPENDIENTEMENTE por el verifier
      (reconstruyó la semántica pre-corrección y los hizo fallar — TEST-001).
- [x] Batería re-verificada: 332 passed (97.86s arquitecto / 85.76s
      verifier / 82-88s coder — **estimación** vs histórico ~81s, no
      presupuesto emparejado); redteam 30/30 sin cambios; fast 7/7; commit
      21 gates con SOLO G-META-1 rojo (pre-bless); ratchet tolerante
      idéntico; `--require all` 10/10 con denominador.

**Veredicto del verifier sobre el diff corregido: APROBADO CON HALLAZGOS
(ninguno bloqueante).** Abiertos para decisión humana (no defectos):
(1) política del caso C — artefacto inválido con coverage-total NO exigida
pasa verde en modo exigible (conforme a la letra del ADR; G3a-2 lo cierra
exigiéndola en CI); (2) presentación: LF+BRF=0 cuenta como "0 de 1 medidas"
aunque el bloqueo diga "medición inválida"; (3) el defecto nombrado puede
ser el de rango y no el del registro (ambos verdaderos).

## G3a-1 — Regresión + promoción + --require + doble clase (SPEC-G3a-1)

- [x] G-INTROVERT en `_COMMIT_GATES` con su entrada literal de full
      RETIRADA (sin duplicación); membresía commit/pr/full probada.
      Verifier: 21 gates en commit, herencia sin duplicar.
- [x] Regresión del escape con medición y baseline PRODUCTIVOS y el
      baseline VIGENTE (sin segundo umbral 0) + control defectuoso
      emparejado (verificado por el verifier independiente).
- [x] `--require` según ADR-G3a-02: entrada validada (vacío/desconocido/
      duplicado/all-solo → exit 2), `all` = inventario explícito, bloqueo
      por ausencia con causa y comando, presencia≠umbral con fronteras,
      denominador y nombres, cero claims de frescura (ayuda explícita).
      Byte-compatibilidad del modo tolerante verificada TRES vías por el
      verifier (diff estático, test de stdout, corrida en vivo contra HEAD).
- [x] Test del CLI con AMBAS clases (exit 1 literal + fase/conteos +
      cotejo con el adaptador).
- [x] Analyzer: solo docstring (verifier: cero lógica).
- [x] Feature verbatim (comparación mecánica del verifier: verbatim True);
      escenarios enlazados a tests existentes (mapa en el veredicto).
- [x] Redteam 30/30 · 13 · 13 · 4 · 0 · 0 sin cambios; fast 7/7; commit
      21 gates con SOLO G-META-1 rojo (pre-bless por encargo — PENDIENTE
      de decisión humana); ratchet tolerante idéntico.
- [x] Costo añadido medido: G-INTROVERT en commit 159/114/164 ms (3 reps,
      verifier); suite completa 86.26/86.85 s limpias (antes histórico
      81.09/80.41/83.76 s — misma máquina; +≈5-6 s por los tests nuevos,
      no por el gate).

**Veredicto del verifier independiente (PROC-005): APROBADO CON
HALLAZGOS** — ninguno bloqueante. Seguimientos registrados (LOW):
(a) instanciar un verde exigible N-de-N con N≥2 en test;
(b) ramas de causa de `_absent_failure` sin test directo (fila
"análisis no disponible", "LCOV sin líneas medibles", "interrogate sin
N%"). No verificado por diseño del encargo (declarado): gates de tier
full/pr (G-MUT, G-COV-DIFF, G-CRAP, G-DRY, G-ACCEPT-MUT) y orden
aleatorio de tests.

## G3a-2 — Paso de CI con ratchet exigible (AUTORIZACIÓN APARTE)

- [ ] Diff exacto del workflow aprobado por el humano ANTES de escribirse.
- [ ] El orden de pasos garantiza la procedencia del LCOV; costo medido.

## Unidad de revisión

- [ ] Verifier independiente reproduce: control negativo, exigible fallando
      sin LCOV, promoción del tier, doble clase del test del CLI.
- [ ] Sin `governance/**`, sin workflows en G3a-1, sin baselines tocados.
- [ ] El reclamo del cierre dice "las comprobaciones enumeradas", nunca
      "main verde completo" (lección de este dossier).

## G3a-2 (Puerta 1 autorizada 2026-09-05) — EJECUTADA en working tree, SIN commit

- [x] Diff del workflow aplicado BYTE A BYTE al aprobado (productor con
      `-m "not property"`, paso exigible posterior, property separado).
- [x] Feature creada verbatim con comentarios:
      `features/wct-ci-ratchet-exigible-001.feature` — parse exit 0,
      ir-dry count 0 en ruta real (G-ACCEPT verde vía commit tier).
- [x] Tests T1–T5 (`tests/unit/test_workflow_contract.py`, 9 tests) con
      rojo honesto: pre-diff 4 FAILED (T1 por tokens `-m`/`not property`;
      T2/T3/T4 por pasos ausentes) · 5 PASSED con controles defectuosos
      emparejados (perdones mutados detectados; ruta de artefacto mutada
      detectada; bajo-baseline bloquea 50<74.5). Defecto propio del
      helper `_positions` (pasos sin `name`) encontrado y corregido ANTES
      del diff para que el rojo quedara atribuido al contrato.
- [x] Post-diff: 9/9 verde. Sin cambios en `tools/wct/**`, baselines,
      dependencias ni manifiestos.
- [x] Incidente honesto: la regresión G3a-1 cazó 4 tests propios
      INTROVERTED (métrica repo 4.0; `test_repo_introverted_ratchet_
      holds_baseline` en rojo). Corregidos con trazado productivo real —
      T2 valida la lista exigida contra REQUIRED_INVENTORY, T3 deriva la
      marca de exclusión de la receta productiva, T4/control anclan la
      identidad del productor a LCOV_ARTIFACT y mutan el paso REAL.
      Resultado: 9/9 extroverted, métrica repo 0.0, analizador intacto.
- [x] Documentación actualizada: README/SPEC/GHERKIN/ADR-G3a-03 con
      estado Puerta 1; PLAN beta.2 fase 0 marcada aprobada.
- [x] Verifier independiente sobre el diff final (PROC-005): veredicto
      abajo.
- [x] Gates de cierre: fast 7/7 · commit 20/21 con SOLO G-META-1 rojo por
      diseño (`modificado: .github/workflows/quality.yml`) · G-ACCEPT y
      G-INTROVERT PASS · collect 343 · battery 341+1 passed ·
      `wct mutate run` exit 0 "sin trabajo diferencial" (delta cero: el
      incremento no toca src).

**Veredicto del verifier independiente (PROC-005): APROBADO CON
HALLAZGOS** — MAYOR-1: T2 solo verificaba subconjunto del inventario
(una debilitación del `--require` a una sola métrica pasaba) · MINOR-2:
checkbox de veredicto prematuro · MINOR-3: control de ruta sintético en
vez de derivado del paso real. El verifier verificó en primera persona:
diff byte a byte el aprobado, feature verbatim (diff mecánico contra
GHERKIN-G3a-2.md), parse exit 0 / ir-dry 0, 9 passed, TEST-003 sin
aserciones mock-only, fuera de alcance limpio (tools/baselines/lock/
pyproject/workflows otros intactos; trabajo ajeno presente e intacto),
integrity falla nombrando SOLO el workflow, claims documentales fieles.
Los TRES hallazgos corregidos en el turno: T2 pina la lista exacta
`["coverage-total", "docstring-coverage"]` ADEMÁS de la validación de
inventario; el control de ruta muta el `run` REAL (solo destino lcov);
este veredicto registrado. Post-fixes: 9/9 passed · 9/9 extroverted ·
repo 0.0 · fast 7/7.
- [ ] Bless humano (fuera de este encargo): `update-manifest` regenera
      lock; luego PR → CI → merge.

## G3a-2 — Ronda de corrección pre-bless (hallazgos humanos 1-2 + verifier ronda 2)

- [x] Hallazgo humano 1 (eco sustituye al consumidor; sondas EN MEMORIA,
      YAML intacto): T2 pina el comando COMPLETO por igualdad shlex.
- [x] Hallazgo humano 2 (`if: false`/`failure()` pasaban): T4
      `test_contracted_steps_execute_normally` — `_executes_normally`
      rechaza CUALQUIER `if` y `continue-on-error` en productor,
      consumidor y property. Sin intérprete de expresiones de Actions.
- [x] MAYOR-1 del verifier ronda 2 (nivel job: `if: false`,
      `continue-on-error`, `defaults.run.shell` neutralizador, `on:`
      reducido — pasaban TODO): T6 `test_commit_gates_job_executes_
      normally` (predicado de job + triggers pull_request/push).
- [x] Controles defectuosos de paso y job derivados del workflow REAL
      (eco/if-false/failure()/perdón/productor + job desactivado/
      perdonado/shell neutralizado): `test_defective_step_mutations_
      are_detected` · `test_defective_job_mutations_are_detected`.
- [x] MINOR-2 del verifier: SPEC T2/T4/T6 re-sincronizados con los
      tests reales; esta ronda documentada en SPEC (sección "Ronda de
      corrección pre-bless").
- [x] MINOR-3 del verifier (working-directory/env a nivel paso):
      residual documentado — el verifier verificó que `ratchet check`
      no lee env y que working-directory falla ruidosamente; no se
      amplía el contrato en esta ronda.
- [x] Incidente honesto de la ronda: el test de job defectuoso nació
      introverted (la red G3a-1, 1.0) — ancla de identidad añadida
      (nombres del consumidor real ⊆ REQUIRED_INVENTORY) → 11/11
      extroverted, repo 0.0.
- [x] Post-fixes: 11/11 passed · 11/11 extroverted · repo 0.0 ·
      fast 7/7 · suite completa y commit re-verificados (abajo).
- [x] Verifier ronda 3 (delta): **APROBADO CON HALLAZGOS** — su MAYOR-1
      de job CERRADO (las 4 sondas de nivel job rechazadas en memoria
      contra las 11 aserciones), MINOR-2 docs CERRADO. Hallazgos nuevos:
      MAYOR (`shell: "/bin/true {0}"` a nivel PASO del consumidor pasaba
      la suite — neutralización selectiva y silenciosa) + MINOR
      (checkbox de este veredicto prematuro — cerrado al registrarlo
      aquí) + 3 residuales de nivel workflow/documento.

## G3a-2 — Corrección terminal post-ronda 3 (allowlist de claves)

- [x] MAYOR ronda 3 cerrado con allowlist terminal: `_is_bare_run_step`
      — los tres pasos contratados son exactamente `{name, run}`
      (`set(step) == {"name", "run"}`): cierra shell/env/working-
      directory/timeout-minutes y todo neutralizador futuro, sin
      enumerar listas negras. Control defectuoso extendido con la sonda
      shell sobre el paso REAL.
- [x] Extendido al perímetro que el verifier probó: `defaults`
      prohibido a nivel DOCUMENTO (T6) y `strategy` prohibido en el job
      (un matrix vacío salta el job — control defectuoso extendido).
- [x] Residual registrado (SPEC §Ronda de corrección, ítem 6): filtros
      de triggers no pineados (presencia sí, semántica no) —
      compensación: ruta protegida + integrity lock.
- [x] Post-fix: 11/11 passed · 11/11 extroverted · repo 0.0 · fast 7/7
      · suite completa 345 passed (107 s) · commit 20/21 SOLO G-META-1
      por diseño · G-ACCEPT/G-INTROVERT PASS.
- [x] Verifier ronda 4 (delta final sobre el allowlist): **APROBADO CON
      HALLAZGOS — recomendación explícita: aprobar para bless**. Su sonda
      shell-a-nivel-paso RECHAZADA; defaults-raíz y strategy.matrix
      RECHAZADOS; filtros de triggers aceptados como residual
      compensado. Dos MINOR nuevos fuera del perímetro contratado:
      MINOR-A (paso forjador insertado entre productor y consumidor
      pasaba — y el docstring de T2 afirmaba «sin restauración
      intermedia» con una aserción de solo-orden: el código era más
      débil que su claim) y MINOR-B (`needs` en cascada). NIT: referencia
      SPEC a `_executes_normally` (subsumida por la allowlist).

## G3a-2 — Cierre post-ronda 4 (adyacencia + needs)

- [x] MINOR-A cerrado por honestidad: la aserción de T2 es ahora de
      ADYACENCIA (`positions[CONSUMER] == positions[PRODUCER] + 1`) —
      el código cumple el claim que su docstring ya hacía. Control
      defectuoso: paso forjador insertado sobre los pasos REALES → la
      adyacencia lo delata.
- [x] MINOR-B cerrado: `_job_executes_normally` prohíbe `needs` (un
      job con needs no corre incondicional); control defectuoso con
      `needs: ["decoy"]` sobre el job REAL.
- [x] NIT cerrado: SPEC T2 re-sincronizado (adyacencia + allowlist, sin
      `_executes_normally`).
- [x] Residual del ítem 6 extendido con `pull_request.types` (misma
      clase que branches-filters, misma compensación).
- [x] Incidente honesto de la ronda: RUF005 en el control forjador
      (concatenación vs unpacking) — G-LINT lo cazó; corregido.
- [x] Post-fix: 11/11 passed · 11/11 extroverted · repo 0.0 · fast 7/7
      · suite completa 345 passed (112 s) · commit 20/21 SOLO G-META-1
      por diseño.
- [x] Verifier ronda 5 (delta de cierre): **APROBADO** — sin
      hallazgos. Barrido de regresión con las doce sondas de las rondas
      2-4: todas rechazadas. Balance del verifier: todo lo que toca
      elementos contratados está sellado (allowlist/adyacencia/predicado
      de job); lo restante es frontera declarada y compensada. De su
      parte, el diff final está aprobado para bless. Opcional registrado
      (no aplicado, no bloqueante): allowlist de claves del job
      (`set(job) == {"runs-on", "steps", "timeout-minutes"}`) cerraría
      la clase de claves no contratadas (p.ej. `env` con PYTEST_ADDOPTS)
      — misma filosofía de `_is_bare_run_step`, decisión del humano en
      el bless o seguimiento posterior.
