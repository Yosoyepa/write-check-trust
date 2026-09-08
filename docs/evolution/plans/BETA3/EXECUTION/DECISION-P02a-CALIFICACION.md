# P02a — calificación focal autorizada

Decisión operativa del arquitecto, posterior a [D1](DECISION-D1.md).
No modifica el contrato de producto ni las configuraciones protegidas.

## Motivo y alcance

`mutate.engine.scan` recorre `policy.paths.source`; la configuración vigente
de mutmut selecciona `src/example`. Por tanto, su resultado por defecto no
califica las fuentes nuevas P02a bajo `tools/wct/evidence`.

Se autoriza una campaña focal adicional de mutmut en copia operativa exclusiva
bajo `build/tmp/b3-ma-p02a-r0/`, con configuración propia de esa fixture.
No editar pyproject, policy ni manifests del candidato para ampliar alcance.
No alterar instalación compartida ni instalar dependencias por esta decisión.

## Condiciones del instrumento

1. Antes de la campaña, comprobar receta con control válido y mutante real;
   registrar imports, fuentes/tests copiados, versión, argv y entorno efectivo.
2. Entorno de resultados nuevo, sin cachés heredadas. Máximo ocho workers.
3. Inventario independiente de identidades generadas frente a resultados;
   conteo igual no sustituye igualdad de identidades. Conservar ambos artefactos.
4. Diferenciar killed, survived, no tests, timeout, errores y no ejecutados.
   Un error de sintaxis/importación no acredita sensibilidad conductual.
5. Registrar límites del motor y evidencia causal disponible; no presentar
   desafíos manuales como mutación exhaustiva ni la campaña focal como G-MUT
   productivo ampliado. Conservar negativos y resultados incompletos.

Los límites de 100 sitios estimados/archivo, 500 LOC, CC y CRAP siguen vigentes.
Si el borrador exige partición, el coder presenta medición y nuevas rutas
cohesionadas; el arquitecto decide antes de crear archivos fuera del allowlist.
No se autoriza esconder complejidad en tablas ni mover umbrales.

Esta decisión registra asistencia de arquitectura al instrumento. No agrega
un éxito al denominador de tareas, no prueba mejora económica y no equivale a
GO de implementación. Coder y verifier deben atribuir sus corridas por separado.
