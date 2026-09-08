# ADR-B3-04 — Adopción por mapeo, compatibilidad explícita y actualización revisable

> Adenda D0: **aceptable como planificación revisable**. Se reutiliza lifecycle;
> `lock` escribe el lock y `sync` escribe un patch, sin apply de vendor actual.
> [personalAssistant](../PILOTO-PREPARACION.md) es el caso seleccionado; Pydantic
> en dominio y roles de infraestructura exigen decisión explícita, no adaptación
> automática ni promesa de que ya conforma. [D0](../D0.md) precisa el MVP.

Estado: **propuesto**, 2026-09-07. No autoriza migrar repos de usuarios.

## Decisión recomendada

La primera experiencia de adopción será de lectura y planificación: inventariar
módulos/dependencias, proponer roles y mostrar incertidumbres. El usuario decide
si el molde describe su arquitectura o si primero necesita otro diseño.

No mover código para acomodar nombres convencionales. Reutilizar el ciclo
existente de `adopt lock/check/sync` para mantener la relación con upstream;
el lock de upstream y la instancia/versionado del molde son conceptos distintos.
Actualizar la herramienta no aprueba automáticamente una modificación de reglas.

## Compatibilidad y brownfield

- Traducir el contrato beta.2 a un perfil de compatibilidad y comparar sus
  resultados antes de activar semántica nueva. No afirmar compatibilidad con
  una comparación de texto solamente.
- Shadow mode mide deuda y falsos positivos sin anunciar conformidad completa.
  Después, el usuario decide qué scope puede exigir y qué deuda existente
  admite temporalmente. No capturar el estado roto como baseline automáticamente.
- No regresión se define por identidades de hallazgo/arista cuando sea posible,
  no solo por conteos: arreglar una violación y crear otra no mantiene la deuda.
- Excepciones con motivo, owner, issue real y revisión/expiración; nunca un
  allowlist global de «legacy» que absuelva todos los cambios futuros.
- Un cambio en un módulo legacy no obliga por defecto a reescribir todo el repo,
  pero tampoco autoriza introducir o desplazar una violación nueva. El scope y
  la estrategia de transición se aprueban antes del primer enforcement.
- Plan/apply deben comprobar que el árbol no cambió desde la revisión; conflicto
  o symlink que escape a la raíz impide aplicar. Nada de `--force` automático.

## Decisión build / reuse

| Necesidad | Primera opción | Por qué |
|---|---|---|
| Dependencias Python | Import Linter + analizadores WCT existentes | ya disponibles; medir límites antes de duplicar |
| Tipos y sustitución | mypy + tests de contrato contra puertos | forma estática y semántica necesitan señales distintas |
| Generar instrucciones | rules engine existente, alimentado por plan efectivo | evita segunda fuente de verdad |
| Upstream y drift | lifecycle de adopt | ya fija SHA y propone diff |
| Scaffold greenfield | ejemplos mínimos; evaluar Copier después | un generador adicional no es requisito para validar el molde |
| Ejecución de agentes/evals | adaptador mínimo a runtime evaluado | core neutral; sin framework propio por anticipación |

## No objetivos y consecuencias

No normalizar todos los repos a Clean Architecture, no ejecutar migraciones
automáticas ni producir dominio/servicios de negocio desde YAML.
Combinaciones como monolito modular + hexagonal requieren contrato de fronteras
entre módulos y calificación propia. Un nombre de patrón no los resuelve.

Beneficio: se conserva propiedad del usuario y se puede adoptar por etapas.
Coste: mapeo inicial, revisión de deuda y fixtures representativos del repo.
Esta fricción debe medirse en el piloto de adopción, no ocultarse detrás del
tiempo de clonar el template.

La [SPEC de moldes](../specs/SPEC-B3-01-moldes.md) y el [PLAN](../PLAN.md)
definen las pruebas de no escritura, actualización y compatibilidad requeridas.
