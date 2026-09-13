# Ejecución del incremento f9_a/load_config — contrato ratificado (2026-09-13)

Estado: **implementación y demostración completadas; diff entregado sin
commit**. Incluye la ratificación humana de los 8 KILLED-POR-EXCEPCIÓN, la
implementación autorizada (2 ficheros de la allowlist), la verificación en el
worktree de la PR y la micro-campaña de exactamente los 4 IDs de
thresholds.yaml. Sin cambios de producto/gobernanza/umbrales; sin ampliar a
los 31 ni a los 928; TEST-007 continúa separado; sin bless, merge, bump, tag
ni release. El bruto histórico de la fase E (27 killed + 4 survived) y sus
sellos permanecen intactos.

## 1. Ratificación humana (verbatim, 2026-09-13)

> Ratifico los ocho IDs enumerados en §1 de
> CIERRE-ADJUDICACION-FASE-E-2026-09-13.md como KILLED-POR-EXCEPCIÓN,
> exclusivamente para los bytes, runtime y evidencia allí identificados.
> Conserva intactos el bruto histórico 27 killed + 4 survived y sus sellos.
>
> Apruebo el contrato mínimo:
> «La raíz devuelta por f9_a es cargable mediante load_config productivo;
> el proyecto retornado es esa misma raíz y policy/thresholds son mapas».
> Esto no declara gobernanza completa ni valida otros gates.

Con la ratificación, el subconjunto de fase E queda: 27/31 killed (19
evidenciados + 8 por excepción ratificados), 4 survived (pendientes de la
decisión del §2 de la adjudicación). El crudo no cambia.

## 2. Implementación (allowlist exacta; diff +22 líneas, 2 ficheros)

Candidato: worktree de la PR (`build/tmp/beta3-ac1-r2-integration`, rama
`codex/beta3-ac1-r2-integration`, HEAD `38bdf881ba35f20d5c0417bd5d39af6bb7e5d0af`)
— los 2 ficheros de la allowlist eran byte-idénticos a `fb7f725` (hashes
congelados verificados antes de editar); la rama sólo había avanzado con
trabajo r3 del coder (`test_accept_campaign.py` + docs). Cambios **sin
commit** (diff en `evidence/cambios.patch`,
`4b3e7aec2d12eed8f9de327ad16ab3ea17f4dde57ca2e6be9416124a6d00e37f`):

- `features/wct-sast-targets-001.feature`: escenario añadido al final, **sin
  segundo encabezado Feature**, con la descripción corregida (filesystem y
  Git mediante `f9_a`; sin Semgrep) y la identidad de la raíz en el Then.
- `tests/unit/test_sast_targets.py`: import de `load_config`; título añadido
  a `APPROVED_SCENARIOS` (el guard `test_gherkin_mantiene_los_escenarios_aprobados`
  exige paridad feature↔constante); binding nuevo
  `test_binding_gobernanza_del_fixture_cargable_por_load_config` — reutiliza
  el patrón de binding existente (un test por escenario que ejecuta su
  semántica con código real), sin ruta adicional fuera de la allowlist.

## 3. Verificación en el worktree

- Colección: 38 ítems (+1), exit 0 (`evidence/coleccion.txt`).
- Focal: `pytest tests/unit/test_sast_targets.py -q` → **38 passed, 0
  skipped**, exit 0 (`evidence/focal.txt`) — incluye el binding nuevo y el
  guard del Gherkin sincronizado.
- Fast gate (`tools.wct.cli gate --tier fast`): **7 PASS, 0 SKIP, 0
  FAIL/ERROR**, exit 0 (`evidence/fast-gate.txt`).

## 4. Micro-campaña (4 IDs, copia aislada, tope 600 s)

Copia: `build/tmp/incremento-f9a-loadconfig/checkout` — `git clone file://`
del worktree + `checkout --detach 38bdf881` + `git apply` del diff
autorizado; **hashes de los 2 ficheros parcheados verificados contra el
worktree**; manifiesto micro de 12 inputs (2 nuevos + 10 intactos del corte
histórico) verificado **antes y después** de la corrida. `pyproject.toml`
privado byte-idéntico al de fases G/E; `mutants/` pre-poblado; entorno limpio.

- Colección en copia: 49 ítems (focal ampliada); baseline: **49 passed, 0
  skipped**, exit 0.
- `mutmut run --max-children 1` con **exactamente** los 4 IDs explícitos:
  **exit 0 en 15 s de 600 s**; «Running clean tests: done» (original verde
  dentro de la campaña); 4/4 🎉.
- Revalidaciones: inventario post-run 959 IDs **conjunto-idéntico** al
  congelado; sólo los 4 con veredicto (raw: 4 killed); **955 restantes
  not-checked** (los 928 de fase E siguen sin veredicto, y los 27 ya
  juzgados no se re-ejecutaron); 12/12 inputs re-verificados.
- Sondas de clasificación (`evidence/sondas-micro.tsv`,
  `evidence/probes-micro/`): **4/4 KILLED-POR-ORACULO** — probe exit 1,
  exactamente `1 failed`:
  `FAILED tests/unit/test_sast_targets.py::test_binding_gobernanza_del_fixture_cargable_por_load_config`
  con `tools.wct.config.ConfigError` desde `tools/wct/config.py:30`
  (`_10`: thresholds.yaml ausente por clave renombrada; `_11` ídem;
  `_12`: contenido no-mapa; `_13`: `schema_version != 1`). El oráculo es el
  contrato ratificado, no una comparación de literales.

**Resultado: los cuatro mutantes quedan rechazados por el contrato nuevo;
sin supervivientes; nada pendiente de adjudicación en este lote.** (Precisión
de ruta por ID, de las sondas selladas: `_10`/`_11` y `_12` fallan con
`ConfigError` en `tools/wct/config.py:30`; `_13` en `:41`
«schema_version no soportado».)

## 5. Intentos instrumentales preservados (transparencia)

Dos intentos fallidos de esta misma sesión, previos o ajenos a veredictos,
conservados en `evidence/intento-*/`:

1. `intento-1/`: el pytest de stats de mutmut (sin `--basetemp`) necesita
   `PYTEST_DEBUG_TEMPROOT` existente; el script no había creado los
   directorios temporales. Falló **antes de ejecutar cualquier mutante**
   (fase stats); copia descartada incluida en la evidencia.
2. `intento-2/`: sondas con `MUTANT_UNDER_TEST` contaminado por mi extracción
   (awk sin `{print $1}` arrastraba el status) → el trampolín despachó el
   original («2 passed»). Detectado por el propio control de clasificación;
   sondas re-ejecutadas con IDs limpios. Los veredictos de campaña nunca
   dependieron de estas sondas.

Ambos son defectos de receta propia, no del producto. **El sello inicial
volvió a incurrir en el defecto de fase G**: la línea de resumen del
manifiesto se escribió en el log DESPUÉS de generarlo. El verificador lo
detectó (1 fallida en `pasos-micro.log`) y el lote quedó RECHAZADO en esa
ronda. Cierre aplicado (documentado en
`evidence/CIERRE-SELLO-MICRO.md`): `evidence-micro.sha256` se conserva sin
sobrescribir (1210 válidas + 1 fallida), el desfase quedó verificado por
reproducción (`53af8d5e…` = log sin su última línea), y el manifiesto
sucesor `evidence-micro-2.sha256` (1213 entradas, **0 fallidas**) sella el
estado final incluyendo ambos intentos. Disciplina reafirmada: la línea de
resumen del manifiesto no se registra en el log sellado; el manifiesto es la
última escritura absoluta. La sustancia de la campaña (veredictos, sondas,
inventario, inputs) estaba en ficheros sellados que siguen verificando; el
defecto afectó sólo al log de pasos.

## 6. Límites

Los 928 IDs de fase E y los 27 juzgados no se re-ejecutaron ni ampliaron;
TEST-007 sigue pendiente para `checks.py`/`fixtures_tools.py`; el bruto y los
sellos de fase E (27+4) permanecen intactos y verificando; esto no acredita
AC1 ni las puertas posteriores (aceptación, cobertura/CRAP, DRY, tier full).
Diff entregado sin commit para revisión; sin bless, merge, bump, tag ni
release.
