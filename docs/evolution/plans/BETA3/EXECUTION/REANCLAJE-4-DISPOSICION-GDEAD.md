# Registro REANCLAJE-4 — auditoría de alcance de la whitelist y disposición documental de los residuos de G-DEAD (2026-09-18)

Estado: **auditoría documental**. Sin cambios de producto, tests, whitelist,
configuración ni gobernanza. Base verificada:
`a6210a6be6f8682a499c8423f45f986082c9a96f` (= remoto = headRefOid PR #56;
main `8a379d6…` y tag `v1.0.0b3.dev1` intactos). Expediente R3 verificado
antes de usar su evidencia (manifiesto 19/19, digest
`244c358ffd44a9c79de149bab4aa25ef1644423589bbc896e3fd7afeafdb8f53`).
Copia aislada: `build/tmp/reanclaje4-20260918/candidato`.

## 1. Estado real reproducido

Receta canónica (cwd=candidato, vulture 2.16, Python 3.13.14, exit 3):
`vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60`
→ **5 hallazgos sobre 4 nombres, idénticos byte a byte** a R3 (diff vacío):

| Ruta:línea | Símbolo | Categoría detector | Confianza |
|---|---|---|---|
| evidence/pytest_payload_classes.py:54 | `utc` (ExecutionStart) | unused variable | 60 % |
| evidence/pytest_payload_classes.py:77 | `utc` (ExecutionEnd) | unused variable | 60 % |
| evidence/pytest_payload_classes.py:97 | `distribution` (PluginClaim) | unused variable | 60 % |
| evidence/pytest_payload_classes.py:100 | `qualified` (PluginClaim) | unused variable | 60 % |
| evidence/pytest_scan_state.py:47 | `expectation` (_ScanState) | unused variable | 60 % |

Reconciliada la partida esperada: 17 entradas aplicadas en R3
(`356a995`), `InstanceReport` eliminado (`e75f96e`), residuo de 5.

## 2. Auditoría de las 17 entradas aplicadas

**Homónimos actuales (medido, grep en src/ y tools/ fuera de la superficie
R8/operador): 0 en src y 0 en tools para las 17.** (Precisión del verifier:
`source_sha256` sí ocurre en `tools/wct/accept/mutation_policy.py` como
clave JSON del schema de política, leída activamente — dentro de la
superficie operador, consistente con el acotamiento; registrarla en futuras
auditorías de homónimos.) El silenciamiento
global de cada nombre no oculta ningún símbolo existente hoy; el riesgo es
solo futuro (un homónimo muerto nuevo quedaría invisible).

| Entrada | Hallazgos que calla | Contrato | Consumidores productivos (src/tools) | Consumidores tests/aceptación | Riesgo concreto | Recomendación |
|---|---|---|---|---|---|---|
| `load_policy` | 1 | REV2 §2 API pública del operador | **ninguno hoy** (llega con la receta §5/fase 2) | typed_operator_steps ×2, unit ×5 | futuro `load_policy` muerto ajeno invisible | conservar **solo con aceptación humana expresa del alcance** |
| `decode_pytest_journal` | 1 | PROPUESTA-P03 §2 API kernel | ninguno (binding fase 2) | 102 llamadas en tests R8 | ídem, nombre específico | ídem |
| `reconcile_pytest` | 1 | §2 API kernel | ninguno (fase 2) | 79 llamadas | ídem | ídem |
| `log_sha256` | 1 | §3 ExecutionEnd (wire) | validación cruda (validate:73) + kwargs builder:71; **0 lecturas de campo** | 0 | futuro homónimo | ídem |
| `pytest_version` `pluggy_version` `observer_version` `runtime_profile_sha256` | 4 | §3 SessionStart (claims) | validación cruda + builder; 0 lecturas de campo | 0 | ídem (compuestos específicos) | ídem |
| `source_sha256` | 1 | §3 PluginClaim | validate + builder; 0 lecturas | 0 | ídem | ídem |
| `effective_sha256` `profile_match` | 2 | §3 OptionsClaim | validate + builder; profile_match 1 lectura test | 1 | ídem | ídem |
| `argument_exit` | 1 | §3 SessionEnd (cotejo exit §5) | builder; 0 lecturas de campo en tools | 0 | ídem | ídem |
| `call_disposition` `pass_eligible` | 2 (types.py) | §2 TestObservation | 0 lecturas en tools | 7 / 28 | ídem | ídem |
| `deselected_property` | 1 | §2 ExecutionObservation | builder | 0 | ídem | ídem |
| `protocol_complete` | 1 | §2 | 0 en tools | 19 | ídem | ídem |
| `preflight_identities` | 1 | §2 PytestObservation | escrito por observation:246 | 2 | ídem | ídem |

**Contraste con la autorización R3 (cláusula y efecto exactos).** La
autorización humana del encargo R3, punto A, dice: «Editar
governance/lint/vulture_whitelist.py para incorporar únicamente las
entradas mínimas justificadas por los falsos positivos identificados en
REANCLAJE-2». Efecto real de cada entrada (demostrado en R3 S1–S3 y por el
verifier con 4 formulaciones): **silencia el nombre globalmente en
src+tools**, sin acotamiento por módulo, clase o sintaxis. La autorización
cubrió «entradas para falsos positivos identificados»; **no contiene
ratificación expresa del silenciamiento global por nombre**. (Nota de
procedencia señalada por el verifier: el verbatim del punto A procede del
texto de autorización recibido en la conversación del encargo R3 —
transcrito también en R4 —; no existe fuente committed que lo reproduzca
literalmente; R3 lo referencia sin transcribirlo.) La aceptación
de alcance registrada en la docstring de la whitelist («se acepta solo para
nombres compuestos específicos del contrato») **la declaró el agente en
R3**, no el humano; el dictamen favorable del verifier de R3 no sustituye
aprobación humana. Conclusión de auditoría: las 17 entradas están
**pendientes de aceptación humana explícita del alcance**; hoy no causan
daño medible (homónimos 0/0) y su retiro re-abriría los hallazgos sin
pérdida de detección actual. No se declara automáticamente conformidad ni
incumplimiento: la decisión es la del §4.

## 3. Disposición de los cinco residuos

Cadena común verificada para `utc`/`distribution`/`qualified`: **validación
productiva del valor crudo** (`payload_validate.py:60,75` `_is_utc`; `:87`
`_optional(_is_text)`; `:90` `_is_bool`) → **construcción** con
normalización (`builders.py:53,71` `utc=_utc(f["utc"])`) → **cero lecturas
del campo** en src/tools tras la construcción. El campo es la observación
conservada que la API retorna al caller.

| Hallazgo | Clase | Justificación causal | Decisión requerida |
|---|---|---|---|
| `utc` ×2 (:54,:77) | **D — información conservada intencionalmente con contrato acreditado** | §3 tabla de payload exige `utc:S` en ExecutionStart y ExecutionEnd; §3: «se valida por stdlib sin consultar reloj… no se usa para ordenar ni medir duración» — metadata conservada, no input de decisión del kernel (la frase «claims del emisor» nombra literalmente a PluginClaim/OptionsClaim, no a utc; corrección del verifier); consumidores presentes: caller/tests (2 lecturas); futuros: P03b/c/P05 | (a) aceptar la entrada global — riesgo demostrado de ocultar homónimos `utc` futuros; (b) **recomendado: residuo visible** hasta que fase 2+/P05 consuma realmente; (c) incremento de producto solo si un contrato futuro exige conducta que lo lea |
| `distribution` (:97) | **D** | §3 PluginClaim; validado `_optional(_is_text)`; 0 lecturas; claims guardados por contrato | mismas tres opciones; recomendado (b) |
| `qualified` (:100) | **D** | §3 PluginClaim; validado `_is_bool`; 1 lectura en tests | ídem |
| `expectation` (:47) | **B — código muerto sin obligación** | Campo de `_ScanState` (privado, **fuera** de la tabla de tipos §2). Definido en `scan_state.py:47`; **única escritura** `observation.py:165` (`_ScanState(expectation=item,…)`); **cero lecturas** (grep `\.expectation` = 0 en src+tools+tests). La FSM usa `execution_id`/`role` (derivados en la misma llamada) y las expectativas originales se validan aparte sobre la tupla (`api_args.py`, `observation_validate.py`). No es C: ningún consumidor requerido por el contrato; no es deuda de implementación conocida — es residuo del diseño del estado interno | Autorizar la eliminación del campo (prompt §6); alternativa: conservación indefinida con residuo visible |

## 4. Controles (reutilización válida de R3 + medición fresca)

- Caso legítimo conserva conducta: focales R8 426/426 y operador 61/61
  vigentes en `a6210a6` (R3/verifier); nada cambió desde.
- Símbolo muerto de nombre distinto sigue detectándose: control
  `zzz_dead_control` de R3/verifier (visible en todas las formulaciones).
- Homónimo ajeno muestra el límite: contrafactual del verifier R3 (añadir
  `utc`/`qualified` ocultó simultáneamente contractuales y probe).
- Fresco (este encargo): homónimos actuales 17/17 = 0 en src y tools
  (`logs/02-homonimos.txt`); sello R8 re-verificado **37/37 contra su
  snapshot histórico** (el archivo del sello está intacto y válido).

## 5. Inventario sucesor del candidato `a6210a6`

- **R8 (37 rutas):** 36 idénticas al manifiesto `93acd1a5…`
  (introducidas en `03b6ef6`); **1 diverge**:
  `tools/wct/evidence/pytest_phases.py` `368443477979ab8f6a6b0202cefee8f7dfe2dfbe4f58fede6ec11e3cc58a64c1`
  → `ea95730c366a2bdf25cf66aef02325383b059521f346a802ddb9af8c035ce2fa`
  (`e75f96e`, eliminación de `InstanceReport`).
- **Fase 1** (subconjunto de 6 entradas de producto del sello `c23d7273…`,
  que totaliza 23 con 17 logs de evidencia): 5 idénticas (`0739f7a`) —
  `features/wct-typed-mutation-001.feature`, `tests/acceptance/steps.py`,
  `tests/acceptance/typed_operator_steps.py`,
  `tools/wct/accept/mutation_cases.py`,
  `tools/wct/accept/mutation_policy.py` —;
  **1 diverge**: `tests/unit/test_accept_typed_operator.py`
  `44ba05971fefe7fddc53dcf732a7d17fc5cb8a72e66adfbce03c42b1969130f0` →
  `655c78fad6bfd22bfc7c2068bbe5dee8a6dcef1bd7e4cfddfc45e0a50316afd1`
  (`757cb53`, oráculo O6).
- **Whitelist** añadida en R3: `governance/lint/vulture_whitelist.py`
  `90e52d7f…` → `8c2f819b3e5431b509cc7bca19cbe44f0693f87ca6b36b5d428e24e5de3ca5fb`
  (`356a995`).
- Distinción expresa: los **manifiestos históricos siguen válidos contra
  sus snapshots** (R8 37/37 re-verificado); es el **candidato actual** el
  que ya no coincide en esas rutas; la **calificación** del scope
  incorporado sigue pendiente. No se declara «roto» ningún archivo de
  sello.
- Evidencia aplicable por identidad: focales R8/operador, conciliación de
  nodeids, sellos de procedencia. Re-medida al tocar algo: la batería
  completa.

## 6. Prompt único de reparación propuesto (NO autorizado todavía)

> **Encargo REANCLAJE-5 (propuesta) — eliminar el campo muerto
> `_ScanState.expectation`.**
>
> - **Base exacta:** `a6210a6be6f8682a499c8423f45f986082c9a96f`
>   (codex/reanclaje-p03a-fase1, PR #56; revalidar remoto y headRefOid).
> - **Objetivo conductual:** ninguno observable cambia: el campo es
>   escrito una vez y jamás leído (REANCLAJE-4 §3); su eliminación no
>   altera decode/reconcile ni findings. La verificación lo demuestra por
>   suite idéntica, no por ausencia de test nuevo.
> - **Allowlist exacta:** `tools/wct/evidence/pytest_scan_state.py`
>   (quitar el campo de `_ScanState`) y
>   `tools/wct/evidence/pytest_observation.py` (quitar el kwarg
>   `expectation=item` de la única construcción, línea ~165). Nada más.
> - **Contrato aplicable:** ninguno afectado (`_ScanState` es interno;
>   tabla de tipos de PROPUESTA-P03 §2 intacta). Ambas rutas son selladas
>   R8 → tratar como sucesor (hashes anterior/nuevo; 36/37 → 35/37
>   idénticas R8).
> - **Secuencia TDD:** no aplica test nuevo (sin cambio conductual);
>   caracterización por suite existente: focales R8 426, operador 61,
>   suite normativa 1181/0, property 1/1, fast 7/7, tier commit 19/21
>   (G-META-1 + G-DEAD ahora **4 hallazgos** tras esta eliminación:
>   utc×2, distribution, qualified).
> - **Controles negativos:** vulture canónico 5→4 exactamente (desaparece
>   solo `expectation`); `zzz_dead_control` de sonda sigue visible; los 4
>   residuos restantes siguen visibles; ruff/mypy de las dos rutas.
> - **Presupuesto:** 600 s agregados (suite ~180 s + commit ~190 s +
>   sondas). Prohibido: whitelist nueva, lecturas artificiales, renombres,
>   bajar confianza, excluir rutas.
> - **Criterios de parada:** entregar tras batería verde con G-DEAD en 4
>   hallazgos documentados; parar ante cualquier fallo de focal/suite
>   (indicaría consumidor oculto del campo: reportar y no reparar).
> - **Autorizaciones humanas previas necesarias:** aprobación de ESTE
>   prompt; y separadamente las decisiones de §4 para utc/distribution/
>   qualified (no incluidas aquí) y la aceptación de alcance de las 17
>   entradas (§2).

## 7. Decisiones humanas exactas requeridas

1. **Aceptación de alcance de las 17 entradas** (§2): ratificar el
   silenciamiento global por nombre (hoy sin daño medible) o retirar
   entradas concretas (re-abre sus hallazgos).
2. **`utc`/`distribution`/`qualified`** (§3): elegir (a) aceptar entradas
   globales, (b) residuo visible — recomendado —, o (c) exigir un
   incremento de producto con consumidor contractual real (fase 2+/P05).
3. **`expectation`**: autorizar o no el prompt §6 (REANCLAJE-5).
4. Pendientes previos: E9+bless del drift (36 rutas), calificación exigible
   del scope, fase 2 (pausa 2026-09-12).

## 8. Dictamen independiente

**APRUEBA los cuatro puntos**: (i) auditoría de las 17 entradas y lectura
de la autorización R3 (con la salvedad de procedencia del verbatim,
incorporada en §2); (ii) clasificación D de utc/distribution/qualified y B
de expectation (contrastadas contra PROPUESTA-P03 §2/§3 en su versión
versionada en main); (iii) inventario sucesor verificado por hash en ambos
sentidos (sello R8 37/37 contra snapshot histórico; 36/37 contra el
candidato actual); (iv) publicación del registro como docs-only en borrador.
Reejecutó: vulture canónico (5 hallazgos idénticos), greps de homónimos
(17/17 = 0), conteo exacto de llamadas (load_policy ×7), cadenas de
validación/construcción (validate:60/75/87/90; builders:53/71),
`\.expectation` = 0, verificación de hashes de commits en ambos sentidos,
`sha256sum -c` de sellos, y control discriminante
`test_pytest_observation.py` → 302 passed. Sus cinco discrepancias eran
documentales y quedan incorporadas arriba (D1 referencia §5→§6; D2
procedencia del verbatim; D3 cita de utc; D4 subconjunto enumerado; D5
nota sobre source_sha256). Ninguna decisión humana queda cerrada por esta
auditoría.
