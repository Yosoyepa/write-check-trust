# Acta REANCLAJE-11 — decisiones humanas D-A (ratificación acotada de 10 equivalencias) y D-B (excepción puntual TEST-002 para 2 mutantes) (2026-09-18)

Registro exacto de las decisiones humanas comunicadas en el encargo
REANCLAJE-11, capítulos «Decisiones humanas de este encargo» (D-A, D-B y
D-CAMPAÑA). **La autoridad de este acta es ese encargo humano.** El verifier
independiente comprueba fidelidad de la transcripción y vigencia de las
premisas; no concede ni amplía autorizaciones. Las decisiones quedan
registradas ANTES de la ejecución de la campaña (encargo §2/§11); su
publicación es posterior a la revisión final.

## 0. Identidad de la base y artefactos de referencia

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base autorizada | `96e304393c83fc78e730c00133bb0bc6b49fbb27` = headRefOid PR #56 (OPEN, borrador) = origin `codex/reanclaje-p03a-fase1` | `gh pr view 56` + `git ls-remote` al iniciar el encargo |
| main / merge-base | `8a379d64ba13bbe43a707fcfd8df0ea336dd97ed` = baseRefOid = merge-base; sin avance remoto posterior al corte | `git ls-remote` + `git merge-base` |
| Manifiesto REANCLAJE-10 | `MANIFIESTO-REANCLAJE10.sha256`, digest `3d965a5271066cf8d32d47eecb52109304babdd56a3cd15c43b65e566ae6bbb5`, 24/24 miembros OK | `sha256sum` + `sha256sum -c` |
| Selección congelada | `logs/03-seleccion-futura-L2.nodeids` de R10, digest `e8dcdff18e4ba85d742f401a3f88ec5454188e721cbcd63da3de80d1b5c65c17`, 141 nodeids únicos (112 schema + 28 PA02/PA03 + PA01-unicode) | `sha256sum` + conteo por prefijo |
| Fuentes (identidad por diff) | diffs de los 12 IDs extraídos byte-exactos del artefacto ORIGINAL R7 `logs/16-survivors-diffs.txt` (sellado en `MANIFIESTO-REANCLAJE7.sha256`, digest `4687309f…`); la transcripción R10 `logs/01-diffs-residuos.txt` fue cotejada hunko a hunko contra él: 12/12 EXACTOS | comparación por script, ambos archivos intactos |
| Precedente de excepción | `ACTA-DECISIONES-FINALES-Y-QACCMUT-2026-09-16.md` §3 (excepción humana puntual a TEST-002 por registro explícito en acta, sin tocar gobernanza) | lectura del documento versionado en la base |

Fuentes afectadas y hashes (sha256, medidos en el candidato; byte-idénticos
al sello R8 `candidate-r8.sha256`):

- `tools/wct/evidence/pytest_wire_composites.py` —
  `8977f5b4532834a984db188c3c34dd4c1413761a81d9e6c31ee844e7e461c9ca` (IDs 1–3).
- `tools/wct/evidence/pytest_wire_framing.py` —
  `a6261613accc69fc2ffe322b02342d6bf6a919b2d930ea3800202d1b8225f562` (IDs 4–12).

Runtime fijado para L2: Python 3.13.14, pytest 9.1.1, mutmut 3.7.0.

## 1. Transcripción fiel de la decisión D-A — ratificación acotada

Texto operativo de la autorización humana (encargo REANCLAJE-11):

> «D-A — Ratificación acotada. Ratifico las diez equivalencias propuestas en
> REANCLAJE-10 §4, exclusivamente sobre las fuentes, contratos, runtime y
> precondiciones allí identificados. […] Toda ratificación debe volver a
> revisión si cambia la fuente relevante, el contrato, el runtime o alguna
> precondición. Un nuevo inventario requiere correspondencia por diff, no
> transferencia por número.»

Alcance y límites globales de D-A (transcritos): la ratificación NO cubre
llamadas directas arbitrarias a `canonical_bytes` ni futuros callers sin las
validaciones citadas; NO declara equivalencia para entradas NaN/Infinity que
sí alcancen `json.dumps`; no cubre los grupos A3 con callers fuera de los
actuales.

## 2. Transcripción fiel de la decisión D-B — excepción puntual TEST-002

Texto operativo de la autorización humana (encargo REANCLAJE-11):

> «D-B — Excepción puntual TEST-002. Conservo el comportamiento actual del
> producto y NO establezco contratos nuevos para: 1. `_DefectError.__init__`,
> mutante 1: `super().__init__(code)` → `super().__init__(None)`. 2.
> `_DefectError.__init__`, mutante 3: `self.execution_id = execution_id` →
> `self.execution_id = None`. Autorizo una excepción humana puntual a TEST-002
> para esos dos mutantes, mediante registro explícito en acta, siguiendo el
> precedente documentado en ACTA-DECISIONES-FINALES-Y-QACCMUT-2026-09-16.md
> §3.»

Ámbito, invalidantes y límites transcritos en §5.2. **No son equivalencias
ratificadas ni kills: permanecen en el bruto con el resultado realmente
observado. No se modifica globalmente TEST-002, ningún umbral, baseline,
detector ni archivo de gobernanza. La excepción no autoriza otros IDs.**

## 3. Registro por ID — equivalencias ratificadas (D-A)

Diff, fuente y hash por ID provienen del artefacto original sellado
(R7 `logs/16-survivors-diffs.txt`; cotejo 12/12 exacto contra la
transcripción R10). El fundamento es el razonamiento estructural/empírico de
REANCLAJE-10 §4, ratificado por la decisión humana.

### Grupo A1 — Subsumción por validación contractual (composites)

Fundamento (D-A, transcrita): «las cadenas cortas afectadas siguen siendo
rechazadas con invalid_field por las validaciones de cwd absoluto y formato
UTC. No es equivalencia universal fuera del dominio wire.»

| # | Identificador completo histórico | Diff (original → mutante) | Fuente / hash |
|---|---|---|---|
| 1 | `tools.wct.evidence.pytest_wire_composites.x__cwd__mutmut_5` | `text = _s(value, min_len=1)` → `text = _s(value, )` | composites `8977f5b4…` |
| 2 | `tools.wct.evidence.pytest_wire_composites.x__utc__mutmut_5` | `text = _s(value, min_len=1)` → `text = _s(value, )` | composites `8977f5b4…` |
| 3 | `tools.wct.evidence.pytest_wire_composites.x__utc__mutmut_6` | `text = _s(value, min_len=1)` → `text = _s(value, min_len=2)` | composites `8977f5b4…` |

- **Clase**: equivalencia ratificada (D-A, grupo A1).
- **Precondiciones**: entradas `str` del dominio wire (las no-`str` ya son
  rechazadas por el type-check de `_s`); contrato §3 de PROPUESTA-P03
  (`47429b88…` congelado) — cwd absoluto POSIX (l.209) y utc con formato
  exacto de 32 caracteres (l.230-233); runtime fijado.
- **Fundamento**: `min_len` solo puede divergir en cadenas de longitud 0
  (mutantes 5) o 1 (mutante 6); el check contractual posterior
  (`not text.startswith("/")`; `_UTC_RE.fullmatch` de 32 chars) rechaza
  exactamente esas cadenas con el mismo `invalid_field` (subsumido).
- **Invalidantes**: reordenar `_cwd`/`_utc` (check contractual antes del
  tamaño); relajar el formato absoluto/regex; cambio de fuente, contrato o
  runtime; nuevo inventario sin correspondencia por diff.
- **Evidencia citada**: R10 §4.1 (texto de ratificación propuesto, ratificado
  por D-A); sondas R8 sin divergencia; diffs sellados R7 logs/16;
  bruto R7: los tres IDs `survived`.

### Grupo A2 — Parámetros falsy de json (framing)

Fundamento (D-A, transcrita): «ensure_ascii=None y allow_nan=None conservan
la semántica de False en la implementación de json del runtime fijado. La
segunda equivalencia no depende de que NaN sea inalcanzable.»

| # | Identificador completo histórico | Diff | Fuente / hash |
|---|---|---|---|
| 4 | `tools.wct.evidence.pytest_wire_framing.x_canonical_bytes__mutmut_3` | `ensure_ascii=False` → `ensure_ascii=None` | framing `a6261613…` |
| 5 | `tools.wct.evidence.pytest_wire_framing.x_canonical_bytes__mutmut_6` | `allow_nan=False` → `allow_nan=None` | framing `a6261613…` |

- **Clase**: equivalencia ratificada (D-A, grupo A2).
- **Precondiciones**: stdlib `json` de CPython del runtime fijado
  (Python 3.13.14); semántica de truthiness de parámetros.
- **Fundamento**: `None` es falsy; `json.dumps` trata `ensure_ascii=None` y
  `allow_nan=None` igual que `False` — serialización byte a byte idéntica
  (incluido `dumps(nan)` raisiendo `ValueError` con `allow_nan=None`).
- **Invalidantes**: una implementación json que distinga `None` de `False`;
  cambio de runtime; cambio de fuente.
- **Evidencia citada**: R10 §4.2 (verificación de salidas idénticas «R10»);
  sondas R8 sin divergencia; diffs sellados R7 logs/16; bruto R7: survived.

### Grupo A3 — Inalcanzabilidad bajo callers actuales (framing)

Fundamento (D-A, transcrita): «canonical_header recibe datos validados;
_parse_line consume el resultado de _loads, que rechaza floats mediante
parse_float y constantes no finitas mediante parse_constant.»

| # | Identificador completo histórico | Diff | Fuente / hash |
|---|---|---|---|
| 6 | `tools.wct.evidence.pytest_wire_framing.x_canonical_bytes__mutmut_11` | `allow_nan=False` removido (default `True`; el diff rellena la línea eliminando el argumento) | framing `a6261613…` |
| 7 | `tools.wct.evidence.pytest_wire_framing.x_canonical_bytes__mutmut_16` | `allow_nan=False` → `allow_nan=True` | framing `a6261613…` |

- **Clase**: equivalencia ratificada (D-A, grupo A3).
- **Precondiciones**: los DOS únicos callers actuales de `canonical_bytes`
  (grep R10): `canonical_header` (datos de `ExecutionExpectation` validados
  por el API público — digests lowerhex64, strings; sin floats) y
  `_parse_line` (el valor pasó por `_loads` con `parse_float` que rechaza
  floats y `parse_constant` que rechaza constantes no finitas: NaN/Infinity
  nunca sobreviven). NaN inalcanzable en ambos.
- **Fundamento**: con `allow_nan=True` (o el default), la única divergencia
  posible sería serializar NaN en lugar de raisear — imposible bajo esos
  callers porque NaN no puede llegar a la serialización canónica.
- **Invalidantes** (transcritos de D-A y R10 §4.3): la ratificación NO cubre
  llamadas directas arbitrarias a `canonical_bytes` ni futuros callers sin
  esas validaciones; nuevo caller sin validación previa; relajar
  `parse_constant`/`parse_float` en `_loads`; cambio de fuente/runtime.
- **Evidencia citada**: R10 §4.3 (grep de callers, límites declarados);
  sondas R8 sin divergencia; diffs sellados R7 logs/16; bruto R7: survived.

### Grupo A4 — Alias de codec (framing)

Fundamento (D-A, transcrita): «utf-8 y UTF-8 resuelven al mismo codec en el
runtime fijado.»

| # | Identificador completo histórico | Diff | Fuente / hash |
|---|---|---|---|
| 8 | `tools.wct.evidence.pytest_wire_framing.x_canonical_bytes__mutmut_18` | `.encode("utf-8")` → `.encode("UTF-8")` | framing `a6261613…` |
| 9 | `tools.wct.evidence.pytest_wire_framing.x__parse_line__mutmut_4` | `text = raw.decode("utf-8")` → `text = raw.decode("UTF-8")` | framing `a6261613…` |
| 10 | `tools.wct.evidence.pytest_wire_framing.x__line_defect__mutmut_7` | `line.decode("utf-8")` → `line.decode("UTF-8")` | framing `a6261613…` |

- **Clase**: equivalencia ratificada (D-A, grupo A4).
- **Precondiciones**: registro de codecs de CPython del runtime fijado
  (búsqueda case-insensitive:
  `codecs.lookup("utf-8") is codecs.lookup("UTF-8")`, verificado R10).
- **Fundamento**: mismo codec, mismos bytes de entrada/salida, mismas
  excepciones en codificación y decodificación.
- **Invalidantes**: manipulación exótica del registro de codecs (fuera del
  runtime del proyecto); cambio de runtime; cambio de fuente.
- **Evidencia citada**: R10 §4.4 (verificación estructural en la base);
  sondas R8 sin divergencia; diffs sellados R7 logs/16; bruto R7: survived.

## 4. Correspondencia exigida — verificación de diffs contra lo autorizado

La correspondencia es inequívoca: los 12 diffs extraídos del artefacto
original coinciden EXACTAMENTE con las mutaciones descritas en las decisiones
D-A/D-B (identificador → diff), sin necesidad de extensión por semejanza.
El mangling especial de `_DefectError` se transcribió sin reescribir a mano
(`xǁ_DefectErrorǁ__init____mutmut_1/3`). Correspondencia verificada por
script hunko a hunko (12/12 EXACTOS, §0).

## 5. Registro por ID — excepciones puntuales (D-B)

Precedente aplicado: ACTA-DECISIONES-FINALES-Y-QACCMUT-2026-09-16 §3 —
«registro humano explícito por acta», sin editar gobernanza (SEC-005/PROC-010),
sin subir umbrales, sin tocar baselines/manifests/gates; un superviviente
exceptuado sigue siendo superviviente en el bruto y no se convierte en
killed, equivalente ni PASS.

### 5.1 ID 11 — mensaje de `_DefectError` (canal interno sin consumidor público)

| Campo | Valor |
|---|---|
| Identificador completo histórico | `tools.wct.evidence.pytest_wire_framing.xǁ_DefectErrorǁ__init____mutmut_1` |
| Diff | `super().__init__(code)` → `super().__init__(None)` |
| Fuente / hash | framing `a6261613accc69fc2ffe322b02342d6bf6a919b2d930ea3800202d1b8225f562` |
| Clase | excepción puntual a TEST-002 (D-B.1) — NO equivalencia, NO kill |

- **Fundamento (transcrito)**: «mensaje interno sin consumidor público
  identificado» — grep R10 re-verificado: cero lectores de
  `str(exc)`/`.args` sobre `_DefectError` en `tools/`; el finding lleva
  `code` (intacto), no el mensaje.
- **Precondiciones (ámbito, transcritas)**: mensaje interno sin consumidor
  público identificado; fuentes y runtime congelados para L2.
- **Invalidantes (transcritos)**: nuevo lector del mensaje; obligación
  contractual nueva; cambio relevante de fuente, consumidor o runtime.
- **Evidencia citada**: R10 §5.1 (clasificación B propuesta, opciones);
  diffs sellados R7 logs/16; bruto R7: survived.

### 5.2 ID 12 — `execution_id` de `_DefectError` (lectores reales; None en caminos actuales)

| Campo | Valor |
|---|---|
| Identificador completo histórico | `tools.wct.evidence.pytest_wire_framing.xǁ_DefectErrorǁ__init____mutmut_3` |
| Diff | `self.execution_id = execution_id` → `self.execution_id = None` |
| Fuente / hash | framing `a6261613accc69fc2ffe322b02342d6bf6a919b2d930ea3800202d1b8225f562` |
| Clase | excepción puntual a TEST-002 (D-B.2) — NO equivalencia, NO kill |

- **Fundamento (transcrito)**: «execution_id con lectores reales, pero None
  en los caminos actuales que generan estos defectos» — lectores:
  `pytest_decode_events.py:125,127` (construcción con atribución) y `:140`
  (lectura hacia `ProtocolFinding.execution_id`, campo contractual §2 l.67
  «str o None»); los raises con atribución solo ocurren en
  `_execution_index` y `_attributed_execution` retorna `None` exactamente
  en los caminos que llegan al raise (verificado empíricamente R10,
  `logs/05-sonda-defecterror3.txt`).
- **Precondiciones (ámbito, transcritas)**: fuentes y runtime congelados
  para L2; ningún camino actual de raise con atribución no-None.
- **Invalidantes (transcritos)**: nuevo camino de raise con atribución
  no-None; obligación contractual nueva; cambio relevante de fuente,
  consumidor o runtime.
- **Evidencia citada**: R10 §5.2 (sonda ex=7 → `foreign_reference` con
  `execution_id=None`; ex="x"/True → `invalid_field` con None); diffs
  sellados R7 logs/16; bruto R7: survived.

## 6. Efecto sobre el bruto y la campaña (D-CAMPAÑA, transcripción acotada)

D-CAMPAÑA autoriza «una campaña nueva completa de L2 con árbol
instrumentado fresco y selección congelada de 141 nodeids». Estas decisiones
«deben registrarse antes de ejecutar» (hecho: este acta precede a la
generación y a la campaña) y «no regularizan retrospectivamente desviaciones
presupuestarias o de custodia anteriores». En el resultado nuevo de la
campaña: los 10 IDs de D-A permanecen en el bruto con su resultado realmente
observado (se espera survived, por ratificación acotada); los 2 IDs de D-B
permanecen en el bruto como survived (excepción, no kill). Ninguno se
convierte en killed ni se elimina del bruto. Si una mutación ratificada o
exceptuada cambia de resultado en la campaña nueva, es caso de investigación
obligatoria (encargo §9) antes de cualquier cierre.

## 7. Sello del registro

Acta escrita antes de la generación del árbol instrumentado y de la
campaña; copia sellada en la custodia del expediente R11
(`custodia/REANCLAJE-11-L2-DECISIONES.md`) junto con el estado del guardián
de presupuestos previo a la ejecución. La publicación en la rama del PR #56
ocurre tras la revisión final del verifier (encargo §11).
