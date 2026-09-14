# GS-2 — receta fail-closed, atribución pendiente y regresiones (2026-09-14)

Sucesor de `ADENDA-GS2-ATRIBUCION-ADJUDICACION-2026-09-14.md`. Tres entregas:
(1) receta de sondas fail-closed, (2) atribución de los 35 kills pendientes,
(3) regresiones mínimas para los 16 supervivientes con la decisión contractual
de diagnóstico aprobada en el encargo. Sin campaña de 118, sin GS-3, sin
cambios de producto, sin bless/merge/bump/tag/release.

## 1. Receta fail-closed (Fase 1)

Lanzador `sonda-fc.sh` en `build/tmp/gs2-cierre.nDW4ha/` (copia experimental
con identidad verificada: scope `0bf26c71…`, pyproject de receta
`2d7ede5a…`): bloquea ANTES de lanzar pytest si (a) asociaciones ausentes o
ilegibles (exit 2), (b) ID fuera del inventario autorizado (exit 3),
(c) selección vacía (exit 4), (d) nodeid fuera de la colección verificada
(exit 5). Sin fallback a suite completa; argv construido explícitamente;
timeout por sonda; meta por sonda con cwd, intérprete, PATH/PYTHONPATH, ID,
argv, nodeids, tiempos monotónicos y exit.

**Controles** (copias manipuladas en `controles/`, nunca la evidencia real):
asociaciones ausentes → 2 sin pytest; selección vacía → 4 sin pytest;
nodeid desconocido → 5 sin pytest; ID ajeno → 3 sin pytest; selección válida
→ ejecuta exactamente los 13 nodeids autorizados. Los controles cazaron y
corrigieron **dos defectos del propio lanzador** (referencia a variable no
inicializada `PYTHONPATH` bajo `set -u`; grafía del inventario: los IDs
públicos van con `x_` simple, p. ej. `x_required_sources__…`, no `x__…`).

## 2. Fase A — atribución de los 35: veredicto DISCREPANCIA-NO-REPRODUCIDA

**Hallazgo mayor del instrumento.** Con el lanzador corregido, las 35 sondas
—y dos controles de sanidad sobre kills con evidencia sellada previa
(`x__build_dirs__mutmut_1`, detectado ayer por aserción conductual
«ERROR vs FAIL»)— devuelven **exit 0: los 47 tests focales pasan bajo el
mutante activado**. En cambio, `mutmut run <id>` con ejecución fresca sigue
dando `killed` (102/16 sin cambios). Diferencia clave encontrada: mutmut
3.7.0 ejecuta pytest **in-process** (`pytest.main` en el mismo intérprete,
`__main__.py:438-451`) secuencialmente para los 118 mutantes; varios logs
sellados de sondas muestran fallos en `trampoline.py:84` («missing 1 required
positional argument») que son **corrupción de despacho del trampolín**, no
comportamiento del programa. Conclusión: **una parte de los 102 killed de la
campaña no es reproducible en procesos frescos y se atribuye a contaminación
de estado del runner in-process (artefacto instrumental)**.

Consecuencias registradas (el histórico NO se reescribe):
- Los 35 pendientes pasan a **DISCREPANCIA-NO-REPRODUCIDA** (veredicto de
  campaña killed no reproducible en sonda fresca; ni killed-evidenciado ni
  equivalencia). `x__unique_dirs__mutmut_6` incluido: su fallo en focal
  fresca (`TypeError` en `trampoline.py:84` al procesar
  `test_fuente_ignorada_por_git_sigue_siendo_exigible`) es del mismo family
  artefacto y se **degrada** respecto de la atribución provisional de la
  adenda anterior.
- Los 63 KILLED-EVIDENCIADO del cierre GS-2 quedan **bajo sospecha de
  artefacto**: sus logs incluyen tanto detecciones conductuales genuinas
  (aserciones de contrato) como TypeErrors de trampolín; la distinción ID a
  ID queda para revisión posterior con un runner fuera del proceso de mutmut
  (fuera de alcance aquí). El bruto histórico 102+16 permanece como está.

Presupuesto A: **≈ 570 s de 600 s** (controles de receta ~15 s incluidos;
35 sondas focales 464,7 s; 2 controles de sanidad 37 s; diagnóstico
`mutmut run` 19 s; intentos invalidados previos a la corrección de la receta
sin costo pytest). Incidentes: el lanzador inicial tenía los dos defectos
descritos; y la primera tanda de demostraciones (Fase 3) falló por resolver
nodeids contra la copia de tests del árbol `mutants/` (desactualizada) —
corregido sincronizando esa copia.

## 3. Fase B — regresiones de los 16 supervivientes: 16/16 RECHAZADOS

Cambios permanentes (allowlist cumplida): `tests/unit/test_sast_targets.py`
(+2 tests, +helper de política, +constant) y
`features/wct-sast-targets-001.feature` (+Scenario Outline de diagnóstico).

- **Decisión contractual aprobada (presentación, este incremento)**: los
  errores de alcance deben identificar la configuración o ruta rechazada;
  los **prefijos** de los ocho mensajes documentados quedan estables; los
  valores variables posteriores no quedan fijados. No se afirma que la
  grafía fuera contractual antes de este encargo.
- **Scenario Outline** «Los errores de alcance identifican la causa del
  rechazo» (8 filas, pasos sin colisión con otros outlines) con binding que:
  exige el inventario completo de filas (no pasa con ejemplos vacíos,
  retirados ni duplicados), ejecuta `required_sources` por la API pública y
  aserta tipo + prefijo (`startswith`).
- **Regresión de conservación**:
  `test_la_declarada_inexistente_no_aborta_las_posteriores` (contrato
  explícito del docstring de `required_sources`).

Demostración (hijo aislado con árbol de mutantes regenerado, tests sincroni
zados; presupuesto B ≈ 95 s de 600 s): **original verde (2 passed)** y
**16/16 supervivientes rechazados** por los oráculos nuevos, con el
mecanismo esperado: 12 por `AssertionError` de prefijo, 2 booleanos y
`relative_path_5` por «DID NOT RAISE SemgrepScopeError», y
`required_sources_17` por `assert [] == ['src/a.py']`
(`evidence/demostraciones-16-ledger.tsv` del expediente sucesor). Incidente
corregido: dos demostraciones se lanzaron con grafía errónea del ID
(`x__…` en lugar de `x_…` para funciones públicas) → sin activación →
re-ejecutadas con el ID correcto; la grafía errónea de esos dos IDs en el
TSV de adjudicación sellado se corrige por esta nota sucesora.

| ID | Expectativa → Resultado |
|---|---|
| `_scoped_dirs__6/7/8`, `_17` | prefijo/raise → RECHAZADO ✓ |
| `_is_string_list__1` | DID NOT RAISE → RECHAZADO ✓ |
| `_build_dirs__11/15/16/17` | prefijo/DID NOT RAISE → RECHAZADO ✓ |
| `_build_dirs__22`, `_relative__4` | prefijo → RECHAZADO ✓ |
| `_python_files__9`, `_relative__9`, `_unique_dirs__12` | prefijo → RECHAZADO ✓ |
| `_relative_path__5` | DID NOT RAISE → RECHAZADO ✓ |
| `_required_sources__17` | `[] == ['src/a.py']` → RECHAZADO ✓ |

Correcciones por nota sucesora (del acta anterior): «un prefijo no decide
grafía» era impreciso — fijar el prefijo fija parte del texto (de hecho esa
es la decisión ahora aprobada); «mensaje observable» no implicaba redacción
previamente contratada; una diferencia sin contrato no equivale
automáticamente a equivalencia; y «IDs que mata» solo se afirma tras
demostración (aquí ya demostrada para los 16).

## 4. Verificación del árbol integrado

Colección **660** (658 + 2 nuevos); suite normativa **660 passed**; property
1 passed; fast 7 PASS; tier commit **18 PASS + exactamente los 3 fallos
preexistentes** con causas re-verificadas e idénticas a la línea base
`c6be7ee`: `G-META-1` (drift del manifiesto de protegidos `tools/wct/**`),
`G-DEPS` (deptry) y `G-DEAD` (vulture sobre `accept/pytest_receipt.py`) —
tres hallazgos distintos; resolver el drift con bless no implica que los
otros dos pasen. Ratchets OK; introvertidos 0; `git diff --check` limpio.

## 5. Presupuestos

- Fase A (receta+atribución): ≈ 570 s de 600 s, con el veredicto
  DISCREPANCIA-NO-REPRODUCIDA para los 35.
- Fase B (demostraciones): ≈ 95 s de 600 s (16 sondas + baseline + 2
  re-ejecuciones tras corrección de grafía).
- Baterías de integración: aparte de ambos presupuestos.
- Verifier: aparte; modalidad documental + re-ejecución de lectura.

## 6. Estado

- Bruto histórico GS-2: 102 killed + 16 survived (inalterado).
- Clasificación causal acumulada: 63 evidenciados (bajo sospecha parcial de
  artefacto, ver §2) + 35 DISCREPANCIA-NO-REPRODUCIDA + 16 supervivientes
  con regresión demostrada. **GS-2 NO está aprobado ni PASS.**
- Los tests nuevos se preservan aunque queden atribuciones abiertas.
- Expediente sucesor: `build/tmp/gs2-cierre.nDW4ha/` (lanzador fail-closed,
  controles, ledgers, demostraciones; sello propio tras cierre de logs).
