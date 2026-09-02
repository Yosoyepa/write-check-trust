# ADR-B-02 — Cuatro claves nuevas en thresholds.yaml + conformidad visible en doctor

Estado: propuesto — **incluye edición de governance/thresholds.yaml: requiere
tu autorización explícita; la aprobación de este plan la constituye y el bless
del PR la blinda** (SEC-005).

## Contexto

4 constantes runtime no tienen clave declarada (ANALYSIS §2): la declaración
"TODOS los números viven aquí" es falsa para ellas. Y la conformidad
declarado↔runtime no es auditable con un comando.

## Decisión

### 1. Claves nuevas (diff exacto a aplicar en governance/thresholds.yaml)

Dentro de la sección `dry:` existente (a continuación de `min_nodes:`):

```yaml
  # Fase β-1 (PR #21): umbral de clones de plantilla (Jaccard sobre AST
  # anonimizado). DEFAULT_TEMPLATE_THRESHOLD antes huérfano en dry/tpl.py.
  template_threshold: 0.90
  # Fase β-1 (PR #21): score de revisión manual sugerida para clones por
  # tokens. review_threshold antes huérfano en dry/analyzer.py.
  review_threshold: 0.95
```

Sección nueva al final del archivo:

```yaml
# ---------------------------------------------------------------------------
# LCOM4 — cohesión de clases
# Fuente: Hitz & Montazeri (1995), "Measuring coupling and cohesion in
# object-oriented systems". Fase β-1 (PR #21), advisory con ratchet.
# ---------------------------------------------------------------------------
lcom:
  # Clases con menos métodos no se evalúan (LCOM4 trivial). MIN_METHODS
  # antes huérfano en lcom/engine.py.
  min_methods: 3
  # LCOM4 >= umbral cuenta como poco cohesiva. LCOM_THRESHOLD antes huérfano
  # en lcom/engine.py.
  threshold: 2
```

Los valores replican los literales actuales: **cero cambio de comportamiento**.

### 2. Cableado de las claves nuevas

`dry/tpl.py`, `dry/analyzer.py` y `lcom/engine.py` leen sus valores vía
`load_config` (o los reciben del gate/caller como parámetro con el contrato de
clave-ausente-falla de ADR-B-01 §3 — la forma exacta la fija el SPEC según el
house-style de cada módulo). Los literales mueren.

### 3. `wct doctor`: sección de conformidad

Doctor gana una sección "Umbrales declarados → gates" que lista EN VIVO (lee
thresholds.yaml, sin lista estática) cada clave cableada por PR-B con su valor
efectivo y el gate que la consume: crap.changed_max, coverage.diff_min,
dead_code.vulture_min_confidence, complexity.xenon_max_*, dry.min_lines,
dry.min_nodes, dry.template_threshold, dry.review_threshold, lcom.min_methods,
lcom.threshold (+ coverage-total baseline de A2 si ya lo muestra). La sección
es advisory: doctor no bloquea, informa.

## Alternativas consideradas

- **(a) Dejar las 4 constantes en código y solo inventariarlas**: rechazada —
  perpetúa la mitad del defecto; el costo de declararlas es un diff bendecido.
- **(b) Doctor con detector automático de "claves sin consumidor"**: rechazada
  por ahora — exige un mapa consumers↔claves mantenible (análisis de código o
  registro declarativo nuevo); el inventario del ANALYSIS cumple el rol hasta
  que el Horizonte 0 decida activar/deprecar/retirar. La sección en vivo de
  claves cableadas no rota porque lee el YAML real.
- **(c) Migrar TODAS las claves huérfanas de una vez**: rechazada — mezcla
  cableado mecánico con decisiones de producto (perfiles, mutación operativa);
  cada una con su PR/ADR propio.

## Consecuencias

- thresholds.yaml pasa a ser la fuente única de verdad para 9 umbrales del
  harness (5 cableados + 4 declarados) — auditables con `wct doctor`.
- La edición de governance queda autorizada por la aprobación de este plan y
  con rastro en integrity-log vía bless del PR.
- Adoptantes ven en doctor exactamente qué números gobiernan sus gates.
