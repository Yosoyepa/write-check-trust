# Registro REANCLAJE-18 — diagnóstico causal del runner y adjudicación completa de L3 (2026-09-19)

Estado: **mecanismo de las discrepancias DEMOSTRADO (fuente + comparaciones
controladas + reproducción nativa), cinco sondas resueltas, los 30
sobrevivientes adjudicados por ID, obligaciones de código de módulo auditadas
con perturbación empírica y métrica 337/357 reconciliada por sitios
concretos.** Bruto histórico INALTERADO: 129 = 99 killed + 30 survived. Sin
reparaciones permanentes, sin campaña, sin ratificaciones. Receta de
recalificación propuesta, no ejecutada.

## 1. Base, identidades y correcciones a R17

Base `5e064a8cd3e44a73b75a0cba430d722b4619847a` == remoto == headRefOid PR #56
(borrador); merge-base = main `8a379d64…`; sin avance. Expediente aislado
`build/tmp/reanclaje18-20260919/`; manifiesto R17 reverificado (61/61) antes
de reusar evidencia; árbol instrumentado copiado y verificado contra la
custodia R17 (6/6 byte-idénticos). **Correcciones a R17 (nota sucesora, sin
reescribir el histórico):** (i) R17 llamó «sitios WCT» a su pasada AST propia:
la métrica CANÓNICA del motor es 337 (== R6); la de R17 (357) contaba además
20 nodos `ast.Constant` de valor None/Ellipsis que `_is_site` excluye
(desglose §7). (ii) R17 §5 citó `member_of_3` como muestra de killed EN
CAMPAÑA por su test letal: impreciso — `member_of_3` es survived EN el bruto
(0 en meta) y muerto SOLO en sonda fresca; su estado de campaña es artefacto
del runner (§3).

## 2. Las cinco sondas pendientes (encargo §4)

`x__within__mutmut_2..6`, lanzador fail-closed, selección completa 452,
activación acreditada (trampolín lee `os.environ` POR LLAMADA — §3), proceso
fresco desde antes del primer import:

| ID | rc | Resultado | Clasificación |
|---|---|---|---|
| `within_2` (`type is int and low<=v<=high` → `… or …`) | 0 | 452 passed | **SURVIVED-REPRODUCIDO-EN-SONDA** |
| `within_3` | 1 | 232 failed, 220 passed | **SURVIVED-EN-CAMPAÑA → DETECTADO-EN-SONDA** |
| `within_4` | 1 | 232 failed | DETECTADO-EN-SONDA |
| `within_5` | 1 | 232 failed | DETECTADO-EN-SONDA |
| `within_6` (`<=high` → `<high`) | 0 | 452 passed | **SURVIVED-REPRODUCIDO-EN-SONDA** |

Con esto, los 30 sobrevivientes quedan: **17 reproducidos** (15 de R17 +
within_2/6) y **13 detectados en sonda** (10 de R17 + within_3/4/5). Bruto sin
cambios. Incidentes de ejecución documentados: 10 arranques inválidos del
lanzador (rutas heredadas; <0.1 s c/u) antes de las corridas válidas.

## 3. Mecanismo de las discrepancias — DEMOSTRADO

**Fuente (mutmut 3.7.0 instalado, lectura íntegra):** el runner ejecuta cada
mutante con `os.fork()` (`__main__.py` l.1473) y el hijo establece
`os.environ["MUTANT_UNDER_TEST"] = mutant_name` DESPUÉS del fork (l.1475),
ejecutando los tests IN-PROCESO con `pytest.main(...)` (l.445, runner por
defecto `run_tests` l.482-484). El padre ya importó todos los módulos durante
las fases previas con `MUTANT_UNDER_TEST="stats"`/`""` (l.753/1413). El
trampolín lee `os.environ.get("MUTANT_UNDER_TEST")` EN CADA LLAMADA
(`mutation/trampoline.py`) — no copia a global.

**Consecuencia:** el hijo hereda por fork los módulos del padre:
`_PAYLOAD_CHECKS` (pytest_payload_validate L49-120) fue construida en import
llamando a `_member_of`/`_within`/`_optional` con despacho ORIGINAL; las
closures almacenadas en la tabla NO son trampolines y jamás se re-despachan.
La activación tardía solo afecta llamadas nuevas. Las funciones llamadas
DURANTE los tests (is_utc, clean_string, validate_payload…) sí despachan la
variante → los 99 killed son medidos correctamente; los 15 mutantes de
factoría son INVISIBLES al runner → exit 0 con el único test atribuido
(~0.08-0.13 s, durations_by_key).

**Comparaciones controladas (proceso fresco, misma fuente/test/datos;
observable: `_within(0,255)` sobre SessionEnd.argument_exit con mutante
`within_6`, high exclusivo):**

| Modo | exit 255 | exit 256 | Lectura |
|---|---|---|---|
| A. Original fresco (sin activación) | aceptado | invalid_observation/argument_exit | tabla con closures originales |
| B. Mutante desde el arranque | invalid_observation | invalid_observation | tabla construida bajo la variante |
| C1. Tabla previa + activación tardía → closure ALMACENADA | aceptado | invalid_observation | la closure antigua conserva comportamiento original |
| C2. …misma activación → llamada NUEVA a `_within(0,255)` | rechazado | rechazado | la factoría SÍ despacha la variante |

C distingue «activación tardía con closure antigua» de «la variante nunca se
activó»: la variante ESTÁ activa (C2) y aun así la tabla no la refleja (C1).

**Reproducción puntual del runner nativo (1 de las 2 autorizadas):** `mutmut
run tools.wct.evidence.pytest_payload_predicates.x__member_of__mutmut_3` en
copia privada → **🙁 survived, exit 0, duración 0.078 s**, sin regeneración
(hashes de metas/stats/fuente idénticos antes y después), pese a que el mismo
test (`test_abnormal_exit_is_visible_as_cause`) lo mata en proceso fresco
(sonda R17). Atribución al runner: **CERRADA** (fuente + A/B/C + reproducción
nativa coinciden; no queda «compatible sin cerrar»).

**IDs afectados por el mecanismo:** exactamente los 15 mutantes de las tres
funciones llamadas solo en import (`_member_of` 5, `_optional` 4, `_within`
6). Los 99 killed no se invalidan: el mecanismo solo OCULTA mutantes (nunca
activa variantes espurias) y sus funciones se llaman durante los tests con el
entorno ya fijado. Nota de estados del instrumento: el runner también define
exit 33 (sin tests asociados) y 37 (type-check) — ninguno se produjo aquí.

## 4. Adjudicación de los 30 sobrevivientes (por ID; bruto intacto)

Consumidor productivo común: `validate_payload` (reconcile de observations
MANUALES admitidas por §2 l.112-116) vía `_PAYLOAD_CHECKS`. Diffs exactos en
`logs/12-diffs-17-reproducidos.json` (expediente).

**Clase B — HUECO DE ORÁCULO bajo contrato vigente (17, reproducidos en
sonda):** cada uno tiene entrada discriminante legítima por la frontera de
reconcile (el decoder rechaza antes estas entradas por el wire; reconcile las
recibe de observations construidas manualmente, admitidas por el API):

| ID (sufijo) | Diff esencial | Entrada discriminante | Cita |
|---|---|---|---|
| clean_string_3 | `size<=MAX and all(...)` → `or` | payload manual con S > 4096 bytes | §2 l.97-99 |
| clean_string_6 | C0/DEL `and` → `or` | payload manual con DEL (0x7F) | §2 l.97-99 |
| clean_string_8 | `ord >= C0` → `>` | payload manual con espacio (0x20) válido | §2 l.97-99 |
| is_argv_5 | `len(value) > 0` → `>= 0` | ExecutionStart manual con argv `()` | §3 l.209 (tupla no vacía) |
| is_broad_text_1 | `type is str and _clean` → `or` | collect_report manual con nodeid sucio | §2 l.97-99 |
| is_cwd_5 | `split("/")` → `split(None)` | cwd manual `/a/./b` | §3 l.209 (sin `.`/`..`) |
| is_cwd_6 | `split("XX/XX")` | cwd manual con segmento `.` | idem |
| is_cwd_11 | `"." not in` → `"XX.XX"` | cwd manual con `.` | idem |
| is_cwd_13 | `".." not in` → `"XX..XX"` | cwd manual con `..` | idem |
| is_digest_1 | `type is str and fullmatch` → `or` | ExecutionStart manual con digest no-lowerhex64 | §2 l.56/201 |
| is_text_6 | `value != ""` → `!= "XXXX"` | nodeid `""` manual en clase no-report | §2 l.98-99 |
| is_u_6 | `<= SEQ_MAX` → `<` | payload manual con U = SEQ_MAX exacto | §2 l.201 |
| is_xfail_3/4/5 | bools `and` → `or` | PhaseMake manual con xfail(run=1) etc. | §2 l.236 |
| within_2 | `type is int and rango` → `or` | SessionEnd manual con argument_exit=True (bool) | §2 l.136 |
| within_6 | `<= high` → `< high` | SessionEnd manual con exit 255 exacto | §2 l.136 / §3 tabla SessionEnd |

Oráculo mínimo por ID: un caso de observation MANUAL (vía reconcile o
`validate_payload` público) con la entrada discriminante →
`ObservationError("invalid_observation", <campo>)`. Original verde en todos
(obligación ya satisfecha por el producto: verificado en sondas). Ninguno es
C: existe entrada discriminante dentro del dominio admitido; ninguno es D.

**Clase E — LIMITACIÓN INSTRUMENTAL (13, survived en campaña por el
mecanismo §3, DETECTADOS en sonda fresca):** `member_of_1/2/3/4/5`,
`optional_1/2/3/4`, `within_1/3/4/5`. En proceso fresco la tabla se construye
bajo la variante y mueren: member_of_1/3/4/5 y within_3/4/5 con 270/232
fallos (rompen payloads válidos: `invalid_observation: …payload.role/…`);
member_of_2 con exactamente `test_manual_invented_outcome_is_invalid_observation`;
optional con ~232. Precondición de su disposal: re-campaña con activación
fiel (§6) o aceptación de la sonda como medición; decisión humana.

## 5. Código de módulo: obligaciones REALES (auditoría con perturbación)

- **`_PAYLOAD_CHECKS` (tabla)**: la omisión de un check (perturbación de una
  línea en copia desechable: quitar `("argument_exit", _within(0,255))` de
  SessionEnd) **NO la detecta ningún test existente** (426 passed, control
  original verde). Es hueco EMPÍRICO. Nota de alcance (hallazgo menor del
  verifier): el par perturbado/control usó el subconjunto pertinente
  schema+observation (426 tests), idéntico en ambos brazos — la comparación
  es válida; los 26 de phases no se incluyeron porque el check perturbado se
  ejercita por el reconcile de observations. Oráculo mínimo propuesto: matriz
  parametrizada INDEPENDIENTE (tipo de payload / campo / valor válido /
  valor inválido / resultado público), transcrita de la tabla §3
  l.206-228 — nunca copiada de producción.
- **Frozen-ness de las 21 clases de payload**: obligación contractual
  vigente (§2 l.60-61 «Todos los tipos de valores son dataclasses frozen»);
  el test existente cubre solo los 9 tipos de observation. Oráculo mínimo:
  aserción frozen sobre las 21 clases (ancla: la tabla contractual de códigos).
- **Campos/orden de las 21 clases**: §3 fija la tabla; hoy solo ExecutionStart
  está transcrito y WIRE_FIELDS cubre el subconjunto wire. Propuesta mayor
  (transcripción completa) — decisión humana D-D.
- **Enums (ROLES/PHASES/OUTCOMES/TERMINATIONS/CHANNEL_DEFECTS)**: cobertura
  solo conductual; transcripción propuesta (decisión).
- **`__all__` de la fachada / re-export EVENT_CATALOG**: obligación débil
  (composición §10); menor, opcional.
- **Constantes/límites**: cubiertos por fronteras reales de conducta; sin
  nueva exigencia.
- Las perturbaciones de tabla NO son IDs mutmut ni se suman al inventario 129.

## 6. Receta fiable de recalificación (PROPUESTA, no ejecutada)

1. **Generación**: `mutmut run ZZ_…NO_MATCH` (filtro sin coincidencias) —
   mutmut GENERA los mutantes; verificación de inventario/diffs por conjuntos.
2. **Ejecución**: arnés EXTERNO (lanzador fail-closed tipo R12–R18): proceso
   NUEVO por ID con `MUTANT_UNDER_TEST` fijado ANTES del primer import (la
   tabla `_PAYLOAD_CHECKS` se construye bajo la variante), cwd+PYTHONPATH en
   la copia instrumentada, selección completa congelada, veredicto por
   identidad (exit codes 0/1/timeout), originales + negativos + canario por
   sesión, presupuesto con guardián y limpieza de hijos. NO es «mutmut run»:
   ambas responsabilidades quedan explícitas y separadas.
3. **Cero herencia**: sin reutilizar metas previas; estados inicial/final
   separados; generación contabilizada aparte de ejecución.
4. Expectativa medible de una re-campaña L3 con tests actuales: los 99 killed
   se conservan; los 13 de clase E pasan a killed; los 17 de clase B
   sobreviven (oráculo pendiente) → bruto esperado 112 killed + 17 survived
   (no impuesto).

## 7. Métricas reconciliadas (337 vs 357)

Métrica CANÓNICA del motor (`mutation_sites`: walk completo, `_is_site`
excluye Constant None/Ellipsis): **337** — coincide con R6. La pasada AST
propia de R17 contaba TODAS las `ast.Constant` (incluidas None/Ellipsis):
**357**. Diferencia exacta por archivo (constantes None/Ellipsis): classes 10,
predicates 5, validate 4, payloads 0, event_catalog 1, limits 0 — **total 20**.
Publicación separada: canónica 337 · AST propia 357 · callables 15 · IDs 129.

## 8. Presupuestos, gates, custodia

Presupuestos (guardián monotónico propio; intentos inválidos incluidos):
S ≈ 172/900 (sync, A/B/C×2 por corrección de firma, reproducción nativa,
5+10 sondas, perturbación de tabla con control) · V: ver §9 · I: fast+commit
(§8.1) · PUB: publicación (§10). Detalle por ledger en el expediente.

- Gates (I): `wct gate --tier fast` rc=0; tier commit **20 PASS · 1 FAIL —
  G-META-1 recalculado: 36 rutas heredadas** (2 modificadas + 34 nuevas
  protegidas; ninguna del delta; main limpio). Sin campañas pesadas (no hay
  cambios de tests/producto).
- Custodia: expediente nuevo con identidades, trazas A/B/C, reproducción,
  sondas, diffs, métricas y tabla de adjudicación; logs cerrados antes del
  manifiesto; digest fuera de miembros; publicación/hooks/CI en archivos
  separados (sello sucesor si hace falta). Históricos intactos.

## 9. Verificación independiente

Verifier final de solo lectura versionada (dictamen en el expediente):
reproduce una comparación decisiva del mecanismo, comprueba las cinco sondas,
revisa la adjudicación por ID, la legitimidad de los oráculos propuestos
(entradas por la frontera de reconcile, no helpers internos), recalcula
métricas/conjuntos y señala lo no demostrado. No concede ratificaciones.

## 10. Próximo incremento mínimo PROPUESTO (no ejecutado)

> **REANCLAJE-19 — reparación acotada L3.** Allowlist propuesta:
> `tests/unit/test_pytest_schema.py` + docs. (1) Tests de matriz para
> `_PAYLOAD_CHECKS` (literales de §3) y frozen-ness de las 21 clases —
> cubriría los 17 de clase B si se añaden también las entradas
> discriminantes por ID (cwd `./..`, argv `()`, xfail bool, exit
> bool/255/256, digest sucio, broad-text, C0/DEL/espacio, SEQ_MAX, vacío,
> >4096). (2) Decisión humana D-D L3: transcripción de enums/campos y
> `__all__`. (3) Decisión sobre la clase E: re-campaña con la receta §6
> (única) o aceptación documentada de sondas. (4) Tras (1): re-campaña L3
> con la receta, expectativa 112+17. L2/L4 conservan sus cierres (el
> hallazgo del runner no los afecta: sus funciones objetivo se llaman en
> tiempo de test; sin invalidante concreto no se reabren).
