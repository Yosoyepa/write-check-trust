# Addenda de cierre documental — SH-P01 / CND-74E0

```text
addenda_id: ADN-E61F            # local opaco, generada en esta corrida
tipo: cierre documental; NO es candidato nuevo ni reparación de producto
task_id: SH-P01
contract_version: sh-p01/1
run_id / candidate_id referenciados: SHR-27687E / CND-74E0 (coder COD-CA7A)
parent_candidate_id (cadena completa): CND-74E0 ← CND-80B8 (REQUIERE_CORRECCION)
acta citada: reviews/REVIEW-CND-74E0.md (SHP01-REVIEW-CND-74E0,
  dictamen CONFORME_AL_CONTRATO en el alcance técnico de SH-P01)
acta del padre: reviews/REVIEW-CND-80B8.md (REQUIERE_CORRECCION, R01–R05)
mode: SH-D
base_sha: 8de9107184288f1aa72c9578a14913686c47ad7c
fecha: 2026-09-07T19:04:54-05:00 (UTC-05:00)
asistencia: diagnóstico del arquitecto (dos actas); esta addenda es trabajo
  documental del coder; ningún registro previo ni documento normativo fue
  editado; ningún archivo de producto/tests/feature/gobernanza fue cambiado.
```

## 1. Identidad de los bytes al cierre (verificada hoy)

Desde `build/tmp/sh-p01-CND-74E0` (rama `codex/beta3-sh-p01-identidades-r1`,
HEAD `8de9107`, 4 entradas intent-to-add, sin otros cambios):

```text
d89be6c7fa40a8f6ed21953414140c223a335a9477fdeb8145595e5c80829e5e  tools/wct/evidence/__init__.py
b7594a3c22f165655308272f680da32c8849640f3e271aa56e405b1f46dc867f  tools/wct/evidence/identities.py
1db53b953d60f19fddb3514dd04ec40882dbf98a03322f87c32ba59ae63088b1  tests/unit/test_evidence_identities.py
d3d64140477e5b67e6ee1f6967fe9cb0c4c285365b562b953043a0056b251b0e  features/wct-evidence-identities-001.feature
```

Agregado con la serialización acordada (UTF-8, dos espacios, rutas relativas
en el orden del acta, LF final):

`909e58a71e9477ccc25822823f8b3615225b68fec713cf03e22be4ccabc09cb4` — sin
drift respecto del handoff R1 y del acta de revisión. Este dictamen cubre
estos bytes y no otros.

## 2. L01 — causa histórica del digest `de207e0d…`: CONFIRMADA con comando
y bytes; mi explicación de R1 era incorrecta

En el registro R1 escribí que `de207e0d…` provenía de «rutas absolutas».
Esa hipótesis es FALSA, como mostró el reviewer (`01a1c071…` con rutas
absolutas; `fae236bb…` sin LF final; ninguno coincide). La causa real,
reproducida hoy desde la raíz compartida del repo:

```bash
cd /home/jandradeu/Documents/well_code_template && sha256sum \
  build/tmp/sh-p01-CND-80B8/tools/wct/evidence/__init__.py \
  build/tmp/sh-p01-CND-80B8/tools/wct/evidence/identities.py \
  build/tmp/sh-p01-CND-80B8/tests/unit/test_evidence_identities.py \
  build/tmp/sh-p01-CND-80B8/features/wct-evidence-identities-001.feature \
  | sha256sum
# → de207e0dc06a995918d5a8f34917744e53aae9e17c97c2aad483a7ee797e86b4
```

Serializaciones en juego (los bytes de los cuatro archivos son idénticos en
las tres; solo cambia el TEXTO de las rutas dentro de las líneas hasheadas):

| Serialización | cwd | Prefijo de ruta en las líneas | Digest |
|---|---|---|---|
| Fórmula del acta (correcta) | worktree del candidato | relativo al worktree | `e3a64265…` |
| Comando original de R0 | raíz compartida del repo | `build/tmp/sh-p01-CND-80B8/…` | `de207e0d…` (reproducido hoy) |
| Intento del reviewer | — | rutas absolutas | `01a1c071…` (su captura) |

Conclusión: el digest histórico NO evidencia alteración de archivos; fue un
error de serialización del manifiesto en R0 (rutas con prefijo del worktree
dentro de la raíz compartida, en lugar de la fórmula declarada). La identidad
de CND-74E0 (`909e58a7…`) y del padre (`e3a64265…`) no está cuestionada. El
registro R0 y el R1 no se editan: esta addenda es la corrección de certeza.

## 3. L03 — atribución de corridas de ratchets

- **Coder (mi sesión R1):** ejecuté y reporté únicamente
  `wct ratchet check --require coverage-total` → exit 0, «medidas 1 de 1
  exigibles» (`build/tmp/sh-p01-CND-74E0-evidence/ratchet-require.txt`),
  además del modo tolerante (`ratchet-tolerant.txt`, exit 0). **No ejecuté
  `--require all`**: omisión registrada, subsanada por el reviewer, no
  reescrita en mi historial.
- **Reviewer:** ejecutó `wct ratchet check --require all` → exit 0,
  **medidas 10 de 10** (acta REVIEW-CND-74E0 §3, captura
  `r1check-ratchets-all.txt` en `build/tmp/sh-p01-r1-review.dbuKI7/`). Esa
  corrida NO es mía y no la atribuyo a mi sesión.
- **Procedencia del LCOV, sin sobreafirmar frescura:**
  - LCOV **focal**: el recién producido por el reviewer es byte-idéntico al
    mío, sha256 `15adcdb0479cfc7c424004fe8d156f2dc33ddddc988d9de904069f62bb78246f`.
  - LCOV **global** consumido por el 10/10 del reviewer: el ENTREGADO POR MÍ
    en R1, sha256 `cdccbe33f605aae94ca052d56f355c4effc3e19f80d6a12f56d1d75363ae45e0`
    (receta productiva sin property: 404 passed, 1 deselected, 113.61s);
    el reviewer NO lo regeneró. Baseline vigente 74.5, sin cambios.
  - Para CI sobre un futuro SHA hay que producir nuevamente el LCOV global y
    consumirlo en el mismo job; el 10/10 de este worktree no se traslada
    automáticamente a otro commit.

## 4. L02 — límite del binding, conservado como está

El binding de `tests/unit/test_evidence_identities.py` acredita el inventario
de filas/casos (cantidad, unicidad, pertenencia) y las celdas estado/
hallazgos/contrato. **NO comprueba** la clase del escenario (flag
`Scenario Outline` vs `Scenario`), el texto de los pasos ni la ejecución de
nada: eso lo demostraron las sondas del reviewer (58 verdes ante esos cambios
de texto). El feature actual SÍ fue cotejado verbatim (lectura y hash del
reviewer). Queda prohibido describir este binding como prueba completa de
semántica, verbatim o ejecución. El seguimiento (ampliar contrato del binding/
ensamblaje, con P06 conservando la puerta de ejecución) es propuesta del
arquitecto en incremento separado; no es condición para otra reparación de
producto de este candidato y NO se implementa aquí.

## 5. Estado de controles al cierre

- **G-META-1 permanece rojo, declarado, pre-bless**: drift exactamente en
  `tools/wct/evidence/__init__.py` y `tools/wct/evidence/identities.py` (las
  dos rutas nuevas de producto contratadas). No se ejecutó `update-manifest`,
  no se tocaron locks ni governance, y no se inventó aprobación de `yosoyepa`.
- Sin commit, push, PR, bless ni publicación. Sin número de PR inventado.
- Producto/tests/feature: sin cambios en este cierre (solo esta addenda).

## 6. Frontera propuesta para una futura PR (decisión humana pendiente)

**Núcleo de producto (los 4 archivos P01, únicos cambios de código respecto
de `8de9107`):**

1. `tools/wct/evidence/__init__.py`
2. `tools/wct/evidence/identities.py`
3. `tests/unit/test_evidence_identities.py`
4. `features/wct-evidence-identities-001.feature`

**Expediente de evidencia elegible — el humano decide qué incluir:**

- `docs/evolution/plans/BETA3/SELF-HOSTING/runs/SHR-015D6C-CND-80B8.md` (handoff R0)
- `docs/evolution/plans/BETA3/SELF-HOSTING/runs/SHR-27687E-CND-74E0.md` (handoff R1)
- `docs/evolution/plans/BETA3/SELF-HOSTING/runs/ADENDA-E61F-CND-74E0.md` (esta addenda)
- `docs/evolution/plans/BETA3/SELF-HOSTING/reviews/REVIEW-CND-80B8.md`
- `docs/evolution/plans/BETA3/SELF-HOSTING/reviews/REVIEW-CND-74E0.md`
- Dossier normativo de la pieza, si se quiere que la PR sea autocontenida:
  `P01-IDENTIDADES.md`, `GHERKIN-P01.md`, `GOBERNANZA.md`, `MOLDE-WCT.md`,
  `REGISTROS.md`, `PROMPT-CODER.md`, `PROMPT-CND-80B8-R1.md`,
  `PROMPT-CIERRE-CND-74E0.md` y demás documentos BETA3 citados.

**Dejado fuera expresamente:** toda documentación ajena con estado sin commit
en el árbol compartido (`docs/evolution/README.md` modificado,
`docs/evolution/plans/G1/**`, `POST-PR36/**`, `REVIEW-G1/**` y el resto del
dossier BETA3 no citado arriba). Ninguna entrada de governance/, workflows ni
generated.

**Artefactos grandes (fuera de la PR, en `build/tmp/`, gitignored):**

| Artefacto | Referencia / hash |
|---|---|
| Worktree padre | `build/tmp/sh-p01-CND-80B8` (agregado `e3a64265…`) |
| Worktree hijo | `build/tmp/sh-p01-CND-74E0` (agregado `909e58a7…`) |
| Patch padre (archivado por reviewer) | `candidate-CND-80B8.patch`, sha256 `460ca37f…` (acta del padre §3) |
| Patch hijo (archivado por reviewer) | `candidate-CND-74E0.patch`, sha256 `635adce1…` (acta R1 §7) |
| Evidencia del coder R0/R1 | `build/tmp/sh-p01-CND-80B8-evidence/`, `build/tmp/sh-p01-CND-74E0-evidence/` |
| Sondas de revisiones | `build/tmp/sh-p01-review.UuPr1u/`, `build/tmp/sh-p01-r1-review.dbuKI7/` |

Su custodia externa aún NO debe darse por hecha: son locales, gitignored y
perdibles ante una limpieza; si el expediente debe sobrevivir, el humano
decide su archival externo.

## 7. Qué NO significa este cierre

Dictamen técnico conforme ≠ beta.3 terminada, ≠ autorización de PR/commit/
push/bless, ≠ evaluación económica: preservar R0 (no conforme), R1 (conforme)
y la asistencia declarada para imputar costes del workflow completo cuando el
custodio aporte recibos. Telemetría del modelo: sigue unavailable para el
coder; identidad del modelo oculta.

```text
next_action: lectura humana/separada del diff exacto (4 archivos + expediente
  elegido); si hay PR, producir LCOV global nuevo para ese SHA antes de
  consumir ratchets y verificar el diff aprobado; bless: autoridad separada.
```
