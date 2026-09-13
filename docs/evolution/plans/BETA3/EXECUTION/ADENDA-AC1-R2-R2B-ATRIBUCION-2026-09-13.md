# Addenda AC1 r2/r2b — alcance, selección y autorización

Fecha: 2026-09-13. Estado: **corrección de trazabilidad; no es una autorización retrospectiva**.

Esta addenda corrige la lectura de `RESULTADO-AC1-L1B-2026-09-13.md` y `RESULTADO-AC1-LOTE-R2-2026-09-13.md` sin editar ninguno de los dos documentos ni sus registros crudos.

## Correcciones

1. **Alcance.** r2 y r2b fueron más allá del encargo limitado de adjudicar los residuos L1. Su ejecución y la posterior investigación de supervivientes sobre cinco módulos AC1 no se reinterpretan aquí como parte de la autorización limitada de L1.
2. **Selección concreta.** La selección de rutas del lote fue una decisión del ejecutor, no del arquitecto. El plan r2 seleccionó `tests/unit/test_accept_pipeline.py` y `tests/unit/test_accept_verdict.py`; al observar 51 `no tests` en `semantic.py`, el ejecutor produjo r2b con esos dos archivos más `tests/unit/test_accept_pytest.py`. El contrato arquitectónico delimitó la frontera AC1, pero no autorizó ni eligió esa receta concreta de r2/r2b.
3. **Evidencia preservada.** Los planes, logs, resultados, reconciliaciones y diffs originales permanecen vigentes e inmutables. En particular, `mutation-code-lot-r2b-survivor-diffs.log` usa `=== ID ===` como cierre del bloque anterior; el índice directo creado con `mutmut show` explica esa convención, no modifica el registro histórico.
4. **Equivalencia frente a ratificación.** La matriz `ADJUDICACION-SUPERVIVIENTES-AC1-R2B-2026-09-13.{md,json}` separa: (a) una equivalencia técnica demostrada para un runtime/precondición declarados, de (b) una ratificación humana. Ninguna clasificación técnica es por sí misma una exención, bless, cambio de contrato, cambio de política o aceptación de supervivientes.
5. **Sin extrapolación ni retroactividad.** La ratificación humana documentada para los cinco residuos L1 en el resultado L1b no se extiende a r2/r2b. Esta addenda no afirma que existiera autorización previa o posterior para r2/r2b y no concede autorización retrospectiva.

## Límites operativos mantenidos

- No se cambiaron fuentes, tests permanentes, gobernanza, workflows, `pyproject.toml`, lockfiles, manifests, bless, merge, versión, tag ni release.
- Las únicas ejecuciones nuevas fueron sondas focales contra fuentes de mutantes ya existentes y verificaciones de sólo lectura de sus artefactos; no se lanzó un lote nuevo ni una recampaña completa.
- El preflight de asociaciones descrito en la matriz es una propuesta futura con rutas exactas; el prototipo queda bajo `build/tmp/` y no cambia la gobernanza ni excluye módulos.

## Anclas de evidencia

- Plan r2: `mutation-code-lot-r2-plan.json`, SHA-256 `8c3572e8ea4f6ccfcebd9ff50f9d59bda8f0daf0936bcfcc8e7db8aba1feaf5b`.
- Plan r2b: `mutation-code-lot-r2b-plan.json`, SHA-256 `34243faf14af68a253732e682e38afde2dd7fc91a41825bdc4cb9ac017bc4869`.
- Matriz de conciliación/sondas/diffs: `ADJUDICACION-SUPERVIVIENTES-AC1-R2B-2026-09-13.json`.

La única decisión aún necesaria es humana: revisar la matriz, ratificar o rechazar expresamente cada clase técnica y, si se desea ampliar algún contrato, autorizar un incremento separado y revisable.
