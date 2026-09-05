# G1 — Registro durable de evidencia (REVIEW-G1 §10)

Todo hallazgo se atribuye por TIPO: **[O] observación** de proceso real sin
intervención · **[I] inyección** controlada en un artefacto real (válida
para representación/respuesta; no prueba ocurrencia natural) · **[L] lectura
de fuente** · **[INF] inferencia** a partir de medidos, con la cadena citada.
Los fixtures bajo `build/tmp/` son efímeros: este registro conserva comandos,
versiones y salidas clave para revisión sin reejecutar.

## Entorno

- mutmut **3.7.0** (`.venv/lib/python3.12/site-packages/mutmut/`,
  `__main__.py`, `mutation/data.py`); Python 3.12.13 (uv).
  Las citas de línea se refieren a ESA instalación; un hash de fuente no se
  registró en el turno original — reproducibilidad por versión declarada.
- Repo en `0f80122`; sondas corridas con `uv run python` (venv activo).

## Sondas y atribución

| Sonda | Comando | Tipo | Salida clave |
|---|---|---|---|
| P1 sano | `mutmut run` + `mutmut results` + `results --all true` | [O] | run exit 0; results **vacío** exit 0 (vacío válido); `--all true` lista `victim.calc.x_add__mutmut_1: killed` |
| P2 defectuoso | ídem, fixture billing/lonely | [O] | run exit **0** con 2 `survived` + 3 `no tests` en results |
| P3 cero mutables | ídem | [O] | run exit **1** "Stopping early… test case for any mutant" (guard del motor) |
| P4a meta corrupto | escribir JSON inválido → `mutmut results` | [I] en artefacto + [O] de la fase results **standalone** | exit 1, JSONDecodeError. **No es la secuencia completa del gate** (REVIEW-G1 §2) |
| P4b meta ilegible | chmod 000 → results | [I] + [O] standalone | exit 1, PermissionError |
| P4c metas borrados | unlink → results | [I] + [O] standalone | exit **0** y salida VACÍA (pérdida silenciosa) |
| P5bis caché | debilitar aserciones conservando llamadas → `mutmut run` | [O] (secuencia completa, gate real) | run exit 0 "0.00 mutations/second"; results vacío; **gate PASS** — falso verde E2E |
| P6bis selección | `mutmut run <nombre>` / patrón sin coincidencia | [O] | seleccionado re-ejecuta ("Mutant results / 🎉 …"); sin coincidencia → AssertionError exit 1 |
| P7/B vocabulario | plantar exits 2 y 34 en meta → results + gate | [I] (representación) | results imprime `check was interrupted by user`, `skipped`; **gate PASS** |
| P8 timeout | `n -= 1` → bucle infinito real | [O] (secuencia completa) | run exit 0 (17 s); results 2 `: timeout`; **gate PASS** — falso verde E2E |
| D3 frescura | debilitar aserciones conservando llamadas → `mutmut run '*'` literal | [O] (fixture único `build/tmp/g1a-freshness/`) | 28.06 mutations/second (re-ejecutó); results: ambos `survived` — la repetición pública derrota la herencia SIN borrar metas |
| Repo main | mtimes de `mutants/src/example/*.meta` (09:10) + G-MUT 1.8 s | [O] | reutilización de resultados REPORTADA; **validez con tests actuales NO acreditada** (REVIEW-G1 §3) |

## Correcciones fácticas incorporadas (vs primer dossier G1)

1. PR-E YA tiene control sano real: `test_clean_tree_passes_with_zero_survivors`
   (`tests/unit/test_gate_mutation.py:57`). G1a lo EXTIENDE (inventario),
   no lo duplica.
2. Herramienta ausente → `Status.SKIP` (`gate/mutation.py:43`) — no ERROR.
3. La tabla de estados son 1 aprobado (killed), 2 defectuosos (survived,
   no tests) y 7 fuera del contrato de certificación — no "ocho fallos".
4. El costo CI no es nulo: `gate_mutation` se ejecuta en CI vía
   `tests/unit/{test_gate_mutation,test_mutation_gate,test_gate_mut_tier,
   test_redteam_engine,test_report_profile}.py` y los casos redteam
   F2-a/F2-b/F5-b (`quality/redteam/cases-tool.yaml`). El fixture timeout
   real suma a suite, coverage y redteam.
5. exit 1 y exit 3 colapsan a `killed` (`__main__.py:82-104`): el inventario
   textual NO conserva causa (límite del claim G1a; G1b lo ataca).

## Delimitación de roles (REVIEW-G1 §10, final)

El rol **specifier** no ejecuta mutación (`.claude/agents/specifier.md`).
Las sondas de este dossier fueron ejecutadas como **arquitecto de
diseño** con autorización diagnóstica explícita del prompt de REVIEW-G1
("evalúa primero repetición pública…"); los fixtures históricos
`build/tmp/g1probe/` NO se recrearon ni modificaron (preservados como
evidencia; REVIEW-G1 los leyó en modo lectura). Directorio único nuevo:
`build/tmp/g1a-freshness/`.
