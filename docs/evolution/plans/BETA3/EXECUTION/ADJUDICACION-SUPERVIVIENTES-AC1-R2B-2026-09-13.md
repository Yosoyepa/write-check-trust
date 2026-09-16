# Adjudicación técnica de supervivientes AC1 r2b

Fecha: 2026-09-13. Estado: **evidencia técnica focal completada; 0/24 ratificaciones humanas**.

Esta matriz adjudica técnicamente los 24 supervivientes de `mutation-code-lot-r2b`. No cambia producto, tests, gobernanza, workflow, `pyproject.toml`, lockfile, bless, merge, versión, tag ni release. La equivalencia técnica aquí registrada **no** es una ratificación humana, una exclusión automática ni una autorización retrospectiva.

## Resultado y límites

- r2 reconcilia 486 IDs: 413 `killed`, 22 `survived`, 51 `no tests`; r2b reconcilia los mismos 486 IDs: 462 `killed`, 24 `survived`.
- Las 22 supervivencias r2 siguen en r2b; de los 51 `no tests`, 49 pasan a `killed` y 2 a `survived`. El listado de 24 no procede de una conversión automática de estados.
- La evidencia r2b se produjo en `13afbcc…`; `git diff --name-only 13afbcc…..7b71c9c… --` sobre las cinco fuentes del lote está vacío. Por tanto, no hubo drift de las fuentes calificadas antes de crear estos documentos.
- La sonda directa ejecutó el original, los 24 mutantes existentes y cuatro canarios muertos, usando el runtime original Python 3.13.14 y sólo el workspace de mutantes. Los 24 stdout y exit codes coinciden con el original; los cuatro canarios divergen. No fue una campaña de mutación ni una corrida pytest.
- Una asociación test→función prueba que el test ejecutó la función durante la medición; **no** demuestra que cada nodeid distinga cada sitio. La discriminación de estos sitios proviene de la sonda y de las precondiciones explicitadas abajo.

### Conteo por disposición técnica

| Disposición técnica | Cantidad | Ratificación humana |
|---|---:|---|
| `EQUIVALENTE_BAJO_ESTADO_INALCANZABLE_PUBLICAMENTE` | 1 | Pendiente; ninguna inferida desde L1/L1b. |
| `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA` | 12 | Pendiente; ninguna inferida desde L1/L1b. |
| `EQUIVALENTE_BAJO_PRECONDICION_DEL_IR_CANONICO` | 2 | Pendiente; ninguna inferida desde L1/L1b. |
| `EQUIVALENTE_BAJO_PRECONDICION_DE_LONGITUD` | 3 | Pendiente; ninguna inferida desde L1/L1b. |
| `EQUIVALENTE_TECNICO_EN_RUNTIME_ACOTADO` | 3 | Pendiente; ninguna inferida desde L1/L1b. |
| `EQUIVALENTE_TECNICO_POR_FALLBACK_TOTAL` | 2 | Pendiente; ninguna inferida desde L1/L1b. |
| `EQUIVALENTE_TECNICO_POR_NORMALIZACION` | 1 | Pendiente; ninguna inferida desde L1/L1b. |

## Evidencia reproducible

- Censo reconciliado: `build/tmp/ac1-r2-qualification/evidence/r2b-adjudication-census.json` (`ab696ee6d802e5662d09c5868f7bad6a3d62c252ab86ba570f6ffc741d9b09bb`).
- Diffs directos con `mutmut show`: índice `31af55af926fa4595e1a520daee3ce17fa834bbb2d919e04093776c8e2b66387` y log `d4cdada80d9bf279199242720259f8fe1c45e557031251d2bd5203788b309d60`. El log histórico de diffs conserva su delimitador de cierre `=== ID ===`; no fue editado.
- Sonda: informe `feadf86d7e4c1714a56d5d3457488e07422736ae2ef85e59fe6de100c7c3a7ba`, log `c8a6e8f30b25b4ffbaeb5d38b12364f6a82fc892ecc4ef95decc0fc5d7adf05a`, driver `c3102c47bc334eb4ec4a44256a4e074a3249b47a30b41ae11300161800b2efc0`; stdout original `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`.
- Primitivas del runtime: `e987e5db2cf4053387a904281f5aa418b6f4ff289c7d2e17376e849952d729b3` (codec `UTF-8`/`utf-8` y JSON no ASCII).
- Preflight de asociaciones: `d785b8db0ea278d0f37279581453591b60da8dca69da753956f5015ea45e0633`; r2 falla por tres funciones de `tools.wct.accept.semantic` y r2b pasa 22/22, 1.402 aristas.

## Matriz por superviviente

La lista exacta de nodeids vive una sola vez en el JSON compañero, bajo `function_test_associations`. Cada fila referencia esa clave para no duplicar asociaciones compartidas.

### `tools.wct.accept.generation.x_generate__mutmut_3`

- **Contrato afectado:** CONTRATO-AC1.md §«Adaptador pytest y compatibilidad»: conservar nombres exactos generados; §«Frontera y entrega»: generate sigue siendo el único escritor del archivo generado.
- **Diff directo (`mutmut show`):**
  ```diff
  -    payload = json.dumps(ir, ensure_ascii=False)
  +    payload = json.dumps(ir, ensure_ascii=None)
  ```
- **Asociación de tests:** `tools.wct.accept.generation.x_generate`; 5 nodeids (tests/unit/test_accept_pipeline.py: 3, tests/unit/test_accept_pytest.py: 2). Lista exacta: JSON `function_test_associations["tools.wct.accept.generation.x_generate"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_TECNICO_EN_RUNTIME_ACOTADO`. La comprobación del runtime registra igualdad de json para `Café Ñ`; la sonda compara bytes UTF-8 generados y el stdout completo.
- **Precondiciones/límite:** Runtime original Python 3.13.14. `json.dumps(..., ensure_ascii=None)` conserva la salida de la API actual igual que `False` para el IR observado, incluido texto no ASCII.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la equivalencia técnica no autoriza una exención ni modifica la política.
- **Incremento mínimo futuro:** `FUT-RUNTIME-ALIASES`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.generation.x_generate__mutmut_63`

- **Contrato afectado:** CONTRATO-AC1.md §«Adaptador pytest y compatibilidad»: conservar nombres exactos generados; §«Frontera y entrega»: generate sigue siendo el único escritor del archivo generado.
- **Diff directo (`mutmut show`):**
  ```diff
  -    output.write_text(source, encoding="utf-8")
  +    output.write_text(source, encoding="UTF-8")
  ```
- **Asociación de tests:** `tools.wct.accept.generation.x_generate`; 5 nodeids (tests/unit/test_accept_pipeline.py: 3, tests/unit/test_accept_pytest.py: 2). Lista exacta: JSON `function_test_associations["tools.wct.accept.generation.x_generate"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_TECNICO_EN_RUNTIME_ACOTADO`. El runtime registra `codecs.lookup('utf-8') == codecs.lookup('UTF-8')`; la sonda escribe y lee bytes no ASCII.
- **Precondiciones/límite:** Runtime original Python 3.13.14; ambos literales resuelven al codec canónico `utf-8`.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la equivalencia técnica no autoriza una exención ni modifica la política.
- **Incremento mínimo futuro:** `FUT-RUNTIME-ALIASES`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.generation.x_scenario_names__mutmut_14`

- **Contrato afectado:** CONTRATO-AC1.md §«Adaptador pytest y compatibilidad»: conservar nombres exactos generados; §«Frontera y entrega»: generate sigue siendo el único escritor del archivo generado.
- **Diff directo (`mutmut show`):**
  ```diff
  -        f"test_{index:03d}_{re.sub(r'[^a-z0-9_]+', '_', scenario['name'].lower()).strip('_')}"
  +        f"test_{index:03d}_{re.sub(r'[^a-z0-9_]+', '_', scenario['name'].lower()).strip('XX_XX')}"
  ```
- **Asociación de tests:** `tools.wct.accept.generation.x_scenario_names`; 21 nodeids (tests/unit/test_accept_pipeline.py: 3, tests/unit/test_accept_pytest.py: 18). Lista exacta: JSON `function_test_associations["tools.wct.accept.generation.x_scenario_names"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_TECNICO_POR_NORMALIZACION`. La sonda usa un nombre con `__`, Ñ, espacios y dos puntos y compara `scenario_names` y el archivo generado; la deducción cubre todo resultado de la normalización actual.
- **Precondiciones/límite:** La normalización actual aplica `lower()` y luego `re.sub(r'[^a-z0-9_]+', '_', ...)` antes de `strip`. Ese resultado sólo contiene `[a-z0-9_]`; no contiene `X`, por lo que los conjuntos de caracteres de `strip('_')` y `strip('XX_XX')` coinciden efectivamente.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se infiere una autorización de cambios textuales desde el resultado equivalente.
- **Incremento mínimo futuro:** `FUT-NORMALIZATION`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.mutation_cases.x_mutations__mutmut_7`

- **Contrato afectado:** CONTRATO-AC1.md §«Ejecución acotada y resultado de campaña»: enumerar una vez por celda con orden e identidad del IR preservados.
- **Diff directo (`mutmut show`):**
  ```diff
  -        for row_index, row in enumerate(scenario.get("examples", [])):
  +        for row_index, row in enumerate(scenario.get("examples", None)):
  ```
- **Asociación de tests:** `tools.wct.accept.mutation_cases.x_mutations`; 55 nodeids (tests/unit/test_accept_pipeline.py: 9, tests/unit/test_accept_pytest.py: 11, tests/unit/test_accept_verdict.py: 35). Lista exacta: JSON `function_test_associations["tools.wct.accept.mutation_cases.x_mutations"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_PRECONDICION_DEL_IR_CANONICO`. Con la clave presente y una lista, los defaults `[]`, `None` y omitido no se observan. La sonda incluye un Outline y un Scenario sin filas y compara `mutations(ir)` completo.
- **Precondiciones/límite:** El IR llega desde `parse_feature` por la frontera AC1. Cada Scenario público se crea con `examples: []`; no se promete aquí aceptar un diccionario IR manual y malformado sin esa clave.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA_DE_LA_FRONTERA_IR; no convertir ausencia de clave en contrato sin decisión explícita.
- **Incremento mínimo futuro:** `FUT-IR-CANONICO`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.mutation_cases.x_mutations__mutmut_9`

- **Contrato afectado:** CONTRATO-AC1.md §«Ejecución acotada y resultado de campaña»: enumerar una vez por celda con orden e identidad del IR preservados.
- **Diff directo (`mutmut show`):**
  ```diff
  -        for row_index, row in enumerate(scenario.get("examples", [])):
  +        for row_index, row in enumerate(scenario.get("examples", )):
  ```
- **Asociación de tests:** `tools.wct.accept.mutation_cases.x_mutations`; 55 nodeids (tests/unit/test_accept_pipeline.py: 9, tests/unit/test_accept_pytest.py: 11, tests/unit/test_accept_verdict.py: 35). Lista exacta: JSON `function_test_associations["tools.wct.accept.mutation_cases.x_mutations"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_PRECONDICION_DEL_IR_CANONICO`. Con la clave presente y una lista, los defaults `[]`, `None` y omitido no se observan. La sonda incluye un Outline y un Scenario sin filas y compara `mutations(ir)` completo.
- **Precondiciones/límite:** El IR llega desde `parse_feature` por la frontera AC1. Cada Scenario público se crea con `examples: []`; no se promete aquí aceptar un diccionario IR manual y malformado sin esa clave.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA_DE_LA_FRONTERA_IR; no convertir ausencia de clave en contrato sin decisión explícita.
- **Incremento mínimo futuro:** `FUT-IR-CANONICO`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.x_parse_feature__mutmut_9`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
  +    for number, raw in enumerate(path.read_text(encoding="UTF-8").splitlines(), 1):
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.x_parse_feature`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.x_parse_feature"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_TECNICO_EN_RUNTIME_ACOTADO`. El runtime registra igualdad de codec y la sonda parsea `Café`, `Ñ` y un nombre con dos puntos usando ambos mutantes.
- **Precondiciones/límite:** Runtime original Python 3.13.14; ambos literales resuelven al codec canónico `utf-8`.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la equivalencia técnica no autoriza una exención ni modifica la política.
- **Incremento mínimo futuro:** `FUT-RUNTIME-ALIASES`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ__init____mutmut_2`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.feature = ""
  +    self.feature = None
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ__init__`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ__init__"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. La sonda combina Background, Outline, Examples, Scenario normal, caracteres no ASCII y fila malformada; el IR, diagnóstico y resultado generado coinciden. La fuente muestra que `_examples` reestablece headers y que Scenario/Background reestablecen el flag.
- **Precondiciones/límite:** La entrada atraviesa el ciclo público `parse_feature` → `_Parser.consume`. Los valores mutados son falsy o se reescriben antes del primer uso observable; `in_examples` sólo se consulta por truthiness.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la representación privada no se eleva automáticamente a contrato exacto.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ__init____mutmut_7`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.headers: list[str] = []
  +    self.headers: list[str] = None
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ__init__`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ__init__"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. La sonda combina Background, Outline, Examples, Scenario normal, caracteres no ASCII y fila malformada; el IR, diagnóstico y resultado generado coinciden. La fuente muestra que `_examples` reestablece headers y que Scenario/Background reestablecen el flag.
- **Precondiciones/límite:** La entrada atraviesa el ciclo público `parse_feature` → `_Parser.consume`. Los valores mutados son falsy o se reescriben antes del primer uso observable; `in_examples` sólo se consulta por truthiness.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la representación privada no se eleva automáticamente a contrato exacto.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ__init____mutmut_8`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.in_examples = False
  +    self.in_examples = None
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ__init__`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ__init__"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. La sonda combina Background, Outline, Examples, Scenario normal, caracteres no ASCII y fila malformada; el IR, diagnóstico y resultado generado coinciden. La fuente muestra que `_examples` reestablece headers y que Scenario/Background reestablecen el flag.
- **Precondiciones/límite:** La entrada atraviesa el ciclo público `parse_feature` → `_Parser.consume`. Los valores mutados son falsy o se reescriben antes del primer uso observable; `in_examples` sólo se consulta por truthiness.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la representación privada no se eleva automáticamente a contrato exacto.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_examples__mutmut_13`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.headers = []
  +    self.headers = None
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_examples`; 89 nodeids (tests/unit/test_accept_pipeline.py: 10, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_examples"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. La sonda combina Background, Outline, Examples, Scenario normal, caracteres no ASCII y fila malformada; el IR, diagnóstico y resultado generado coinciden. La fuente muestra que `_examples` reestablece headers y que Scenario/Background reestablecen el flag.
- **Precondiciones/límite:** La entrada atraviesa el ciclo público `parse_feature` → `_Parser.consume`. Los valores mutados son falsy o se reescriben antes del primer uso observable; `in_examples` sólo se consulta por truthiness.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la representación privada no se eleva automáticamente a contrato exacto.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_17`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -            "line": number,
  +            "XXlineXX": number,
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. Los campos `line`, `steps` y `examples` de ese dict no salen al IR canónico por esta ruta. La sonda observa Background más escenarios y obtiene IR, nombres y bytes idénticos.
- **Precondiciones/límite:** El dict mutado representa sólo el estado temporal de Background durante el ciclo público. `_target` usa `self.background` para Background; `_examples` rechaza Background antes de acceder a sus examples; Background no se añade a `scenarios` del IR final.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se rebaja el compromiso público de Background, sólo se delimita el estado temporal no observable.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_18`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -            "line": number,
  +            "LINE": number,
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. Los campos `line`, `steps` y `examples` de ese dict no salen al IR canónico por esta ruta. La sonda observa Background más escenarios y obtiene IR, nombres y bytes idénticos.
- **Precondiciones/límite:** El dict mutado representa sólo el estado temporal de Background durante el ciclo público. `_target` usa `self.background` para Background; `_examples` rechaza Background antes de acceder a sus examples; Background no se añade a `scenarios` del IR final.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se rebaja el compromiso público de Background, sólo se delimita el estado temporal no observable.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_19`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -            "steps": self.background,
  +            "XXstepsXX": self.background,
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. Los campos `line`, `steps` y `examples` de ese dict no salen al IR canónico por esta ruta. La sonda observa Background más escenarios y obtiene IR, nombres y bytes idénticos.
- **Precondiciones/límite:** El dict mutado representa sólo el estado temporal de Background durante el ciclo público. `_target` usa `self.background` para Background; `_examples` rechaza Background antes de acceder a sus examples; Background no se añade a `scenarios` del IR final.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se rebaja el compromiso público de Background, sólo se delimita el estado temporal no observable.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_20`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -            "steps": self.background,
  +            "STEPS": self.background,
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. Los campos `line`, `steps` y `examples` de ese dict no salen al IR canónico por esta ruta. La sonda observa Background más escenarios y obtiene IR, nombres y bytes idénticos.
- **Precondiciones/límite:** El dict mutado representa sólo el estado temporal de Background durante el ciclo público. `_target` usa `self.background` para Background; `_examples` rechaza Background antes de acceder a sus examples; Background no se añade a `scenarios` del IR final.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se rebaja el compromiso público de Background, sólo se delimita el estado temporal no observable.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_21`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -            "examples": [],
  +            "XXexamplesXX": [],
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. Los campos `line`, `steps` y `examples` de ese dict no salen al IR canónico por esta ruta. La sonda observa Background más escenarios y obtiene IR, nombres y bytes idénticos.
- **Precondiciones/límite:** El dict mutado representa sólo el estado temporal de Background durante el ciclo público. `_target` usa `self.background` para Background; `_examples` rechaza Background antes de acceder a sus examples; Background no se añade a `scenarios` del IR final.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se rebaja el compromiso público de Background, sólo se delimita el estado temporal no observable.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_22`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -            "examples": [],
  +            "EXAMPLES": [],
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. Los campos `line`, `steps` y `examples` de ese dict no salen al IR canónico por esta ruta. La sonda observa Background más escenarios y obtiene IR, nombres y bytes idénticos.
- **Precondiciones/límite:** El dict mutado representa sólo el estado temporal de Background durante el ciclo público. `_target` usa `self.background` para Background; `_examples` rechaza Background antes de acceder a sus examples; Background no se añade a `scenarios` del IR final.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se rebaja el compromiso público de Background, sólo se delimita el estado temporal no observable.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_header__mutmut_23`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -        self.in_examples = False
  +        self.in_examples = None
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_header`; 107 nodeids (tests/unit/test_accept_pipeline.py: 28, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_header"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. La sonda combina Background, Outline, Examples, Scenario normal, caracteres no ASCII y fila malformada; el IR, diagnóstico y resultado generado coinciden. La fuente muestra que `_examples` reestablece headers y que Scenario/Background reestablecen el flag.
- **Precondiciones/límite:** La entrada atraviesa el ciclo público `parse_feature` → `_Parser.consume`. Los valores mutados son falsy o se reescriben antes del primer uso observable; `in_examples` sólo se consulta por truthiness.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la representación privada no se eleva automáticamente a contrato exacto.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_row__mutmut_11`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -        raise ValueError(f"{self.path}:{number}: fila Examples sin escenario")
  +        raise ValueError(None)
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_row`; 86 nodeids (tests/unit/test_accept_pipeline.py: 7, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_row"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_ESTADO_INALCANZABLE_PUBLICAMENTE`. La fila Examples malformada alcanzable toma antes el diagnóstico de longitud exacto. La rama `current is None` no se alcanza desde la gramática pública; la sonda verifica el diagnóstico alcanzable y el análisis de transiciones explica la no alcanzabilidad.
- **Precondiciones/límite:** Sólo se considera la API pública `parse_feature`, no una llamada artificial a `_row` ni mutación externa de `_Parser`. `_row` sólo se invoca cuando `in_examples` es truthy; `_examples` lo activa únicamente con `current` no nulo y no Background; ninguna transición pública vuelve `current` a `None`.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA_DE_DEFENSA_INTERNA; decidir si ese diagnóstico debe hacerse alcanzable/contractual. No se declara eliminado ni irrelevante.
- **Incremento mínimo futuro:** `FUT-PARSER-DIAGNOSTIC`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_row__mutmut_18`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.current["examples"].append(dict(zip(self.headers, values, strict=True)))
  +    self.current["examples"].append(dict(zip(self.headers, values, strict=None)))
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_row`; 86 nodeids (tests/unit/test_accept_pipeline.py: 7, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_row"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_PRECONDICION_DE_LONGITUD`. Con longitudes ya iguales, `zip(strict=True)`, omitido, `None` o `False` producen el mismo mapeo. La sonda incluye una fila válida y una de longitud incorrecta, cuya excepción se observa antes de zip.
- **Precondiciones/límite:** En `_row`, `len(values) == len(headers)` se comprueba antes del único `zip` que construye una fila. La primera fila es header y retorna antes de ese `zip`.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se añade un test de estado interno sólo para forzar un mutante equivalente.
- **Incremento mínimo futuro:** `FUT-PARSER-STRICT`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_row__mutmut_21`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.current["examples"].append(dict(zip(self.headers, values, strict=True)))
  +    self.current["examples"].append(dict(zip(self.headers, values, )))
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_row`; 86 nodeids (tests/unit/test_accept_pipeline.py: 7, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_row"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_PRECONDICION_DE_LONGITUD`. Con longitudes ya iguales, `zip(strict=True)`, omitido, `None` o `False` producen el mismo mapeo. La sonda incluye una fila válida y una de longitud incorrecta, cuya excepción se observa antes de zip.
- **Precondiciones/límite:** En `_row`, `len(values) == len(headers)` se comprueba antes del único `zip` que construye una fila. La primera fila es header y retorna antes de ese `zip`.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se añade un test de estado interno sólo para forzar un mutante equivalente.
- **Incremento mínimo futuro:** `FUT-PARSER-STRICT`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_row__mutmut_22`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.current["examples"].append(dict(zip(self.headers, values, strict=True)))
  +    self.current["examples"].append(dict(zip(self.headers, values, strict=False)))
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_row`; 86 nodeids (tests/unit/test_accept_pipeline.py: 7, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_row"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_PRECONDICION_DE_LONGITUD`. Con longitudes ya iguales, `zip(strict=True)`, omitido, `None` o `False` producen el mismo mapeo. La sonda incluye una fila válida y una de longitud incorrecta, cuya excepción se observa antes de zip.
- **Precondiciones/límite:** En `_row`, `len(values) == len(headers)` se comprueba antes del único `zip` que construye una fila. La primera fila es header y retorna antes de ese `zip`.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; no se añade un test de estado interno sólo para forzar un mutante equivalente.
- **Incremento mínimo futuro:** `FUT-PARSER-STRICT`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.parsing.xǁ_Parserǁ_scenario__mutmut_18`

- **Contrato afectado:** CONTRATO-AC1.md §«Decisiones y alcance»: preservar rechazos, diagnósticos y líneas, Background, tipos Outline y orden/contenido del IR; este registro no convierte cada campo interno en contrato público.
- **Diff directo (`mutmut show`):**
  ```diff
  -    self.in_examples = False
  +    self.in_examples = None
  ```
- **Asociación de tests:** `tools.wct.accept.parsing.xǁ_Parserǁ_scenario`; 100 nodeids (tests/unit/test_accept_pipeline.py: 21, tests/unit/test_accept_pytest.py: 28, tests/unit/test_accept_verdict.py: 51). Lista exacta: JSON `function_test_associations["tools.wct.accept.parsing.xǁ_Parserǁ_scenario"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_BAJO_MAQUINA_DE_ESTADOS_PUBLICA`. La sonda combina Background, Outline, Examples, Scenario normal, caracteres no ASCII y fila malformada; el IR, diagnóstico y resultado generado coinciden. La fuente muestra que `_examples` reestablece headers y que Scenario/Background reestablecen el flag.
- **Precondiciones/límite:** La entrada atraviesa el ciclo público `parse_feature` → `_Parser.consume`. Los valores mutados son falsy o se reescriben antes del primer uso observable; `in_examples` sólo se consulta por truthiness.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la representación privada no se eleva automáticamente a contrato exacto.
- **Incremento mínimo futuro:** `FUT-PARSER-PRIVATE`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.semantic.x_phase_status__mutmut_3`

- **Contrato afectado:** CONTRATO-AC1.md §«Adaptador pytest y compatibilidad»: skip, xfail, error de colección/interno o fase incompleta son error, no killed.
- **Diff directo (`mutmut show`):**
  ```diff
  -    if wasxfail or outcome == "skipped":
  +    if wasxfail or outcome == "XXskippedXX":
  ```
- **Asociación de tests:** `tools.wct.accept.semantic.x_phase_status`; 16 nodeids (tests/unit/test_accept_pytest.py: 16). Lista exacta: JSON `function_test_associations["tools.wct.accept.semantic.x_phase_status"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_TECNICO_POR_FALLBACK_TOTAL`. Para `outcome == 'skipped'`, reemplazar la comparación inicial deja caer en `_failure`, que devuelve `error`; `wasxfail` sigue devolviendo `error` en ambos. La sonda cubre setup/call × passed/skipped/failed × wasxfail × excepción, incluido el caso canario wasxfail/passed.
- **Precondiciones/límite:** La implementación actual de `_failure` conserva su fallback `error` fuera del único mismatch semántico de call.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la equivalencia técnica no cambia el contrato de que skip es error.
- **Incremento mínimo futuro:** `FUT-SEMANTIC-FALLBACK`; véase el catálogo siguiente. No se implementa ahora.

### `tools.wct.accept.semantic.x_phase_status__mutmut_4`

- **Contrato afectado:** CONTRATO-AC1.md §«Adaptador pytest y compatibilidad»: skip, xfail, error de colección/interno o fase incompleta son error, no killed.
- **Diff directo (`mutmut show`):**
  ```diff
  -    if wasxfail or outcome == "skipped":
  +    if wasxfail or outcome == "SKIPPED":
  ```
- **Asociación de tests:** `tools.wct.accept.semantic.x_phase_status`; 16 nodeids (tests/unit/test_accept_pytest.py: 16). Lista exacta: JSON `function_test_associations["tools.wct.accept.semantic.x_phase_status"]`.
- **Observación original/mutante:** la corrida seleccionada r2b informó `survived`; la sonda original devolvió exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae`, y el mutante exit 0 / stdout `c69927c763d5a4413a0894587f50ac03849ea89778412038debe28bdfcf25fae` (`matches_original=true`).
- **Clasificación técnica:** `EQUIVALENTE_TECNICO_POR_FALLBACK_TOTAL`. Para `outcome == 'skipped'`, reemplazar la comparación inicial deja caer en `_failure`, que devuelve `error`; `wasxfail` sigue devolviendo `error` en ambos. La sonda cubre setup/call × passed/skipped/failed × wasxfail × excepción, incluido el caso canario wasxfail/passed.
- **Precondiciones/límite:** La implementación actual de `_failure` conserva su fallback `error` fuera del único mismatch semántico de call.
- **Decisión humana:** PENDIENTE_RATIFICACION_HUMANA; la equivalencia técnica no cambia el contrato de que skip es error.
- **Incremento mínimo futuro:** `FUT-SEMANTIC-FALLBACK`; véase el catálogo siguiente. No se implementa ahora.

## Catálogo de incrementos mínimos futuros (no implementados)

### `FUT-RUNTIME-ALIASES`

No añadir una prueba que finja distinguir una observación idéntica. Si una decisión humana exige fijar la grafía de `ensure_ascii` o de un codec, trátese como política/estilo explícita en un incremento separado; no como contrato funcional AC1 inventado.

### `FUT-NORMALIZATION`

No cambiar nada mientras se conserve la normalización actual. Si se cambia el orden de `lower`, `re.sub` o `strip`, añadir el borde público en `tests/unit/test_accept_pipeline.py`; no probar una variable privada sólo para matar este operador equivalente.

### `FUT-IR-CANONICO`

No añadir test para diccionarios IR malformados mientras la frontera sea `parse_feature`. Si se amplía `mutations` para aceptar IR externo sin `examples`, definir primero la semántica y cambiar de forma mínima `tools/wct/accept/mutation_cases.py` con su prueba de frontera en `tests/unit/test_accept_pipeline.py`.

### `FUT-PARSER-PRIVATE`

No añadir tests que muten `_Parser` internamente. Si se decide que alguno de esos estados debe ser observable, escribir primero un caso Gherkin/entrada pública en `tests/unit/test_accept_pipeline.py`; tocar `tools/wct/accept/parsing.py` sólo si esa conducta pública no puede expresarse sin producto.

### `FUT-PARSER-DIAGNOSTIC`

La decisión mínima es humana: conservar `fila Examples sin escenario` como defensa interna o hacerla alcanzable por gramática pública. Sólo en la segunda opción: caso público en `tests/unit/test_accept_pipeline.py` y ajuste mínimo de `tools/wct/accept/parsing.py`; no forzar `_row` directamente.

### `FUT-PARSER-STRICT`

No añadir un test de implementación mientras la comprobación de longitud anteceda a `zip`. Si se modifica esa precondición, fijar el caso de fila de Examples despareja en `tests/unit/test_accept_pipeline.py` y conservar el diagnóstico público exacto.

### `FUT-SEMANTIC-FALLBACK`

No añadir una aserción artificial para dos retornos iguales. Si cambia `_failure` o se amplía la matriz de outcomes/fases, extender el caso observable en `tests/unit/test_accept_pytest.py`, en particular las combinaciones skip/wasxfail.

## Preflight futuro de asociaciones

El siguiente incremento es independiente de que se ratifiquen o no estas equivalencias. Debe fallar cerrado ante cualquier función instrumentada sin nodeids asociados; no debe excluir módulos, alterar gobernanza ni reutilizar resultados.

- **Prototipo de evidencia no versionado:** `build/tmp/ac1-r2-qualification/r2b-adjudication/preflight_associations.py` (`b7fd59cfe3a29ed302206ef43cfc5d9bd11a78dd868f778e483b789858fdbb13`).
- **Resultado observado:** r2 `FAIL-missing-test-associations` (tools.wct.accept.semantic.x__failure, tools.wct.accept.semantic.x_phase_status, tools.wct.accept.semantic.x_scenario_status); r2b `PASS` con 22/22 funciones.
- **Rutas exactas propuestas para un incremento autorizado futuro:** `tools/wct/accept/mutation_preflight.py` y `tests/unit/test_accept_mutation_preflight.py`. La receta del próximo lote debe invocarlo contra `build/tmp/ac1-r2-qualification/mutation-code-lot-r3/mutants/mutmut-stats.json` antes de aceptar/ejecutar el lote.
- **Regla propuesta:** comparar exactamente las claves de `function_hashes` con `tests_by_mangled_function_name`; lista ausente, no-lista o lista vacía es fallo. Informar las funciones y el módulo derivado del nombre mangled; salir no cero. No añadir exclusiones ni editar `governance/**`, workflows o configuración de mutmut.

## Decisiones humanas pendientes

- **H-01 — ¿Ratificar, rechazar o pedir evidencia adicional para cada clase de equivalencia técnica?** Hasta entonces los 24 conservan estado humano pendiente; L1/L1b no cuenta como ratificación de r2/r2b.
- **H-02 — ¿La entrada IR externa sin la clave examples queda fuera de contrato o debe tener semántica explícita?** Sólo la ampliación exige el incremento FUT-IR-CANONICO.
- **H-03 — ¿El diagnóstico interno fila Examples sin escenario debe permanecer defensa inalcanzable o convertirse en comportamiento público?** Sólo la segunda opción autorizaría FUT-PARSER-DIAGNOSTIC.
- **H-04 — ¿Se autoriza implementar el preflight propuesto antes de un lote futuro?** Su objetivo es bloquear asociaciones incompletas sin editar gobernanza ni excluir semantic.py.

## Artefactos crudos preservados

Los resultados originales siguen siendo la evidencia primaria y no se reescribieron. Sus SHA-256 son:

- `mutation-code-lot-r2-plan.json`: `8c3572e8ea4f6ccfcebd9ff50f9d59bda8f0daf0936bcfcc8e7db8aba1feaf5b`
- `mutation-code-lot-r2-preflight.log`: `fd06990e173b8f3ec02fe8c07527cf1d4179e93eeccf17997d5e26e18c489195`
- `mutation-code-lot-r2-reconciliation.json`: `225358094b113c5bf2f11ca4a67da76656c3cf9d186ad830e042203ac43e808b`
- `mutation-code-lot-r2-results-all.log`: `b5d2b3090c4beeabf798b0e8674f9561c49094cebd3357686233a04f4fd95e30`
- `mutation-code-lot-r2-run.json`: `45e7255fd1c315d4afec67a659dccd7132d845d4e43714e6b26f75277ec6d792`
- `mutation-code-lot-r2-run.log`: `1f47f9c071ae166c5b3e726e50a3c99dd12c17ba6055a16a2c1612fd22099304`
- `mutation-code-lot-r2-survivor-diffs.log`: `f83d1ff8602099b61c81e5c4770591082fcf110899e794b66a66d6710bc446d6`
- `mutation-code-lot-r2b-plan.json`: `34243faf14af68a253732e682e38afde2dd7fc91a41825bdc4cb9ac017bc4869`
- `mutation-code-lot-r2b-preflight.log`: `e53e11cee19f9ba5303889bbadbe4fb1b14bad43226ffca4f4bc8914c9e6e2fa`
- `mutation-code-lot-r2b-reconciliation.json`: `d7658739162bc44077cf2562147b82c43db7fe65d8bd83481f7b65b7c4ed1876`
- `mutation-code-lot-r2b-results-all.log`: `bd48c8dfe6cf2726fe4869855c11b3104338e6375fd58ece3f47f981340d43df`
- `mutation-code-lot-r2b-run-tail.log`: `5116a2ceb868406afb2257c756f1b4005fce44595296d6bd67206cebe25a369f`
- `mutation-code-lot-r2b-run.json`: `09a6521576b1761a923d97ff75bcab997b4b2d8599ee5e3ac190be366c2d08c6`
- `mutation-code-lot-r2b-run.log`: `1de66473c5067fc0593b5d082223f5f1f0f77888e20c046eaf5285e9dffd0770`
- `mutation-code-lot-r2b-survivor-diffs.log`: `09408e7237cfabb4b4657c47e950a54a5cc95070f95719e04a228e31427811d6`

La corrección de alcance y atribución se encuentra en `ADENDA-AC1-R2-R2B-ATRIBUCION-2026-09-13.md`; no modifica los resultados históricos.
