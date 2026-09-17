# 1.0.0b3.dev1 — salida incremental (preparación)

Versión de desarrollo de beta.3 basada en la integración de PR #53,
commit `259ac4364699c70950e108be785ae9c8b32f1d15`.

Incluye el motor de evidencia de aceptación, endurecimiento del transporte,
reconciliación del alcance Semgrep y partición de módulos con fachadas.
La evidencia, adjudicaciones y límites están en los expedientes BETA3.
No declara beta.3 completa ni equivale a una release estable.

Este incremento cambia únicamente la versión del proyecto y de Commitizen
a `1.0.0b3.dev1`, explicita el esquema `pep440` y regenera el lock sin
actualizar dependencias. Tag previsto: `v1.0.0b3.dev1`.

## Antes de publicar

- Revisión independiente del incremento y bless humano de las rutas protegidas.
- Integridad y CI verdes sobre el candidato publicado e integrado.
- Generación y validación del SBOM y smokes sobre los artefactos finales.
- Custodia de artefactos con hashes y recuperación comprobada.
- Tag ligado al SHA final verificado y GitHub prerelease, no publicación PyPI.

Los builds locales previos al bless son comprobaciones preliminares: no son
artefactos finales de release. No se ha creado el tag ni publicado la prerelease.
