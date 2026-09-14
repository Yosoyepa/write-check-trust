# GS-2 — resultado del lote de mutación `semgrep_scope.py` (2026-09-14)

Resumen versionado del lote GS-2 (sucesor de
`CIERRE-GS1-O1-O5-INTEGRACION-2026-09-14.md`). El expediente completo y
sellado vive bajo `build/tmp/gs2.YfTuE4/` (referencia por hashes, no custodia
durable). **Dictamen del lote: FAIL-survivors-stop** (16 supervivientes
confirmados + 39 kills pendientes de evidencia causal). No acredita AC1, no
ratifica equivalencias, no repara producto, no abre GS-3.

## 1. Identidad

- Base congelada: `ee1e878e2ed3f4012d93ea985b7055b80d3f9e49` (SHA publicado
  por la fase 1; PR #53 sigue borrador). Clon Git real desprendido, árbol
  limpio, runtime existente sin sync (Python 3.13.14, mutmut 3.7.0,
  pytest 9.1.1, semgrep 1.174.0, git 2.55.0).
- Fuente objetivo: `tools/wct/gate/semgrep_scope.py`, SHA-256
  `0bf26c714de0c512ed76ecbd9008efe3a2be7199ca241273a802bc24279bb12e` —
  **idéntico al histórico de referencia** (sin cambios que re-planificar).
  Sin reparaciones tras la campaña (hash re-verificado).
- Configuración mutmut SOLO en la copia (`only_mutate` exclusivo de scope,
  focal `tests/unit/test_sast_targets.py`, `-m "not property"`, sin detección
  Git): pyproject adaptado `2d7ede5a9e1839b2a3cc386e262badf3fc70e1fdb47f2ec45
  10491fd24a6911f`; original `b10f99b8…` preservado; diff registrado. La
  adaptación NUNCA vuelve al producto.

## 2. Preflight (puerta previa: APROBAR-CAMPAÑA)

- Corte 6/6 verificado (scope + test + feature + conftest + pyproject +
  uv.lock); AST: 8 funciones de módulo, 0 decoradas, clase
  `SemgrepScopeError` sin métodos.
- Colección 47 ítems; baseline independiente **47 passed, 0 skipped,
  0 xfail, exit 0**; `semgrep` y `git` presentes.
- Gen-only con firma admisible («1 files mutated, 78 ignored, 0
  unmodified» + AssertionError del filtro sin coincidencias; sin «Running
  mutation testing»); stats prístina `f17ccd82…`.
- Inventario: **118 mutantes mutmut**, todos not-checked; **8/8 funciones
  AST cubiertas, 0 ausencias**; métrica WCT-sites reproducida: **68 sitios**
  (idéntica a la adenda de planificación; tres métricas separadas:
  68 sitios ≠ 118 mutantes ≠ tiempos).
- Asociaciones 118/118 no vacías (32 nodeids, 0 fuera de colección); una
  tanda previa inválida (salida vacía) declarada y repetida.
- Procedencia `__file__` bajo `checkout/mutants/…` sin fuga; canario:
  control 31 passed exit 0, variante defectuosa `x_relative_path__mutmut_1`
  exit 1 con AssertionError. ID ejecutado en calibración: solo el canario
  (re-ejecutado fresco en campaña). `print-time-estimates` NO invocado.

## 3. Campaña y presupuestos

- Campaña serial `--max-children 1` con los **118 IDs explícitos** desde el
  inventario congelado (sin globs, re-ejecución fresca): exit 0, **274.46 s**
  (tope de puerta 1200 s).
- Presupuesto A (preflight+calibración+campaña): **≈ 505 s de 1800 s**.
  Presupuesto B (sondas causales): **541.5 s de 600 s** con guardián
  (`DETENIDO_POR_PRESUPUESTO_B=1`).

## 4. Resultado bruto y clasificación causal

- **Bruto mutmut: 102 killed + 16 survived = 118**; conjunto post ≡
  congelado; 0 timeouts, no-tests, suspicious ni skips.
- Clasificación revisada (`clasificacion-gs2.tsv`, una fila por ID):

| Clase | N |
|---|---|
| KILLED-EVIDENCIADO (sonda exit 1 con test y causa en fase call) | 63 |
| SURVIVED-CONFIRMADO (sonda exit 0, todos los tests asociados pasan) | 16 |
| PENDIENTE-SIN-SONDA (bruto killed preservado; presupuesto B agotado) | 39 |
| Contradicciones / instrumentales | 0 |

- Verificación independiente final: **APROBAR-EXPEDIENTE-GS2** (0
  bloqueantes, 6 menores), con auditoría documental del 100 % de los 79
  logs de sonda y recomputación de conjuntos, hashes y presupuestos.

## 5. Supervivientes (16) — FAIL-survivors-stop

Diffs preservados (`survivor-diffs.log`); agrupación propuesta para el
próximo incremento de adjudicación (sin reparaciones aquí):

| Familia | IDs | Hueco propuesto |
|---|---|---|
| Literales de `raise SemgrepScopeError` en sitios sin cubrir (None / XX…XX / MAYÚSCULAS) | `_build_dirs__15/16/17/22`, `_python_files__9`, `_relative__4/9`, `_scoped_dirs__6/7/8/17`, `_unique_dirs__12` (12) | Oráculo de prefijo del diagnóstico, patrón O1 de GS-1 |
| Operadores booleanos | `_build_dirs__11` (`or`→`and`), `_is_string_list__1` (`and`→`or`), `_relative_path__5` (`or`→precedencia) (3) | Casos frontera de validación de tipos y escape |
| Control de bucle | `_required_sources__17` (`continue`→`break`) (1) | Caso con múltiples candidatos tras el salto |

Los 39 kills sin sondear quedan PENDIENTE-SIN-SONDA: su sensibilidad descansa
en el bruto mutmut y quedan abiertos a evidencia causal posterior (presupuesto
B agotado; declarado, no oculto).

## 6. Limitaciones

1. FAIL-survivors-stop: GS-2 NO está aprobado; la adjudicación de los 16
   supervivientes es un incremento separado con decisión humana.
2. Los 39 PENDIENTE-SIN-SONDA no tienen evidencia causal propia.
3. El runner persistente de mutmut y los tiempos por paso no quedan con
   timestamps en los logs (corroboración indirecta por duraciones y estados).
4. Constantes de módulo (`_SOURCE_KEYS`, `_IGNORED_PARTS`) no son
   trampolinables: limitación instrumental declarada, no cobertura.
5. La fila E4 de la matriz de decisiones queda sin tocar en este commit: su
   actualización corresponde a quien consolide el estado de lotes.

Expediente: `build/tmp/gs2.YfTuE4/` — sello `gs2.sha256` (106 miembros,
SHA-256 `088a22eadcf6da8909a53af6093e32c45063561d455408d34f6be47bbb7bd98e`),
verificación 106/106 fuera de los miembros; puerta previa
`build/tmp/verifier-gs2-preflight/dictamen-preflight-gs2.md` (APROBAR-CAMPAÑA);
cierre `build/tmp/verifier-gs2-final/dictamen-final-gs2.md`
(APROBAR-EXPEDIENTE-GS2).
