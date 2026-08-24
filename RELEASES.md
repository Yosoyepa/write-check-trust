# Política de releases y madurez

Inspirada en el modelo CNCF (sandbox → incubating → graduating), adaptada a
un template de tooling. La señal de cada nivel es **evidencia verificable**,
no autopercepción.

## Alpha — `0.x` (COMPLETADO)

Desarrollo de features contra [PLAN.md](PLAN.md). Todo puede cambiar sin
aviso. Cerrada en `0.5.0` con: 34+ gates en 4 tiers, full 30/30 en CI,
red team 30/30 (2 por F1–F15), 12 ratchets activos, mutación diferencial,
lock de integridad y separación autor/verificador.

## Beta — `1.0.0-beta.N` (DECLARADA en `1.0.0-beta.1`)

El contrato del template (CLI, gates, gobernanza) está completo y congelado
salvo rupturas anunciadas con bump de `N`. Criterios de entrada — todos
verificables:

| Criterio | Evidencia |
|---|---|
| Features del roadmap β completas | β-1 métricas estructurales (PR #21), β-2 ciclo del adoptador (PR #23), β-3 higiene (esta PR) |
| Adopción real medida | 1 adoptador (personalAssistant, 15+ fases de feedback) con ciclo de vida mecanizado (`adopt lock/check/sync` validado contra él) |
| Verde reproducible desde cero | `adoption-smoke.yml`: clon limpio → doctor + fast + commit sin intervención |
| Higiene de release | CHANGELOG.md (Keep a Changelog), ADOPTERS.md, esta política, semver declarado |
| Seguridad | pip-audit/semgrep/bandit/detect-secrets por PR, SBOM por release, branch protection con checks requeridos |

Durante beta: compatibilidad best-effort entre `beta.N`; una ruptura sube
`N` y se documenta en CHANGELOG.

## GA — `1.0.0`

1. **3 adoptadores externos** con uso real en dev/test (lista en
   [ADOPTERS.md](ADOPTERS.md)); el piloto cuenta como uno.
2. **Continuidad**: co-maintainer documentado o proceso de sucesión
   (hoy: mantenedor único — honestamente pendiente).
3. Cero cambios de contrato durante 30 días de beta estable.
4. Guía de migración para el salto a 1.x (`adopt sync` + diff-review).

## Versionamiento del template vs. proyectos adoptados

El semver del template describe **su** contrato. Los adoptadores no se
acoplan por versión sino por **hash de commit exacto** (`.wct-upstream.json`,
patrón cruft): tu repo decide cuándo moverse, `wct adopt check/sync` te dice
qué te vas a encontrar. El proyecto generado nace con su propio 0.1.0.
