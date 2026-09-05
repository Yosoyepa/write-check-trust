# VERIFICATION — PR-C: DoD de merge y secuencia humana

> DoD por feature/workstream/commit/revisión en [DoD.md](DoD.md).

## Definition of done (merge)

1. Escenarios de [GHERKIN-C.md](GHERKIN-C.md) aprobados y aterrizados.
2. DoD-F1/F2/F3 completos (mapeo criterio→evidencia en cada handoff).
3. Matriz completa con salida real + presupuesto de runtime.
4. PR abierto enlazando el plan.

## Matriz de verificación

| Verificación | Comando | Criterio |
|---|---|---|
| Suite | `uv run pytest -q` | 228 base + nuevos, 0 failed |
| Red team completo | `uv run wct selftest redteam` (quality group instalado) | 30/30 con conteos por arnés: 10 engine · 12 tool · 4 hook · 4 heuristic; **0 SKIP** con tools presentes |
| Red team sin tools | mismo comando con PATH sin las herramientas (o contenedor mínimo) — verificado vía tests con which falseado | 12 SKIP visibles listados; 18/30 rechazados; exit ≠ silencio |
| Tier fast / commit | `wct gate --tier fast` / `--tier commit` | 7 PASS / solo G-META-1 (tools/wct sin bless) |
| Tier pr (post-bless) | `wct gate --tier pr` | 26 PASS — G-REDTEAM dentro de presupuesto |
| Presupuesto runtime | delta de `selftest redteam` vs captura paso 0.2 | **≤ +25 s** con tools presentes; sin tools, ≤ baseline |
| Aceptación | `wct accept parse` | EXIT=0 |

## Predicciones falsables

- `selftest redteam` con quality group: `30/30` con el desglose por arnés —
  la palabra "rechazados" ya no cubre heurísticas sin etiqueta.
- Sin herramientas externas: exactamente 12 SKIP nombrados, 0 falsos
  rechazados.
- **Falsos negativos posibles**: si algún motor productivo no caza su
  defecto plantado, el caso queda ROJO y el PR lo declara en el handoff —
  es el primer hallazgo real de la calificación del instrumento (O-002) y
  se decide: defecto del motor (issue) o expectativa irreal (ajuste como
  propuesta documentada). El PR NO se fuerza a verde escondiendo el caso.
- Runtime del tier pr: G-REDTEAM ≈ baseline +≤25 s.

## Secuencia humana (bless único)

```bash
git checkout fix/redteam-productive
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: PR-C red team productivo (plan docs/evolution/plans/PR-C)"
git add -A && git commit -m "chore: bless PR-C productive red team (PR #N)" && git push
```

## Post-merge

- El Horizonte 1 queda completo: reporte honesto (A1), self-measurement
  (A2), config con autoridad (B), calificación por adversarios reales (C).
- Los falsos negativos que haya destapado C alimentan el gate de decisión
  del roadmap ("rediseñar o degradar gates antes de medir modelos").
