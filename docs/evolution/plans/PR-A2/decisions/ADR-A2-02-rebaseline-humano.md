# ADR-A2-02 — Re-baseline humano de coverage-total: 100 → 73

Estado: propuesto — **esta es la decisión de governance que solo el humano
puede tomar** (SEC-005/PROC-008).

## Contexto

El baseline semilla dice 100.0 con nota "cobertura de rama del repo completo"
— pero midió 61 statements de `src/example`. El scope de A2 hace real esa
promesa (2 509 statements) y el total real es **73 %** (medido dos veces bajo
la semántica final de A1, con y sin property: idéntico).

## Decisión

Secuencia humana sobre la rama del PR, antes del merge:

1. Verificación del coder + revisión de arquitecto (todo verde salvo
   G-META-1 por diseño).
2. El humano corre `uv run wct ratchet record --metric coverage-total
   --approved-by "yosoyepa" --reason "re-baseline por cambio de scope en PR
   #N: 100 era src/example (61 stmts, seed); real con src+tools/wct = 73 %"`
   → escribe el baseline con commit real, owner y fecha.
3. El humano corre el bless del PR (`mutate update-manifest --approved-by`,
   razón citando el PR) → cierra G-META-1.
4. CI → squash merge. Desde ese momento, 73 % es el piso y el ratchet solo
   admite subidas (`ratchet record` futuro con valor mayor).

## Por qué esto no es "bajar el umbral para pasar"

PROC-008 prohíbe subir umbral para pintar verde. Aquí el movimiento es
distinto y legítimo:

- El 100 nunca fue una medición: es semilla (`recorded_by: "seed"`) sobre un
  scope que excluía al medidor mismo. No existe serie histórica que se rompa.
- La nota del propio baseline declara la intención ("repo completo") que el
  scope viejo incumplía. A2 corrige el instrumento, no el número.
- El nuevo 73 es la primera medición real, con commit, owner y razón — el
  punto de partida verificable de una serie que solo puede mejorar. Un 100
  aplicado hoy produciría un árbol permanentemente rojo o, peor, presión para
  excluir código del scope de nuevo: sobreafirmar es el defecto que PR-A1
  vino a matar.

## Alternativas consideradas

- **(a) Mantener 100 y excluir del scope lo no cubierto** (poda agresiva de
  `omit`): rechazada — es fabricar la cifra, el anti-patrón central del
  dossier.
- **(b) No aplicar el baseline todavía (solo scope), dejar 73 sin piso un PR
  más**: rechazada — separar scope de aplicación deja una ventana donde el
  árbol mide 73 y nada defiende ese piso; el PR que "aplique después" llegaza
  indefinidamente (el 100 decorativo lleva vigente desde la semilla).
- **(c) Baseline 73 redondeado a la baja (70) para dar holgura**: rechazada —
  registrar menos de lo medido es regalar terreno gratis; el ratchet admite
  subidas incrementales con cada PR que mejore cobertura.

## Consecuencias

- `ratchet check` reporta `coverage-total: actual=73, baseline=73` PASS desde
  el día uno; el primer PR que baje la cobertura sin compensar rompe el gate.
- La decisión queda auditada: baseline con commit del PR, owner, razón y este
  ADR referenciado desde el plan.
- Los adoptantes heredan el mecanismo, no el número: cada repo registra su
  propio punto de partida (documentado en SPEC §docs).
