# Prompt de continuación — primera puerta de beta.3

> **Antecedente:** este prompt abrió D0 y ya no es el siguiente encargo.
> El usuario ahora pide WCT sobre WCT con coder ciego; usar
> [PROMPT-CODER de SH-P01](SELF-HOSTING/PROMPT-CODER.md) para aprobar e implementar
> solo la primera pieza. Se conserva el texto siguiente como historia, no para
> repetir planificación ya terminada.

Copiar el siguiente encargo si se acepta estudiar esta dirección. No equivale
a aprobar implementación, bless, gasto de API ni publicación.

> Asume el rol de arquitecto/specifier para WCT beta.3. Lee AGENTS.md y el dossier
> `docs/evolution/plans/BETA3/` completo, especialmente RESEARCH, ADRs, las dos
> SPEC, GHERKIN, EVALS y PLAN. Contrasta su base `8de9107` con el HEAD actual;
> conserva cualquier trabajo ajeno sin commitear. Esta tarea es de decisiones
> y especificación, no de código productivo.
>
> La dirección que quiero evaluar es un molde hexagonal Python verificable,
> mapeable a codebases existentes, con evidencia por alcance y medición de
> coste por solución correcta para modelos económicos. No prometas corrección
> universal, múltiples arquitecturas ya soportadas ni ahorro no medido.
>
> Cierra primero D0 con una propuesta concreta:
>
> 1. Reconciliar qué parte de policy/rules/archmetrics/wire/runner/adopt/report
>    se reutiliza y qué consumidor debe cambiar. Enumerar la cadena
>    campo → consumidor → test → evidencia y cualquier límite sin soporte.
> 2. Fijar el MVP a una raíz y un paquete Python por instancia, dos layouts
>    equivalentes, un caso brownfield y un puerto con pruebas de comportamiento.
>    No imponer nombres de carpetas ni generar lógica del negocio.
> 3. Especificar el primer incremento B3-P1 de evidencia: scope exacto,
>    compatibilidad de GateResult/salida histórica, inventario independiente,
>    fixtures positivos/negativos, presupuesto técnico por medir y Gherkin
>    listo para aprobación. No iniciar B3-P2 hasta que ese contrato sea claro.
> 4. Decidir explícitamente si beta.3 requiere mutación fresca/completa. Retomar
>    G1b sin llamarlo resuelto: identidades, invalidación dentro del workspace,
>    symlinks, source_paths, concurrencia y causa. Si se difiere, listar qué
>    claims quedan prohibidos y cómo se reflejan en perfil y experimento.
> 5. Preparar la selección de repos/tareas, oráculo independiente y presupuesto
>    para el piloto A0/A3/B3/A4. No ejecutar APIs ni elegir margen de no
>    inferioridad a partir de resultados. Modelos/tarifas/tope total requieren
>    mi aprobación antes de gastar.
> 6. Revalidar PR #33, issues #12/#35 y metadata de la release beta.2. Reportar
>    discrepancias y la decisión necesaria, sin modificar GitHub ni mover tags.
>
> Entrega ADRs aceptables/rechazables con motivos, Gherkin del primer incremento,
> matriz de pruebas y PRs candidatas pequeñas. Señala qué decisión necesitas de
> mí para D1. No modifiques governance, thresholds, workflows, pyproject, lock,
> código o tests ejecutables. No hagas commit, push, bless o release. Si hace
> falta corregir el dossier, limita los cambios a documentación y reporta el
> resultado real de fast antes del handoff.

Después de D0 habrá otro encargo separado de implementación con escenario y
frontera aprobados. La autorización de usar un modelo económico no autoriza
aceptar su autoinforme, leer holdout o alterar el verificador.
