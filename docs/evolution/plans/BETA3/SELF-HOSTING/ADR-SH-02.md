# ADR-SH-02 — Convertir hallazgos de revisión en contratos previos

Fecha: 2026-09-07. Decisión documental adoptada para preparar los siguientes
encargos, por solicitud del usuario de incorporar estas lecciones a las
especificaciones/moldes. **No autoriza P02, bless, merge ni release.**

## Contexto comprobado

P01 R0 necesitó reparación; R1 fue conforme al contrato de esa pieza. El
[dictamen R0](reviews/REVIEW-CND-80B8.md), el
[dictamen R1](reviews/REVIEW-CND-74E0.md) y la
[adenda de cierre](runs/ADENDA-E61F-CND-74E0.md) distinguen fallos de producto,
insuficiencias del instrumento y errores del reporte. Es insuficiente dejar
ese aprendizaje solo en actas que el siguiente coder no tiene que leer.

| Evidencia / motivo | Decisión preventiva | Comprobación antes de entregar |
|---|---|---|
| R0: CRAP 10/7; controles por defecto medían `src`, no la pieza de `tools/wct` | Matriz ruta → capacidad → productor, con alcance explícito | Resultado focal por función y cobertura de la pieza, no solo verde global |
| R0: invertir orden de duplicados seguía pasando | Cada invariante tiene control correcto y variante incorrecta discriminante | La variante falla por la aserción pertinente; no por import roto |
| R0: diccionario ocultaba duplicados; R1 aún no prueba tipo/texto/ejecución de escenario | Declarar campos cubiertos por el binding y sus límites | Para bindings futuros, tipo, pasos y filas exigidos por contrato tienen negativos propios |
| R0/R1: tres hashes distintos para los mismos archivos | Serialización de manifiesto versionada, con lista y orden fijados | Reproducción exacta, también desde otra ubicación |
| Coder 1/1 frente a reviewer 10/10 con LCOV global heredado | Separar autor de corrida, presencia y procedencia | Recibo productor/consumidor, mismo árbol, sin atribución cruzada |
| Evidencia grande solo en `build/tmp` | Estado de custodia explícito | No borrar worktrees/evidencias mientras no exista copia verificada |
| Modelo secreto, asistencia y reparaciones registradas | Congelar calidad antes de conciliar costes | Sin inferir ahorro, autonomía o causalidad de un candidato conforme |

## Decisión y precedencia

1. Adoptar [sh-delivery/2](ENTREGA-v2.md),
   [wct-harness-local/2](MOLDE-WCT-v2.md) y el
   [prompt de preparación](PROMPT-CODER-v2.md) para encargos posteriores.
   Son controles de proceso revisables, **no nuevos gates ejecutables**.
2. El paquete de tarea debe contener lo necesario antes del primer cambio:
   contrato de comportamiento, lista de archivos, matriz de comprobaciones,
   controles discriminantes, recibo de entendimiento y condiciones de parada.
3. No reescribir `sh-p01/1`, contratos v1, handoffs ni actas para aplicar v2
   retrospectivamente. El código CND-74E0 conserva sus cuatro hashes. Los
   README de entrada reciben únicamente un aviso de precedencia; la historia
   que sigue se conserva íntegra.
4. Las nuevas obligaciones se congelan por lote. Corregir un defecto del
   calificador requiere nueva versión y conservar las evaluaciones originales.
5. La autorización de commit/push de esta integración no es aprobación del
   resto del roadmap BETA3 ni permiso para que el agente se atribuya el bless.

## Alternativas y consecuencias

Solo añadir otro prompt informal mantendría las causas fuera del contrato.
Automatizar ahora un compilador de moldes, un ledger o un sandbox ampliaría
P01 sin sus consumidores ni Gherkin aprobados. Se elige un contrato documental
corto de entrada y entrega, reutilizando los controles existentes y declarando
dónde falta cobertura. P07/P08 podrán automatizarlo después de calificarse.

Hay coste de preparación y revisión. Medir iteraciones por defecto, escapes,
tiempo de revisión y coste por tarea; no prometer que v2 elimina reparaciones.
Los casos aprendidos de P01 ya son públicos: no sirven como holdout ciego.
