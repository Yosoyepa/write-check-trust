# Evidencia de preparación del carril de automejora

Fecha: 2026-09-07. Rol: arquitecto/specifier. **No es un resultado del coder
ciego ni una calificación de beta.3.** No se ejecutaron llamadas OpenRouter.

## 1. Corte y entorno observados

- CWD: `/home/jandradeu/Documents/well_code_template`.
- Rama: `codex/plan-beta3-moldes-evals`.
- HEAD: `8de9107184288f1aa72c9578a14913686c47ad7c`,
  `refactor(dry): parse_tree compartido — G-DRY-TOK con cero clones (#44)`.
- Python 3.12.13; Linux `7.1.13-200.fc44.x86_64`, glibc 2.43.
- uv 0.11.31; pytest 9.1.1; pytest-cov 7.1.0; coverage 7.15.4;
  import-linter 2.13; ruff 0.16.4. No se instalaron/actualizaron dependencias.
- Fecha/versiones son de la preparación. Registrar de nuevo en cada candidato;
  no usar este entorno como promesa de compatibilidad de toda plataforma.

## 2. Comprobaciones realizadas este turno

| Comando | Resultado real | Qué acredita / qué no |
|---|---|---|
| `uv run pytest --collect-only -q` | exit 0; **347 tests collected in 0.35s** | colección de suite existente, no ejecución de P01 |
| `uv run pytest -q` | exit 0; **347 passed in 94.37s** | suite completa actual, incluida property; no LCOV fresco ni experimento de modelo |
| `uv run lint-imports` | exit 0; **4 kept, 0 broken; 9 files, 8 dependencies** | contratos de `example`, no arquitectura del harness |
| `uv run wct archmetrics --json` | exit 0; cycles=[], violations=[] | paquetes example; adapters/domain en zona pain según sus métricas, sin violación del baseline. No significa todos los paquetes saludables |
| `uv run wct gate --tier fast` | exit 0; **7 PASS, 0 SKIP, 0 FAIL/ERROR** | G-META-2/RULES-DRIFT/SUPPRESS/DEBT/LINT/FMT/TYPE; no tier commit/full |
| `uv run wct integrity check` | exit 0, sin diagnóstico de drift | configuración/código protegidos existentes sin cambios de esta entrega |
| `git diff --check` | exit 0 | whitespace de tracked; las nuevas Markdown se revisan aparte |
| `uv run wct accept parse <copia-P01>` | exit 0; **1 Scenario Outline, 18 filas** | gramática del bloque Markdown copiado, no ejecución de steps |
| `uv run wct accept ir-dry <copia-P01>` | exit 0; **findings=[], count=0** | sin duplicación IR detectada, no aceptación ni mutación |

La copia se creó con apply_patch bajo
`build/tmp/beta3-selfhosting-spec.hBjUIs/p01.feature`, directorio exclusivo e
ignorado. No se añadió feature de producto ni se ejecutó generate/run/mutate.
Se usó la guía de arquitectura para las sondas y la guía de aceptación para
validar la forma; no se confundió su resultado con una feature implementada.

Los tiempos son observaciones individuales, no presupuesto emparejado. La
cifra histórica 345 pertenece a otro corte. No se observó un flake en esta
corrida; una sola corrida no demuestra ausencia de flakiness.

### Comprobación documental

- 31 Markdown de BETA3 inspeccionadas, incluidas las **12 nuevas SELF-HOSTING**.
- 136 enlaces locales resueltos; cero rotos. Fences, whitespace y separación
  de encabezados comprobados; sin defectos detectados.
- 18 IDs/estados/findings idénticos entre tabla normativa P01 y Gherkin; copia
  efímera byte-idéntica al bloque. I19–I22 siguen como contratos adicionales,
  no tests que se hayan ejecutado.
- Hashes de los 19 documentos previos: 12 idénticos; en los otros 7, al retirar
  exclusivamente el nuevo bloque inicial de precedencia, contenido idéntico.
- Primera sonda de consistencia de tablas: falló por asumir siete columnas
  donde la SPEC tiene seis. Se corrigió el comprobador y se repitió con cero
  discrepancias; no se cambiaron expectativas para complacer esa sonda.
- `git status --porcelain` acotado a código/tests/features/gobernanza/config y
  README raíz: sin cambios tracked ni nuevos archivos en esas fronteras.

## 3. Evidencia de los hallazgos de arquitectura

Fuentes locales inspeccionadas, referidas desde este documento:

- [Policy](../../../../../governance/policy.yaml): paths.source/src y código
  protegido; root/layers del ejemplo.
- [Configuración de herramientas](../../../../../pyproject.toml): coverage
  incluye src y tools/wct; mutmut source_paths solo src/example.
- [Registro de gates](../../../../../tools/wct/gate/runner.py): G-TYPE incluye
  tools/wct y src; G-ARCH/ARCHMETRICS/MUT remiten al ejemplo; COGNITIVE a src.
- [Modelo histórico](../../../../../tools/wct/model.py) y
  [ejecución](../../../../../tools/wct/gate/exec.py): GateResult y resumen no
  constituyen captura completa de argv/causa/terminales.
- [Aceptación](../../../../../tools/wct/accept/pipeline.py) y
  [steps del ejemplo](../../../../../tests/acceptance/steps.py): función por
  escenario, filas en bucle; handler de reserva, no de evidencia.
- [Ratchets](../../../../../tools/wct/ratchet/measure.py): ruta LCOV histórica,
  validación/casos existentes y required aditivo.
- [Mutación](../../../../../tools/wct/mutate/verdict.py): clasificación limitada
  de reporte, no reconciliación de tres inventarios con expected independiente.

El análisis de alcance es lectura y sondas, no una campaña adversarial nueva
contra todos los gates. Los límites G1b provienen también de SPEC/antecedentes
locales, no de mutación reejecutada en este turno.

## 4. Preservación y autoría

Antes de actuar había cuatro archivos tracked modificados del usuario y
varios directorios documentales sin seguimiento. Se crearon documentos solo
en SELF-HOSTING y se añadieron punteros de precedencia a siete documentos
BETA3: README, D0, PLAN, EVALS, PILOTO-PREPARACION, PRD y PROMPT.

El contenido previo se conserva; no se editan ADRs/SPEC anteriores para
simular aceptación. Ningún cambio a código, tests, features productivas,
governance, workflows, pyproject, uv.lock, README raíz, G1, POST-PR36 o REVIEW-G1.

Digest de `git diff --binary` tracked antes/después de la preparación:
`f604fe3876cfce5a87391d29f5aeda2e902b712fa2ba1288260555958893d0cd`.
Es igual porque esta entrega vive en BETA3 aún no trackeado. Los hashes previos
de los 19 documentos BETA3 se tomaron para comprobar preservación adicional;
el diff Git por sí solo no demuestra qué pasó con archivos no trackeados.

No commit, push, PR, bless, bump, tag o release. No se consultó la identidad
secreta del coder ni configuración de su cuenta.

## 5. No realizado / pendiente real

- P01–P10 no implementadas; ningún resultado de beta.3 en esta entrega.
- Ningún coder/verifier nuevo ejecutado; esta revisión documental no se
  presenta como auditoría independiente del código futuro.
- No nueva corrida de commit/full, redteam, mutación, LCOV/ratchets frescos,
  orden aleatorio, SBOM o calificación de release.
- No se ha creado/aislado un oráculo privado, ni probado una frontera de OS
  contra código hostil. Los casos públicos P01 **no son holdout**.
- No hay corpus comparativo congelado, runtime de accounting validado, recibos
  de inferencia, estimaciones de ahorro ni aprobación de un lote de modelos.
- Antes del coder: el usuario envía/acepta contrato y Gherkin de P01. Antes
  de puntuar costes: el custodio aporta recibos/uso, no solo nombre/tarifa.

Estos pendientes no impiden la primera implementación supervisada P01 tras
su aprobación. Sí impiden llamar al dossier «beta.3 completada» o «eficacia
económica de WCT demostrada».
