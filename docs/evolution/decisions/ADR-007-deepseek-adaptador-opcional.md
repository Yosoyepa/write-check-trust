# ADR-007 — Integrar DeepSeek Harness solo como adaptador opcional

- Estado: **Propuesto**
- Fecha: 2026-09-01
- Decisores requeridos: mantenedor de WCT y responsable del Evidence Lab
- Alcance: frontera de integración futura; no añade dependencia

## Contexto

DeepSeek Harness aporta SDK programático, sesiones durables, token meter,
snapshots, replay y mock de protocolo. Esas capacidades podrían reducir trabajo
para el Evidence Lab. Sin embargo, el proyecto está en developer preview/alpha,
posee una superficie amplia y no ofrece por sí mismo el corpus ni la inferencia
causal que WCT necesita.

Acoplar el dominio de WCT a su runtime contradiría la neutralidad de provider y
haría que una dependencia experimental condicionara el core de calidad.

## Decisión propuesta

Definir primero contratos neutrales del plano de evaluación. DeepSeek Harness,
si una PoC posterior demuestra valor neto, será un adaptador periférico y
opcional. No será dependencia de `domain`/`application`, requisito para ejecutar
gates ni fuente única de verdad de costo, seguridad o sesiones.

La versión/commit se fijará por experimento. Sus eventos se transformarán al
contrato neutral conservando provenance. Cualquier capacidad no representable se
declarará, no se filtrará como tipo específico al dominio.

## Alcance máximo de la PoC

- una tarea pequeña;
- A0 y A3;
- un modelo y un provider;
- workspace/home/session aislados;
- captura de evento, tokens y terminación;
- replay sin API;
- oracle oculto independiente;
- comparación contra runner mínimo;
- sin nuevos plugins de negocio ni cambio del core de gates.

## Criterios de adopción

- reduce esfuerzo neto frente al runner mínimo;
- produce el contrato neutral sin pérdida crítica;
- distingue uso exacto de estimado;
- cierra y reproduce artefactos;
- no expone holdout al agente;
- puede deshabilitarse sin afectar WCT;
- su licencia y supply chain son aceptables;
- breaking changes quedan aislados al adaptador.

## Criterios de rechazo

- requiere tipos DeepSeek en el dominio;
- obliga a adoptar toda su arquitectura de plugins;
- no permite reconciliar tokens/costo;
- snapshots se vuelven el único oracle;
- se confía en el runtime como sandbox suficiente;
- no existe replay determinista o cierre de sesión;
- la actualización del runtime modifica silenciosamente tratamientos previos.

## Consecuencias positivas

- Reutiliza infraestructura sofisticada sin perder neutralidad.
- Permite sesiones y replay más temprano si la PoC funciona.
- Conserva una vía de salida y comparación con otros runtimes.

## Costos y riesgos

- Mantener un adaptador frente a una API alpha.
- Duplicidad temporal con el runner mínimo.
- Diferencias de semántica entre providers y métricas de tokens.
- Tentación de adoptar features de runtime fuera del problema de WCT.

## Alternativas descartadas

### Adoptarlo como runtime obligatorio

Descartada por madurez, acoplamiento y alcance superior al problema.

### Copiar módulos seleccionados al repositorio

Descartada por deuda de mantenimiento, licencias/provenance y divergencia futura.

### Ignorarlo por completo

Descartada como decisión prematura: sus patrones de replay y ruta real son
directamente relevantes y una PoC acotada puede aportar evidencia.

## Condición de aceptación

No iniciar la PoC hasta que ADR-004 y los contratos de SPEC-001/SPEC-003 estén
aprobados. La PoC necesita un informe de salida con tiempo ahorrado, gaps y una
decisión explícita de adoptar, posponer o rechazar.
