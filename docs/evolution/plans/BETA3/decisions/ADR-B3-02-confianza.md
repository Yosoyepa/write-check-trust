# ADR-B3-02 — Confianza por evidencia y alcance, no por número de gates

> Adenda D0: se recomienda **aceptar con SPEC-P1**. El destino de la rebanada
> beta.3 descrito abajo se entrega por etapas: [P1](../specs/SPEC-B3-P1-evidencia.md)
> solo tests→LCOV→ratchet, con salida opt-in y GateResult intacto; arquitectura
> empieza después. [D0 §4](../D0.md) recomienda beta.3 limitada sin mutación
> fresca/completa obligatoria y mantiene abiertos todos los requisitos de G1b.

Estado: **propuesto**, 2026-09-07. Complementa O-001/O-006 y no reemplaza G1b.
Motivación: [F04–F06/F09–F10](../RESEARCH.md).

## Decisión recomendada

Conservar `GateResult` como resultado de un gate y envolverlo en un registro de
ejecución versionado. El cierre del perfil comprueba separadamente:

1. resultados: qué falló o pasó;
2. completitud: cuáles obligaciones fueron ejecutadas;
3. validez: correspondencia entre árbol, configuración, scope y artefactos;
4. calificación: qué poder discriminador se probó para cada claim.

Un SKIP requerido impide cerrar el perfil, aunque el modo tolerante histórico
permita trabajar. La salida existente no cambia silenciosamente: primero
exponer la semántica nueva de forma opt-in y probar compatibilidad.

## Fronteras de confianza

| Contexto | Garantía posible | Control necesario |
|---|---|---|
| Uso local cooperativo | detectar errores accidentales y drift | hashes, manifest, comparación de inputs y evidencias |
| Agente con permiso de escribir todo el repo | no puede certificar su propio verificador | checks sobre runner/config protegidos fuera de su modificación |
| Experimento adversarial | ejecución y scoring separados del agente | aislamiento de sistema, sin secretos ni socket Docker, política de red y recursos |
| Publicación | relación entre SHA calificado, tag y assets | validación remota y custodia del manifiesto de release |

Un SHA/hash detecta diferencias; **no prueba autenticidad si el agente también
puede regenerar el hash**. Un directorio `build/tmp/run-X` evita colisiones por
nombre; no impide que un proceso con el mismo acceso lea otros directorios.
El workspace privado de G1b atiende un problema específico de mutación y no
debe anunciarse como sandbox para agentes no confiables.

La API del proveedor no entregará secretos al proceso que ejecuta código del
modelo: un runtime aprobado gestiona inferencia y acceso mínimo. El oráculo
oculto vive fuera del workspace y su feedback no vuelve al agente durante el run.
El código generado sigue siendo no confiable cuando se lo evalúa: el sandbox
de scoring tampoco recibe secretos ni acceso a infraestructura real.

## Rebanada beta.3

Comenzar por claims usados en el molde: alcance arquitectónico, conformidad de
imports, ejecución de tests/contratos y cobertura producida en la cadena actual.
El registro enumera los demás como limitados/no acreditados. No es necesario
reescribir todos los gates para no mentir sobre los que aún no tienen evidencia.
La elección del subset se congela antes de evaluar modelos, no según quién ganó.

Mutación conserva su límite G1a mientras no se apruebe y verifique G1b. Completar
G1b requiere demostrar identidad del inventario, pertenencia al run, invalidación,
concurrencia y significado del rechazo. Si la causa no es observable, se mantiene
«killed reportado» en vez de «test detectó el defecto».

## Alternativas y consecuencias

- Rechazado: «34/34 = confianza 100 %»; aliases, heurísticas y scopes difieren.
- Rechazado: tomar el LCOV más reciente por mtime; un reloj o archivo copiado no
  demuestra procedencia.
- Rechazado: mismo agente genera solución, tests, metadatos y aprueba el cierre.
- Elegido: guardas deterministas más oráculos independientes; revisión humana
  donde el requisito no es verificable automáticamente.
- Coste: nuevos contratos de evidencia y tests de corrupción. Limitar retención,
  proteger datos y medir overhead antes de convertirlo en camino obligatorio.

Los tests de confianza incluyen reemplazo de árbol durante el run, resultado
truncado, scope vacío, salida de otro run, cambio de config y verificador alterado.
El detalle contractual se encuentra en [SPEC-B3-02](../specs/SPEC-B3-02-evidencia-contexto.md).
