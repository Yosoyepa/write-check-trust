# GS-2 — revalidación de atribución y preparación del cierre beta.3 (2026-09-15)

Documento de coordinación. Sucede a
`GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15.md` (que permanece intacta) y
consolida tres frentes ejecutados en copias aisladas bajo
`build/tmp/gs2-coord.vdQDdj/` — A: revalidación de mutantes GS-2; B:
diagnóstico G-DEPS/G-DEAD; C: preparación de GS-3 y camino de cierre — más una
verificación independiente de solo lectura. **No ejecuta GS-3, no repara
gates de producto y no declara PASS de G-MUT, AC1 ni beta.3**; la PR #53
permanece en borrador.

## 0. Base, corte y custodia

- Worktree de integración `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`, corte congelado
  `bdb7db31e3ad5e68adb01fc2b62364fab5858db0` (local == remoto al congelar).
  PR #53: OPEN, borrador, `mergeStateStatus: BLOCKED`, `commit-gates: FAILURE`.
- Trabajo ajeno preservado sin stagear:
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` (untracked; incidente
  ya registrado en la matriz).
- Expedientes históricos reverificados hoy sin modificar: `gs2.YfTuE4`
  (106/106), `gs2-adenda.67I6HX` (12/12), `gs2-cierre.nDW4ha` (129/129),
  `gs2-diac.yuISyH` (20/20).
- Runtime de sondas: `build/tmp/sh-p01-CND-80B8/.venv` (Python 3.13.14,
  mutmut 3.7.0, pytest 9.1.1, semgrep 1.174.0). Runtime de gates: venv de
  integración (ruff, mypy, deptry 0.25.1, vulture 2.16).
- **Custodia**: la evidencia bajo `build/tmp/` es local y temporal; la custodia
  durable de estas conclusiones son este registro y sus dos anexos. La tabla
  completa de 118 IDs actualizada (sha256 `8cc6f1d6…`) y el detalle por ID de
  las sondas (`A4-detalle-34.tsv`, sha256 `295bc575…`) viven en el expediente
  local; el delta durable es la tabla de §1.3 y la reconciliación de §1.5.

## 1. GS-2 — revalidación de la atribución pendiente (frente A)

### 1.1 Qué se ejecutó

- Inventario abierto derivado por conjuntos (no asumido):
  `ids-35-pendientes.txt` (35) − {`x__unique_dirs__mutmut_7`} = **34 IDs**
  (3 `x__unique_dirs` con 13 tests/ID; 7 `x_relative_path` con 31;
  24 `x_required_sources` con 14).
- 34 sondas mutante frescas + 3 controles originales (2 frescos y el sellado de
  u7 para la selección de 13 tests, con identidad de selección documentada) +
  canario fresco original/mutante + 7 controles negativos fail-closed sin
  pytest. Sondas seriales; sin `mutmut run`; sin regenerar el inventario; sin
  reabrir los 16 oráculos, los 63 históricos ni los 4 de la adenda; u7 no se
  reejecutó (promoción documental).
- **Scripts efectivos y metadatos de activación** (hashes idénticos al CORTE):
  `sonda-succ.sh` sha256 `042c0cb4897027bba84178a315e6949aee04fa3e455c2221d223b6cb739b66c8`;
  `instrumento.py` sha256 `6bbecee201bfc794e2855fc2c792280d428d65857e0a0172f01a290d424adda1`;
  `associations.txt` sha256 `e4ab74bd738b451df0d3ee14db65b2593a5cde7abac92e31885aba875880a877`;
  fuente mutada sha256 `1ccdf8d6794bd0e1bfbfe7b5b1ff99cbd9d5447430fcdb8a12cf32cceb894faa`;
  tests de la sonda sha256 `8b0f71e375c7581fab06287f3eb9a25082ca760074862bab4cee03778b0ed2fe`.
- La reserva de la receta queda resuelta: `sonda.sh` de la adenda
  (sha256 `e78c7555…`) conserva su `local` fuera de función como defecto latente
  **sin modificar**, y la receta efectiva (`sonda-succ.sh`) no usa `local` a
  nivel superior; `bash -n` OK.

### 1.2 Controles

- **Canario fresco** `x__build_dirs__mutmut_1`: original exit 0 (`11 passed`);
  mutante activado exit 1 (`AssertionError: ERROR vs FAIL`, causa histórica).
- **7/7 negativos fail-closed sin pytest**: asociaciones ausentes/vacías (exit 2),
  selección vacía (exit 4), nodeid fuera de colección (exit 5), ID sin prefijo
  (exit 1), ID ajeno al inventario (exit 3), modo inválido (exit 1). Sin
  log/meta de sonda.
- **Activación in-process**: 34/34 metas de los IDs abiertos con
  `selftest-esperado == selftest-leido == ID completo`; en todos los logs,
  `INST-SONDA` con `mutant_under_test`, `fuente` dentro de la copia y
  `variante_en_tabla`. El eco del shell o el exit code no se usan como
  acreditación.

### 1.3 Resultado de los 34 IDs abiertos

34/34: exit mutante 1, activación acreditada, fase **call**, causa atribuida al
mutante (diff de la función explicado contra el consumidor y control original
verde). **0 discrepancias, 0 timeouts, 0 bloqueos durante las sondas.** Tests
que matan: 25 × `test_binding_fixture_adversarial_raiz_propia`, 5 ×
`test_binding_ejecuta_la_matriz_del_gherkin`, 2 ×
`test_matriz_literal[ruta-con-escape]`, 1 × `test_binding_fuente_ignorada`,
1 × `test_build_anidado_respeta_el_limite_de_directorio`.

| ID | selección | control original | exit | test que mata | causa | dur (s) |
|---|---|---|---|---|---|---|
| `x__unique_dirs__mutmut_6` | 13 tests | sellado-diac: exit 0 (13 passed in 8.97s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__relative__mutmut_orig() missing 1 required positional argument: 'raw' | 1.678 |
| `x__unique_dirs__mutmut_8` | 13 tests | sellado-diac: exit 0 (13 passed in 8.97s) | 1 | test_binding_fixture_adversarial_raiz_propia | assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | 1.873 |
| `x__unique_dirs__mutmut_9` | 13 tests | sellado-diac: exit 0 (13 passed in 8.97s) | 1 | test_binding_fixture_adversarial_raiz_propia | assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | 1.581 |
| `x_relative_path__mutmut_1` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_binding_ejecuta_la_matriz_del_gherkin | AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | 1.565 |
| `x_relative_path__mutmut_2` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_binding_ejecuta_la_matriz_del_gherkin | AttributeError: 'NoneType' object has no attribute 'parts' | 1.811 |
| `x_relative_path__mutmut_3` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_binding_ejecuta_la_matriz_del_gherkin | TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | 1.733 |
| `x_relative_path__mutmut_4` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_matriz_literal[ruta-con-escape] | AssertionError: assert False | 6.701 |
| `x_relative_path__mutmut_6` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_binding_ejecuta_la_matriz_del_gherkin | AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | 1.898 |
| `x_relative_path__mutmut_7` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_matriz_literal[ruta-con-escape] | AssertionError: assert False | 6.121 |
| `x_relative_path__mutmut_8` | 31 tests | fresco: exit 0 (31 passed in 8.19s) | 1 | test_binding_ejecuta_la_matriz_del_gherkin | AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | 1.857 |
| `x_required_sources__mutmut_1` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: unsupported operand type(s) for /: 'NoneType' and 'PosixPath' | 1.896 |
| `x_required_sources__mutmut_10` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not subscriptable | 1.748 |
| `x_required_sources__mutmut_11` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__build_dirs__mutmut_orig() missing 1 required positional argument: 'policy' | 1.502 |
| `x_required_sources__mutmut_12` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__build_dirs__mutmut_orig() missing 1 required positional argument: 'policy' | 1.468 |
| `x_required_sources__mutmut_13` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | AttributeError: 'NoneType' object has no attribute 'update' | 1.608 |
| `x_required_sources__mutmut_14` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | AttributeError: 'NoneType' object has no attribute 'is_dir' | 1.806 |
| `x_required_sources__mutmut_15` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: can't multiply sequence by non-int of type 'PosixPath' | 1.812 |
| `x_required_sources__mutmut_16` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fuente_ignorada | AssertionError: assert <Status.PASS: 'PASS'> is <Status.ERROR: 'ERROR'> | 5.269 |
| `x_required_sources__mutmut_18` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not iterable | 1.458 |
| `x_required_sources__mutmut_19` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | 1.597 |
| `x_required_sources__mutmut_2` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not iterable | 1.611 |
| `x_required_sources__mutmut_20` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | AttributeError: 'NoneType' object has no attribute 'rglob' | 1.689 |
| `x_required_sources__mutmut_21` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not iterable | 1.461 |
| `x_required_sources__mutmut_22` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__python_files__mutmut_orig() missing 1 required positional argument: 'builds' | 1.465 |
| `x_required_sources__mutmut_23` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__python_files__mutmut_orig() missing 1 required positional argument: 'builds' | 1.590 |
| `x_required_sources__mutmut_24` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__python_files__mutmut_orig() missing 1 required positional argument: 'builds' | 1.380 |
| `x_required_sources__mutmut_25` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not iterable | 1.578 |
| `x_required_sources__mutmut_3` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: unsupported operand type(s) for /: 'NoneType' and 'PosixPath' | 1.540 |
| `x_required_sources__mutmut_4` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not iterable | 1.415 |
| `x_required_sources__mutmut_5` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__unique_dirs__mutmut_orig() missing 1 required positional argument: 'declared' | 1.528 |
| `x_required_sources__mutmut_6` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: x__unique_dirs__mutmut_orig() missing 1 required positional argument: 'declared' | 1.343 |
| `x_required_sources__mutmut_7` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | AttributeError: 'NoneType' object has no attribute 'get' | 1.415 |
| `x_required_sources__mutmut_8` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_binding_fixture_adversarial_raiz_propia | TypeError: 'NoneType' object is not iterable | 1.387 |
| `x_required_sources__mutmut_9` | 14 tests | fresco: exit 0 (14 passed in 8.82s) | 1 | test_build_anidado_respeta_el_limite_de_directorio | TypeError: unsupported operand type(s) for /: 'NoneType' and 'PosixPath' | 5.022 |

Los `TypeError` de despacho (p. ej. u6 `_relative(root, )`) están provocados por
llamadas mal formadas escritas en el cuerpo del propio mutante; el frame del
trampolín es el paso a `orig_func` (H2 ya retirado como artefacto).

### 1.4 Promoción de `x__unique_dirs__mutmut_7`

Evaluado contra el criterio causal y promovido **con la evidencia sellada** de
la comparación mínima anterior (no reejecutado): selección de 13 tests idéntica
a la vigente de `x__unique_dirs` (contra `associations.txt`, colección y meta
sellado); original exit 0 (`13 passed in 8.97s`); mutante activado exit 1 con
`TypeError: unsupported operand type(s) for /: 'PosixPath' and 'NoneType'` en
fase call (`semgrep_scope.py:1769`), causa `setdefault(None, raw)` (línea 706);
`INST-SONDA` con `variante_en_tabla`. Veredicto:
**KILLED-EVIDENCIADO-SUCESOR**.

### 1.5 Reconciliación de los 118 IDs

- Composición histórica: 63 KILLED-EVIDENCIADO-HISTÓRICO + 4
  KILLED-EVIDENCIADO-ADENDA + 34 EVIDENCIA-DE-SONDA-INSUFICIENTE (incluye u7)
  + 1 PENDIENTE-DE-REVALIDACIÓN (u6) + 16 SURVIVED-HISTÓRICO = **118**.
- Composición final: 63 + 4 + **35 KILLED-EVIDENCIADO-SUCESOR** + 16 = **118**.
  Los 35 sucesores = 33 ex-`EVIDENCIA-DE-SONDA-INSUFICIENTE` revalidados con
  sonda fresca + u6 con sonda fresca + u7 promovido por evidencia sellada.
- Los 16 supervivientes conservan `SURVIVED-HISTÓRICO`: su rechazo 16/16 por las
  regresiones de `ddb1b46` es evidencia de sensibilidad de tests, no una
  re-medición de la campaña GS-2.
- La tabla completa de 118 IDs con estado histórico, evidencia sucesora y
  estado final está en el expediente local (`clasificacion-reval-A.tsv` sha256
  `91b5e14d…`; `tabla-118-actualizada.md` sha256 `8cc6f1d6…`); el delta durable
  es esta sección y la tabla de §1.3.

### 1.6 Presupuesto

- A: **101.111 s de 600 s** (38 ejecuciones de pytest: 34 mutantes + canario
  original/mutante + 2 originales frescos; 7 controles negativos sin pytest;
  0 reintentos).
- Verificación independiente: **+1.219 s** de reejecución de 1 sonda (u6),
  con cargo al mismo presupuesto → **102.330 s de 600 s (17.1 %)**.
- B: 3164 ms de 300 s. C: documental, sin ejecución. Coordinación/gates: aparte.

### 1.7 Verificación independiente

Dictamen **APROBAR-EXPEDIENTE CON RESERVAS (D-1 a D-4), ninguna bloqueante**
— no equivale a APROBAR-GATE. Reejecutó la sonda de u6 en copia propia: exit 1,
misma causa/clase/fase que A, activación bajo su copia; reejecutó deptry y
vulture byte-idénticos; confirmó sello 176/176 sin autocontención, aritmética
118, controles 7/7, original `gs2-diac` 20/20 intacto, clon de B limpio y
fidelidad de C al corte. Reservas: (D-1) rotulación u6/u7 en un resumen de
INFORME-A y (D-2) cita de hash obsoleta de `A4-detalle-34.tsv`
(real `295bc575…`) — ambas corregidas en este registro y sin efecto sobre
evidencia ni sellos; (D-3) `camino-cierre` de C es snapshot previo al cierre de
A — reconciliado en §4; (D-4) la cita de presupuesto de sondas GS-3 era
estimación propia — etiquetada así en el anexo.

### 1.8 Qué queda concluido y qué no

- **Concluido**: la atribución pendiente de GS-2 queda resuelta y, bajo la
  evidencia sucesiva, no quedan residuos abiertos: inventario completo
  reconciliado, 102 detecciones (63 + 4 + 35) con evidencia y 16 regresiones
  demostradas, con verificación independiente favorable.
- **No concluido**: no se ejecutó una campaña completa ni `mutmut run`; no hay
  PASS de G-MUT ni re-calificación global del lote GS-2 (decisión humana); no
  se reabrieron los 63 históricos ni los 4 de la adenda; los 16 siguen
  supervivientes; AC1 y beta.3 no quedan acreditados.

## 2. Fallos preexistentes G-DEPS y G-DEAD (frente B)

Solo diagnóstico, sin reparar. Detalle completo en
`ANEXO-GDEPS-GDEAD-DIAGNOSTICO-2026-09-15.md`.

- **G-DEPS**: `deptry src tools --known-first-party example --known-first-party tools`
  → **exit 1**; 1 hallazgo, **defecto real de declaración**:
  `tools/wct/accept/pytest_receipt.py:11` importa `pytest` y solo está declarado
  como dev (el módulo se empaqueta y se carga por reflexión). Reparación mínima
  propuesta: `[project.optional-dependencies] accept = ["pytest>=8.3"]` +
  `uv lock` (sonda → exit 0). **Requiere autorización humana** (SEC-005:
  `pyproject.toml`/`uv.lock` protegidos).
- **G-DEAD**: `vulture src tools/wct governance/lint/vulture_whitelist.py
  --min-confidence 60` → **exit 3**; 7 hallazgos, todos **falsos positivos
  sustentados**: 6 hooks pluggy en `pytest_receipt.py` (28/37/42/46/82/103,
  invocados por reflexión) y `BinaryIO` en `process.py:10` (literal en
  `cast("BinaryIO", …)`, líneas 38-39). Reparación mínima: 6 entradas canónicas
  en `governance/lint/vulture_whitelist.py` (ADR-D-02, sonda provista) y, para
  `BinaryIO`, descomillar los dos `cast` (sin allowlist). **Requiere
  autorización humana**; aplicar la whitelist no cierra G-META-1 (E9).
- Preexistencia verificada: `git diff c6be7ee bdb7db3` sobre las 5 rutas
  implicadas está vacío. Presupuesto: 3164 ms de 300 s (17 comandos).

## 3. GS-3 — preparación, no ejecutada (frente C)

Prompt propuesto íntegro y autosuficiente en
`ANEXO-PREPARACION-GS3-2026-09-15.md` (sha256 `69fff5cb…`, mismo texto
verificado por el verifier). Resumen:

- **Alcance confirmado**: `tools/wct/gate/semgrep.py`, sha256
  `0126c4e1bdad3a445a3d3821b46cdd75d1ebec6e2d080ab299fd8d2ebd682657` en el
  corte (idéntico a `fb7f725`), 96 líneas, 3 funciones sin decorar, 51 sitios
  WCT (17 + 13 + 6 + 15), tests focales con guard de `semgrep`, procesos
  `git`/`semgrep`. Archivo nuevo: TEST-007 no le aplica.
- **Precondiciones**: autorización humana + dictamen independiente previo
  (PROC-005); decisión sobre GS-2 (E4); runtime `sh-p01-CND-80B8` con PATH al
  `bin` (semgrep 1.174.0 no está en el PATH por defecto); clon aislado con
  hashes congelados; baseline con 0 skips; receta fail-closed con activación
  acreditada dentro del proceso real.
- **Receta y controles**: fases P0–P12 (gen-only con firma admisible, snapshot
  de stats antes de leer, sin `print-time-estimates`, campaña serial con IDs
  explícitos, sellado como última escritura) y controles C0–C2 + negativos
  N1–N3 (incluido el patrón defectuoso `sonda-fc.sh:67-69` como negativo).
- **Presupuesto (estimación sujeta a autorización)**: bloque A
  generación+calibración+campaña ≤ 3600 s (tope de lote de
  `PREPARACION-LOTE-GATE-SELFTEST` §6; calibración obligatoria a 10 IDs);
  bloque B sondas ≤ 1800 s (estimación propia, ≈10–20 s/sonda; timeout 120 s);
  verificación independiente aparte.
- **Paradas**: skips, inventario vacío, falta de asociación, activación no
  acreditada, supervivientes (`FAIL-survivors-stop`), timeouts/ERROR-INTERNO,
  presupuesto agotado, drift de hashes y GS-2 sin decisión.
- **Estado**: plan **listo**; ejecución **bloqueada** por autorización humana,
  decisión sobre E4 y los pendientes D-A/D-C. No hay bloqueo técnico del módulo.

## 4. Camino de cierre hasta beta.3 (frente C, reconciliado)

Cierre AC1 ≠ cierre integral beta.3 (`PLAN.md` §1/§2/§4/§5;
`PREPARACION-SALIDA-INCREMENTAL…` §2/§8). Estados: cerrado con evidencia /
pendiente / bloqueado / no iniciado.

| # | Tramo | Estado tras este incremento | Fuente |
|---|---|---|---|
| 1 | GS-2 (`semgrep_scope.py`) | **Atribución pendiente resuelta** (§1; sin PASS de lote/AC1) | Matriz E4; este registro; `GS2-DIAGNOSTICO…` §9 |
| 2 | GS-3 (`semgrep.py`) | Plan listo (anexo); **ejecución pendiente/bloqueada** por autorización + D-A/D-C | Matriz E5; anexo GS-3 |
| 3 | Residuos r3 y hooks (`§A–D`) y destino de los 928 (E1/E2) | Pendiente de decisión humana | Matriz §A–D, E1, E2; `RESULTADO-AC1-LOTE-R3…` |
| 4 | REGISTRY (E6) y TEST-007 (E7) | Pendiente | Matriz E6/E7; `ADENDA-PREPARACION…` §5 |
| 5 | Aceptación y puertas posteriores (E8) | No iniciado | Matriz E8; `DECISION-INTEGRACION…` §6/§7.4 |
| 6 | G-META-1/G-DEPS/G-DEAD | Diagnóstico G-DEPS/G-DEAD hecho (anexo); reparación pendiente de autorización; G-META-1 (E9) pendiente de revisión humana | `CIERRE-GS1…` §1/§4.4; `GS2-CIERRE…` §4; anexo |
| 7 | Calificación pre-merge (D1) | Pendiente (checkout aislado del SHA candidato) | `PREPARACION-SALIDA…` §2.2/§8; `PLAN.md` §4 |
| 8 | Bless humano y drift de integridad (E9) | Bloqueado hasta revisión humana; la PR #53 sigue `commit-gates: FAILURE` | Matriz E9; `DECISION-D1.md` |
| 9 | CI, merge y post-merge (E11) | Bloqueado hoy (borrador, `BLOCKED`, CI en rojo) | Matriz E11; PR #53 |
| 10 | Versión, custodia, SBOM, smokes y prerelease (E10/D3) | Pendiente; beta.3 integral exige `PLAN.md` §5 | Matriz E10; `PREPARACION-SALIDA…` §5–§8; `RELEASES.md` |

Orden crítico: (1) decisión humana sobre GS-2/E4 → (2) autorizar y ejecutar
GS-3 → (3) residuos r3/hooks y 928 → (4) REGISTRY/TEST-007 → (5) aceptación y
E8 → (6) reparar G-DEPS/G-DEAD y revisar G-META-1 → (7) pre-merge → bless → CI
verde → merge → post-merge → (8) versión/custodia/SBOM/smokes/D3/prerelease.

## 5. Decisiones humanas necesarias

1. **GS-2/E4**: aceptar la revalidación como atribución resuelta y decidir si
   el lote GS-2 puede re-calificarse como PASS o permanece NO PASS (no hubo
   `mutmut run` ni campaña completa en este incremento).
2. **G-DEPS**: autorizar la reparación en `pyproject.toml` +
   `[project.optional-dependencies] accept` + `uv lock` (SEC-005).
3. **G-DEAD**: autorizar la ampliación de `governance/lint/vulture_whitelist.py`
   (ADR-D-02) y, opcionalmente, el descomillado de los `cast` en `process.py`;
   secuenciar con la revisión de G-META-1/E9.
4. **G-META-1/E9**: revisión humana del drift de las 20 rutas protegidas
   pre-bless.
5. **GS-3**: autorizar (o corregir) la ejecución con el prompt del anexo.
6. **D-A/D-C** (matriz §A–D), destino de los 928 (E2), REGISTRY (E6),
   TEST-007 (E7) y diseño de aceptación (E8).
7. Nada de este incremento habilita bless, merge, bump, tag ni release.

## 6. Publicación y preservación

- Entregables temporales (local-only, con hashes de custodia):
  `subA/INFORME-A.md` `b33b6d82…`, `subB/INFORME-B.md` `92558e6e…`,
  `subC/INFORME-C.md` `014cee8d…`, `subC/camino-cierre.md` `911f7ccc…`,
  `subV/INFORME-V.md` `407c6bcf…`, `subA/reval-A.sha256` `8c1f15d3…`
  (176/176).
- Durable: este registro y los anexos
  `ANEXO-GDEPS-GDEAD-DIAGNOSTICO-2026-09-15.md`,
  `ANEXO-PREPARACION-GS3-2026-09-15.md`; filas E4 y E5 de la matriz.
- No se copian expedientes ajenos ni se publican materiales sin verificación.
