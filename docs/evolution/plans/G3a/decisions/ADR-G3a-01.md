# ADR-G3a-01 — La regresión del escape vive en la suite que CI ejecuta

Estado: propuesto (requiere aprobación humana). Trazabilidad: encargo
humano post-#38; ANALYSIS §2.

## Contexto

El escape #37/#38 demostró que un contrato que solo vive en un tier que CI
no corre (`full`) y en un comando que nadie ejecuta obligatoriamente
(`ratchet check`) es invisible para CI. La única capa garantizada es la
suite de tests.

## Decisión (versión aceptada con ajuste obligatorio 4 del humano)

1. **Test repo-pinned** `test_repo_introverted_ratchet_holds_baseline`:
   compara `measurements(REPO)["introverted-tests"]` contra el **baseline
   VIGENTE** (`baseline` + `compare` productivos de `ratchet/measure.py`).
   **Sin un segundo umbral 0 hardcodeado**: si el humano sube el baseline
   con `ratchet record`, este test lo sigue — no invalida decisiones
   futuras. Un introvertido nuevo rompe la suite → CI lo bloquea en el PR,
   sin esperar al post-merge. Es la forma canónica de "convertir el
   incidente en regresión": el invariario queda dentro de la capa que
   siempre corre.
2. **Control defectuoso emparejado** (especificidad, patrón R01): un
   fixture con UN test introvertido y baseline propio 0 → `check()`
   productivo lo reporta. Sin él, un `measurements` roto que siempre
   retornara 0 pasaría la regresión.
3. **Promoción de G-INTROVERT a tier commit** (vive en ADR-G3a-03 §G3a-1):
   además del test pineado, el gate pasa a correr en el tier que CI ya
   ejecuta — doble red, sin tocar el workflow.

## Alternativas rechazadas

- **Runbook/memoria del arquitecto** ("corre ratchet check antes de cada
  PR"): es exactamente lo que falló en #37; los procesos que dependen de
  recordar no son contratos.
- **Solo promover el gate sin el test pineado**: el gate compara contra
  baseline; un raise indebido del baseline (PROC-008 lo prohíbe, pero el
  mecanismo no lo impide físicamente) dejaría el test pineado como única
  alarma — por eso ambos.
- **Meta-test que corre `wct ratchet check` como subprocess en CI**:
  duplica el paso de G3a-2 y mide el comando, no el invariario.

## Consecuencias

- La métrica `introverted-tests` queda vigilada en dos capas (suite y gate
  commit). El resto de métricas estáticas del ratchet NO se pinean una a
  una en G3a-1 (ocho tests repo-pinned sería ruido); su ejecución exigible
  es G3a-2 (ADR-G3a-02).
- El test pineado consume `measurements()` completa (8 métricas estáticas,
  baratas) y asevera SOLO introverted-tests: no convierte el ratchet entero
  en suite (eso exigiría artefactos; ADR-G3a-02 lo trata por vía de CI).
