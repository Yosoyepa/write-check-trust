# Documentación

| Documento | Contenido |
|---|---|
| [Catálogo de gates](gates.md) | Los 31 gates en 4 tiers (fast/commit/pr/full): qué exige cada uno y con qué herramienta se verifica. |
| [Arquitectura](architecture.md) | Modelo de confianza (persuasión vs prueba), capas, métricas A/I/D y plano de control con lock de integridad. |
| [Runbook del mantenedor](runbook.md) | Bless, manifiesto de mutación, Dependabot en bloque, ratchets, flaky tests, webhooks y CI. |
| [Assets](assets/) | Logo, banners (claro/oscuro), GIF demo y social preview. |

## Documentación de proyecto (raíz)

| Documento | Contenido |
|---|---|
| [PLAN.md](../PLAN.md) | Decisiones, fases, límites y catálogo de gates del desarrollo del harness. |
| [RESEARCH.md](../RESEARCH.md) | Investigación fuente: conflictos, evidencia y razonamiento detrás de cada decisión. |
| [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | Avisos de terceros y licencias de dependencias. |

## Decisiones de arquitectura (ADR)

| ADR | Decisión |
|---|---|
| [ADR-001](../governance/decisions/ADR-001-ponytail.md) | Vendorizar la escalera minimalista (Ponytail) con overrides obligatorios. |
| [ADR-002](../governance/decisions/ADR-002-ruff.md) | Ruff como motor único de lint, formato y orden de imports. |
| [ADR-003](../governance/decisions/ADR-003-crap-threshold.md) | Umbral CRAP ≤ 6. |

## Comunidad

- [Cómo contribuir](../CONTRIBUTING.md)
- [Código de conducta](../CODE_OF_CONDUCT.md)
- [Reportar vulnerabilidades](../SECURITY.md)
