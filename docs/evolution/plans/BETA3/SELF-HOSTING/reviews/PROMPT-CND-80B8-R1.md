# Encargo de reparación R1 — SH-P01, mismo coder ciego

Preparado por el arquitecto a partir de
[REVIEW-CND-80B8](REVIEW-CND-80B8.md). **No ejecutado.** El envío del bloque
siguiente por el usuario autoriza solo una nueva entrega SH-D de P01. No
modifica el contrato `sh-p01/1`, sus 18 filas ni umbrales. Los diagnósticos
publicados dejan de ser material de examen privado.

---

Continúa como coder de SH-P01. El primer candidato CND-80B8 tiene dictamen
REQUIERE_CORRECCION. Autorizo reparar los hallazgos R01–R05 del acta, con las
fronteras siguientes. **Sin commit, push, PR, bless, P02 ni cambios al juez.**

Usa el modelo asignado, sin identificarlo, buscar su precio, cambiarlo ni
escalar a otro. Modelo/recibos permanecen con el custodio. Registra diagnóstico
del arquitecto como asistencia; no afirmes trabajo sin ayuda tras recibirlo.
No se prescribe el algoritmo del fix ni se exige presupuesto monetario.

## 1. Lectura, identidad y preservación

Lee AGENTS.md, tu rol coder y estos archivos en su ruta original:
`/home/jandradeu/Documents/well_code_template/docs/evolution/plans/BETA3/SELF-HOSTING/`:
P01-IDENTIDADES, GHERKIN-P01, GOBERNANZA, MOLDE-WCT, REGISTROS y
`reviews/REVIEW-CND-80B8.md`. No reescribas ninguno ni el handoff previo.

Base: `8de9107184288f1aa72c9578a14913686c47ad7c`. El original vive en
`/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8`.
Valida sus cuatro hashes contra el acta antes de reutilizarlo. Su digest
agregado reproducible es
`e3a6426553e7b3c00445ad249f0dd8f31fb098d7e5276e11cc97667bfdd77a6a`.

Asigna IDs opacos nuevos de run/candidato, conserva coder_blind_id COD-CA7A
si sigue siendo la misma sesión/operador, y registra parent_candidate_id
CND-80B8, modo SH-D. Si cambió la asignación del coder, pide al custodio un ID
ciego correcto, sin revelar identidad. No inventes continuidad del modelo.

Prepara **otro worktree exclusivo** bajo `build/tmp/`, en una rama nueva
`codex/beta3-sh-p01-identidades-r1` si está libre; no sobreescribas una existente.
Tras verificar base y hashes, puedes reproducir allí los cuatro archivos del
primer candidato, conservando el original y su patch archivado. No editar,
hacer stash/checkout/reset ni limpiar el árbol documental compartido.

Antes de implementar, comprueba Python, lock, grupos/herramientas ya disponibles
y receta de tests. El prompt anterior prohibía instalación y el primer venv
careció de quality: **no repitas esa ambigüedad**. Si el nuevo entorno necesita
sync, reporta la necesidad exacta y espera preparación/autorización del operador;
no añadas/actualices dependencias ni cambies intérprete silenciosamente. Con
entorno preparado, usa ejecución sin sync automático y registra versiones.

## 2. Reparación del producto y de sus tests

Allowlist: únicamente los mismos cuatro archivos nuevos de P01 respecto de
la base, más un registro nuevo de esta entrega bajo SELF-HOSTING/runs. Se
permiten outputs/sondas exclusivos bajo build/tmp; no son nuevas capacidades
del producto. No modificar otros tests, governance, runner, CLI, manifests,
locks, workflows, documentos normativos ni entregas anteriores.

1. **R01:** reduce la complejidad de `_inventory_findings` y `_resolved_status`
   con responsabilidades cohesivas y comportamiento conservado. CRAP de toda
   función cambiada debe quedar ≤6 con medición real sobre tools/wct/evidence.
   No subir umbrales, añadir supresiones ni esconder ramas tras estructuras
   opacas solo para engañar al analizador. Conserva la API, pureza, orden y
   diagnósticos completos. `__all__` con los tres símbolos aprobados es válido.
2. **R02:** refuerza I21 con expected literal: dos o más IDs duplicados en
   cada inventario, permutaciones de entrada y salida completa en orden.
   Revisa múltiples missing/unexpected dentro del mismo código. Demuestra
   que el orden descendente incorrecto falla y el orden correcto pasa. La
   regresión puede empezar en verde contra el original, porque su lógica ya
   ordena bien: su rojo semántico debe venir de la variante, no de un fallo
   de import ni de inventar un defecto en el producto original.
3. **R03:** el binding debe comprobar cardinalidad y unicidad **antes** del
   dict por ID, y no ignorar escenarios distintos del primero. Guarda negativos
   con la fila I01 repetida y un Scenario Outline extra, usando el parser real;
   deben fallar donde antes había 54 verdes. El feature aprobado original debe
   seguir pasando y permanecer verbatim. No añadas handlers P06 ni modifiques
   el parser. No dupliques el algoritmo productivo en el expected de tests.

Conserva las 18 filas originales y I19–I22; añadir casos discriminantes no
autoriza borrar pruebas históricas, normalizar identidades ni cambiar estados.
Guarda salidas de los rojos, clase bootstrap/semántica y diff de cada intento.
No llames mutmut/G-MUT a variantes manuales. Conserva controles válidos, incluida
una solución de conteo alternativa si afirmas haberla calificado.

## 3. Evidencia y matriz final

4. **R04:** crea una entrega append-only que cite las discrepancias del padre;
   no corrijas retrospectivamente su archivo. Registra separadas las corridas
   completas, focales y el G-TEST de unit/integration sin property. Nunca
   conviertas una corrida fallida/con skips ni un G-TEST parcial en «401 passed».
   Extrae los nodeids reales y vincula Ixx→nodeid→resultado; no reconstruyas el
   orden de parámetros manualmente. Usa los nuevos conteos reales tras añadir
   tests, no fuerces 401/54 como constantes de aceptación.
5. **R05 y calidad:** tras el último cambio, ejecuta colección completa,
   suite completa, focal con cobertura de rama explícita del módulo, fast,
   commit y ratchets. Para CRAP usa el motor instalado con alcance
   `tools/wct/evidence`, umbral vigente 6 y LCOV nuevo de esa misma versión.
   Las pruebas focales no sustituyen gates; el G-CRAP histórico de src no
   acredita esta pieza. Si CRAP queda rojo, corrige antes de pasar a DRY.
   Respeta PROC-004; en P01 las variantes son calibración manual y la mutación
   de aceptación sin handlers no aplica. Declara esas exclusiones, sin verdes
   ficticios ni ampliación de `paths.source` para forzar G-MUT.
6. Produce además **cobertura global nueva**, separada de la focal, con la
   receta productiva: `uv run --no-sync pytest --cov --cov-branch
   --cov-report=lcov:build/coverage/lcov.info -q -m "not property"`. Conserva
   argv, exit, digest del LCOV y snapshot. Ejecuta ratchets tolerante y
   `--require all`, declarando sus productores y métricas: presencia por sí
   sola no acredita frescura, y el LCOV focal no sustituye al global. Ante un
   rojo, diagnostica; no subas baselines ni regeneres locks. Tras CRAP conforme,
   completa DRY con alcance explícito, respetando las matrices de tests.
7. Verifica diff/allowlist e integridad. G-META-1 pre-bless puede seguir rojo
   únicamente por las dos rutas nuevas de producto contratadas: nómbralas.
   No generalices «solo G-META» si otros controles exigidos fallan o no se
   ejecutaron. `git diff --check` y fast antes de entregar, salidas reales.

Hash de cada archivo **después del último cambio**; manifest UTF-8 de cuatro
líneas `sha256`, dos espacios y ruta relativa, en el orden del acta, con LF
final. Conserva bytes y digest agregado calculado, no uno transcrito de memoria.
No es un manifiesto de gobernanza y no autoriza update-manifest. Los outputs
deben llevar ruta/hash, argv/cwd, alcance, inicio/fin cuando disponibles y exit;
si algo no se capturó, unavailable con causa, sin inventar un recibo.

## 4. Parada y devolución

Entrega el candidato hijo, diff completo y registro con todos los intentos,
incidentes, asistencia, desviaciones y checks no ejecutados. Conserva los
artefactos del padre y los de esta reparación en directorios distintos.
No implementes las propuestas del harness F01–F06: necesitan otra decisión.

Detente para revisión ciega de los bytes finales. No elijas un verifier/modelo
ni declares tu propia aprobación. El arquitecto repetirá los desafíos y
pedirá una lectura separada/humana antes del GO; bless sigue siendo otra
autoridad y no es el arreglo para un incumplimiento de calidad.

---
