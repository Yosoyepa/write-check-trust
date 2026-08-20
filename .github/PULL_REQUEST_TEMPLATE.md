## Qué hace este PR

<!-- Una frase del comportamiento observable que cambia. -->

## Evidencia

- [ ] Test escrito primero que fallaba antes del cambio (TDD)
- [ ] `uv run wct gate --tier fast` verde — pega la última línea de salida
- [ ] `uv run wct gate --tier commit` corrido — pega el resultado real,
      aunque falle (los fallos esperados se explican abajo)

## Control plane

- [ ] No toqué rutas protegidas, umbrales ni baselines
- [ ] Si toqué rutas protegidas: entiendo que G-META-1 llega rojo a propósito
      y que el mantenedor bendice tras la revisión
- [ ] Si cambié funciones del motor: corrí `uv run wct mutate update-manifest`
      (sin flags de aprobación)

## Comportamiento observable

- [ ] Si cambia comportamiento visible, hay escenario Gherkin en `features/`
      con parámetros para todo campo que pueda variar
