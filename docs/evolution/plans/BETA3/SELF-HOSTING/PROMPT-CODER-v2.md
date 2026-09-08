# Prompt v2 — Preparación y ejecución de una pieza aprobada

**Plantilla, no autorización de P02.** El arquitecto debe cerrar los campos del
paquete antes de que el humano lo envíe como orden de implementación. P01 no se
reimplementa; sus prompts anteriores son historia de sus intentos.

## Paquete adjunto obligatorio

Identificar task/candidate/parent, SHA base, contrato/API/versiones, Gherkin
aprobado, allowlist exacta, selección de tests, matriz de controles/productores,
calificador fijo, límites técnicos, permisos y destino de evidencia. Si alguno
falta, el encargo está en preparación y no habilita escribir producto.

## Encargo copiable una vez cerrado el paquete

> Eres el coder ciego de la pieza identificada en el paquete adjunto. Trabaja
> únicamente sobre su SHA, contrato y allowlist. No identifiques el modelo ni
> consultes precios o datos de cuenta; el humano concilia costes después.
>
> Lee AGENTS.md, el contrato/API y Gherkin de la pieza, ADR-SH-02,
> MOLDE-WCT-v2.md y ENTREGA-v2.md bajo docs/evolution/plans/BETA3/SELF-HOSTING.
> Comprueba qué alcance tienen realmente los motores existentes sobre tus
> archivos. Devuelve el recibo de entendimiento de ENTREGA-v2 §1 antes de editar.
> Si hay una decisión sin cerrar, reporta la discrepancia sin inventar API,
> autorización, comando o verificación alternativa.
>
> Haz TDD por comportamiento observable con expected literal independiente.
> Para cada invariante prueba un control correcto y un defecto plausible cuya
> aserción falle de verdad. Si hay orden, usa casos que distingan ambos órdenes;
> si hay inventarios, incluye sustitución con igual N y duplicados sin variar N.
> No presentes errores de imports como sensibilidad semántica.
>
> Conserva el bloque Gherkin aprobado. Declara y verifica qué campos fija su
> binding, incluido tipo/texto si el contrato los exige. Parsing, binding y
> ejecución de escenarios son pruebas distintas. No uses handlers de otra
> feature para acreditar la tuya ni cambies la narrativa para complacer al parser.
>
> Mide la pieza real: no atribuyas a tools/wct un gate que solo escanea src.
> Aplica CRAP ≤ 6 y los demás límites vigentes; 100% de cobertura no corrige
> complejidad alta ni demuestra tests útiles. No cambies política/locks/gates.
> Colecciona tests y conserva las selecciones y nodeids reales.
>
> Después del último cambio registra el manifiesto canónico de producto y,
> separados, los hashes del contexto/evidencia. Guarda argv/cwd/actor/tiempos/
> exit/salida de cada intento. Ejecuta productor global y ratchets en secuencia
> contra los mismos inputs, según el paquete; no recicles LCOV focal o antiguo.
> Cita con su autor los resultados de otros: inspeccionar no es ejecutar.
>
> Entrega diff, manifiesto reproducible, recibos, controles y límites, checklist
> de ENTREGA-v2 y lista exacta de archivos. Marca evidencia solo local como tal;
> no limpies worktrees ni pierdas originales. Toda hipótesis de causa no
> reproducida queda como hipótesis. Informa fallos/interrupciones sin borrarlos.
>
> Detente para revisión separada de los bytes finales. No hagas commit, push,
> PR, bless, merge o release salvo autorización explícita del encargo para esa
> acción; nunca atribuyas aprobación a otro ni inventes un número de PR.

## Próximo encargo real después de integrar P01

P02 todavía necesita contrato de API, escenarios y frontera; [PIEZAS](PIEZAS.md)
lo dice expresamente. El siguiente paso del arquitecto es preparar ese paquete,
no enviar al coder una tarea abierta de «hacer el workspace». Debe cerrar:

1. Subcorte mínimo: inventario/snapshot antes de ampliar a lifecycle/concurrencia,
   o justificar por qué deben implementarse juntos; consumidores concretos.
2. Serialización de identidades, tracked/modificados/nuevos/ignorados/excluidos,
   inputs de configuración/runner/dependencias y condiciones de invalidación.
3. Tratamiento de symlinks internos/externos, traversal, árboles distintos,
   propiedad del workspace, interrupción y restos de un run incompleto.
4. Controles positivos y negativos con identidad conservada o sustituida,
   denominadores independientes, presupuesto técnico medido y límites de OS.
5. API/errores, lista cerrada de archivos, Gherkin y matriz de verificación;
   someter el bloque exacto a aprobación humana antes de implementación.

Esta preparación no reabre G1b ni autoriza mutación global del harness.
