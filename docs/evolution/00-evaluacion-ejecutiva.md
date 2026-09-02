# Evaluación ejecutiva

## Conclusión

WCT ya posee una arquitectura útil de defensa en profundidad: reglas compiladas,
tiers, ratchets, verificaciones de arquitectura, seguridad, pruebas, mutación,
aceptación y red team. La oportunidad principal de la siguiente fase beta no es
añadir más gates indiscriminadamente. Es convertir el conjunto actual en un
sistema de evidencia cuyos alcances, umbrales, omisiones y resultados sean
comprobables.

Hoy puede afirmarse que el repositorio ejecuta una colección amplia de controles
y que las suites observadas pasan. Aún no puede afirmarse, con evidencia causal,
que:

- todos los controles implementan exactamente su regla declarada;
- un tier `full` verde representa cobertura completa de capacidades;
- el harness se somete a las mismas métricas que impone al código de ejemplo;
- `30/30` casos de red team equivale a 30 fallos reales rechazados por los gates;
- los escenarios Gherkin verifican siempre comportamiento ejecutable y no vacío;
- un modelo económico con WCT alcanza o supera a un modelo de referencia.

## Evidencia observada en el corte

Se ejecutaron verificaciones de solo lectura sobre la revisión indicada en el
[índice](README.md):

| Observación | Resultado | Lectura correcta |
|---|---:|---|
| `wct doctor` | verde | instalación y wiring básico disponibles |
| tier `fast` | 7/7, 0,91 s | anillo rápido operativo |
| tier `commit` | 20/20, 6,32 s | controles de commit operativos en este entorno |
| tier `full` | 32 `PASS`, 1 `SKIP`, 43,85 s | no equivale a 33 capacidades presentes |
| tests recolectados | 180 | la colección existe; no prueba orden aleatorio |
| cobertura efectiva reportada por `coverage` | 97 % sobre 61 statements | el scope observado es `src/example`, no el harness |
| baseline de cobertura | 100 | `G-COV-TOTAL` no lo compara y aun así pasa |
| archivos presentes en LCOV | 9 bajo `src/example` | `tools/wct` queda fuera del resultado |
| `wct mutate scan` | scope `src/example` | la mutación no califica el núcleo del harness |
| orden aleatorio | opción no reconocida | `pytest-randomly` no está disponible |
| duplicación por tokens | `SKIP` | falta `jscpd`; el tier se considera no bloqueado |

Estos son resultados de una fotografía local, no una serie histórica ni una
comparación entre modelos.

## Tesis de evolución

La evolución propuesta tiene cinco movimientos, en este orden:

1. **Honestidad de evidencia.** Cada resultado debe declarar valor observado,
   umbral, baseline, scope, herramienta, versión, artefacto y motivo de `SKIP`.
2. **Calificación del instrumento.** Probar los gates mediante repositorios
   fixture buenos y malos que ejecuten la ruta real, con métricas de falsos
   positivos y falsos negativos.
3. **Oráculo independiente.** Evaluar la solución con tests y revisiones ocultas
   que no formen parte de WCT ni estén disponibles para el agente.
4. **Experimentos causales.** Comparar brazos que separen reglas, gates y bucle
   de reparación, manteniendo tarea, entorno y presupuesto equivalentes.
5. **Evidencia externa.** Repetir en proyectos y equipos distintos, conservar
   resultados adversos y publicar límites, no solo éxitos.

## Modelo conceptual

WCT debe distinguir dos planos:

- El **plano de control** guía y restringe al agente durante el trabajo: reglas,
  hooks, gates, ratchets y diagnósticos.
- El **plano de evaluación** mide después, con información que el agente no pudo
  optimizar directamente: oráculos ocultos, revisión independiente, costo,
  latencia, trayectoria y escapes.

Si ambos planos usan exactamente el mismo test, la medición es circular. Que el
agente logre poner verde el test que vio solo demuestra capacidad de adaptación
al feedback; no demuestra generalización ni ausencia de defectos.

## Prioridades recomendadas

### P0 — verdad antes de escala

- Contrato de resultados y reporte de evidencia.
- Calificación end-to-end de cada gate y de sus estados `PASS/FAIL/SKIP/ERROR`.
- Corrección conceptual del scope de cobertura, mutación y property tests.
- Prueba de no vacuidad para aceptación y mutación Gherkin.
- Conformidad entre configuración declarada y comportamiento efectivo.
- Separación entre “no bloqueó” y “perfil completo/certificado”.

### P1 — medir el uplift

- Evidence Lab con tareas versionadas, brazos experimentales y ledger inmutable.
- Corpus curado con oráculos ocultos y casos adversariales.
- Benchmark de modelo económico con ablaciones.
- Telemetría de tokens, costo, tiempo, tool calls, reparaciones y fallos.
- Reproducción determinista de trayectorias y pruebas de ruta real.

### P2 — generalizar

- Observatorio de adopción y valor longitudinal de ratchets.
- Adaptadores para runtimes de agentes y benchmarks externos.
- Programa de postmortems que convierta escapes en fixtures permanentes.
- Extensión a otros lenguajes solo después de estabilizar el contrato de
  evidencia independiente del stack.

## Qué significaría éxito

La beta estará lista para hacer una afirmación fuerte cuando pueda responder,
con artefactos reproducibles:

- cuál era la tarea, snapshot y versión del modelo;
- qué cambió únicamente por activar WCT;
- qué calidad midió un oráculo que el agente no conocía;
- qué gates detectaron cada defecto y cuáles lo dejaron escapar;
- cuánto costó cada brazo y cuánto costó cada éxito;
- qué incertidumbre estadística tiene el uplift;
- qué herramientas faltaron o fueron omitidas;
- qué parte del resultado puede reproducirse sin una API real;
- y qué limitaciones o casos negativos siguen abiertos.

La meta no debería ser maximizar una puntuación única, sino desplazar la frontera
de Pareto: más éxito semántico y menos escapes por dólar y minuto, sin degradar
seguridad, mantenibilidad ni confiabilidad.
