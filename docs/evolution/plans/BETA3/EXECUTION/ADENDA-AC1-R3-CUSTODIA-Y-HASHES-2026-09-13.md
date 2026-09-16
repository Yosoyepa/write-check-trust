# Addenda AC1 r3 — custodia, hashes y orden de identidad

Fecha: 2026-09-13. Estado: **corrección de proceso documental; no modifica evidencia histórica ni ratifica supervivientes**.

Esta addenda acompaña, sin editar, `RESULTADO-AC1-LOTE-R3-2026-09-13.md`, los logs r3, sus JSON, diffs, preflight ni resultados. El estado histórico sigue siendo `FAIL-survivors-stop` con 47 supervivientes sin ratificar.

## Correcciones registradas

1. **Hashes desde bytes.** El auditor reproducible `build/tmp/ac1-r2-qualification/r3-adjudication/audit_evidence.py` recalculó los 14 hashes de la tabla histórica directamente desde disco y obtuvo 14/14 coincidencias. El manifiesto derivado es `build/tmp/ac1-r2-qualification/r3-adjudication/r3-adjudication-manifest.json`, SHA-256 `b7964b8377beb71e2baea90d50412f2d7724d05459276f24b98688eed6fd6352`. No se escribió ni sustituyó ningún artefacto histórico.
2. **Parser de estados.** Una primera expresión local buscaba estado al principio de línea y por ello no contó filas. El log real usa `    <id>: killed|survived`; la receta final aplica `^\s*(tools\.wct\.accept\..+?):\s+(killed|survived)$`, obtiene 497 IDs únicos y reconcilia exactamente `450 killed + 47 survived`. El error fue sólo de lectura local; no cambió resultados, hashes ni archivos del lote.
3. **Orden frente a identidad.** Los 47 IDs tienen el mismo conjunto en `results-all.log`, `mutation-code-lot-r3-reconciliation.json` y el log de diffs. El orden de resultados/diffs es numérico de mutmut (`…_9` antes de `…_86`); el JSON de reconciliación y la sonda focal usan la misma lista ordenada léxicamente. La receta persiste los tres órdenes y sus relaciones; no los presenta como una igualdad falsa.
4. **Alcance de bytes actual.** Las cuatro fuentes y tres tests cualificados del worktree actual coinciden con el manifiesto r3. El `pyproject.toml` de la copia r3 tiene el SHA del config temporal de mutmut y difiere intencionalmente del checkout: la diferencia se limita a esa receta privada, no a las fuentes/tests adjudicados. El manifiesto registra ambos hashes en vez de silenciarla.

## Límites mantenidos

- Las nuevas ejecuciones fueron sólo sondas focales contra `mutation-code-lot-r3/mutants/`, con `MUTANT_UNDER_TEST`, control original y seis canarios ya killed. No hubo `mutmut run`, recampaña r3, gate prohibido ni lote nuevo.
- La comprobación alternativa de los dos hooks decorados es una propuesta no ejecutada. La exclusión por decoradores de mutmut queda clasificada como limitación instrumental.
- La matriz técnica no es bless, ratificación humana, cambio de contrato, aprobación de PR, merge, bump, tag ni release.

La matriz completa se encuentra en `ADJUDICACION-SUPERVIVIENTES-AC1-R3-2026-09-13.{md,json}`; toda reparación propuesta requiere autorización separada y no se implementa en esta addenda.
