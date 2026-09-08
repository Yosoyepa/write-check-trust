# P02a R3 — autorización humana acotada

Fecha: 2026-09-08. El usuario respondió «autorizo» a la solicitud explícita
de adjudicar los 54 supervivientes exactos de P02a para continuar hardening,
conservando resultados brutos y reservando bless/publicación a aprobación humana.

## Alcance aprobado

- Candidato: `e4b25b2b16183de4da325f2c1264a53a1d5590e1eda1e1943635d1e3eb080570`.
- Inventario: [P02a-ADJUDICACION-R3.json](P02a-ADJUDICACION-R3.json),
  54 IDs revisados individualmente: 47 E y 7 D. La propuesta original se
  conserva sin reescribir su estado histórico; esta decisión registra la autorización posterior.
- Resultado bruto: 1564 generados, 1510 killed, 54 survived, cero timeouts.
- Perfil: Linux, CPython 3.13.14, Git 2.55.0, mutmut 3.7.0, fuentes y deltas
  identificados en el inventario. No extrapolar a otra versión o candidato.

Se permite continuar la calificación focal pese a esos supervivientes
adjudicados. No se convierten en killed, no se ocultan y no se publica
«cero supervivientes» ni «G-MUT productivo PASS» por esta autorización.
Las siete D siguen siendo variantes contractualmente permitidas, no equivalentes.

## Límites y secuencia

No cambia governance, thresholds, reglas generadas ni manifests. No es un
permiso general para exceptuar supervivientes: IDs nuevos o cambios de
fuente, operador, runtime o supuestos contractuales requieren nueva revisión.

Continúa aceptación mutada → LCOV reciente/CRAP → DRY → gates y matriz global,
con evidencia focal del harness porque los gates por defecto recorren `src`.
Los fallos adicionales y SKIP se reportan; no se reinterpretan como verdes.
Un revisor distinto del autor comprobará el incremento final.

La integración del producto y el bless permanecen pendientes. Esta decisión
no autoriza ejecutar un bless en nombre del usuario ni publicar beta.3.
El expediente [REVIEW-P02a-R3.md](REVIEW-P02a-R3.md) conserva la situación
anterior y las limitaciones de custodia local y medición económica.
