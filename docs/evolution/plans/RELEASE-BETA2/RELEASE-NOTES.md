# WCT v1.0.0-beta.2 — Controles más explícitos, evidencia más útil

WCT es un template y un arnés de calidad para desarrollo Python asistido por
IA. Esta beta endurece sus propios controles y hace más visible qué se ha
verificado, con qué herramientas y sobre qué alcance.

**Es una prerelease, no una versión GA.** Un proyecto que pasaba en beta.1
puede encontrar nuevos bloqueos: conviene revisar la actualización y
diagnosticar cada resultado antes de cambiar código o configuración.

## Novedades

- **Ratchets exigibles:** `wct ratchet check --require
  coverage-total,docstring-coverage` exige las mediciones indicadas sin
  desactivar las comparaciones de las demás. Conserva el modo tolerante.
- **CI con productor y consumidor de cobertura:** genera LCOV sin property,
  ejecuta inmediatamente el ratchet exigible y mantiene property en un paso
  propio. Once tests de contrato vigilan estos pasos y regresiones conocidas.
- **G-INTROVERT en commit:** la honestidad de las aserciones se comprueba
  antes del merge, con una regresión específica del escape #37/#38.
- **Mutación y red team productivos:** clasificación del inventario recibido
  del motor, verificación diferencial de sobrevivientes y corpus de 30
  adversarios basado en motores reales y hooks, sin casos declarados como
  heurísticos.
- **Reporte y configuración más transparentes:** cobertura del propio arnés,
  conformidad configuración/runtime y límites de los perfiles de verificación.
- **README renovado:** propuesta de valor, arranque, adopción y límites
  reorganizados; se conserva el GIF original. Tiers documentados: fast 7,
  commit 21, pr 27 y full 34.

## Actualización desde beta.1

1. Revisa el [CHANGELOG](https://github.com/Yosoyepa/write-check-trust/blob/v1.0.0-beta.2/CHANGELOG.md)
   y fija el tag o SHA de upstream que vas a adoptar.
2. En un proyecto con el arnés ya integrado, usa `adopt check` y `adopt sync`
   contra tu clon upstream. El segundo propone un parche; revísalo antes de
   aplicarlo. No copies baselines del ejemplo a un repositorio legacy.
3. Si incorporas el workflow, conserva la cadena de cobertura y el paso
   separado de property. Un ratchet exigible sin medición bloquea.
4. Diagnostica los rojos nuevos. Un falso positivo debe reportarse con
   evidencia; no se corrige silenciando controles o elevando umbrales.

La versión de Python normalizada del paquete es `1.0.0b2`; el tag de esta
prerelease es `v1.0.0-beta.2`. El template declara Python 3.11–3.14 y su CI
usa Python 3.12; no se afirma una matriz multiversión verificada.

## Límites que se mantienen

- Mutación diferencial configurada en `src/example`, no en todo `tools/wct`.
- `--require` acredita presencia y umbral, no frescura o completitud por sí
  solo. La procedencia del LCOV depende de la corrida que lo genera.
- G1b (frescura, completitud y aislamiento de mutación) no está entregado.
- Los análisis estáticos pueden producir falsos positivos; los tests por
  subprocess tienen una limitación conocida en G-INTROVERT.
- Parsear Gherkin no equivale a ejecutar cada feature. La narrativa libre
  bajo `Feature:` sigue pendiente en #35; se usan comentarios.
- No se afirma un aumento causal de calidad o ahorro de modelos económicos.

Distribución: template por tag y GitHub prerelease. No publicación en PyPI
ni marketplace en esta salida. Política de madurez:
[RELEASES.md](https://github.com/Yosoyepa/write-check-trust/blob/v1.0.0-beta.2/RELEASES.md).
