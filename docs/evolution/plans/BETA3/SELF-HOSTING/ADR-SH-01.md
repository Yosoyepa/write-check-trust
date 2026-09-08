# ADR-B3-SH-01 — Automejora gobernada y evaluación ciega

Estado: **propuesto para las decisiones técnicas**. La dirección de automejora
y el cegamiento del modelo fueron solicitados por el usuario el 2026-09-07.
Ni Gherkin nuevo ni diff futuro quedan aprobados por este estado.

## Contexto y hallazgos que motivan la decisión

| ID | Evidencia del corte beta.2 | Riesgo para este caso de uso | Consecuencia de diseño |
|---|---|---|---|
| SH-F01 | `policy.yaml: paths.source=[src]`; G-ARCH/ARCHMETRICS apuntan al ejemplo; `mutmut.source_paths=[src/example]` | Llamar «harness endurecido» a un verde que mide otro código | Inventario y matriz de alcance propios para cada pieza de `tools/wct`; no ampliar policy por conveniencia |
| SH-F02 | `tools/wct/**` es código protegido y también contiene integridad, gates y reportes | El candidato puede modificar el juez o su señal | Referencia W0 y revisión fuera de la autoridad del coder; promoción explícita |
| SH-F03 | `accept.generate` crea una función por escenario; `execute_scenario` itera las filas | N de tests no demuestra que todas las filas hayan terminado | Bindings fila→nodeid o terminal por fila verificable, calificados en P03/P06 |
| SH-F04 | `GateResult.command` es string y `_captured` conserva Status, no todo el exit/protocolo | Reconstruir argv/causa/identidad desde un resumen pierde información | Captura directa en el proceso nuevo; mantener intacto el formato histórico |
| SH-F05 | LCOV histórico bajo `build/coverage/lcov.info`; G1b sigue limitado | Presencia o hash de un archivo no demuestra procedencia ni frescura | Cadena P1 privada, expected separado y claims acotados |
| SH-F06 | Primera selección del piloto era personalAssistant; ahora se pide WCT sobre WCT | Mezclar trayectoria de desarrollo con experimento o inferir generalización | Dos carriles y dos corpus; WCT primero, validación externa después |
| SH-F07 | Usuario mantiene secreto modelo y aplaza datos OpenRouter | Pedir marca/precio antes de puntuar introduce sesgo; no guardar usage impide coste posterior | Custodia privada, IDs ciegos, dictamen de calidad fijado antes del descegamiento |
| SH-F08 | `classify_inventory` valida reporte de mutmut, pero no compara tres inventarios independientes | Reusar ese PASS para P1 importaría sus límites y semántica equivocada | Nueva función pequeña de reconciliación; no otro motor de mutación |

Evidencia local verificable en [EVIDENCE](EVIDENCE.md). SH-F02 es un riesgo de
diseño, no una acusación de que un coder haya manipulado el repositorio.

## Decisión

### 1. WCT será el primer codebase, no su propio árbitro exclusivo

- **W0:** referencia publicada, commit beta.2 `8de9107…`, config/locks/tools
  fijados. Sus controles tienen límites y no son un oráculo de verdad universal.
- **Wn:** versión promovida tras revisión de las piezas anteriores.
- **Candidato:** patch que se evalúa. Los informes que él produce son entradas
  no confiables; no son la autoridad que lo acepta.
- **Qn:** calificador del lote: contratos aprobados, fixtures/oráculo,
  control de alcance y revisión del arquitecto/verifier. Su identidad queda
  fuera del permiso de escritura del coder.

Para evaluar una nueva pieza se fijan Wn y Qn **antes** de comenzar. El patch
puede mejorar Wn, pero no cambia retroactivamente Qn. Tras el cierre se decide
si se promueve como Wn+1. Si se corrige Qn por defecto, conservar el resultado
anterior, versionar el instrumento y reexaminar todos los afectados, no solo
el candidato que convenga.

No implementar en P01 una plataforma de agentes, firma digital o sandbox.
La primera separación puede ser operativa, con copias y revisión humana,
declarando sus límites. Un directorio privado o un worktree **no es** una
frontera de seguridad contra procesos con el mismo usuario del sistema.

### 2. Dos tipos de molde, sin vender dos arquitecturas soportadas

`wct-harness-local/1` es el **contrato de desarrollo de las piezas nuevas**:
núcleo puro, adaptadores de IO y ensamblaje explícito. No transforma todo el
legacy en seis carpetas ni concede excepciones globales a `tools/wct`.

`hexagonal-python/1` sigue siendo el único **pack de producto propuesto** para
adoptadores en beta.3. Cuando exista su compilador, el molde local podrá ser
una instancia/perfil calificado. Hoy es un contrato revisable, no un pack
ejecutable ya instalado. [MOLDE-WCT](MOLDE-WCT.md) fija aristas y consumidores.

### 3. Una pieza pequeña antes de toda la cadena

Descomponer P1a/b/c sin cambiar sus objetivos. P01 realiza la igualdad exacta y
no vacua de identidades; P02–P06 aportan snapshot, ejecución, artefactos,
cierre e integración. P01 no expone un comando que diga acreditar tests.
Se evita tanto esperar a terminar beta.3 para medir como aprobar con un kernel
que todavía no está conectado a procesos reales.

### 4. Cegamiento sin perder auditabilidad

El usuario custodia modelo, proveedor, routing y recibos. El arquitecto no
busca esa identidad ni infiere preferencias por estilo del código. Revisa
entregas como `CODER-CIEGO-01`. Después del dictamen congelado se calcula
coste con los datos de consumo y tarifas correspondientes a las corridas.

La falta de presupuesto monetario acordado **no bloquea este diseño ni la
calificación de código**, conforme al usuario. No implica permiso para que
este agente inicie llamadas externas o una campaña ilimitada. La cantidad de
entregas y oportunidades de reparación se fija por comparabilidad, no para
adivinar cuánto cuesta un modelo secreto.

## Precedencia y alcance de la enmienda

- Este carril sustituye el **orden inmediato** de D0: WCT antes de
  personalAssistant; no borra el requisito de generalización externa.
- Refinar P1a en P01/P02 no autoriza P1 completo. Prevalece el contrato exacto
  P01 para esa pieza; el contrato global P1 gobierna su integración futura.
- El modelo nominal no debe constar en documentos visibles al evaluador. La
  exigencia anterior de modelo/tarifa pública antes de evaluar se reemplaza
  para este ensayo por custodia ciega y reconciliación posterior.
- No altera GateResult, los ADRs de compatibilidad, G1b, umbrales, canales de
  release ni permisos de bless. La resolución «B3-05» de D0 sobre mutación
  limitada no se renumera: este ADR tiene el identificador distinto SH-01.
- La beta.3 completa mantiene los objetivos de producto originales. Publicar
  solo evidencia/automejora exige un recorte humano de release; no llamar
  «moldes entregados» a estos documentos.

## Alternativas y coste de la decisión

| Alternativa | Motivo para no elegirla ahora |
|---|---|
| Coder mejora y se autoaprueba con sus gates nuevos | Circularidad: no separa código correcto de indicador debilitado |
| Reorganizar todo WCT en hexágono antes de medir | Diff grande, deuda heredada y efecto del refactor confundirían el experimento |
| Añadir `tools/` a mutación global inmediatamente | G1b/selección/coste no calificados; requiere autorización protegida distinta |
| Solo contar tests/gates verdes | No descubre sustituciones, casos omitidos ni oráculos débiles |
| Publicar benchmark después de una entrega exitosa | Sesgo de selección y ninguna estimación del contrafactual |

Coste aceptado: preparación y revisión humana, fixtures independientes y
registro de fallos, además del coste del coder. Se miden por separado. El
molde reduce elecciones; no elimina la necesidad de entender el requisito.
