# WCT beta.2 — decisión de salida y plan acotado

Estado: propuesta de release, NO autorización de publicación ni de cambios
protegidos. Corte auditado: `f449cd6967b7aef2fdd3e52b663e1e14f4a2bd08`,
2026-09-05 America/Bogota (merge registrado el 2026-09-06 UTC).

## Decisión

G3a-1 se puede cerrar como incremento fusionado. Recomiendo preparar
`v1.0.0-beta.2`, NO publicar todavía y NO promover a GA `1.0.0`.
La siguiente implementación recomendada es G3a-2, después de aprobar su
diff exacto. G1b queda separado; no es necesario resolver todo el backlog
para publicar otra beta con límites explícitos.

Esto distingue tres decisiones: cierre de G3a-1 (acreditado), preparación
de beta.2 (recomendada), publicación (pendiente de evidencia y autorización).

## Evidencia y hallazgos

| ID | Hallazgo y motivo | Consecuencia |
|---|---|---|
| R01 | PR #39 MERGED en `f449cd6`; quality del push a main SUCCESS. La CI del SHA publicado, no solo la de la rama, está verde. | Cerrar G3a-1. No reabrir sus correcciones pre-bless. |
| R02 | La frase «el escape ya es imposible por construcción» excede la evidencia. G-INTROVERT corre en commit y hay regresión específica, pero el analizador conserva límites y full sigue fuera de quality. | Claim: «el escape observado #37/#38 tiene regresión y control en commit/CI», no garantía universal. |
| R03 | quality genera LCOV pero todavía no ejecuta ratchet exigible. Su comando de cobertura tampoco excluye property, aunque el builder productivo usa `-m "not property"` y TEST-008 exige separación. G-TEST de commit solo ejecuta unit/integration con `not property`. | G3a-2 debe alinear productor y consumidor; excluir property sin paso separado perdería su ejecución actual en CI. |
| R04 | El último full-hardening consultado falló en `82d686d`, anterior a G3a-1, por G-DRY-TOK. El upload posterior no encontró `quality/reports/`. | No demuestra que main actual falle, pero tampoco hay evidencia full actual ni artefactos de esa corrida. Repetir sobre candidato exacto; conservar evidencias en rutas reales. |
| R05 | adoption-smoke pasó en `82d686d`, no en el candidato. Impone 120 s al tier commit. El commit tier en quality de `f449cd6` tardó unos 98 s, en otro procedimiento. | Repetir clon limpio/bootstrap/doctor/fast/commit con presupuesto vigente. No usar 98 s como prueba del smoke ni subir 120 s automáticamente. |
| R06 | CHANGELOG Unreleased vacío pese a 13 commits posteriores a beta.1; STATUS tiene cifras y fecha antiguas. Inventario real: fast 7, commit 21, pr 27, full 34. | Notas deben cubrir todo beta.1→candidato, no solo #39. Documentar migración y endurecimiento que puede bloquear adoptantes antes verdes. |
| R07 | GitHub devuelve `isPrerelease=false` para beta.1. pyproject sigue beta.1 y CLI muestra su normalización `1.0.0b1`. | Publicar beta.2 con prerelease=true explícito. No modificar silenciosamente la release histórica. Actualizar versión/lock por herramientas y comprobar CLI/metadata/tag coherentes. |
| R08 | RELEASES exige SBOM por release. No se ha acreditado un SBOM del candidato. G-SBOM es opcional en runtime y escribe `build/sbom.json`, no el directorio de upload de full-hardening. | Exigir SBOM real del candidato, registrar alcance (entorno con tooling vs dependencias desplegables) y conservarlo como evidencia/asset. SKIP no basta. |
| R09 | PR #33 sigue abierta (4 actualizaciones, solo uv.lock); último check falla en integridad por uv.lock modificado. | Es una PR inconclusa, no prueba de incompatibilidad de dependencias. Revisar aparte; no bless automático ni incluirla por conveniencia en la release. |
| R10 | G-TEST-RANDOM existe pero no pertenece a ningún tier; pytest-randomly no está declarado en los grupos inspeccionados. | «full verde» no demuestra TEST-006. Preparar verificación con semilla y entorno reproducibles; cualquier dependencia nueva requiere aprobación. Registrar limitación explícita si se decide una excepción, no inventar una corrida. |
| R11 | GA exige tres adoptadores, continuidad, 30 días sin cambio de contrato y guía de migración. ADOPTERS documenta un piloto. | No hay evidencia para GA. Beta.2 es la línea coherente con RELEASES.md. |

Fuentes remotas consultadas mediante `gh`, sin mutaciones externas:

- [PR #39](https://github.com/Yosoyepa/write-check-trust/pull/39).
- [quality del main auditado](https://github.com/Yosoyepa/write-check-trust/actions/runs/34005021634).
- [full histórico fallido](https://github.com/Yosoyepa/write-check-trust/actions/runs/33379724160).
- [adoption-smoke histórico](https://github.com/Yosoyepa/write-check-trust/actions/runs/33392278416).
- [PR #33](https://github.com/Yosoyepa/write-check-trust/pull/33) y
  [su fallo de integridad](https://github.com/Yosoyepa/write-check-trust/actions/runs/33971068449).
- [release beta.1](https://github.com/Yosoyepa/write-check-trust/releases/tag/v1.0.0-beta.1).

Fuentes locales: RELEASES.md, ADOPTERS.md, CHANGELOG.md, docs/STATUS.md,
pyproject.toml, Makefile, .github/workflows/{quality,full-hardening,adoption-smoke}.yml,
tools/wct/gate/runner.py y dossier G3a. Ningún fallo histórico se atribuye
al candidato actual sin reproducirlo.

## Etapa A — G3a-2, diff propuesto para aprobación

Frontera propuesta: quality.yml y documentación/tests de su contrato.
No llevar full a todas las PR, no añadir otra corrida de coverage, no
implementar G1b ni modificar baselines.

```diff
       - name: Generate branch coverage
-        run: uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q
+        run: uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property"
+      - name: Require measured ratchets
+        run: uv run wct ratchet check --require coverage-total,docstring-coverage
+      - name: Run property tests separately
+        run: uv run pytest -q tests/property
```

La separación property es una ampliación explícita respecto del paso único
del ADR-G3a-03 original: necesita reconciliar ese ADR y aprobación humana
del diff completo. Su motivo es preservar la ejecución que hoy sucede
dentro de coverage, no añadir una batería que ya corra en commit. Medir
el costo de proceso adicional; no prometer coste cero.

Motivo de la lista explícita: exigir las dos mediciones dependientes de
artefacto/herramienta, conservando todas las comparaciones estáticas por
la aditividad de G3a-1. `all` amplía automáticamente la obligación si el
inventario cambia; no es necesario para esta frontera.

La frescura se acredita por checkout limpio, productor exitoso y consumidor
posterior en el mismo job, sin restauración intermedia de LCOV. El orden
solo NO protege un workspace reutilizado con un artefacto viejo; los tests
deben comprobar esas premisas. No añadir `continue-on-error` ni `always()`
al consumidor para convertir el fallo del productor en consumo de residuos.

Criterios de aceptación propuestos:

1. LCOV ausente o inválido exigido bloquea; válido bajo baseline bloquea;
   válido sobre baseline pasa. No manipular baseline para obtener verde.
2. Interrogate ausente/no medible bloquea; una métrica estática roja sigue roja.
3. En workspace aislado sin LCOV previo, la receta produce el artefacto
   consumido por el paso exigible. Productor fallido no habilita publicación.
4. Property queda excluido de cobertura y conserva ejecución separada:
   commit lo excluye y no lo sustituye. Un property defectuoso debe poner
   CI roja en su paso propio, sin contaminar LCOV.
5. Registrar costo del paso añadido y tiempo del job. No atribuir a G3a-2
   la investigación emparejada RG12 de mutación, que pertenece a G1b.
6. Verifier independiente sobre diff final, aprobación/bless del workflow,
   CI en PR y post-merge verdes. Preservar el resto del árbol.

## Etapa B — candidato de release

Preparar en checkout aislado basado en commit identificado, sin stash ni
staging global del trabajo ajeno. La versión final del candidato incluye
G3a-2 si se acepta esta secuencia; no publicar retrospectivamente f449cd6
como si ya lo incluyera.

- Actualizar CHANGELOG, STATUS, cifras de tiers y enlaces rotos a RELEASES
  (desde docs el archivo está en ../RELEASES.md). Revisar documentación de
  adopción y notas beta.1→beta.2, incluyendo PR-A1/A2, B, C, D, E, F, G1a,
  reparación y G3a. No anunciar mejoras medidas de modelos económicos:
  todavía no hay benchmark que pruebe ese beneficio.
- Proponer bump exacto de `[project].version`, `[tool.commitizen].version`
  y regeneración del lock sin actualización incidental de dependencias.
  Son archivos protegidos: aprobación explícita y bless posterior.
- Decidir distribución: por defecto tag + GitHub prerelease del template,
  no PyPI ni marketplace. Si se pretende distribuir wheel/sdist, añadir
  build/instalación/CLI smoke y revisión de contenido del paquete antes de
  autorizar ese canal; no asumir que un tag prueba empaquetado.
- Documentar compatibilidad probada: CI inspeccionada usa Python 3.12,
  mientras pyproject permite 3.11–3.14. No afirmar matriz multiversión
  verificada. Proponer matriz si forma parte del compromiso de release.

## Etapa C — puerta de publicación

Requisitos propuestos para esta salida (no cambiar umbrales para aprobar):

- [ ] SHA candidato final y árbol aislado limpio, versión y lock consistentes.
- [ ] quality verde en ese SHA; requerimiento G3a-2 aplicado con LCOV nuevo.
- [ ] full-hardening sobre ese SHA, sin FAIL/ERROR; inventariar SKIP y no
      aceptarlo para controles requeridos de release, especialmente SBOM.
- [ ] Respetar orden mutación → aceptación mutada → CRAP → DRY; el workflow
      full actual ejecuta aceptación mutada después del tier. No afirmar que
      ese workflow por sí solo demuestra el orden de PROC-004.
- [ ] Evidencia de TEST-006 con semilla/entorno, o decisión humana explícita
      sobre el incumplimiento; sin ocultarlo detrás del agregado full.
- [ ] Adoption smoke limpio sobre candidato, commit ≤120 s, sin cambios
      silenciosos al presupuesto; capturar salida y entorno.
- [ ] SBOM y evidencia de controles conservados con SHA, comandos, resultados,
      scopes y omisiones; un log efímero local no es asset de release.
- [ ] CHANGELOG/migración/limitaciones revisados; autorización humana final.
- [ ] Crear tag nuevo inmutable y prerelease=true solo tras autorización;
      verificar smoke disparado por tag antes de declarar release cerrada.

Si cambia código protegido después del bless o el SHA tras las pruebas,
recalificar lo afectado. No reutilizar el bless de #39 para cambios nuevos.
No mover tags para maquillar un fallo: diagnóstico y decisión explícita.

## Qué queda fuera

G1b conserva sus bloqueos de identidades, frescura dentro del workspace,
symlinks y perturbaciones/concurrencia. #35 (narrativa Gherkin) y #12
(deuda del harness) siguen abiertos. No son automáticamente bloqueantes de
otra beta si sus limitaciones siguen explícitas. Deduplicación se vuelve
prioritaria SOLO si la corrida de release actual la señala como bloqueo;
no inferirlo del resultado viejo. PR #33 requiere decisión separada y audit
actual de dependencias; su estado abierto no impide por sí solo beta.2.

## Verificación de esta auditoría

Ejecutado: inspección Git local y GitHub, lectura de contratos/workflows,
inventario runtime de tiers, `wct gate --tier fast` 7/7, integrity check
exit 0, CLI `wct 1.0.0b1`. No ejecutados en este turno: suite completa,
full, adoption smoke, random, generación de coverage/SBOM ni publicación.
La batería de 334 tests del handoff es evidencia reportada por el ejecutor;
no se presenta como una nueva corrida de esta auditoría.

## Prompt para continuar

> Prepara G3a-2 y el candidato v1.0.0-beta.2 siguiendo este dossier. G3a-1
> está cerrado en PR #39; no reabras sus correcciones. Primero presenta
> para mi aprobación el diff exacto de quality.yml de la etapa A y los
> escenarios de aceptación; no edites archivos protegidos hasta recibirla.
> Después de aprobarse, implementa solo G3a-2 con TDD y verifier independiente.
> Mantén G1b, PR #33, issues #12/#35 y documentación ajena separados.
> Prepara luego notas completas beta.1→candidato y propuesta exacta de bump,
> lock y distribución. Presenta la matriz de release con SHA, full, smoke
> limpio ≤120 s, ratchets con LCOV recién producido, SBOM y orden aleatorio;
> documenta rojos, SKIP y faltantes sin bajar umbrales. Pide por separado
> aprobación de cambios protegidos, bless y publicación. No crees tag,
> release, push ni merges por inferencia de este encargo. Entrega un GO/NO-GO
> sustentado, no un «todo verde» agregado.
