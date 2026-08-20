# Política de seguridad

## Versiones soportadas

| Versión | Soportada |
|---|---|
| 0.1.x | sí |

## Cómo reportar una vulnerabilidad

**No abras un issue público.** Usa el reporte privado de vulnerabilidades de
GitHub (pestaña *Security* → *Report a vulnerability*) o contacta al
mantenedor (@jandradeu). Incluye pasos de reproducción, impacto estimado y
versión afectada.

Objetivo de respuesta inicial: 72 horas. La corrección se coordina por el
canal privado y se publica junto con el advisory cuando exista fix.

## Alcance

- El harness (`tools/wct/**`), sus hooks y su CLI.
- La cadena de suministro del repositorio: `uv.lock`, workflows de CI y
  configuración de pre-commit.
- Fuera de alcance: vulnerabilidades en proyectos que adoptan el template
  (repórtalas en el canal de cada proyecto).

## Postura proactiva

- Auditoría de dependencias desplegables en cada corrida de CI (`pip-audit`,
  gate G-AUDIT) y SBOM en cada release.
- Escaneo de secretos con baseline auditado (`detect-secrets`, gate G-SECRET);
  el baseline está sellado por el lock de integridad.
- El control plane (reglas, umbrales, workflows, motor) está protegido con
  hashes por G-META-1 y solo el mantenedor puede bendecir cambios, con
  aprobación registrada y citada.
