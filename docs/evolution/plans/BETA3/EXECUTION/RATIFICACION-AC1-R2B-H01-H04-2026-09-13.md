# Acta de ratificación AC1 r2b — decisiones H-01…H-04 (2026-09-13)

Estado: ratificación humana registrada y acotada. **No** es bless, merge, tag,
bump, release, cambio de gobernanza ni excepción general. AC1 continúa
pendiente de las demás fuentes y puertas de calificación. Base de la
ratificación: PR #53 en `daab7e8fa8294f6cef810f3a54501e6ff0a583c0`, cuyo commit
añade la matriz técnica `ADJUDICACION-SUPERVIVIENTES-AC1-R2B-2026-09-13.{md,json}`
y su addenda de trazabilidad.

## H-01 — Ratificación de las 24 equivalencias (alcance acotado)

Respuesta registrada para el coder, verbatim:

> Ratifico H-01 para los 24 IDs exactos de la matriz publicada en daab7e8,
> exclusivamente bajo sus bytes, runtime y precondiciones documentados.
> Esta decisión no autoriza excepciones generales ni cambios de gobernanza.
> Si cambian esas precondiciones, la adjudicación debe revisarse.
>
> H-02: no ampliar ahora el contrato a IR externo sin examples.
> Mantener explícita la frontera de IR canónico.
>
> H-03: conservar la defensa interna del parser.
> No crear estados públicos artificiales ni tests de implementación
> para distinguir mutantes inobservables desde la API contratada.
>
> H-04: autorizar el preflight como instrumento de la receta de calificación,
> no como módulo nuevo del producto WCT en este incremento.
>
> Antes de usarlo:
> - contrastar un inventario independiente de funciones esperadas;
> - rechazar inventario vacío, funciones omitidas y asociaciones inválidas;
> - comprobar que los nodeids asociados existen en la colección seleccionada;
> - declarar que asociación no implica discriminación;
> - comprobarlo contra r2 y r2b existentes, sin lanzar otra campaña.

Los 24 IDs ratificados son exactamente los de `survivors` en
`ADJUDICACION-SUPERVIVIENTES-AC1-R2B-2026-09-13.json` (fuente de identidad;
24/24 coinciden con la reconciliación `mutation-code-lot-r2b`), agrupados por
su clasificación técnica:

| Clasificación técnica | N | IDs |
|---|---:|---|
| `EQUIVALENTE_TECNICO_EN_RUNTIME_ACOTADO` | 3 | `generation.x_generate__mutmut_3`, `generation.x_generate__mutmut_63`, `parsing.x_parse_feature__mutmut_9` |
| `EQUIVALENTE_TECNICO_POR_NORMALIZACION` | 1 | `generation.x_scenario_names__mutmut_14` |
| `EQUIVALENTE_BAJO_PRECONDICION_DEL_IR_CANONICO` | 2 | `mutation_cases.x_mutations__mutmut_7`, `mutation_cases.x_mutations__mutmut_9` |
| `EQUIVALENTE_BAJO_PRECONDICION_DE_LONGITUD` | 3 | `parsing.xǁ_Parserǁ_row__mutmut_18`, `_21`, `_22` |
| `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA` | 12 | `parsing.xǁ_Parserǁ__init____mutmut_2/7/8`, `xǁ_Parserǁ_examples__mutmut_13`, `xǁ_Parserǁ_header__mutmut_17–23`, `xǁ_Parserǁ_scenario__mutmut_18` |
| `EQUIVALENTE_BAJO_ESTADO_INALCANZABLE_PUBLICAMENTE` | 1 | `parsing.xǁ_Parserǁ_row__mutmut_11` (véase H-03) |
| `EQUIVALENTE_TECNICO_POR_FALLBACK_TOTAL` | 2 | `semantic.x_phase_status__mutmut_3`, `semantic.x_phase_status__mutmut_4` |

**Condiciones de alcance** (verificables, no decorativas):

- **Bytes**: las cinco fuentes del lote con los SHA-256 del manifiesto
  `mutation-code-lot-r2b/mutation-inputs.sha256` (`672c41f5…`, `d40dd194…`,
  `7e324c02…`, `14249343…`, `a4528b8e…`); la matriz acredita
  `git diff 13afbcc…7b71c9c…` vacío sobre ellas.
- **Runtime**: `sh-p01-CND-80B8/.venv`, tal como lo registran los planes r2/r2b;
  la versión triple (Python 3.13.14, mutmut 3.7.0, pytest 9.1.1) queda
  acreditada por la evidencia de primitivas de runtime del integrador
  (`r2b-runtime-equivalence-primitives.json`) y verificada en vivo durante la
  revisión de esta acta.
- **Precondiciones**: las declaradas fila a fila en la matriz; esta acta no
  las reescribe ni amplía.

Si cambian los bytes, el runtime o alguna precondición, la adjudicación
revierte a revisión. No se concede ninguna exención general para versiones
futuras y no se modifican gobernanza, umbrales ni mecanismos de excepción.

**Contabilidad de resultados** (se mantienen separados, sin convertir
equivalentes en killed):

- Resultado bruto r2b: **486 = 462 killed + 24 survived** (y 0 de otras clases).
- Adjudicación: **24 equivalentes aceptados en alcance acotado**.
- Resultado ajustado: **462/462 de los no equivalentes** killed. Esto **no**
  afirma cierre integral de AC1: quedan el transporte, `gate/*`,
  `selftest/fixtures_tools.py` y las puertas posteriores (aceptación,
  cobertura/CRAP, DRY, tier full).

No se pedirá otra ronda de investigación de estos 24 casos; corresponde
guardar este cierre y pasar al siguiente trabajo pendiente.

## H-02 — Frontera de IR canónico (no ampliar contrato)

No se amplía ahora el contrato a IR externo sin `examples`. Los dos mutantes
`EQUIVALENTE_BAJO_PRECONDICION_DEL_IR_CANONICO`
(`mutation_cases.x_mutations__mutmut_7/9`) quedan ratificados **solo** bajo la
precondición documentada: el IR llega de `parse_feature` por la frontera AC1 y
cada Scenario público se crea con `examples: []`. Un diccionario externo
arbitrario sin esa clave queda explícitamente **fuera del contrato**; el
catálogo `FUT-IR-CANONICO` de la matriz sigue siendo propuesta futura no
autorizada.

## H-03 — Defensa interna del parser (mantener interna)

El mutante `EQUIVALENTE_BAJO_ESTADO_INALCANZABLE_PUBLICAMENTE`
(`parsing.xǁ_Parserǁ_row__mutmut_11`, rama `current is None` de `_row`) queda
ratificado como equivalente **manteniendo la defensa interna**: no se hará
públicamente alcanzable un estado inválido solo para matar un mutante, ni se
crearán tests de implementación sobre `_Parser` interno. El diagnóstico interno
no se declara eliminado ni irrelevante; `FUT-PARSER-DIAGNOSTIC` sigue siendo
propuesta futura no autorizada.

## H-04 — Preflight de asociaciones: instrumento de receta, no producto

Se autoriza el preflight como **instrumento de la receta de calificación**, no
como módulo nuevo del producto WCT: las rutas
`tools/wct/accept/mutation_preflight.py` y `tests/unit/test_accept_mutation_preflight.py`
del catálogo `future_preflight` **no se construyen** en este incremento.

**Comprobación contra r2 y r2b existentes (sin lanzar otra campaña)** — ya
ejecutada por el prototipo del integrador y verificada en esta acta:

- `build/tmp/ac1-r2-qualification/evidence/r2-r2b-association-preflight.log`:
  r2 → `FAIL-missing-test-associations` (19/22 funciones asociadas; faltan las
  tres de `semantic`, el módulo entero reportado como `missing_modules`),
  exit 2; r2b → `PASS` (22/22), exit 0. El defecto de receta de r2 habría sido
  **rechazado por el preflight**, que es exactamente el comportamiento exigido.
- Stats verificadas por SHA-256 en el propio log (`5f8c4cf0…` y `94910bb7…`).

**Requisitos obligatorios antes de usarlo en cualquier receta** (además de la
regla actual del prototipo, que solo contrasta `function_hashes` contra
asociaciones):

1. Contrastar un **inventario independiente de funciones esperadas** (AST del
   candidato) contra el inventario del instrumento: un módulo entero fuera no
   debe poder aprobar.
2. Rechazar inventario vacío, funciones omitidas y asociaciones inválidas
   (salida no cero, con lista explícita de lo que falta).
3. Validar que los **nodeids asociados existen** en la colección de la
   selección focal real.
4. Declarar en su salida que **asociación no implica discriminación**: prueba
   que el test ejecutó la función, no que distinga cada sitio.
5. No excluir módulos para obtener verde, no reutilizar veredictos de corridas
   anteriores y no tocar gobernanza.

El prototipo vive bajo `build/tmp/` (`r2b-adjudication/preflight_associations.py`,
SHA-256 `b7fd59cfe3a29ed302206ef43cfc5d9bd11a78dd868f778e483b789858fdbb13`) y
así permanece hasta que un incremento autorice su incorporación instrumentada.

## Plan del siguiente lote pendiente — NO EJECUTADO

Lote de **transporte** AC1 (`mutation-code-lot-r3`, denominación de secuencia
de lotes; sin relación con recetas anteriores). Queda **a la espera de
autorización humana explícita**; nada de esto se ha ejecutado.

- **Rutas de producto** (`only_mutate`):
  `tools/wct/accept/campaign.py` (`686070cd…`), `tools/wct/accept/process.py`
  (`bdbb5646…`), `tools/wct/accept/pytest_receipt.py` (`d4f136ae…`),
  `tools/wct/accept/pipeline.py` (`af67b206…`, fachada de 20 LOC sin
  funciones propias: se incluye por completitud de frontera; se espera cero o
  casi cero sitios).
- **Inventario (AST, HEAD `daab7e8`)**: 17 funciones en 3 módulos —
  `campaign.py` 114 LOC/4 funciones (`_environment`, `_attempt`, `_results`,
  `run_mutations`), `process.py` 76 LOC/5 (`_terminate`, `_read`, `_observe`,
  `_execute`, `run_process`), `pytest_receipt.py` 94 LOC/8 (los seis hooks
  pytest + `__init__` + `_cases`). Sitios exactos: se miden en preflight;
  estimación por densidad observada (1,3–1,5 sitios/LOC): ≈ 370–430 sitios.
- **Tests focales** (`pytest_add_cli_args_test_selection`):
  `tests/unit/test_accept_campaign.py` (292 LOC),
  `tests/unit/test_accept_pytest.py` (417 LOC),
  `tests/unit/test_accept_pipeline.py` (474 LOC, necesario para las
  asociaciones de la fachada y el ciclo público). `-m "not property"`;
  `also_copy = ["src", "features", "governance"]`;
  `use_git_change_detection = false`.
- **Runtime**: el original del expediente, `sh-p01-CND-80B8/.venv`
  (Python 3.13.14, mutmut 3.7.0, pytest 9.1.1), entorno privado
  (`TMPDIR`, `PYTEST_DEBUG_TEMPROOT`, `PYTHONSAFEPATH=1`,
  `PYTHONDONTWRITEBYTECODE=1`, variables de protocolo limpias), serial
  `--max-children 1`.
- **Preflight obligatorio (H-04 endurecido)**: antes de lanzar campaña, el
  instrumento (con los cinco requisitos del acta ya implementados bajo
  `build/tmp/`) debe aprobar: inventario independiente = instrumentado (17/17,
  sin módulos omitidos), cero funciones sin asociación y nodeids existentes en
  la colección de los tres ficheros focales. Una falta es parada, no verde.
- **Presupuesto**: `timeout --signal=INT --kill-after=30s 3600s mutmut run
  --max-children 1 '*'`. Duración estimada: 10–30 min (los tests focales de
  campaña lanzan procesos reales por intento; la medición del preflight fijará
  la estimación antes de arrancar). Copia nueva bajo
  `build/tmp/ac1-r2-qualification/mutation-code-lot-r3/`; sin reutilizar
  veredictos de r2/r2b.
- **Cierre esperado**: el mismo estándar — reconciliación completa, cero
  no-tests/timeout/suspicious/skipped, y adjudicación separada de cualquier
  superviviente antes de declarar nada.

## Revisión independiente (realizada)

Revisión de sólo lectura por el verifier (PROC-005), con recálculo de hashes,
identidad 24/24 contra el JSON y la reconciliación, lectura adversarial del
prototipo de preflight y verificación de que el lote r3 no existe: **dictamen
APROBADO-COMMIT, 5/5 áreas PASS, sin correcciones exigibles**. Evidencia del
verifier (local): `build/tmp/adjudicacion-ac1-l1/verifier-ratificacion/VERIFICACION-AC1-R2B-RATIFICACION-2026-09-13.log`.
