# ADR-G3a-04 — G-INTROVERT y subprocess: limitación documentada, doble clase de aserciones

Estado: propuesto (requiere aprobación humana). Trazabilidad: hallazgos del
humano sobre #38; ANALYSIS §4; G1/EVIDENCE.md §addenda punto 2.

## Contexto

El detector de introvertidos (`introvert/analyzer.py:71-112`) solo reconoce
como "traza al SUT" los nombres importados in-process (o derivados). Un test
que ejercita el entrypoint por subprocess y asevera sobre su salida —
comportamiento observable legítimo — puede salir "introverted" siendo bueno.
La reparación #38 resolvió el bloqueo del ratchet cotejando contra el
veredicto del SUT in-process, pero con tres costos señalados por el humano:
esperar el exit con `EXIT_CODES` de producción (un cambio incorrecto
compartido pasa inadvertido), la pérdida de las comprobaciones explícitas de
fase/conteos, y la re-ejecución del adaptador sobre el mismo fixture
(compartiendo caché).

## Decisión

1. **Política de doble clase para tests de subprocess del CLI** (aplicable
   al de mutación y a futuros): conservar ASERTOS INDEPENDIENTES del
   contrato observable (exit `1` literal, `estado: FAIL`, `fase: criterio`,
   conteos con `survived=`) **Y** la concordancia con el adaptador
   (veredicto in-process: mismas identidades en la salida). Las dos clases
   fallan por razones distintas: la independiente ancla el contrato público;
   la concordancia detecta divergencia CLI↔adaptador. Ninguna sustituye a
   la otra.
2. **Limitación del detector documentada** en el propio analyzer (docstring
   del módulo): no reconoce subprocess como traza; veredictos
   introverted/cloistered sobre tests de subprocess NO son por sí solos
   señal de test malo — el control de calidad es la doble clase.
3. **No ensanchar el detector en G3a**: enseñarle a reconocer
   salida-de-entrypoint-del-SUT como traza exige medir sensibilidad/falsos
   positivos propios (F11 de POST-PR36: no añadir gates ni reglas sin medir
   su sensibilidad). Queda registrado como candidato futuro con ADR propio.

## Alternativas rechazadas

- **Solo asertos independientes** (estado pre-#38): el analizador no los
  reconoce y el ratchet razonablemente exige traza — reaparece el choque.
- **Solo concordancia con el adaptador** (estado #38): ancla el exit a
  `EXIT_CODES` de producción — drift compartido invisible; y pierde la
  comprobación explícita del contrato impreso.
- **Exención del test en una allowlist del ratchet**: esconde la clase de
  test en lugar de hacerla medible; la doble clase es honesta y más
  fuerte que cualquiera de las dos solas.

## Consecuencias

- El test del CLI vuelve a comprobar fase/conteos explícitos y el exit
  literal 1, además del cotejo con `mutation_verdict` — el costo de
  re-ejecución del adaptador se conserva (comparte caché con el subprocess
  sobre el mismo fixture; determinista en este fixture) y se declara en el
  docstring del test.
- `introverted-tests` sigue en 0 con el test volviendo "extroverted" por
  la vía del cotejo (la clase independiente no traza, la de concordancia
  sí — la regla del analizador queda satisfecha legítimamente).
