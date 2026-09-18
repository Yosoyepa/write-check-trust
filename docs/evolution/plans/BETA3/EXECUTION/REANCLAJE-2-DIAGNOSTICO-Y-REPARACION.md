# Registro REANCLAJE-2 — diagnóstico y reparación acotada de los rojos técnicos de PR #56 (2026-09-18)

Estado: **reparación parcial**. La suite normativa queda verde y el tier
commit queda con G-META-1 (drift protegido declarado) y **G-DEAD** como
únicos rojos; G-DEAD requiere autorización humana de whitelist (§3) y no se
tocó gobernanza. Sin bless, update-manifest, alza de baselines, supresiones
ni exclusión de tests. Base autorizada:
`7dd6ee634497dfa3ff3866dce8909ef83892236f` (verificada contra remoto y
headRefOid de PR #56 antes de trabajar; sin avance). Candidato sucesor:
copia aislada con raíz Git propia
`build/tmp/reanclaje2-20260918/candidato`, cuyo único cambio es el archivo
de §2. Antecedentes: registro REANCLAJE-1, expediente
`build/tmp/reanclaje1-20260918-exp/` (manifiesto
`fe1b7d540c6f05eed2e6ceea4a5a9b30b7da7ba3e033cb465ed348d3ecffa00c`,
re-verificado 19/19 al iniciar).

## 1. Inventario obligatorio de los cuatro rojos

Reproducidos causalmente con runtime acreditado (venv exclusivo del worktree
REANCLAJE-1, grupo quality completo) en la copia aislada; logs
`build/tmp/reanclaje2-20260918/logs/`.

| Gate | Comando (receta del gate) | Exit | Diagnóstico | Causa inmediata → raíz | Relación | ¿En main 8a379d6? |
|---|---|---:|---|---|---|---|
| G-TEST | `pytest -q tests/unit tests/integration -m "not property"` | 1 | `1 failed, 1180 passed`; nodeid fallido `tests/unit/test_ratchet_check.py::test_repo_introverted_ratchet_holds_baseline` | `introverted-tests: actual=1, baseline=0` → el test sellado O6 (`test_policy_and_operator_import_no_tests_or_evidence_modules`) no trazaba sus aserciones al SUT (AST puro sobre archivos) y el analizador lo clasificaba «introverted» | Misma causa raíz que G-INTROVERT | NO: en main el ratchet pasa (baseline 0); la regresión la introdujo la incorporación REANCLAJE-1 |
| G-INTROVERT | analizador `tools/wct/introvert/analyzer.py` vía gate | FAIL | 1 test «las aserciones no trazan al SUT»: `tests/unit/test_accept_typed_operator.py:430` | Ídem | Eco de G-TEST | NO: main tiene 0 introverted |
| G-DEAD | `vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60` | 3 | **25 hallazgos reales** (la tabla del CLI muestra solo el primero en el summary; lista completa en `r3-dead-gate-real.log`): 24 falsos positivos sobre la superficie R8/operador + 1 código realmente muerto | vulture no escanea `tests/` (consumidores del API pública y de los campos de dataclass del wire); `InstanceReport` no tiene referencia alguna | Independiente del ratchet | NO: main pasa G-DEAD (la whitelist vigente cubre la superficie AC1; la R8 no estaba) |
| G-META-1 | `wct integrity check` | 1 | Drift de 35 rutas protegidas (1 modificada + 34 nuevas) | Incorporaciones autorizadas de REANCLAJE-1, pendientes de E9+bless | Independiente | NO: main pasa (lock bendecido) |

Los 4 fallos del primer run de REANCLAJE-1 (secrets/sast con venv sin grupo
quality) fueron **ambientales**, no de producto: idénticos en base con el
mismo runtime, resueltos con el entorno íntegro. No se cuentan como rojos.

## 2. Reparación O6 (autorizada condicionalmente)

- Ruta: `tests/unit/test_accept_typed_operator.py`; nodeid conservado:
  `test_policy_and_operator_import_no_tests_or_evidence_modules`.
- Hash anterior (sello de fase 1 c23d7273):
  `44ba05971fefe7fddc53dcf732a7d17fc5cb8a72e66adfbce03c42b1969130f0`.
  Hash nuevo del candidato sucesor:
  `655c78fad6bfd22bfc7c2068bbe5dee8a6dcef1bd7e4cfddfc45e0a50316afd1`.
  Diff: `+39/−5` (expediente `o6-reparacion.diff`).
- Diseño: se conserva íntegra la inspección AST contractual y se añade un
  **oráculo sobre el resultado observable del SUT**: los módulos del motor,
  identificados desde sus funciones públicas ya cargadas
  (`load_policy`, `validate_policy`, `mutations` → `sys.modules[…].__module__`),
  no exponen en su espacio de nombres ningún objeto originado en `tests.*` o
  `tools.wct.evidence.*` (helper privado `_foreign_engine_imports`, en el
  mismo archivo). Sin mocks, sin estados fabricados, sin llamadas
  decorativas: la aserción deriva del estado real cargado del SUT.
- Analizador: veredicto **extroverted — «la aserción traza a un valor del
  SUT»**; conteo global introverted: **0**.

### Demostraciones exigidas

- **A (fidelidad y estados realizables)**: el comportamiento contractual O6
  (VERIFICACION.md: «motor sin imports tests/evidence por inspección AST») se
  conserva y se refuerza con su manifestación runtime; los módulos ya están
  cargados al importar el propio archivo de tests (estado real, no
  construido). Ambos oráculos son necesarios (ver C).
- **B (original verde)**: `1 passed in 0.19s` (`o6-b-verde.log`); ruff
  format/check limpios.
- **C (sensibilidad por perturbación puntual en copia desechable)**:
  - C1 — implementación plausiblemente incorrecta: import de
    `tools.wct.evidence.pytest_types` añadido al inicio de
    `mutation_cases.py` → **FAILED en la aserción runtime (línea 465)**,
    `1 failed in 0.24s` (`o6-c1-sensibilidad.log`). Variante previa con
    `tests.acceptance.steps` rompió por import circular durante la
    colección — también detección, descartada como demostración por no ser
    fallo limpio de la aserción; se conservó el intento.
  - C2 — import diferido dentro de función de `mutation_policy.py`
    (nunca ejecutado al importar): la sonda runtime no lo ve; **la aserción
    AST (línea 479) lo rechaza**, `1 failed in 0.21s`
    (`o6-c2-sensibilidad.log`). Prueba que la pata AST no es decorativa.

## 3. G-DEAD / preflight_identities — diagnóstico, sonda y propuesta (NO aplicada)

- Símbolo paradigmático: `preflight_identities`,
  `tools/wct/evidence/pytest_types.py:152` — campo del dataclass
  `PytestObservation`. **Invocación real, no solo documental**: lo escribe
  `pytest_observation.py:246` (`preflight_identities=preflight`) y lo leen
  tres tests (`test_pytest_phases.py:174`, `test_pytest_schema.py:191`,
  `test_pytest_observation.py:2766`). Es API pública contractual del
  resultado de `reconcile_pytest` (PROPUESTA-P03 §2/§7). Vulture no rastrea
  el kwargs del constructor ni el acceso desde tests (fuera de su scope de
  escaneo `src tools/wct`). **Falso positivo confirmado.**
- El hallazgo no está aislado: la superficie incorporada produce **24 falsos
  positivos** análogos (3 funciones públicas del API — `load_policy`,
  `decode_pytest_journal`, `reconcile_pytest` — consumidas por
  tests/acceptance; 21 nombres de campos de dataclasses del contrato de
  wire, escritos por el decodificador) y **1 código realmente muerto**:
  `class InstanceReport` (`pytest_phases.py:25-26`), sin referencia alguna
  en `tools/` ni `tests/` (grep exhaustivo). No corresponde a despacho
  dinámico ni a integración pendiente: es residuo de una iteración previa
  del contrato de fases (R8 sellado lo conserva).
- **Sonda experimental (ADR-D-02: ampliar exige sonda que mida)**:
  whitelist experimental FUERA de governance
  (`build/tmp/reanclaje2-20260918/vulture-whitelist-experimental.py` =
  vigente + 21 nombres) pasada explícitamente al comando:
  hallazgos **25 → 1**, y el restante es exactamente `InstanceReport`
  (control negativo: el verdadero positivo NO queda oculto).
- **Diff propuesto para aprobación humana (texto; NO aplicado al candidato
  ni publicado como configuración vigente)** — añadir a
  `governance/lint/vulture_whitelist.py` las entradas
  `load_policy, decode_pytest_journal, reconcile_pytest, utc, log_sha256,
  pytest_version, pluggy_version, observer_version, runtime_profile_sha256,
  distribution, source_sha256, qualified, effective_sha256, profile_match,
  argument_exit, call_disposition, pass_eligible, expectation,
  deselected_property, protocol_complete, preflight_identities` con esta
  justificación y la referencia a esta sonda. Reserva declarada: los nombres
  de la whitelist de vulture son globales (no por archivo); entradas genéricas
  (`utc`, `expectation`, `qualified`) podrían enmascarar futuros verdaderos
  positivos homónimos en `src/tools` — decisión humana.
- **InstanceReport**: NO se propone whitelist (ocultaría código muerto
  real). Propuesta mínima para un incremento futuro con allowlist propio:
  eliminar la clase de `pytest_phases.py` (bytes sellados R8 → exige
  re-sello/tratamiento de sucesor y re-verificación de la suite R8).

## 4. Sellos y vigencia del candidato sucesor

- Sellos intactos y re-verificados: R8 `93acd1a5…` 37/37; fase 1
  `c23d7273…` — **exactitud matizada**: el manifiesto sigue describiendo los
  bytes históricos; el archivo `tests/unit/test_accept_typed_operator.py`
  del candidato sucesor YA NO coincide con su entrada
  (`44ba0597…` → `655c78fa…`, §2). No se afirma identidad completa con el
  sello de fase 1 para ese archivo; la procedencia histórica se conserva
  separada (bytes originales en el candidato histórico y en el manifiesto
  sellado).
- Evidencia que conserva vigencia por identidad: todo lo que no depende del
  test O6 — focales R8 (426), colección/nodeids (idénticos), conciliación
  1183, drift 35, sellos de procedencia.
- Evidencia re-medida en este registro: focal del operador (61), ratchet,
  analizador, suite normativa completa, property, fast, tier commit
  (batería §5).
- REANCLAJE-1: expediente sellado intacto (`fe1b7d54…`, 19/19).

## 5. Batería del candidato sucesor (runtime íntegro acreditado)

| # | Comprobación | Resultado |
|---|---|---|
| 1 | Colección + conciliación nodeids vs 7dd6ee6 | 1183; **nodeids idénticos** (diff vacío) |
| 2 | Focal operador completo | **61 passed** |
| 3 | Consumidores AC1 + ratchet (6 archivos) | **252 passed** |
| 4 | Property separada | 1 passed |
| 5 | fast | **7 PASS · 0 FAIL, exit 0** |
| 6 | Suite normativa completa | **1181 passed · 0 failed, exit 0** (125 s) |
| 7 | tier commit | **21 gates: 19 PASS · 2 FAIL** — G-META-1 (drift declarado) y G-DEAD (pendiente de autorización); G-TEST y G-INTROVERT **PASS** |
| 8 | Drift recalculado | 35 rutas (1 modificada + 34 nuevas), sin cambios vs REANCLAJE-1 |

**REPARACIÓN PARCIAL — pendiente de autorización** (G-DEAD): la condición
del objetivo «G-META-1 como único rojo» no queda alcanzada dentro de las
autorizaciones de este encargo; se declara en lugar de editar gobernanza.

## 6. Presupuesto

~290 s de 1800 s agregados de ejecución (reproducción causal, reparación,
demos C1/C2, sonda, batería; se incluyen los intentos descartados: sonda C1
con import circular y dos invociones de shell fallidas por cwd eliminado —
incidente instrumental registrado, shell restaurado recreando el directorio;
sin efecto sobre árboles de trabajo). Reejecuciones del verifier aparte,
dentro del mismo presupuesto.

## 7. Decisiones humanas requeridas

1. Aprobar (o rechazar) el diff de whitelist de §3 — habilitaría G-DEAD
   verde salvo `InstanceReport`.
2. Disposición de `InstanceReport` (eliminación con allowlist y tratamiento
   de sucesor del sello R8, o excepción documentada).
3. Las ya pendientes de REANCLAJE-1: E9+bless del drift, pausa de fase 2,
   merge de #56.
