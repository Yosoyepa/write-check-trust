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
