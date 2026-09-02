# ADR-B-01 — Los gates construyen sus comandos desde thresholds.yaml

Estado: propuesto (se ejecuta al aprobarse GHERKIN-B.md).
Contexto: [ANALYSIS.md §1](../ANALYSIS.md).

## Contexto

5 claves de thresholds.yaml tienen equivalente literal en gates y no las lee
nadie. La cabecera del YAML instruye bendecir los cambios de umbral — pero
cambiarlos no altera comportamiento alguno. Además, `crap.profiles` declara
umbrales full-repo por perfil que ningún gate consume.

## Decisión

1. **Patrón de cableado = A2**: cada gate afectado pasa de `external()` estático
   a función dinámica cuyo comando se construye en `checks.py` leyendo
   `load_config(root)`; `runner.py` solo registra y ejecuta (respeto al margen
   G-SIZE de runner.py).
2. **5 cableados**: `crap.changed_max` → G-CRAP `--max-crap`;
   `coverage.diff_min` → G-COV-DIFF `--fail-under`;
   `dead_code.vulture_min_confidence` → G-DEAD `--min-confidence`;
   `complexity.xenon_max_{absolute,modules,average}` → G-CC flags;
   `dry.min_lines`/`dry.min_nodes` → parámetros de G-DRY-TPL.
3. **Contrato de clave ausente**: si la clave falta o es ilegible, el gate
   FALLA nombrando la clave esperada — mismo contrato que G-COV-TOTAL con su
   baseline (A2): el gate nunca corre con un valor por defecto silencioso.
   Excepción: claves de G-DRY-TPL (motor AST interno, no comando externo) —
   el engine de `dry/tpl.py` recibe los valores como parámetro desde el gate
   con el mismo contrato de fallo explícito.
4. **Valores actuales preservados**: los fixtures de regresión asertan que con
   el YAML vigente los comandos son idénticos a los de hoy. PR-B no cambia
   ningún umbral — solo quién es la fuente.

## Alternativas consideradas

- **(a) Consumir `crap.profiles` resolviendo `policy.profile`**: rechazada por
  ahora — no existe gate full-repo de CRAP que la consuma; el único gate CRAP
  es de código cambiado y la propia YAML lo documenta ("No depende del
  perfil"). Inventar el consumidor es alcance nuevo → backlog con nota.
- **(b) Inyectar solo defaults en `external()` (comando base + overrides)**:
  rechazada — mezcla fuente estática y dinámica; el comando dejaría de ser
  auditable en un solo lugar.
- **(c) Un wrapper genérico "plantilla de comando con placeholders"**: rechazada
  — sobre-ingeniería para 5 gates; cada función dinámica es ~15 líneas legibles
  (A2 lo demostró).
- **(d) Dejar los literales y solo documentar la divergencia**: rechazada — es
  el statu quo que el dossier clasificó como defecto (config que miente).

## Consecuencias

- Subir `crap.changed_max` de 6 a 8 (con bless) pasa a tener efecto real — la
  gobernanza recupera autoridad sobre los números.
- Los gates cableados ganan una lectura de YAML por corrida (µs; sin impacto
  de presupuesto).
- tests de regresión fijan los comandos actuales: cualquier drift futuro
  entre YAML y comando rompe suite, no producción silenciosa.
