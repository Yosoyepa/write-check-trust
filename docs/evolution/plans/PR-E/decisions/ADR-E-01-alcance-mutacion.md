# ADR-E-01 — Alcance de la mutación: corridas reales sobre fixtures; wholesale rechazado con números

Estado: aceptado (arquitecto con delegación vigente, 2026-09-05).
Contexto: [ANALYSIS.md](../ANALYSIS.md) §1.

## Decisión

La redención de F2-a/F2-b/F5-b exige corridas REALES de mutación, y esa
realidad se entrega donde es barata y verificable: fixtures diminutos con
su propio `[tool.mutmut]` donde `mutmut run` mide sobrevivientes de
verdad a través de la función de gate productiva. El alcance del repo
(`src/example`) NO cambia en esta PR; G-MUT se cablea al tier full
(ADR-E-02).

## Alternativas consideradas

- **(a) Extender `source_paths` a `tools/wct` (el wholesale)**: rechazada
  CON NÚMEROS — 4.235 sitios / 57 archivos / 16 sobre el presupuesto de
  G-MUT-SITES / ≈21 horas por corrida a ~18s de suite. El costo no compra
  señal hasta que exista mutación diferencial por función cambiada.
- **(b) Staged: un módulo del harness primero**: rechazada — la
  configuración de mutmut es global (una lista de paths + una selección
  de tests); un módulo del harness ya arrastra la suite completa (~18s
  por mutante ≈ 15 min para introvert/) y ningún tier lo soporta. Misma
  espera que (a) con menos valor.
- **(c) Redimir con imitaciones mejoradas**: rechazada de raíz — es lo
  que PR-C desterró; el punto de la redención es que la corrida exista.

## Consecuencias

- El red team queda con UN solo residuo declarado (F4-b, diff-cover con
  fixture git) — 29/30 casos productivos.
- La deuda "el harness se muta a sí mismo" queda reformulada con
  honestidad: existe (fixtures reales, tier full), y su extensión al
  código del harness tiene precio medido y condiciones explícitas
  (mutación diferencial, suite más rápida, o partición masiva previa).
- `wct mutate` sobre el repo no cambia: manifiesto, scope y selección
  intactos.
