# Cierre GS-1 (O1–O5) — integración y preservación (2026-09-14)

Registro versionado del incremento que integra el refuerzo O1–O4, el
contrato de presentación O5 y la reparación del inventario del binding, sobre
el lote de calificación GS-1 (`semgrep_schema.py` + `semgrep_verdict.py`).
Este documento es la custodia durable en-repo; los expedientes de medición
viven bajo `build/tmp/` y se citan por hashes, no como custodia.

## 1. Base e identidad del incremento

- Rama: `codex/beta3-ac1-r2-integration`; base aplicada: `c6be7ee618b6f2b3c8
  ed2b70325f68e95403abfa` (PR #53, borrador; preflight: local == remoto,
  índice limpio, único untracked el documento ajeno conocido
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, conservado fuera
  del incremento).
- Diff integrado: `incremento-o1-o5-combinado.diff`, SHA-256
  `84622ba140f7e039b8735c14235ea9b54cced0e3801bcf577000c23f3374d9fd`
  (verificado contra el valor publicado antes de aplicar; `git apply
  --check` previo). Contenido: refuerzo O1–O4 + contrato O5 + reparación del
  inventario del binding. **+116/−0** sobre exactamente los dos archivos de
  la allowlist.
- **Enmienda G-ACCEPT (misma allowlist, post-diagnóstico)**: la verificación
  del árbol integrado detectó un fallo NUEVO de `G-ACCEPT`
  (placeholder-variant: los pasos del outline O5 colisionaban con los del
  primer outline). Corregido reformulando los cuatro pasos del outline O5
  (Given/And/And/When con sufijo «para el resumen») y su lista de steps en
  el binding. Comparación de puerta: en `c6be7ee` puro el tier commit da
  **18 PASS + 3 FAIL preexistentes** (G-META-1, G-DEPS, G-DEAD — drift
  protegido E9, deptry y vulture, medidos en clon desechable); con el
  incremento y la enmienda el tier commit da **exactamente los mismos 3
  FAIL** y 18 PASS: el incremento no añade ningún fallo nuevo.
- **Estado final integrado** (hashes de esta enmienda incluida):
  - `tests/unit/test_sast_targets.py` → `8b0f71e375c7581fab06287f3eb9a25082
    ca760074862bab4cee03778b0ed2fe`
  - `features/wct-sast-targets-001.feature` → `0ae2e7fc82767e92a442fcb774844
    6d6e1aee988c6514dd6cc0ce2fef1390943`
  - diff final vs `c6be7ee` de los dos archivos: SHA-256
    `7a7e811377c61add1c351ce1b20d5ecfe2176684986e6d9383b89878a83032c1`
- Sin cambios de producto, gobernanza, umbrales ni dependencias. Sin
  pyproject experimental (el de `c6be7ee` se conserva).

## 2. Procedencia (expedientes y sellos)

| Expediente | Contenido | Sello | Verificado |
|---|---|---|---|
| `build/tmp/gs1-r2.g7ofy2/` | GS-1 repetición R2: campaña completa 282 IDs con tests reforzados O1–O4; bruto propio 280 killed + 2 survived | `gs1-r2.sha256` (90 miembros; SHA `0697e4516f2bada77406a6f6b5cee2a4b78e3375c56e8bd18432f52fb37f6a92`) | 90/90 OK (2026-09-14) |
| `build/tmp/gs1-o5.n0f5G7/` | Cierre O5: contrato de presentación + microcampaña de los 2 IDs residuales | `cierre-o5.sha256` (18 miembros; SHA `de763527cda1730dcb4e7508f6644252261f29ed3ca4a2af4125b82a53a21adc`) | 18/18 OK (2026-09-14) |
| `build/tmp/gs1-o5r.gfd7de/` | Reparación del binding O5 (inventario de filas) | `reparacion-binding-o5.sha256` (24 miembros; SHA `6a7308d91d48abe5a005a72456858322c98b5002445d70ff799b0d8f6574e474`) | 24/24 OK (2026-09-14) |
| `build/tmp/gs1-ac1.TOngPy/` | GS-1 original + addenda de cierre (antecedente) | `evidence-gs1.sha256` `088b5c42…`, `addenda-gs1-cierre.sha256` `e1bf0621…` | hashes de manifiesto intactos (2026-09-14) |

Dictámenes independientes de esos expedientes: R2 VERIFICADO (0 bloqueantes,
4 menores); fidelidad O5 APROBAR-MICROCAMPANA (0/0); sensibilidad O5
APROBAR-CIERRE-O5 (0 bloqueantes, 3 menores); reparación APROBAR-REPARACION
(0 bloqueantes, 2 menores).

## 3. Qué se verificó ahora y qué procede de evidencia histórica

- **Re-verificado ahora (sobre el árbol integrado)**: identidad de sellos y
  del diff; `git diff --check`; colección; suite normativa completa sin
  property; property por separado; gate fast; ratchets; control de
  introvertidos; y los cuatro controles negativos del inventario O5 en copia
  aislada (examples vacío, solo FAIL, solo ERROR, fila duplicada) — todos
  bloquean en la aserción de inventario. Resultados y comandos: ver el
  registro de ejecución de este incremento (comentarios del commit y
  `pasos` del encargo).
- **Procede de evidencia histórica (no se re-ejecutó aquí)**: la campaña R2
  de 282 mutantes (bruto 280 killed + 2 survived), las sondas causales de
  O1–O4 (31 kills evidenciados) y las dos sondas O5 (2 rechazos evidenciados
  bajo el contrato de presentación aprobado). **No se declara una nueva
  campaña conjunta 282/282**: la contabilidad por capas es
  R2 = 280 killed + 2 survived (histórico intacto) y O5 posterior = dos
  rechazos evidenciados.
- **Revisión documental vs re-ejecución**: los dictámenes citados combinan
  lectura crítica de sellados (documental) con re-ejecución parcial en copias
  propias (re-ejecución: controles negativos, colección y focal por el
  verifier de la reparación). La sensibilidad de mutantes del cierre O5 y de
  la reparación quedó acreditada por el ejecutor (sondas selladas), no por
  re-sondeo del verifier; así se declara como limitación.

## 4. Limitaciones

1. El contrato de presentación O5 es acotado: solo los resúmenes que
   enumeran fuentes omitidas quedan bajo resumen exacto; si se retirara,
   `x__finding_summary__mutmut_8` y `x__omission_verdict__mutmut_25`
   volverían a ser **supervivientes de comportamiento no contratado** (no
   «equivalentes-propuestos»: la equivalencia nunca fue ratificada).
2. La tasa de mutación global de GS-1 no se re-declara: no hubo re-campaña
   tras integrar el contrato O5 (los dos rechazos son evidencia sucesiva de
   sensibilidad, no un nuevo veredicto de campaña).
3. El guard de nombres del Gherkin sigue cubriendo solo nombres y las filas
   del primer outline; el inventario O5 lo cierra para el outline nuevo.
4. CI de la PR #53: el check `commit-gates` falla en `c6be7ee` por
   `wct integrity check` (drift del manifiesto de rutas protegidas
   `tools/wct/**`, 20 rutas, pre-bless, pendiente E9 de la matriz). Este
   incremento no toca rutas protegidas; el fallo preexistente persiste y se
   registra sin ejecutar bless.

## 5. Estado

**Residuos GS-1 resueltos mediante evidencia sucesiva**: los 33
supervivientes de R1 quedaron reducidos a 2 en R2 (31 muertos por O1–O4) y
esos 2 quedaron rechazados bajo el contrato O5 integrado aquí. La entrada E3
de `MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md` queda actualizada para
enlazar este cierre; las demás decisiones de la matriz no cambian.
GS-2 (`semgrep_scope.py`) continúa como lote PROPUESTO (E4) y se ejecuta en
un incremento separado sobre el SHA que publique este commit.
