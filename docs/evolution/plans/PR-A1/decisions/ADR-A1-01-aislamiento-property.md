# ADR-A1-01 — Aislamiento de property tests por marker y deselección por gate

Estado: propuesto (se ejecuta al aprobarse GHERKIN-A1.md).
Contexto: [ANALYSIS.md §1.1](../ANALYSIS.md) · [RESEARCH.md R1/R5](../RESEARCH.md).

## Contexto

TEST-008 (hard) exige que los property tests estén marcados con
`@pytest.mark.property` y fuera de coverage, mutación, CRAP y aceptación.
Hoy: marker declarado sin uso, G-COV-TOTAL los ejecuta (colección vía
`testpaths=["tests"]`), y mutmut los corre por mutante (selección explícita
en `pyproject.toml:82-88`). G-TEST los excluye por accidente de rutas; G-PROP
los ejecuta dedicadamente (correcto).

## Decisión

1. Marcar los módulos bajo `tests/property/` con `pytestmark =
   pytest.mark.property` a nivel de módulo (no decorator por test: un módulo
   nuevo sin marker rompería el contrato inadvertidamente — el marker por
   módulo es el que el test de contrato puede verificar).
2. Las invocaciones de **G-COV-TOTAL** y **G-TEST** añaden
   `-m "not property"`. G-TEST ya no los corre por rutas; la bandera convierte
   el aislamiento de incidental a contractual (si mañana alguien marca un test
   en tests/unit, G-TEST tampoco lo correrá).
3. **G-PROP no recibe bandera alguna**: sigue ejecutando `tests/property`.
4. Se retira `"tests/property/test_inventory_properties.py"` de
   `pytest_add_cli_args_test_selection` (pyproject).
5. CRAP y aceptación no requieren cambio: CRAP se calcula sobre cobertura por
   rama del diff (la cobertura ya queda corregida por 2), y la aceptación
   corre tests generados de escenarios, no property.

## Alternativas consideradas

- **(a) `addopts` global `-m "not property"`**: rechazada. `addopts` se aplica
  a TODA invocación de pytest, incluida G-PROP — habría que re-marcarse con
  `-m property` en el gate dedicado y en cada corrida manual de la suite.
  Una exclusión global con excepciones por comando es más frágil que
  exclusiones explícitas en los dos gates que deben excluir.
- **(b) `--ignore=tests/property` en G-COV-TOTAL**: funciona hoy pero es
  frágil ante reorganización de directorios (si property migra a
  `tests/unit/properties/`, el ignore muere silenciosamente y el marker
  sigue vivo). El marker viaja con el test; la ruta no.
- **(c) `coverage omit` de líneas específicas**: no aplica — omit excluye
  fuentes medidas, no ejecución de tests (ver R1); el defecto es de colección.
- **(d) No aislar, aceptar la contaminación como menor** (1 solo test):
  rechazada por principio: el contrato es del mecanismo, no del censo actual;
  el siguiente property test heredaría el hueco gratis.

## Consecuencias

- La cifra de cobertura pasa a reflejar solo la suite unit/integration/CRAP:
  medido, sin efecto numérico hoy (73 % → 73 %; ANALYSIS §2).
- El tiempo por mutante de mutmut baja (sin hypothesis + shrinking por
  mutante).
- `pyproject.toml` (protegido) se toca → cubierto por el bless único del PR.
- Tests de contrato (SPEC-A1-01) aserten las **invocaciones construidas** de
  los gates, no la mera presencia del marker — un marker sin exclusión sería
  falsa sensación de aislamiento.
