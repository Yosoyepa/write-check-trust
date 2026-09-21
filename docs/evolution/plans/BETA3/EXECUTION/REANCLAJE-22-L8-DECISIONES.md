# Registro REANCLAJE-22 — decisiones humanas, ratificaciones y alcance

Estado: **decisiones D-0, D-A, D-D y D-E9 del encargo registradas ANTES de
implementar o sondear; alcance, allowlist, aislamiento, arnés y presupuestos
fijados; sin reparaciones ni sondas ejecutadas todavía al momento de este
registro.** La evidencia, la tabla sucesora de los 131, la sensibilidad de
los 29 y los resultados de los controles de módulo se documentan en
`REANCLAJE-22-L8-REPARACION.md`.

Fecha de registro: 2026-09-21. Rol: coder opencode2 bajo supervisión de
Architect (encargo autorizado por decisión humana).

## 1. Base, identidades y aislamiento

- Base comunicada y HEAD técnico: `b7604c8dc915cd6965061f8d51a8e98013f73aa8`.
- Remoto `origin/codex/reanclaje-p03a-fase1` == `b7604c8…` (verificado con
  `git ls-remote`, sin avance). PR #56 en borrador (estado heredado de R21;
  `gh` no está instalado en este entorno — se reporta como observación real,
  no se pronostica).
- Main de referencia `8a379d64ba13bbe43a707fcfd8df0ea336dd97ed` == merge-base
  de la rama (rama estrictamente por delante). Tag `v1.0.0b3.dev1` es
  anotado: objeto `5aeb9ce5…`, peeled `8a379d64…` = main, intacto.
- Copia aislada con raíz Git propia:
  `build/tmp/reanclaje22-20260921/tree` (clon local, checkout detached en la
  base, `.venv` propio creado con `uv sync --frozen --offline` incluyendo el
  grupo `quality`). El checkout principal, su índice, `main`, tags y los
  expedientes históricos no se tocan.
- El expediente R21 fue producido en otra máquina (`/home/jandradeu/…`) y
  llegó por migración; su identidad material viaja en los sellos R20
  (`custodia/sellos-R20.json`) y en el manifiesto R21
  (`MANIFIESTO-REANCLAJE21.sha256`). Este incremento reconstruye las copias
  instrumentadas DESDE la custodia sellada y verifica cada hash antes de
  usarlas (lanzador fail-closed).
- Runtime de esta copia: Python 3.13.12, pytest 9.1.1, mutmut 3.7.0. La
  máquina de R21 usó Python 3.13.14; la diferencia de patch se declara y no
  altera identidad de fuentes/tests (ambos verificados por hash).

## 2. D-0 — Evidencia y desviaciones de R21

Se acepta como insumo técnico la evidencia identificada de R21, incluidas las
corridas declaradas dentro del exceso aproximado de 16,5 s, condicionada a su
identidad, causalidad y trazabilidad verificables. Esta admisión:

- NO declara cumplido el presupuesto de R21;
- NO concede autorización retroactiva general;
- NO autoriza nuevos excesos;
- NO convierte un manifiesto divergente en íntegro.

Se conservan separados cuatro planos: (a) evidencia técnicamente admitida;
(b) incumplimiento del presupuesto R21 (§8 de su registro); (c) divergencia
de miembros escritos después del sello
(`logs/00-ledger-guardian.csv`: divergencia puramente aditiva, prefijo
sellado de 907 líneas íntegro + filas post-sello de verifier/publicación);
(d) sello sucesor R21. Cualquier artefacto que no cumpla sus condiciones se
excluye de la admisión y se explica su efecto.

## 3. D-A — Diez equivalencias acotadas (ratificadas)

Ratificación exclusiva bajo las fuentes, contratos y precondiciones de R21:

- a) Ocho variantes de `pytest_builders::_build_execution_start`: mutmut_1,
  7, 8, 9, 19, 35, 36 y 37. Fundamento: role/input_sha256/context_sha256/
  recipe_sha256 son placeholders sustituidos incondicionalmente desde la
  cabecera (`_reconstruct_refs`) antes de publicar el `JournalEvent`; los
  caminos de error descartan el evento completo y no exponen el payload
  intermedio.
- b) Dos variantes de `pytest_schema::_consume_header`: mutmut_10 y
  mutmut_13. Fundamento: el cambio de `unterminated` converge en la
  clasificación posterior de la misma línea (`_line_defect` re-deriva el
  defecto), conservando los observables contractuales: defecto, offset,
  consumo, eventos y tail.

Condiciones obligatorias asumidas (verificación por ID en el registro de
reparación):

1. Resolver los IDs completos desde el inventario sellado y los diffs
   sellados; los números solos no identifican equivalencias.
2. Comprobar cada mutación exacta contra el diff sellado.
3. Registrar por ID: hash de fuente instrumentada, frontera pública,
   fundamento e invalidantes.
4. No extender la disposición a llamadas directas a helpers privados ni a
   otros operadores.
5. Si una premisa no se confirma o aparece un contraejemplo admitido, se
   detiene la ratificación de ese ID y se entrega el caso; no se fuerza el
   resultado.

Estas ratificaciones cambian disposición, no resultado instrumental: el bruto
R20 permanece **398 = 359 killed + 39 survived**.

## 4. D-D — Controles de módulo

Autorizado:

- Una matriz conductual independiente para las 17 lambdas de `_BUILDERS`,
  construida y observada desde el camino de decodificación admitido, con
  esperados derivados de la tabla contractual (no del propio builder).
- Los controles del catálogo contractual de `inventory` (transcripción
  literal de `PROPERTY_FINDING_CODES`/`NON_BLOCKING_CODES` y su efecto sobre
  clasificación/emisión).

No autorizado (y excluido):

- Inventar un contrato literal de `__all__`.
- Imponer estructura a `ExecutionInventory` sin obligación contractual.
- Refactorizar producto para hacerlo instrumentable.
- Sumar las ocho variantes físicas no registradas de `ObservationError` al
  inventario histórico de 398.

## 5. D-E9 — Integridad

El drift de referencia corregido es **36 = 2 modificadas + 34 nuevas**; debe
re-medirse cuando corresponda y no copiarse como resultado actual. El bless
queda FUERA de este encargo; la reparación y las sondas L8 no dependen de
actualizar `integrity.lock`. G-META-1 puede permanecer como rojo declarado de
la PR, re-medido y con número de hallazgos separado de la duración.

## 6. Allowlist exacta y no-goals

Únicos archivos versionados que este encargo puede tocar:

1. `tests/unit/test_pytest_schema.py`
2. `tests/unit/test_pytest_observation.py`
3. `docs/evolution/plans/BETA3/EXECUTION/REANCLAJE-22-L8-DECISIONES.md`
4. `docs/evolution/plans/BETA3/EXECUTION/REANCLAJE-22-L8-REPARACION.md`

Sin globs documentales ni autorización implícita para otros REANCLAJE-2*.
Artefactos temporales: `build/tmp/reanclaje22-20260921/` (expediente, fuera
de Git). Prohibido modificar permanentemente producto, features, contratos,
gobernanza, whitelist, baselines, umbrales, dependencias, `pyproject.toml`,
`uv.lock`, `integrity.lock`, `integrity-log.md`, manifiestos, logs o árboles
históricos. No se implementa binding PA01–PA12, ni otros lotes, ni trabajo
sobre los 928 IDs.

No-goals del encargo: recampaña completa L8, bless, merge, bump, tag,
release, aceptación mutada, cobertura/CRAP/DRY/full, Q-ACCMUT.

## 7. Arnés y presupuestos

- Arnés: `lanzador22.py` (heredero fail-closed de los controles 1-7 de
  R20/R21) + `guardian22.py` (guardián de sobres con reserva previa, reloj
  monotónico, killpg solo de procesos propios y ledger por paso). Copia
  histórica `mutants-22` (tests sellados, modo `sealed`) para el Frente A;
  copia de sensibilidad (tests del candidato, modo `working`) para los
  controles de los 29 y los 10.
- Sobres (encargo §8, sin transferencias; incluye intentos inválidos y
  subagentes): A=600 s, B=1200 s, C=600 s, V=360 s, I=900 s, PUB=180 s.
  Total máximo 3840 s.
- **V=360 s queda reservado en exclusiva a Architect/verifier**; el
  coordinador no lo consume y no delega un segundo verifier sin
  coordinación. Las reejecuciones independientes se coordinan por `ask`
  antes de ejecutarse.
- Plan preventivo: cada sonda con timeout compatible con el saldo reservado;
  sin pkill general; sin trabajo suplementario tras el cierre del sobre. Si
  se agota un sobre, se entrega lo acreditado y el residuo exacto, sin tomar
  saldo de V o I para ocultar excesos de A/B/C.

## 8. Publicación y verificación

- Solo tras el dictamen favorable de Architect (solicitado con `ask` ANTES
  de cada commit/push) y con hooks instalados/activos, diff completo y
  staging inspeccionados, rutas explícitas de allowlist, `git diff --check`
  limpio, conventional commit con byline del rol.
- Autorizados: commit de tests y commit documental separados, push normal a
  la rama de PR #56 (sin `-A`, sin bypass, sin force push). PR permanece en
  borrador.
- CI sobre el SHA publicado: se reporta el resultado REAL observado; si el
  paso de integridad bloquea los siguientes, se declaran NO EJECUTADOS; no
  se pronostica el resultado post-bless. La reparación puede declararse
  completa en su alcance solo con sensibilidad sustentada de los 29 y
  controles fieles; eso NO cierra L8 (falta la recampaña posterior).

## 9. Preparación del siguiente encargo (NO ejecutado)

Se prepara, sin ejecutar, el prompt de la única recampaña L8 sobre el
candidato final: selección congelada, activación dentro del proceso,
causalidad por fase, presupuesto propio estimado por calibración y puerta
independiente previa. La expectativa eventual 388 killed + 10 survived sobre
398 es solo una hipótesis comprobable y nunca se reconstruye sumando
campañas ni se impone al instrumento.

## 10. Estado final de las decisiones a la entrega (2026-09-21)

- **D-0**: evidencia R21 admitida con los cuatro planos separados; cada
  artefacto sin condiciones quedó excluido o caracterizado.
- **D-A**: las diez equivalencias ratificadas se comprobaron por ID (diff
  sellado, frontera pública, fundamento e invalidantes) y sobreviven a la
  selección Y2 (10/10); la verificación independiente muestreó una
  (`consume_header_10`).
- **D-D**: matriz conductual de las 17 lambdas y catálogo de `inventory`
  implementados; perturbaciones temporales 6/6 detectadas; `ObservationError`
  con 0 IDs registrados y precisión conservada (reconteo: 3 variantes + orig).
- **D-E9**: drift re-medido en Y2: **36 = 2 modificados + 34 nuevos
  protegidos**; G-META-1 único rojo declarado (gate real 20 PASS + 1 FAIL);
  bless fuera de alcance.
- **Dictamen técnico de Architect**: FAVORABLE a la reparación Y2; NO cierra
  L8/beta3; NO declara conformidad retroactiva de custodia; publicación
  pendiente de dictamen final.
- **Custodia (sin eufemismo, sin autorización retroactiva)**: la iteración
  correctiva editó 5 miembros del sello Y2; Y2 ya no verifica íntegro y los
  bytes originales de esos miembros NO se conservan como copia verificable
  (solo hashes del manifiesto y caracterización en notas); Y2b cubre el
  estado corregido. No legitima ediciones futuras de miembros sellados.
- **Sellos**: X 200/200 (`5a274c6b…`) · Y2 con 5 divergencias documentadas
  (`a0211b90…`) · Y2b 75/75 (`8ed6a293…`) · GATE adicional 10/10
  (`bfbbfe67…`).
- **Recampaña completa y bless NO autorizados**; prompt REANCLAJE-23
  preparado y no ejecutado.
- **Entrega documental final** preparada en la copia Git aislada nueva
  `publicacion/tree` (base `b7604c8`, tests Y2 byte-idénticos, solo los dos
  documentos de allowlist actualizados, 4 rutas staged, hooks activos,
  freeze de hashes fuera del árbol mutable), pendiente de dictamen final;
  sin commit/push.
