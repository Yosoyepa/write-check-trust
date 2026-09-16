# GS-3 — calificación de mutación de `tools/wct/gate/semgrep.py` (2026-09-15)

Ejecución del lote GS-3 sobre el corte congelado de la PR #53. **Resultado:
FAIL-survivors-stop — 74 killed + 34 survived de 108 mutantes**; los
supervivientes quedan conservados y su adjudicación pertenece a un incremento
separado. **Este lote no acredita AC1 ni beta.3, no cierra G-MUT y no
repara producto, tests, features ni gobernanza.** La PR #53 permanece en
borrador.

Antecedentes de solo lectura: `ANEXO-PREPARACION-GS3-2026-09-15.md` (receta
corregida P0–P12), `GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15.md` (lanzador
fail-closed e instrumento reutilizados), `GS2-REVALIDACION-Y-PREPARACION-CIERRE-2026-09-15.md`,
`REPARACION-INTEGRACION-GDEPS-GDEAD-2026-09-15.md` y
`MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md`.

## 0. Corte, alcance y custodia

- Corte autorizado y medido: `eec71fb1a1dc502b3ab7d557893fcdae4a33be2b`
  (local == origin al ejecutar; PR #53 OPEN, borrador).
- Alcance exclusivo: `tools/wct/gate/semgrep.py`, sha256
  `0126c4e1bdad3a445a3d3821b46cdd75d1ebec6e2d080ab299fd8d2ebd682657`
  (sin deriva pre/post; la condición de BLOQUEO del anexo no se activó).
- Runtime: `build/tmp/sh-p01-CND-80B8/.venv` — Python 3.13.14, mutmut 3.7.0,
  pytest 9.1.1, semgrep 1.174.0, git 2.55.0. Sin instalaciones ni sync.
- Copia aislada: clon `file://` + `checkout --detach` en
  `build/tmp/gs3.PDSK9G/checkout`; árbol limpio salvo el `pyproject.toml`
  experimental (solo `[tool.mutmut]`, sha256 `c8676dfd…`), que no se devuelve
  al producto.
- Expediente local sellado `build/tmp/gs3.PDSK9G`: manifiesto `gs3.sha256`
  (259 miembros, sin auto-hash; verificación 259/259) con digest separado
  `63c83bd2db9af58f4044957bd3a3b4c94cc87bfc94afdfb1ced258fb5b03b990`.
  **Custodia durable: este documento**; la evidencia bajo `build/tmp/` es
  local y temporal.
- Estado E4 (redacción autorizada): «GS-2: atribución pendiente y residuos
  resueltos mediante evidencia sucesiva; sin nueva campaña conjunta ni
  acreditación integral de AC1».

## 1. Baseline e instrumento (sobre A)

- Colección real: 49 nodeids de `tests/unit/test_sast_targets.py`; baseline
  **49 passed, 0 skipped, 0 xfail, exit 0** (12.47 s); semgrep y git
  resueltos en `PATH` (los 4 tests con guard no saltan).
- Configuración experimental: `only_mutate = ["tools/wct/gate/semgrep.py"]`,
  `source_paths = ["tools"]`, `also_copy = ["src", "features",
  "governance"]`, selección focal y `-m "not property"`; `mutants/`
  pre-poblado por tar (lección RECETA-FASE-G P3b).
- Lanzador fail-closed `sonda-fc.sh` (`3a4b7888…`) e instrumento temporal
  `instrumento.py` (`26e44b52…`): ID completo del inventario, asociaciones
  legibles, selección no vacía, nodeids verificados, entorno saneado antes de
  asignar el modo, modo explícito, cwd/PYTHONPATH dentro de la copia, timeout
  120 s y códigos 2–8.
- Negativos sin pytest: N1 (lanzador que no reasigna `MUTANT_UNDER_TEST`)
  produce `INST-GS3 mutant_under_test=<AUSENTE>` con exit 0 → **no se cuenta
  como evidencia**; N2 inexistente→3, incompleto→1, prefijo ajeno→1;
  N3 asociaciones vacías→2, selección vacía→4, nodeid fuera→5.
- Canario `x__topology__mutmut_1` (`completed = None`): control original exit
  0 (14.595 s); mutante exit 1 (2.599 s) con `AttributeError: 'NoneType'
  object has no attribute 'returncode'` (`semgrep.py:91`) y `FAILED
  test_binding_fixture_adversarial_raiz_propia`; activación acreditada
  (`mutant_under_test` == ID, `fuente` bajo `checkout/mutants`,
  `variante_en_tabla=mutants_x__topology__mutmut`, `selftest-esperado ==
  selftest-leido`).

## 2. Inventario: métricas separadas

| Métrica | Valor | Fuente |
|---|---|---|
| Funciones AST | 3: `_topology`, `_policy`, `gate_sast_semgrep` (0 decoradas) | `evidence/inventario-ast.txt` |
| Sitios WCT (motor productivo) | **51** = `<module>` 17 + `_topology` 13 + `_policy` 6 + `gate_sast_semgrep` 15 | idem |
| Mutantes generados por mutmut | **108** = 26 `x__topology` + 8 `x__policy` + 74 `x_gate_sast_semgrep` | `evidence/ids-objetivo.txt` |
| Mutantes ejecutados | **108** (campaña serial, IDs explícitos) | `evidence/results-post.txt` |
| No instrumentable | código de módulo (17 sitios: `GATE_ID`, `COMMAND`, `__all__`): mutmut 3.7.0 no trampoliniza módulo | limitación instrumental declarada |

Gen-only admisible: exit 1 con la firma exacta `Filtered for specific mutants,
but nothing matches` (`__main__.py:1247`), «1 files mutated, 78 ignored,
0 unmodified», stats corrida y 0 «Running mutation testing»; snapshot previo
`evidence/mutmut-stats-pristine.json` (`git_commit == eec71fb1a1dc`,
3 funciones). Sin `print-time-estimates`.

## 3. Asociaciones y activación

- **108/108** IDs con asociación no vacía; 0 nodeids fuera de la colección;
  sin fallback a suite completa. Selecciones: `_policy` 2 tests;
  `_topology` y `gate_sast_semgrep`, 4 tests.
- Activación acreditada en **108/108** sondas mutantes: `mutant_under_test`
  == ID completo, `fuente` bajo `checkout/mutants/tools/wct/gate/semgrep.py`,
  `variante_en_tabla` no vacía y `selftest-esperado == selftest-leido`.
- Verifier independiente (puerta previa, PROC-005): **APROBAR-CAMPAÑA**;
  reejecutó los controles negativos sin escrituras (<0.1 s).

## 4. Calibración (primeros 10 IDs) y proyección

- `x__topology__mutmut_1..10`: 9 exit 1 (2.6–3.7 s) y 1 exit 0
  (`x__topology__mutmut_6`, `check=None` ≡ `check=False`, 16.177 s).
- Proyección declarada: medio observado 4.43 s/ID → 108 × 4.43 ≈ 479 s;
  cota conservadora 108 × 12.47 ≈ 1347 s. Consumido real de campaña: 479 s.

## 5. Campaña GS-3 (sobre A)

- `mutmut run --max-children 1 <108 IDs explícitos>`, ejecución fresca,
  serial; **exit 0 en 479 s**; los IDs calibrados no heredan resultados.
- Rejuego de conjuntos: inventario congelado == IDs ejecutados == IDs con
  resultado (108); 0 duplicados, 0 ajenos, 0 `not checked`.
- Corte post-run sin deriva: 8/8 rutas de producto y `semgrep.py`
  re-verificados; pyproject experimental intacto.
- Bruto mutmut: **74 killed + 34 survived**.

## 6. Atribución causal (sobre B)

- 108 sondas mutante frescas con el lanzador fail-closed (tras una
  interrupción del operador se re-ejecutó el ID invalidado `mutmut_64`).
  Sonda vs campaña: 74×exit 1 y 34×exit 0, sin cruces.
- **74/74 killed** con `FAILED`, causa mecánica y sin fallo de
  infraestructura (0 ImportError, 0 INTERNALERROR, 0 errores de colección).
  Tests que matan: 61 × `test_binding_fixture_adversarial_raiz_propia`,
  9 × `test_raiz_absorbida_por_ancestro_ajeno_es_error`,
  4 × `test_fallo_de_ejecucion_del_instrumento_es_error`.
- Familias de causa dominantes: `TypeError`/`AttributeError` por colapso de
  construcciones (`Popen`, `subprocess.run`, `classify`, `required_sources`)
  y cambios de veredicto (`Status.ERROR = Status.FAIL` y análogos).
- Clasificación completa por ID: `evidence/clasificacion.tsv`; diffs de las
  108 variantes: `evidence/diffs-completos.txt` (sha256 `67aa8607…`).

## 7. Supervivientes (FAIL-survivors-stop)

34 supervivientes con ID, diff, selección y resultado conservados
(`evidence/supervivientes.tsv`, `evidence/supervivientes-diffs.txt`).
Agrupaciones candidatas **no ratificadas** (la equivalencia o el gap se
deciden en la adjudicación):

| Grupo | IDs | Mecanismo | Sonda que falta |
|---|---|---|---|
| a | `x__topology__{6,11,20}`, `x_gate_sast_semgrep__{26,31}` | `check=False` → `None`/omitido/`True` | forzar fallo real de git (nonzero) |
| b | `x_gate_sast_semgrep__{24,29,33}` | `text=True` → `None`/`False`/omitido (bytes que `json.loads` acepta) | aserción de tipo de `stdout` |
| c | `x_gate_sast_semgrep__{6–13}` | campos de `GateResult` en rama SKIP (ruta muerta con semgrep presente) | `shutil.which` ausente |
| d | `x_gate_sast_semgrep__{43,46,50,53,54,55}` | campos/aritmética de `GateResult` en rama ERROR | aserción de `gate`/`duration_ms` |
| e | `x_gate_sast_semgrep__{56,59,60,61,65,66,67,69,70,71,74}` | campos y aritmética del retorno final (`GATE_ID`, duración, `details`, `command`, separador de `join`) | contrato del consumidor `runner.py` |
| f | `x__policy__mutmut_8` | mensaje del `SemgrepScopeError` (solo se asertó el tipo) | aserción del mensaje |

Ningún superviviente se reparó, ningún contrato se relajó y no se ratificó
ninguna equivalencia. El lote **no declara PASS de G-MUT ni de ningún gate**.

## 8. Presupuestos reales

| Sobre | Consumido | Tope | Detalle |
|---|---|---|---|
| A (instrumento, baseline, generación, calibración, campaña) | **~706.6 s (19.6 %)** | 3600 s | baseline 14 + gen 15 + inventario 2 + asociaciones 124 + launcher pre-campaña 72.5 + campaña 479 + verifier ~0.1 |
| B (atribución y sondas) | **~524.5 s (29.1 %)** | 1800 s | 108 sondas 510.361 + intento invalidado de `mutmut_64` ≤14.1 (re-ejecutado) |
| Revisión documental | aparte | — | verifier de puerta 0.1 s; verifier final 0 s de ejecución |

## 9. Dictamen independiente

- **Puerta previa**: **APROBAR-CAMPAÑA**; la campaña no arrancó sin dictamen.
  Salvedades documentales, todas explicadas y sin efecto sobre la ejecución:
  `sha256sum -c` da 8/9 en el árbol congelado porque `corte.sha256` fija el
  `pyproject.toml` pristino (`c3a1b3e7…`) y el árbol lleva la config
  experimental (`c8676dfd…`, copiada al expediente); `nodeids.txt` incluye
  2 líneas de resumen de pytest (inocuas para el launcher, que usa
  `grep -Fxq`); la etiqueta de calibración 44.3 s vs 41.729 s medidos;
  `gs3-run.txt` es bookkeeping del operador fuera del expediente; y la
  notación «N1 (18)» del paquete de puerta es un desliz de rotulación sin
  efecto (el artefacto `negctl-N1.log` es consistente). Los scripts usados
  sin hash en el borrador
  (`variantes.py` `09b75e02…`, negativo N1 `03498cbd…`) quedaron incorporados
  al sello.
- **Revisión final del expediente sellado**: **CONFORME CON RESERVAS**
  (R1–R4, menores, ninguna bloqueante): R1 cota del intento invalidado
  (14.099 s medidos), R2 N2/N3 sin log individual, R3 evidencia de
  supervivientes distribuida en ficheros, R4 `campaign-argv.txt` es registro
  normalizado. Modalidad: documental con reejecución de solo lectura; revisó
  100 % de sello, conjuntos, clasificación, causas, activación,
  infraestructura, presupuestos y los 34 diffs; por muestreo profundo 8
  killed + 6 supervivientes. Consumo del verifier: 0 s de A/B.
- El resultado **FAIL-survivors-stop queda debidamente sustentado** conforme
  al anexo GS-3 §7.5.

## 10. Siguiente incremento mínimo propuesto (no ejecutado)

Adjudicación de los 34 supervivientes en un lote separado, con decisión
humana previa y las sondas que el verifier señaló: ausencia forzada de
semgrep (grupo c), tipo de `stdout` (b), contrato del consumidor para
`details`/`command`/`duration_ms` (d/e), mensaje del raise (f) y `check=True`
ante fallo real de git (a). Sin reparaciones, cambios de contrato ni
ratificación de equivalencias dentro de este expediente.

Nada de este registro habilita bless, update-manifest, merge, bump, tag ni
release; PR #53 sigue en borrador con `commit-gates: FAILURE` por el drift
de integridad pre-bless (G-META-1/E9).
