# Registro REANCLAJE-3 — cierre de G-DEAD por disposición individual (2026-09-18)

Estado: **reparación parcial**. Se aplicaron 17 entradas de whitelist
justificadas individualmente y se eliminó `InstanceReport` (código muerto
confirmado). G-DEAD queda con **5 hallazgos de residuo** que requieren
decisión humana expresa (§4/§5): no se forzó el verde. El cambio de
gobernanza es **autorización humana explícita de este encargo** (punto A),
no aprobación del verifier. Base verificada:
`ef9fd12a181237a7181111c27cd81df602c329ca` (= remoto = headRefOid PR #56,
antes y después). Candidato: `build/tmp/reanclaje3-20260918/candidato`
(raíz Git propia; cambios exactamente en 2 rutas autorizadas + este
registro). Expediente antecedente verificado: manifiesto REANCLAJE-2
`857092056e0bf5eaf7b186d371151fa2130c11acc46a8a5ceed12656179940c7` (25/25).

## 1. Reproducción y semántica del detector

- Comando canónico (cwd=candidato, runtime acreditado venv REANCLAJE-1,
  vulture 2.16, Python 3.13.14, exit 3):
  `vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60`
  → **25 hallazgos, idénticos byte a byte** a los del expediente REANCLAJE-2
  (diff vacío). Sin hallazgos nuevos.
- **Semántica demostrada (controles S1–S3, copia desechable con homónimos
  muertos ajenos en `src/example/domain/dead_homonyms_probe.py` y control
  único `zzz_dead_control`)**: las tres formulaciones posibles de entrada —
  nombre suelto (`utc`), cualificada (`ChannelEnd.utc`) y atributo en clase
  (`class ChannelEnd: utc`) — se comportan **idénticamente**: silencian el
  nombre **globalmente** en src+tools (desaparecen ambos hallazgos
  contractuales del nombre Y el homónimo muerto ajeno). **No existe
  formulación acotada en vulture 2.16** sin cambiar detector o política
  (excluidos de este encargo). `--exclude` y bajar confianza: prohibidos.

## 2. Tabla de los 25 hallazgos y disposición final

Categorías de evidencia: [API] función pública con llamadas en tests
(vulture no escanea `tests/`); [WIRE] campo mandatorio del contrato de
payload (PROPUESTA-P03 §3) escrito por el decodificador vía kwargs del
constructor (relación invisible al detector); [LEÍDO] además, leído en
aserciones de tests; [MUERTO] sin consumidores ni contrato; [PESO] escrito
y nunca leído, interno (no contrato).

| # | Ruta:línea | Símbolo | Evidencia | Disposición |
|---|---|---|---|---|
| 1 | accept/mutation_policy.py:23 | `load_policy` | [API] 7 llamadas (typed_operator_steps ×2, test_accept_typed_operator ×5) | **whitelist** |
| 2 | evidence/pytest_observation.py:44 | `decode_pytest_journal` | [API] 102 llamadas en tests R8 | **whitelist** |
| 3 | evidence/pytest_observation.py:207 | `reconcile_pytest` | [API] 79 llamadas en tests R8 | **whitelist** |
| 4 | evidence/pytest_payload_classes.py:54 | `utc` (ExecutionStart) | [WIRE][LEÍDO 2] §3 tabla payload | **rechazada** (genérica; §3-residuo) |
| 5 | evidence/pytest_payload_classes.py:75 | `log_sha256` (ExecutionEnd) | [WIRE] §3 | **whitelist** |
| 6 | evidence/pytest_payload_classes.py:77 | `utc` (ExecutionEnd) | [WIRE] | **rechazada** (genérica) |
| 7 | :85 | `pytest_version` (SessionStart) | [WIRE] §3 claims del emisor | **whitelist** |
| 8 | :86 | `pluggy_version` | [WIRE] | **whitelist** |
| 9 | :87 | `observer_version` | [WIRE] | **whitelist** |
| 10 | :88 | `runtime_profile_sha256` | [WIRE] | **whitelist** |
| 11 | :97 | `distribution` (PluginClaim) | [WIRE] | **rechazada** (genérica) |
| 12 | :99 | `source_sha256` | [WIRE] | **whitelist** |
| 13 | :100 | `qualified` | [WIRE][LEÍDO 1] | **rechazada** (genérica) |
| 14 | :114 | `effective_sha256` (OptionsClaim) | [WIRE] | **whitelist** |
| 15 | :115 | `profile_match` | [WIRE][LEÍDO 1] | **whitelist** |
| 16 | :212 | `argument_exit` (SessionEnd) | [WIRE] conservado para cotejo exit | **whitelist** |
| 17 | evidence/pytest_phases.py:25 | `InstanceReport` | [MUERTO] ver §3 | **eliminado** |
| 18 | :31 | `call_disposition` | campo de la clase muerta (las 7 lecturas corresponden al homólogo de pytest_types.py:123) | **whitelist** |
| 19 | :32 | `pass_eligible` | campo de la clase muerta (las 28 lecturas corresponden al homólogo de pytest_types.py:122) | **whitelist** |
| 20 | evidence/pytest_scan_state.py:47 | `expectation` (_ScanState) | [PESO] escrito (`pytest_observation.py:165`), **cero lecturas**; interno, fuera del contrato de tipos §2 | **residuo** (eliminación no autorizada aquí) |
| 21 | evidence/pytest_types.py:122 | `pass_eligible` | [LEÍDO] §2 | whitelist (ídem 19) |
| 22 | :123 | `call_disposition` | [LEÍDO] | whitelist (ídem 18) |
| 23 | :134 | `deselected_property` | [WIRE] inventario ExecutionObservation §2 | **whitelist** |
| 24 | :138 | `protocol_complete` | [LEÍDO 19] §2 | **whitelist** |
| 25 | :152 | `preflight_identities` | [LEÍDO 2] §2, escrito :246 | **whitelist** |

Correspondencia hallazgos↔entradas (aritmética corregida tras el
dictamen del verifier): de los 25 hallazgos — 23 falsos positivos + 1
muerto (`InstanceReport`) + 1 no-FP (`expectation`, peso interno). Las 17
entradas aplicadas cubrían 19 hallazgos (dos de ellos, phases:31/32, eran
campos de la clase muerta y desaparecen físicamente con ella); tras la
eliminación, silencian 17 de los 22 restantes. Quedan 4 hallazgos FP
rechazados (3 nombres genéricos: `utc`×2, `distribution`, `qualified`) + 1
no-FP (`expectation`). **21 entradas NO eran mínimas ni correctas al
completo**: las 4 genéricas se retiraron de la propuesta de REANCLAJE-2.

## 3. InstanceReport — eliminación (condición §5 satisfecha)

Definición `tools/wct/evidence/pytest_phases.py:25-33` (dataclass frozen).
Comprobaciones: sin `__all__` en el módulo; **cero referencias** en
`tools/`, `tests/`, `src/`, features y JSON (las únicas menciones son los
registros REANCLAJE-2/3); ausente de la tabla de tipos contractuales de
PROPUESTA-P03 §2 (el tipo de instancia contractual es `TestObservation`,
con campos homónimos: leftover de una iteración previa); igual de muerto en
el candidato R8 original; sin usos dinámicos (grep de cadenas/getattr).
**Sin consumidores ni compromiso de API → eliminada solo la clase**; los
imports del módulo (`PhaseObservation`, `ProtocolFinding`,
`TestObservation`) quedan usados por el resto del código (ruff/mypy
limpios). Hash anterior `368443477979ab8f6a6b0202cefee8f7dfe2dfbe4f58fede6ec11e3cc58a64c1`
→ nuevo `ea95730c366a2bdf25cf66aef02325383b059521f346a802ddb9af8c035ce2fa`
(−11 líneas). No se añadieron tests «afirmando la ausencia»: el
comportamiento real no cambió (suite y focales idénticos).

## 4. Whitelist aplicada y residuo

`governance/lint/vulture_whitelist.py`: +17 entradas con `noqa` puntual y
docstring de alcance con la sonda y los controles. Hash anterior
`90e52d7fc135bde01d7c87100eb4a189a3b53b3401edf742edfdeda289f455c0` → nuevo
`8c2f819b3e5431b509cc7bca19cbe44f0693f87ca6b36b5d428e24e5de3ca5fb`.

Controles: **A** ✔ (los 18 hallazgos de las 17 entradas desaparecen);
**B** ✔ (InstanceReport seguía detectándose tras la whitelist y antes de
eliminarlo: corrida intermedia con 6 hallazgos); **C** ✔ (los 5 residuos y
`zzz_dead_control` siguen detectándose); **D** ✔ (demostró silenciamiento
global de homónimos → 3 entradas genéricas NO aplicadas).

**Residuo (5 hallazgos) — decisión humana requerida:**
1. `utc` ×2, `distribution`, `qualified`: campos wire contractuales, pero
   nombres genéricos cuya entrada silenciaría homónimos ajenos futuros en
   todo src+tools (demostrado). Sin formulación acotada. Alternativas: (a)
   aceptar el riesgo y autorizar las 3 entradas; (b) dejar el residuo
   visible; (c) en un incremento de producto, exponer lecturas reales dentro
   de tools/wct (hoy prohibido cambiar P03a).
2. `expectation`: peso muerto interno (escrito, jamás leído; `_ScanState`
   privado). Propuesta mínima: eliminar el campo en un incremento con
   allowlist propia (análoga a InstanceReport).

## 5. Batería del candidato sucesor (runtime íntegro)

Colección 1183, nodeids idénticos; focales R8 **426/426**, operador
**61/61**, AC1+ratchet **252/252**; property 1/1; fast **7/7**; suite
normativa **1181 passed · 0 failed** (178 s); **tier commit 21 = 19 PASS ·
2 FAIL** (G-META-1 + G-DEAD-residuo); G-TEST y G-INTROVERT PASS. **Drift
re-medido: 36 rutas = 2 modificadas** (`governance/lint/vulture_whitelist.py`
—nueva en el conjunto por este encargo— y `tools/wct/accept/mutation_cases.py`)
**+ 34 nuevas**. Presupuesto ≈ 480 s de 1800 s (+ reejecuciones del
verifier).

## 6. Sellos y vigencia sucesora

R8 `93acd1a5…`: **claim de identidad completa ROTO para
`pytest_phases.py`** (hash del manifiesto `368443477979ab8f6a6b0202cefee8f7dfe2dfbe4f58fede6ec11e3cc58a64c1`
—corrección del verifier: `5f538fb5…` era el de
`tests/unit/test_pytest_phases.py`, que sigue verificando— ≠ sucesor
`ea95730c…`); 36/37 rutas siguen verificando. Fase 1 `c23d7273…`: ya
matizado en REANCLAJE-2 por el test O6. REANCLAJE-1 `fe1b7d54…` y
REANCLAJE-2 `85709205…`: intactos y re-verificados. Evidencia que conserva
vigencia: focales R8 (426 — `pytest_phases.py` perdió solo una clase muerta
sin efecto observable), conciliación de nodeids, sellos de procedencia.
Re-medida aquí: toda la batería §5.

## 6bis. Dictamen del verifier independiente (transcripción resumida)

Cuatro niveles: **(A)** disposición de los 17 falsos positivos — APROBADA
tal como está (conteos exactos verificados: 7/102/79 llamadas; kwargs de
builders; §2/§3 de PROPUESTA-P03; 4 formulaciones de entrada probadas, todas
globales); **(B)** eliminación de InstanceReport — CORRECTA Y COMPLETA
(−11 líneas exactas, imports vivos, sin tests cosméticos); **(C)**
publicación del delta en PR #56 en borrador — APROBADA, condicionada a (D);
**(D)** residuos: 5 hallazgos con decisión humana, E9+bless de 36 rutas,
re-anclaje del sello R8 para pytest_phases.py, calificación del scope y
fase 2 separada. Discrepancias D1–D4 (documentales) incorporadas arriba;
D3 era del propio encargo (la expectativa literal del control D con la
whitelist vigente se invierte por diseño: al rechazar las entradas
genéricas, los homónimos muertos utc/qualified SIGUEN visibles —
comportamiento deseado; el contrafactual del verifier demostró el
silenciamiento global).

## 7. Decisiones humanas pendientes

1. Residuo §4 (3 entradas genéricas: aceptar/rechazar/alternativa de
   producto; disposición de `expectation`).
2. E9 + bless del drift —ahora **36 rutas**— antes de merge.
3. Calificación exigible del código incorporado (mutación/aceptación/
   cobertura/CRAP/DRY/full) en encargos propios; fase 2 sigue separada.
