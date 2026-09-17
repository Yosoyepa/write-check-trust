# GS-3 — contratos D1–D5, regresiones y equivalencias (2026-09-15)

Incremento posterior a la adjudicación (`ADENDA-GS3-ADJUDICACION-2026-09-15.md`).
Convierte los oráculos experimentales de los 27 supervivientes A+B en
regresiones permanentes, formaliza D1–D5, ratifica en alcance cuatro
equivalencias y documenta la investigación de las tres restantes.
**El bruto histórico no cambia: 108 = 74 killed + 34 survived. No se ejecutó
`mutmut run` ni la campaña completa; no se declara PASS de G-MUT, AC1 ni
beta.3; GS-3 no queda cerrado.**

## 0. Alcance del aviso

- Contratos D1–D5 agregados a `docs/gates.md` (§Contrato de `G-SAST-SEMGREP`)
  y trazados a cuatro Scenario Outlines nuevos en
  `features/wct-sast-targets-001.feature`, ejecutados por cuatro tests de
  binding en `tests/unit/test_sast_targets.py`.
- Sin cambios de producto, gobernanza, dependencias ni umbrales. La fuente
  `tools/wct/gate/semgrep.py` permanece en sha256
  `0126c4e1bdad3a445a3d3821b46cdd75d1ebec6e2d080ab299fd8d2ebd682657`.

## 1. Contratos formalizados (D1–D5)

| Decisión | Contrato | Escenario (feature) | Test |
|---|---|---|---|
| D1 | `G-SAST-SEMGREP` + `Status.SKIP` + summary exacto `herramienta ausente: semgrep`; sin acreditar `REGISTRY` | «La herramienta ausente produce un SKIP visible del gate» | `test_binding_la_herramienta_ausente_declara_skip_visible` |
| D2 | `git rev-parse` no-cero no aborta el preflight ni implica PASS ni oculta el resultado posterior; el rechazo por ancestro no cambia | «El preflight tolera un Git no cero acotado…» | `test_binding_el_preflight_tolera_git_no_cero_acotado` |
| D3 | `duration_ms` = milisegundos truncados entre inicio y construcción, en ERROR y retorno final; excluye SKIP | «La rama de error…» y «El retorno final…» | `test_binding_la_rama_de_error_expone_causa_y_duracion`, `test_binding_el_retorno_final_expone_duracion_y_comando` |
| D4 | `command` del retorno final = representación informativa con argumentos separados por un espacio; no promete uso en shell | «El retorno final…» | `test_binding_el_retorno_final_expone_duracion_y_comando` |
| D5 | policy ilegible → ERROR con summary que empieza por `governance/policy.yaml ilegible:` y conserva la causa | «La rama de error…» | `test_binding_la_rama_de_error_expone_causa_y_duracion` |

Detalles exigidos y cumplidos: D1 sustituye el punto de detección
(`shutil.which`) sin desinstalar Semgrep; D3 usa el punto de sustitución
existente (`semgrep.time.monotonic`) con reloj controlado, sin sleeps; D4 fija
un esperado independiente tipado en el Feature
(`semgrep --quiet --error --severity ERROR --config governance/semgrep --json`)
y conserva la aserción sobre el resultado público, con el argv realmente
invocado como corroboración secundaria; D5 usa un fallo determinista
(`ConfigError("causa determinista de lectura")`) y no fija la redacción de
terceros.

## 2. Regresiones de los 27 IDs A+B

Los 27 IDs (13 A + 14 B de la adjudicación) quedan cubiertos por las familias
de test anteriores. Sensibilidad demostrada sobre el **árbol mutante real**
(mismo generado sellado, sha256 `6dcf432d…`), con activación acreditada
in-process (`INST-GS3R`, `fuente_sha256` y `variante_en_tabla`):

| Familia | IDs | Test que los mata |
|---|---|---|
| E1 SKIP | 6,7,8,9,10,11 (A) + 12,13 (B) | `test_binding_la_herramienta_ausente_declara_skip_visible` |
| E2 Git | top_20 (B) | `test_binding_el_preflight_tolera_git_no_cero_acotado` |
| E5a ERROR | 43,46 (A) + 50,53,54,55 (B) | `test_binding_la_rama_de_error_expone_causa_y_duracion` |
| E6 policy | policy_8 (B) | `test_binding_la_rama_de_error_expone_causa_y_duracion` |
| E5b final | 56,59,60,65,66 (A) + 61,67,69,70,71,74 (B) | `test_binding_el_retorno_final_expone_duracion_y_comando` |

- Control original: verde (exit 0); 27/27 mutantes con `FAILED` en el test
  esperado y exit 1 (`evidence/sensibilidad-27-final.txt`,
  `evidence/probes/mutante/*.log|.meta`).
- No se re-corrieron los 74 kills históricos ni la campaña.
- La tabla de adjudicación se usó como punto de partida; los tests nuevos son
  permanentes y no dependen del arnés experimental.

## 3. Cuatro equivalencias ratificadas (D6 acotado)

Ratificadas **solo** para los IDs y el runtime inspeccionado (Python 3.13.14,
`subprocess.run` con `if check and retcode:`):

- `tools.wct.gate.semgrep.x__topology__mutmut_6` (`check=False` → `check=None`)
- `tools.wct.gate.semgrep.x__topology__mutmut_11` (`check` omitido)
- `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_26` (`check=None`)
- `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_31` (`check` omitido)

Evidencia estructural y de runtime en `evidence/equivalencias-ratificadas.txt`
(funciones del generado y líneas `+` de `diffs-completos.txt` del sello
coincidentes; semántica del falso documentada). Sondeos propios: `top_6` y
`top_11` tuvieron sonda E2 en la adjudicación; `gate_26` y `gate_31` se
sustentan en estructura y campaña con activación. En este incremento los
cuatro pasan los tests nuevos (exit 0, `evidence/ratificados-4-final.txt`).
**Alcance limitado**: no se extiende a `check=True` (top_20 es B y se mata).
**Revisión obligatoria** si cambian la fuente, el runtime o las precondiciones
relevantes.

## 4. Tres equivalencias pendientes: investigación bytes/string

IDs `mutmut_24` (`text=True`→`None`), `mutmut_29` (omitido) y `mutmut_33`
(`text=False`). No ratificadas por este encargo. Se ejecutó el gate real con
un instrumento fiel (binario `semgrep` falso que escribe bytes por stdout,
ejecutado por `subprocess.run` real), original y las tres variantes, con cinco
casos (`evidence/bytes-resultados.jsonl`):

| Caso | Original | Mutantes 24/29/33 | Dominio |
|---|---|---|---|
| JSON válido con no-ASCII (`café ☕`) | ERROR `error del instrumento` | idéntico | admitido (UTF-8 sin BOM): **equivalente** |
| JSON truncado | ERROR `salida ilegible` | idéntico | admitido: **equivalente** |
| UTF-8 inválido | `UnicodeDecodeError` | misma excepción y mensaje | fuera de dominio: mismo desenlace |
| BOM UTF-8 + JSON válido | ERROR `salida ilegible` | PASS | **fuera de dominio: diferencia observable** |
| BOM UTF-16 + JSON válido | `UnicodeDecodeError` | PASS | **fuera de dominio: diferencia observable** |

Conclusión: en el dominio admitido (salida JSON UTF-8 sin BOM, válida o
malformada) las tres mutaciones son observacionalmente equivalentes; las
diferencias existen solo ante entradas que no son salida contractual del
instrumento (BOM). No se cambió producto ni se inventó contrato; no se añadió
aserción sobre tipos internos. **Decisión humana mínima**: ratificar o
rechazar las tres con esta evidencia; mientras no se ratifiquen, GS-3 no se
declara cerrado.

## 5. Controles negativos del binding

Cuatro alteraciones temporales del Feature en la copia aislada bloquearon
(exit 1) en el test correcto: Examples vacío, fila retirada, fila duplicada y
campo alterado (`evidence/controles-binding.txt`, `control-final-*.log`).
El Feature fue restaurado (verificado por `cmp`).

## 6. Batería de integración (candidato final)

- `git diff --check`: limpio; solo 4 rutas previstas (tests, feature,
  `docs/gates.md`, este registro) más el hunk de la matriz.
- Colección: 664 tests en `tests/unit tests/integration tests/property`
  (la colección completa da 665 al añadir `tests/acceptance/generated`); focal `tests/unit/test_sast_targets.py`:
  **53 passed**; property: **1 passed**.
- Fast: **7/7 PASS**. Tier commit: **20 PASS + 1 FAIL esperado (G-META-1)**;
  causa real: pre-bless del lock de integridad (`vulture_whitelist.py`, deriva
  del commit `b4403c5`, ajena a este incremento). G-ACCEPT, G-INTROVERT,
  G-SUPPRESS, G-SIZE, G-COGNITIVE y G-DEPS en PASS.
- `evidence/focal-candidato.txt`, `fast-candidato.txt`,
  `tier-commit-candidato.txt`, `coleccion-candidato.txt`,
  `property-candidato.txt`.

## 7. Dictamen independiente y correcciones sucesoras

Verifier de solo lectura: **CONFORME CON RESERVAS (R1–R6, menores; autoriza
publicar)**. Atendidas antes de publicar:

- **R1**: el Scenario D2 ahora declara el paso del instrumento acotado que
  consume `payload`/`exit` (feature + binding actualizados).
- **R2**: `verifica-equivalencias.py` compara la línea `+` del diff sellado,
  no solo la presencia del bloque; evidencia regenerada.
- **R3**: `coleccion-candidato.txt` registra el comando exacto y su salida.
- **R4/R5/R6**: declaradas aquí: diferencias fuera de dominio de §4, G-META-1
  pre-bless de §6 y ratificación D6 acotada, sin tocar documentos sellados.

Tras R1–R3 se re-ejecutaron las sondas completas sobre el artefacto final
(2 controles originales, 54 sondas mutantes + 3 del verifier, 8 ratificados,
20 corridas bytes, 8 controles de binding).

## 8. Presupuesto y custodia

- Experimental: **95 corridas / 149.137 s de 900 s** (incluye intentos
  invalidados por la corrección R1, re-ejecuciones del verifier y controles
  negativos). `evidence/presupuesto-regr.tsv`.
- Expediente: `build/tmp/gs3-regr.2382315502` (local, temporal), manifiesto y
  digest al cierre; scripts efectivos: `sonda-regr.sh`, `instrumento.py`,
  `investiga-bytes.py`, `corre-bytes.sh`, `aplica-control.py`,
  `verifica-equivalencias.py`. Sellos históricos intactos (`gs3.PDSK9G`
  259/259 `63c83bd2…`; `gs3-adj.y9i6Rh` 99/99 `e2e1bd12…`).
- La evidencia durable es este registro; `build/tmp` es local y temporal.

## 9. Estado real

- D1–D5 formalizados e implementados; 27/27 A+B con regresión permanente y
  sensibilidad medida sobre el árbol mutante real.
- 4 equivalencias ratificadas en alcance; 3 pendientes de decisión humana con
  investigación completa (sin ratificar).
- GS-3 **no cerrado**; AC1 y beta.3 no declarados. Fast verde; tier commit con
  el único rojo pre-existente de G-META-1 (pre-bless ajeno).
