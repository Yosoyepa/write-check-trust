# Addenda GS-2 — cierre de atribución y adjudicación (2026-09-14)

Sucesora de `GS2-SEMGREP-SCOPE-RESULTADO-2026-09-14.md`. Cierra hasta donde
permite la evidencia y el presupuesto: la atribución causal de los 39
PENDIENTE-SIN-SONDA y la adjudicación técnica de los 16 supervivientes, con
propuesta mínima de regresiones para un incremento posterior. **No repite la
campaña de 118, no implementa reparaciones, no abre GS-3, no ratifica
equivalencias.**

## 0. Contabilidad inalterable

- Bruto histórico GS-2 (intacto): **118 = 102 killed + 16 survived**.
- Clasificación causal inicial (sello `gs2.sha256`, 106/106, SHA
  `088a22eadcf6da8909a53af6093e32c45063561d455408d34f6be47bbb7bd98e`):
  63 KILLED-EVIDENCIADO + 16 SURVIVED-CONFIRMADO + 39 PENDIENTE-SIN-SONDA.
- Fuente medida: `tools/wct/gate/semgrep_scope.py`
  `0bf26c714de0c512ed76ecbd9008efe3a2be7199ca241273a802bc24279bb12e`
  (sin cambios; base `ee1e878e2ed3f4012d93ea985b7055b80d3f9e49`).
- Clasificación sucesora de este incremento (NO sustituye la inicial, la
  extiende): de los 39, **4 pasan a KILLED-EVIDENCIADO** y **35 permanecen
  PENDIENTE-SIN-SONDA**. Cada conclusión enlaza ID → estado anterior →
  evidencia adicional (`evidence/clasificacion-sucesora-39.tsv` del
  expediente sucesor).

## 1. Fase A — atribución de los 39 (resultado parcial, presupuesto agotado)

- 39 IDs congelados con unicidad y pertenencia al inventario de 118
  (`ids-39-pendientes.txt`).
- **Incidente propio de receta (documentado, invalidó parte del plan)**: la
  copia privada no incluyó `evidence/associations.txt`; el selector de tests
  devolvió vacío y cada sonda corrió la suite completa (~116–122 s en lugar
  de ~4,4 s). Detectado tras 4 sondas; proceso detenido; asociaciones
  restauradas desde el expediente original tras la detención.
- **4/39 atribuidos** con evidencia válida (`atribucion-39-ledger.tsv`):
  `x__unique_dirs__mutmut_2/3/4/5` — todos exit 1 con fallo en
  `test_redteam_tools.py::test_tool_case_catches_planted_defect[F9-a]`
  (consumidor extremo a extremo del gate sobre el fixture F9-a) y causa
  mutante-provocada en fase call (3 TypeError provocados + 1 AssertionError
  contractual del summary: «F9-a: ruta de alcance no normalizable bajo la
  raíz: None»). Desviación de especificación declarada: la detección se
  observó por la suite completa, no por los tests asociados focales.
- **5.ª sonda interrumpida in-flight** (`x__unique_dirs__mutmut_6`, log al
  76 % sin fallo): intento invalidado, no atribuye.
- **Presupuesto agotado**: 477,4 s (sondas válidas) + 5.ª invalidada (parcial,
  techo nominal ~116 s) ≈ 593 s de 600 s. Los **35 restantes permanecen
  PENDIENTE-SIN-SONDA** por agotamiento; su sensibilidad sigue apoyada en el
  bruto mutmut bajo la selección focal.

## 2. Fase B — adjudicación de los 16 supervivientes (documental)

Base: diffs sellados (`survivor-diffs.log`), sondas exit 0 del cierre GS-2,
lectura de `semgrep_scope.py` (hash `0bf26c71…`) y su consumidor
`semgrep.py:88` (`str(exc)` → summary visible del gate). **Sin ejecución
adicional** (presupuesto agotado): las demostraciones de oráculo quedan como
primer paso TDD del incremento de reparación. Tabla completa por ID:
`evidence/adjudicacion-16.tsv` del expediente sucesor. **Las 16 filas se
proponen como clase A — GAP-DE-ORÁCULO BAJO CONTRATO VIGENTE**; ninguna es
defecto del original (el original cumple el contrato documentado) y **no se
ratifica equivalencia alguna**.

| Grupo | IDs | Mutación y entrada que distingue | Oráculo mínimo propuesto |
|---|---|---|---|
| Booleanos | `_build_dirs__11` | `or`→`and` en la guardia; `paths.build={"a":1}` → original levanta, mutante acepta claves como builds | `raises` + prefijo «policy.paths.build debe ser una ruta string» |
| Booleanos | `_is_string_list__1` | `and`→`or`; `paths.source="src"` → original levanta por sitio B, mutante desagrega chars → `[]` silencioso | `raises` + prefijo «policy.paths.source debe ser una lista de rutas string» |
| Booleanos | `relative_path__5` | `or`→`(and or)`; `source=["."]` → original None→levanta, mutante declara la raíz entera | `raises` + prefijo «ruta de alcance no normalizable» |
| continue→break | `_required_sources__17` | `continue`→`break` en declarada inexistente; `source=["no-existe","src"]` → original `["src/a.py"]`, mutante `[]` | aserción de conservación (contrato explícito: «Un directorio declarado inexistente no aporta fuentes») |
| Literales (8 sitios) | `_scoped_dirs__6/7/8` (mapa), `_scoped_dirs__17` (lista string), `_build_dirs__15/16/17` (build string/lista), `_build_dirs__22` (build no normalizable), `_python_files__9` (fuente escapa), `_relative__4` (no normalizable), `_relative__9` (escapa), `_unique_dirs__12` (ambigua) | `None`/`XX…XX`/MAYÚSCULAS en el mensaje; el resumen del gate pasaría a «None» o cambia de grafía | aserción de prefijo del mensaje original en cada sitio (4 sitios ya alcanzados por tests que solo exigen `raises` — B, E, F, H; 4 requieren entradas nuevas — A, C, D, G) |

Matices de contrato (por qué prefijo y no igualdad): el contrato vigente
exige rechazo y tipo (`SemgrepScopeError` ya asertado en los tests que
alcanzan cada sitio) y el mensaje es la superficie de diagnóstico del gate;
el texto exacto no está asertado hoy. El oráculo de prefijo mata las tres
variantes de cada sitio **sin decidir la cuestión de grafía**: si el humano
declara no contractual el texto exacto, las variantes XX/MAYÚSCULAS (4 IDs)
pasarían a equivalentes-propuestas y las None (8 IDs) seguirían siendo hueco
por degradación del diagnóstico («None» como summary).

## 3. Fase C — propuesta mínima de reparación (NO ejecutada)

| # | Caso conductual | IDs que mata de verdad | Entrada | Resultado esperado | Test propuesto (patrón) |
|---|---|---|---|---|---|
| 1 | Declarada inexistente no aborta | `_required_sources__17` | `source=["no-existe","src"]` | `["src/a.py"]` | aserción de conservación |
| 2 | source como string no lista | `_is_string_list__1`, `_scoped_dirs__17` | `source="src"` | `SemgrepScopeError` prefijo sitio B | `raises` + prefijo |
| 3 | build como mapa | `_build_dirs__11`, `_15`, `_16`, `_17` | `build={"a":1}` | `SemgrepScopeError` prefijo sitio C | `raises` + prefijo |
| 4 | «.» como declarada y como build | `relative_path__5`, `_relative__4`, `_build_dirs__22` | `source=["."]` y `build=["."]` | `SemgrepScopeError` prefijos sitios F y D | 2 `raises` + prefijo |
| 5 | Symlink dentro de source | `_python_files__9` | `src/sub/link.py`→fuera | `SemgrepScopeError` prefijo sitio E | prefijo sobre el raise ya alcanzado |
| 6 | «../afuera» declarada | `_relative__4` | `source=["../afuera"]` | prefijo sitio F | prefijo sobre raise ya alcanzado (comparte caso con 4) |
| 7 | Symlink en la declarada misma | `_relative__9` | `source=["enlace"]`→fuera | prefijo sitio G | entrada nueva + `raises` + prefijo |
| 8 | Policy sin paths | `_scoped_dirs__6/7/8` | `policy={"schema_version":1}` | prefijo sitio A | entrada nueva + `raises` + prefijo |
| 9 | Ambigüedad | `_unique_dirs__12` | `source=["src","./src"]` | prefijo sitio H | prefijo sobre el raise ya alcanzado |

**Allowlist propuesta para el incremento de reparación**:
`tests/unit/test_sast_targets.py` exclusivamente (los casos caben en el
módulo focal; sin archivos nuevos de test, sin feature, sin producto).
Nota de conteo: la tabla tiene 9 filas; los casos 4 y 6 comparten el oráculo
del sitio F, así que son **8 oráculos distintos** los que cubren los 16 IDs.

## 4. Limitaciones y bloqueos de integración

1. Los 35 PENDIENTE-SIN-SONDA no tienen evidencia causal propia; atribuirlos
   requiere presupuesto de sondas propio (estimado ≈ 155 s a ~4 s/sonda con
   la receta correcta de tests asociados).
2. Las propuestas de oráculo no fueron demostradas por ejecución en este
   incremento (presupuesto agotado por el incidente de §1); su demostración
   (original verde + mutante rechazado) es el primer paso del incremento de
   reparación.
3. La detección de los 4 IDs atribuidos se observó por un consumidor
   extremo a extremo (redteam sobre F9-a), no por los tests focales SAST.
4. Bloqueos de integración de la PR #53, separados y con causas distintas:
   `G-META-1` (drift del manifiesto de rutas protegidas, pre-bless),
   `G-DEPS` (deptry) y `G-DEAD` (vulture). Tres hallazgos distintos: resolver
   el drift con bless NO implica que G-DEPS o G-DEAD pasen; cada uno exige su
   propio diagnóstico. Este incremento no los aborda.

## 5. Custodia

Expediente sucesor: `build/tmp/gs2-adenda.67I6HX/` — sello
`adenda-gs2.sha256` (12 miembros, SHA-256
`a479c18afb26b11bee1a0e50b787506a89594318eebba5a2f3af1b3e561881aa`),
verificación 12/12 fuera de los miembros. El expediente original
`gs2.YfTuE4/` (sello 106/106) no fue modificado. La evidencia bajo
`build/tmp/` es referenciada por hashes; la custodia durable en-repo es este
documento.
