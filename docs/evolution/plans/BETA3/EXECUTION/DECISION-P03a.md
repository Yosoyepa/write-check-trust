# Decisión arquitectónica — P03a puro

Estado: **contrato aprobado por el arquitecto bajo D1**. No es aprobación de
producto, bless, release ni del plugin/supervisor posteriores.

## Bytes y frontera aprobados

- PROPUESTA-P03.md:
  `47429b8896a38bcd0ec2c835d17a385dd68a4585e5b4207ab86127486ae9f251`.
- SONDA-P03.md:
  `cb1bc987fd41cf74d85ef723c3abf19a3e146a019fea5f60b095abe15d2e01dd`.
- Golden wire1938 bytes:
  `52eed49e69f6d98da227347396eaa42a57d0c854e93cd662c75d9e76173a6730`.

Se aprueban las dos APIs puras, modelos congelados, codec compacto, FSM,
inventarios, Gherkin de doce familias y mapa completo con las addendas de
offsets/instancias, únicamente dentro de las diez rutas de §10.
El coder incorporará el golden literal en tests; no dependerá de build/tmp.
La dependencia productiva es P01 integrado, no una implementación P02 pendiente.

## Motivos y revisión

El formato verbose se retiró antes de implementar: no cabía razonablemente
en el presupuesto conjunto de metadata de WCT con el crecimiento observado.
El compacto declara referencias una vez y conserva identidad, orden, fases,
metadatos de excepción y ambos reports. La medición de355192 bytes para644
tests normales es simulación, no un journal ejecutado ni acreditación de coste.

El arquitecto leyó el contrato y la sonda completos, luego el diff correctivo.
El verifier documental independiente rechazó dos defectos y revisó su cierre:
offsets de bytes antes no conservados en el modelo y unicidad por nodeid que
impedía preservar dos instancias terminales repetidas. La revisión corregida
dio conformidad documental y fast7/7. No ejecutó la FSM futura.

Decisiones explícitas:

1. Offset/end_offset son observaciones lógicas, no campos elegidos por el
   emisor en el wire. start_seq diferencia instancias sin deduplicar nodeids.
2. El límite efectivo max_bytes es obligatorio y declarado por caller; no
   acredita el ledger global. P03c/P06 deben restar metadata real y reservar
   cierre dentro de los2MiB conjuntos. No imponer nuevos topes fijos a P02.
3. Claims de plugins/runtime no se convierten en verificación por llegar en
   un JSON válido. Provenance permanece caller-supplied-unverified.
4. P03b/P03c, recetas de coverage y acreditación P05/P06 siguen fuera. No se
   crean stubs ni se altera el runner/CLI para aparentar la cadena completa.
5. Se aplica ADENDA-MOLDE-ORACULOS.md; tampoco este contrato autoriza excluir
   mutantes. La propuesta de adjudicación permanece en su puerta humana.

## Preparación de ejecución

Antes de iniciar coder: registrar base exacta que contiene esta decisión,
allowlist de §10, hash contractual y recibo de entendimiento. El expediente
de entrega será `SELF-HOSTING/runs/HANDOFF-B3-MA-P03A-R0.md`; artefactos en
un directorio nuevo exclusivo bajo build/tmp/b3-ma-p03a-r0. No sobrescribir
un intento previo si existe. Tests previos, colección real, controles válidos,
sensibilidad y revisión independiente del digest final son obligatorios.

No hay coder P03a lanzado ni implementación acreditada al emitir esta decisión.
La preparación no da por completada beta.3 ni modifica las puertas humanas.
