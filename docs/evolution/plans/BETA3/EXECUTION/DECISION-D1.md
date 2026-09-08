# D1 — delegación y autorización de P02a

## Autoridad y límites

El usuario respondió «apruebo» a la pregunta explícita de delegar al arquitecto
la aprobación de contratos y Gherkin de P02–P10, manteniendo los bless y la
publicación bajo aprobación humana. Se registra esa delegación, no una
autorización para atribuir al usuario futuros bless ni relajar gobernanza.

El arquitecto aprueba ahora el corte P02a descrito abajo. Las piezas posteriores
requieren su propio contrato, challenge separado y decisión registrada antes
de implementación. Esta decisión no acredita todavía ningún producto P02a.

## Contrato congelado y alcance

- Base documental: `25d73824ff5adf03b5a5a8a66821eab896cf6409`, sobre
  main `0228acc6ff83e5e4312ade22295a67796763b99c`.
- [PROPUESTA-P02a.md](PROPUESTA-P02a.md), SHA-256
  `3e70dc048779ede4a73510de7a0ded493596e4661a3ba809aee5c52b45c13fa3`.
- API, errores, límites, matriz de 41 familias/42 filas, Gherkin verbatim y
  diez archivos de §10 aprobados, con el handoff adicional exacto del
  [encargo](ENCARGO-P02a.md).
- [Sonda Git](SONDA-GIT-P02a.md), SHA-256
  `78232d23c0f5159443a45fb741fd82f4f6cfa3a138666d15ef07f9097b96147d`:
  preparación revisada, no sustituto de tests del producto.

Motivo: las consultas Git y sus riesgos identificados se reconciliaron antes
del coder; el inventario independiente es prerrequisito de la atribución de
evidencias. La aprobación conserva las limitaciones de captura cooperativa,
contexto caller-declared y custodia local. No promete aislamiento ni frescura
de ejecuciones posteriores.

Los encabezados históricos «propuesta/no iniciar sin D1» se conservan; esta
acta satisface esa puerta para los bytes citados, sin reescribir su historia.
Una revisión de API o allowlist necesita decisión nueva antes de implementarse.

## Entrega y promoción

Coder en worktree aislado, sin commit/push/bless. Verifier separado sobre el
digest final; coordinador integra únicamente el incremento revisado. No se
reutilizan artefactos P01 como verificación de P02. Los resultados pertenecen
a B3-MA-D; modelo original ciego y coste unavailable permanecen separados.

G-META-1 pre-bless no equivale a CI verde. Al llegar a esa puerta se presentarán
PR, SHA, rutas protegidas y comando al humano. Tags/releases continúan fuera
de esta delegación.
