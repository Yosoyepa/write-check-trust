# P02a — responsabilidad de required inputs

El coder preguntó antes de fijar su expected si los mínimos del perfil en §3
debían estar hardcoded en `capture_inputs`. El arquitecto resuelve conservando
la letra del contrato congelado, no agregando una exigencia oculta.

Los mínimos `src`, `tools/wct`, `tests` y los cinco archivos enumerados son
obligación del caller revisado. P06 debe comprobarlos al construir InputSpec.
P02a valida tipos, versiones/valores, listas no vacías, duplicados/anidación,
existencia, intersección con exclusiones y una raíz con archivo seleccionado.
No añade una segunda validación hardcoded del subconjunto mínimo.

La selección de archivos no depende de estrechar `required_*`: siempre se
inventarían todos los regulares no excluidos. Los fixtures de calificación IA
conservan los nombres/disposición mínimos fijados en el contrato. Una captura
con otros required inputs no acredita conformidad completa del caller P1.

Motivo: distinguir contrato de enumeración y ensamblaje evita dos políticas
divergentes. La obligación pendiente de P06 queda explícita y se probará con
un caller que omita un mínimo y su control válido.

Registro de aprendizaje: ambigüedad consultada y resuelta antes de expected;
fuente `coder-test`/consulta de contrato, asistencia de arquitectura. No es un
defecto de una entrega completa, ni una detección de un gate, ni evidencia de
ahorro. El contrato original no se reescribe ni se recalifica retroactivamente.
