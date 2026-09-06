# ADR-G3a-02 — Ratchets exigibles: presencia verificada, umbral intacto, sin claims de frescura

Estado: **aceptado con ajustes obligatorios** (yosoyepa, 2026-09-05, encargo
G3a-1; sustituye la versión propuesta). Trazabilidad: encargo humano §3;
ANALYSIS §3; G1/EVIDENCE.md §addenda.

## Contexto

`ratchet check` omite en silencio métricas sin medición (measure.py:118-140)
y consume LCOV sin comprobar procedencia (medido: 3 días de antigüedad).
Un ratchet que no se midió no "se mantuvo": no opinó, y el verde lo calla.

## Contrato de `wct ratchet check --require`

1. **Entrada validada**: `--require` acepta SOLO nombres del inventario
   soportado o `all`. Lista vacía, nombre desconocido o duplicado → error
   de uso nombrando el problema y los nombres válidos. Los duplicados NO se
   colapsan en silencio (son error): un typo duplicado debe verse.
2. **Inventario explícito**: `all` = constante de código con las métricas
   SOPORTADAS (las 8 estáticas + docstring-coverage + coverage-total),
   INDEPENDIENTE de lo que una corrida particular logre medir. El
   inventario es la lista de lo exigible, no de lo medido.
3. **Bloqueo por tres causas distintas, todas nombrando la métrica**:
   exigible AUSENTE (sin medición en esta corrida: artefacto faltante o
   herramienta ausente, con el comando que la produce), exigible con
   medición INVÁLIDA, o nombre NO SOPORTADO (aunque se pida por lista).
4. **Presencia ≠ umbral, y exigir es ADITIVO** (corrección por hallazgo
   humano pre-bless, 2026-09-05): una exigible medida se comprueba IGUAL
   que hoy contra el baseline (compare productivo), y el modo exigible
   **conserva TODAS las comparaciones del modo tolerante** — `--require`
   añade obligaciones de presencia, jamás filtra ni apaga rojos
   existentes (`--require suppressions` con introverted por encima del
   baseline SIGUE rojo por introverted). "Medida pero por encima del
   baseline" y "no medida" son fallos distintos con textos distintos, sin
   líneas duplicadas. Fronteras probadas: presente y en baseline (verde),
   presente y por encima (rojo por umbral), ausente (rojo por presencia),
   y exigible-que-no-toca + otra métrica en rojo (el rojo sobrevive).
5. **Medición inválida bloquea** (corrección por hallazgo humano
   pre-bless): una exigible cuyo artefacto produce un dato IMPOSIBLE es
   bloqueo, no verdecito. Caso medido por el humano: LCOV con LH=2 sobre
   LF=1 → 200% que el parser actual acepta. El modo exigible valida
   coherencia de contadores por registro (0 ≤ LH ≤ LF, 0 ≤ BRH ≤ BRF,
   totales > 0) y rango del resultado [0, 100]; violación →
   `"<métrica>: medición inválida (…)"` nombrando el defecto del
   artefacto — texto distinto de ausencia y de umbral. **El modo tolerante
   conserva su comportamiento byte-compatible** (no hereda la validación:
   su contrato histórico queda intacto). El comando productor de
   coverage-total se alinea con la receta productiva del gate
   (`-m 'not property'`, checks.py:73-82) — un test ancla esa igualdad.
6. **Denominador y nombres publicados**: la salida exigible lista las
   métricas exigidas, las medidas y declara `medidas N de M exigibles`.
   Un verde siempre dice qué midió.
7. **Sin claim de frescura**: `--require` NO acredita que el LCOV provenga
   de esta corrida — solo que existe una medición y cumple el baseline.
   La procedencia es G3a-2 (orden de pasos del workflow) con contrato
   propio. Ningún texto del comando sugiere lo contrario.
8. **Baselines sin medidor, documentados no verificados**: si el baseline
   registra una métrica que esta corrida no puede medir (p. ej.
   coverage-total sin LCOV), el modo exigible la bloquea al exigirla y el
   reporte la lista como "no medida"; NUNCA se presenta como verificada.
9. **Modo sin `--require` byte-compatible**: salida y semántica idénticas
   a las actuales (modo exploratorio tolerante, sin endurecer a escondidas).

## Alternativas rechazadas

- Derivar `all` de `measurements()` (lo medido como lo exigible): makes
  absence self-justifying — exactamente el fallo que corrige este ADR.
- Guard de mtime como mecanismo de procedencia: racial y falseable; la
  procedencia estructural (orden de pasos) es G3a-2.
- Colapsar duplicados o ignorar desconocidos: esconde errores de tipeo del
  operador en un comando cuyo propósito es ser explícito.

## Consecuencias

- `--require` es un contrato de PRESENCIA y UMBRAL, no de frescura ni de
  completitud del artefacto: sus límites quedan declarados en el propio
  output/ayuda.
- G3a-2 (no autorizado aún) añadiría la procedencia por orden de pasos del
  workflow; sin ese paso, un LCOV rancio sigue pasando `--require` —
  limitación conocida y documentada, no oculta.
