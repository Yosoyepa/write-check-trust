# P02a — aceptación semántica no alcanzada por el runner histórico

Fecha: 2026-09-08. Autor: arquitecto. Candidato R3 `e4b25b2b…` conservado.

## Reproducción independiente

Desde `build/tmp/beta3-p02a-candidate`, runtime compartido sin sync y
`PYTHONPATH` apuntando al candidato:

```bash
uv run --no-sync wct accept generate features/wct-evidence-inputs-001.feature \
  --output build/tmp/p02a-accept-preflight.EaXAOu/test_generated.py
uv run --no-sync pytest -q build/tmp/p02a-accept-preflight.EaXAOu/test_generated.py \
  --basetemp build/tmp/p02a-accept-preflight.EaXAOu/pytest
```

Generación exit 0. Ejecución exit 1, **1 failed in 0.24s**:

```text
AssertionError: missing acceptance step: el repositorio temporal revisado del caso "IA01"
```

El fallo proviene de `tests/acceptance/steps.py:35`, antes de ejecutar la API
P02a. Es el control original sin mutaciones, no un mutante killed ni un defecto
demostrado de `capture_inputs`. El archivo generado queda como evidencia local;
la salida se conserva en esta transcripción del resultado real de la herramienta.

## Causa y riesgo de falso verde

El generador invoca el ejecutor del ejemplo de reserva de inventario, que no
entiende el vocabulario P02a. `run_mutations` considera killed cualquier exit
no cero y no verifica primero el caso sano. Lanzarlo así podría producir
un informe de detección enteramente debido a handlers ausentes.

El binding congelado `_assert_input_contract` sí controla estructura y
literales, pero lee el feature original y no consume `WCT_ACCEPT_IR`. Usarlo
sin adaptación como runner tampoco mide las mutaciones entregadas por el CLI.
Comparar 210 celdas mutadas contra una tabla fija mediría sensibilidad
estructural, no ejecución del comportamiento. No se lanza esa campaña redundante.

## Decisión

La autorización humana de los 54 supervivientes de código **no exceptúa**
aceptación. No continuar a CRAP/DRY/full como si esta etapa hubiera pasado.
Las pruebas API y binding previamente verdes conservan su alcance, sin sumar
ambas para afirmar ejecución semántica de las filas mutadas.

Se prepara un contrato focal de aceptación semántica bajo la delegación de
arquitectura existente, con control sano, entradas/expected consumidos del IR,
observaciones del SUT y errores del instrumento separados de rechazos válidos.
No se autoriza editar el candidato congelado ni modificar el ejecutor general
o las reglas para ocultar esta carencia. Bless/publicación siguen pendientes.

Feedback para futuros moldes: preflight del runner sano y prueba de que consume
el IR mutado deben ocurrir **antes** de lanzar campañas o declarar readiness;
el nombre de un gate y un exit no cero no prueban discriminación semántica.
