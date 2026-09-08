# Evidencia de ejecución — primera ola beta.3

Fecha local: 2026-09-07; las capturas posteriores a medianoche UTC corresponden
a 2026-09-08 UTC. **Registro de trabajo real, no calificación de beta.3.**
Actor central: arquitecto. Los dictámenes de subagentes se atribuyen aparte;
ni sus propuestas ni esta revisión equivalen a implementaciones P02–P10.

## 1. Frontera y entorno

- Worktree documental: `build/tmp/beta3-execution.uW30FJ`, rama
  `codex/beta3-execution-contracts`, creado desde PR #45 en `4666927`.
- Worktree P01: `build/tmp/sh-p01-CND-74E0`; mantiene su rama de PR #45.
- Entorno central reutilizado, sin sync/install: Python 3.13.14,
  `UV_PROJECT_ENVIRONMENT=.../build/tmp/sh-p01-CND-80B8/.venv`, `uv run --no-sync`.
  `PYTHONPATH` se fijó al worktree que correspondía a cada comando; no al R0.
- El árbol original no se cambió de rama, no recibió stash ni staging. Digest
  de su diff tracked inicial/final de esta comprobación:
  `f604fe3876cfce5a87391d29f5aeda2e902b712fa2ba1288260555958893d0cd`.
  Esto no hashea los archivos untracked; se conserva su inventario separado.
- No se han inspeccionado modelo privado, cuenta, configuración del proveedor,
  telemetría privada ni holdout. Consumo/coste de esta coordinación: unavailable.

Las capturas centrales ya devueltas por herramientas se exportaron sin resumir
a `build/tmp/beta3-campaign-review.Sjppx9/`: `lint-imports.txt`,
`archmetrics.txt`, `dry.txt`, `commit.txt`, `fast.txt`, `captures.json`.
Son custodia local, **no asset remoto duradero**. No borrar estos temporales
como si fueran basura; el expediente histórico R0/R1 tampoco se modifica.
Después se conservaron también `post-bless.txt`, `ci-pr45.json`,
`ci-main-p01.json` (consultas JSON de GitHub reformateadas), `parse-r1.txt`,
`parse-r2.txt`, los dos bloques Gherkin y copias exactas de propuestas R1/R2.

## 2. Checks centrales sobre el código de 4666927

Cada comando llevó el entorno explícito de §1. El dossier documental estaba
en preparación; los cuatro archivos P01 conservaban sus hashes congelados.

| Comando | Exit / resultado real | Alcance que sí acredita |
|---|---|---|
| `uv run --no-sync lint-imports` | 0; 4 contratos kept, 0 broken; 9 archivos, 8 dependencias | Ejemplo configurado, no arquitectura futura del harness |
| `uv run --no-sync wct archmetrics --json` | 0; cycles/violations vacíos; dos zonas pain históricas | Paquetes `example.*`, con baseline; no todo paquete saludable |
| `uv run --no-sync wct dry --json` | 0; 3 unidades, sin candidatos/errores | Scope por defecto del ejemplo, no duplicación de futuros adaptadores |
| `uv run --no-sync wct gate --tier commit` | 1; 20 PASS, 0 SKIP, 1 FAIL G-META-1; G-TEST 102671 ms | Código P01 y gates efectivos; no verde completo pre-bless |
| `uv run --no-sync wct gate --tier fast` | 0; 7 PASS, 0 SKIP, 0 FAIL/ERROR | Fast sobre producto preexistente; no prueba comportamiento de documentos |

`wct integrity check` pre-bless nombró exactamente los nuevos protegidos
`tools/wct/evidence/__init__.py` e `identities.py`. La corrida remota inicial
[34174535018](https://github.com/Yosoyepa/write-check-trust/actions/runs/34174535018)
falló en integridad y dejó pasos posteriores SKIPPED. No se les atribuye éxito.

Sonda runtime de `TIERS` y `REGISTRY`: `G-TEST-RANDOM` registrado, pero no
pertenece a fast, commit, pr ni full. Es evidencia de una brecha de ensamblaje,
no ejecución de orden aleatorio. La matriz de salida ahora exige ese check
explícitamente; todavía no se modificó ningún workflow o tier.

No se corrieron full/pr, mutación, redteam, orden aleatorio, SBOM ni una
calificación de release en esta primera batería. No se produjo LCOV nuevo aquí.
El 10/10 y las métricas de R1/integración previa conservan su fecha y actor;
no se reciclan como verificación contemporánea de esta ola.

## 3. Bless observado y revisión separada de sus bytes

En la lectura final del worktree P01 se encontraron cambios no creados por el
arquitecto de esta ola en exactamente tres archivos: `integrity.lock`,
`integrity-log.md`, `generated/mutation-manifest.json`, bajo `governance/`.
El log identifica `yosoyepa`, 2026-09-08T01:06:57.927155+00:00, PR #45 y
`46669278ece7e3b7cc8059a5eff9ae27c2735284`, con la razón del bless solicitado.
**El arquitecto no ejecutó `update-manifest` ni añadió una aprobación humana.**

Hallazgo B3-FP-01: los nueve hashes del manifiesto cambiaron sin cambiar `src`.
Se detuvo su incorporación hasta obtener explicación reproducible. Revisión
separada, solo lectura, de `qualification_audit`:

- `tools/wct/mutate/engine.py:24` usa SHA256 de `ast.dump` por defecto.
- Python 3.12.13 local reprodujo los 9/9 hashes anteriores. Python 3.13.14
  reprodujo los 9/9 nuevos; `show_empty=True` en 3.13 reprodujo los anteriores.
  El cambio de serialización de listas vacías explica este caso exactamente.
- La serialización productiva de 3.13 coincidió byte a byte con el artefacto:
  1292 bytes, SHA256
  `04bf135aefe3aa7d3e578b7e541d03e01559740d6507e21bb25ea0cafaf953e8`.
- `integrity.review` devolvió `([], [])` en ambas sondas. `src` sin diff;
  los cuatro archivos P01 conservaron los hashes de CND-74E0.
- Scan 3.13: 0 changed; scan 3.12: 9 changed, ninguno over_limit;
  G-MUT-SITES PASS. El consumidor compara desigualdad: aquí añade trabajo,
  no omite cambios. No se encontró un falso negativo causado por este drift.
- La sonda 3.12.13 con PyYAML reutilizado no es la CI 3.12.14 ni la sustituye.

Decisión: el drift conservador no invalida P01 ni justifica mezclar un arreglo
protegido no revisado. Se incorporan los tres artefactos humanos coherentes,
sin alterarlos. Commit `3795032`, `chore: record approved P01 integrity
artifacts`, hooks fast y conventional PASS; staging explícito de tres rutas.

Verificación central post-bless, antes del commit, sobre ese mismo producto y
artefactos: `wct gate --tier commit` exit 0, **21 PASS, 0 SKIP, 0 FAIL/ERROR**;
G-META-1 coincide con lock, G-TEST 97267 ms. `git diff --check` exit 0.

Seguimiento propuesto B3-FP-01, dueño de decisión `yosoyepa`: fingerprint
versionado/portable y runtime del productor, pruebas cruzadas entre versiones,
control de cambio semántico real y medición del trabajo extra. Es un ID local,
no un issue creado ni una implementación autorizada. `show_empty=True` es un
control diagnóstico de este caso, no una solución universal ya calificada.
Motivo: evitar reparaciones aparentes y coste de mutación por diferencias del
instrumento, sin debilitar detección ni modificar el juez a mitad de un lote.

## 4. Revisión de los contratos nuevos

- `molds_audit`: revisión independiente de README/CADENA, sin bloqueantes;
  LOW corregido por el arquitecto: `_lcov_records` es lector de la vía exigible,
  no el parser tolerante. No se modificó `measure.py`.
- `p02_spec`: propuesta P02a con API, errores, selección, codec, positivos y
  negativos, allowlist y binding explícito. El parser/IR productivo en memoria
  arrojó 1 Outline, 39 filas/38 familias, 0 findings, según su captura.
  Eso no ejecuta P02a, no acredita symlinks ni valida todavía la receta Git.
- El challenge independiente de P02a y las sondas de su protocolo se registran
  antes de pedir aprobación para el coder. Las propuestas P02b–P10 siguen
  necesitando contratos específicos por incremento, no solo sus títulos.

La revisión de P02a produjo tres hallazgos **antes de implementar**:

| Hallazgo | Evidencia / decisión | Motivo |
|---|---|---|
| PG01 | Show-prefix devuelve un LF; contrato de framing explícito sin `strip()` | No rechazar un repo válido por expectativa ambigua |
| PG02 | Status ejecutó un filtro clean controlado; revisión 2 rechaza claves efectivas antes de status | Una consulta Git de lectura puede ejecutar código configurado |
| PG03 | Git conserva outputs eliminados, sin carpeta presente; proyección por tipo/path de índice/HEAD | No invalidar inputs sanos ni excluir un regular llamado `build` |

El reviewer añadió `--no-lazy-fetch` para no descargar objetos faltantes.
Sondas registradas en [SONDA-GIT-P02a](SONDA-GIT-P02a.md), SHA
`78232d23c0f5159443a45fb741fd82f4f6cfa3a138666d15ef07f9097b96147d`:
includes/worktree detectados, tipos de eliminados staged disponibles y
partial clone **local** negativo frente a completo positivo, mismo HEAD.
No son tests de un algoritmo P02a ya existente ni auditoría universal de Git.

Propuesta 1 conservada: `fce6603d8177235023542e9bd4a6b49eb70d025feddc9cf21bd64b5eae62c978`.
Texto decisorio de revisión 2 revisado: `1aac1287b73974338d9a9516491788493c6382db678e5b32c1ad810bc9d541c2`;
la addenda posterior solo actualiza preparación. Ambos tienen copia local.
El reviewer leyó tanto R2 como SONDA §11; **sin bloqueantes documentales nuevos**,
presentable para aprobación humana. El arquitecto repitió parse/IR de R2:
1 Outline, 42 filas únicas, 0 findings. No ejecutó handlers ni generó tests P02.

Estos hallazgos miden aprendizaje del proceso de especificación/revisión,
no defectos de un coder que todavía no había recibido P02. Las limitaciones
del instrumento son feedback de WCT; no se imputan al modelo secreto original.

QA documental central: enlaces relativos y fences de los ocho documentos de
EXECUTION comprobados con script local de lectura; sin fallos en esa captura.
El prefijo añadido al README BETA3 enlaza la entrada y evidencia existentes.
Fast repetido sobre el SHA integrado: 7/7. Los checks de producto no validan
la verdad de un documento: esa revisión se hizo por lectura y challenge.
El encargo P02a está preparado, pero no enviado a ningún coder; D1 pendiente.

La última revisión separada de `qualification_audit` encontró una contradicción
normativa adicional: el binding decía que positivo y alteración debían fallar.
Se corrigió **antes del coder**: positivo PASS; cada alteración FAIL por la
aserción pertinente. El hallazgo pertenece a la especificación, no a P01 ni a
un modelo implementador. Refuerza la necesidad de controles válidos (SH-C13);
un contrato parseable también puede contener una expectativa incorrecta.

No se confunde recibir una especificación con aprobarla. Esta ola usa tres
subagentes para preparación/revisión; no produjo tres candidatos de código
barato ni una tasa de éxito experimental.

## 5. Cierre remoto de P01 y siguiente puerta

Artefactos incorporados y push en
`3795032c6a7e1a39b3e2ce4a33927b5953d195e4`. La
[CI de PR #45](https://github.com/Yosoyepa/write-check-trust/actions/runs/34176799250)
terminó success: job 3m17s, commit 21/21, coverage normal 404 passed/1 deselected,
property separado 1 passed, exigibles **2/2** y redteam 30/30. La cobertura del
diff y el wiring de aceptación también corrieron y pasaron. No son 10 exigibles
en CI y no se atribuye ejecución de P02.

PR #45 **MERGED** a 2026-09-08T01:33:44Z, squash
`0228acc6ff83e5e4312ade22295a67796763b99c`. Comparación Git entre el árbol del
commit aprobado y el squash: sin diff, exit 0. El worktree documental se
rebasó a ese main sin conflictos, conservando sus adiciones documentales.
El worktree original con trabajo ajeno no se movió ni se limpió.

[CI post-merge de main](https://github.com/Yosoyepa/write-check-trust/actions/runs/34177065165)
success sobre **0228acc**, job 4m2s (01:33:50–01:37:52 UTC):

- Tier commit: 21 PASS, 0 SKIP, 0 FAIL/ERROR.
- Coverage normal: 404 passed, 1 deselected, 107.23s; LCOV producido en ese job.
- Ratchets exigibles: medidas 2 de 2; property separado: 1 passed, 0.33s.
- Redteam: 30/30 adversarios rechazados; wiring de aceptación PASS.
- Cobertura del diff de PR: SKIPPED por ser push a main; no se declara ejecutada
  en esta corrida. Sí pasó en la corrida de PR inmediatamente anterior.

Integridad local sobre el SHA integrado: exit 0. La verificación post-merge
pesada aquí citada es **remota**, no una batería local adicional inventada.
No se hizo bump, tag, release, SBOM ni calificación full de beta.3.

**P01 integrado; beta.3 no completa.** La aprobación del Gherkin P02a y de
cada modificación protegida posterior sigue siendo una puerta real; no se
la reemplaza por esta evidencia ni por una etiqueta verde.
