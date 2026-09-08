# SH-P01 — Reconciliación pura de identidades

Estado: **lista para aprobación del escenario y encargo del coder**. No
implementada. Versión de contrato `sh-p01/1`. Refina la parte de identidades de
B3-P1a sin aprobar P1b/c ni alterar [SPEC-P1](../specs/SPEC-B3-P1-evidencia.md).

## 1. Resultado y razón del corte

WCT podrá comparar tres inventarios sin confundir igualdad de conteos con
igualdad de obligaciones. Es un kernel **interno**: no corre pytest, no mide
cobertura, no autentica entradas y no afirma que un test haya pasado.

La búsqueda en `tools/wct` encontró clasificación/duplicados en
`mutate/verdict.py`, pero no esta operación de tres inventarios. Esa API
consume texto de mutmut y retorna GateResult con otros límites. No reutilizarla
fingiendo equivalencia ni refactorizarla en este incremento. Usar colecciones
de stdlib; no dependencia nueva ni motor genérico de grafos.

## 2. Frontera exacta del diff

**Allowlist de producto/tests (archivos nuevos):**

- `tools/wct/evidence/__init__.py`: solo docstring; sin efectos ni reexports.
- `tools/wct/evidence/identities.py`: tipos públicos y función de este contrato.
- `tests/unit/test_evidence_identities.py`: contratos/filas parametrizadas.
- `features/wct-evidence-identities-001.feature`: bloque de GHERKIN-P01 verbatim.

**Registro permitido:** un archivo nuevo por entrega bajo
`docs/evolution/plans/BETA3/SELF-HOSTING/runs/`, con ID asignado por el operador.
No editar los documentos normativos ni una entrega previa. Logs grandes y
fixtures temporales solo bajo un directorio exclusivo de `build/tmp/`.

No tocar archivos existentes de producto/tests, `GateResult`, CLI, runner,
ratchet, mutación, `tests/acceptance/steps.py`, pyproject, uv.lock, governance,
workflows, generated, README raíz ni documentación ajena. Si la API ya existe
en el árbol de trabajo, **parar y reconciliar**, no sobreescribirla.

Rama propuesta: `codex/beta3-sh-p01-identidades`, en copia de implementación
preparada por el operador. Este encargo no autoriza checkout/stash de la rama
documental compartida, commit, push, PR, bless, instalación ni acceso remoto.

## 3. API obligatoria, sin implementación prescrita

Import: `tools.wct.evidence.identities`.

Operación: `compare_identities(*, expected: tuple[str, ...], collected:
tuple[str, ...], executed: tuple[str, ...]) -> IdentityComparison`.

Tipos públicos: dataclasses inmutables, campos en este orden:

| Tipo | Campos y dominio |
|---|---|
| `IdentityFinding` | `inventory`: `expected`, `collected` o `executed`; `code`: uno de §4; `identity`: string o `None` exclusivamente para `empty_expected` |
| `IdentityComparison` | `status`: `match`, `mismatch`, `empty` o `invalid`; `findings`: tuple de `IdentityFinding` |

Anotar los vocabularios con tipos cerrados, sin `Any`. No hace falta crear un
enum, clase base o registry por cada string. No añadir campos, API JSON/CLI,
banderas de tolerancia, auto-repair ni un bool `passed` ambiguo.

Los tres argumentos deben ser tuplas de strings. Cualquier otro contenedor
(incluido string/lista/generador) o elemento no string levanta `TypeError` en
la frontera pública, antes de producir un reporte. No atrapar errores de
programación y convertirlos en `match`. El texto del TypeError no es contrato.

Identidades opacas: igualdad exacta de strings Python; no `strip`, lower,
normalización Unicode, resolución de paths ni extracción parcial del nodeid.
Espacios, `::` y parámetros forman parte de la identidad. Solo el string
literal vacío `""` es inválido en esta capa. Determinar si un string tiene
formato válido de nodeid es responsabilidad del adaptador P03, no de P01.

## 4. Reglas y precedencia

Para cada inventario se retiene el multiconjunto original para detectar
duplicados; las diferencias se calculan sobre el conjunto de **strings no
vacíos**, sin perder los problemas encontrados antes. No deduplicar la entrada
y recién después validarla.

| Código | Inventario / identidad | Emisión |
|---|---|---|
| `empty_expected` | expected / `None` | no queda ninguna identidad esperada no vacía |
| `empty_identity` | inventario afectado / `""` | una o más entradas vacías; una finding por inventario |
| `duplicate_identity` | inventario afectado / identidad no vacía | aparece más de una vez; una finding por identidad |
| `missing_identity` | collected o executed / identidad | está en expected no vacío y falta en ese inventario |
| `unexpected_identity` | collected o executed / identidad | está en ese inventario y no en expected no vacío |

Vacíos repetidos producen `empty_identity`, no además `duplicate_identity` de
vacío. Duplicados no vacíos sí conservan también missing/unexpected cuando
corresponda. No se trunca la lista de hallazgos.

Decisión, en orden:

1. Cualquier `empty_identity` o `duplicate_identity` → `invalid`.
2. Sin lo anterior, `empty_expected` → `empty`, aunque observed tenga elementos.
3. Cualquier missing/unexpected → `mismatch`.
4. En otro caso, `match`: expected no vacío e igualdad exacta de los tres.

Emitir **todos** los hallazgos aplicables, también los de menor precedencia.
Orden canónico: inventario `expected, collected, executed`; dentro de cada uno
el orden de códigos de la tabla anterior; dentro del código, identidad
lexicográfica Python (`None` solo se usa en el primer código). Repetir o permutar
los mismos inventarios no cambia el resultado.

Un `executed` presente pero ausente en `collected` no se compensa: el missing
de colección sigue visible. No se asignan estados terminales, exits o
autenticidad a esos nombres. Eso pertenece a P03/P05.

## 5. Ejemplos normativos independientes del SUT

Abreviaturas: E/C/X = expected/collected/executed; `m` = missing_identity;
`u` = unexpected_identity; `d` = duplicate_identity; `z` = empty_identity;
`e` = empty_expected. `C:m:B` es una finding concreta, no texto de diagnóstico
del producto. Las tuplas de tabla son datos, no órdenes de shell.

| Caso | E | C | X | Status | Findings exactas en orden |
|---|---|---|---|---|---|
| I01 | (A) | (A) | (A) | match | ninguna |
| I02 | (B,A) | (A,B) | (B,A) | match | ninguna |
| I03 | (A,B) | (A,C) | (A,C) | mismatch | C:m:B; C:u:C; X:m:B; X:u:C |
| I04 | (A,B) | (A) | (A,B) | mismatch | C:m:B |
| I05 | (A,B) | (A,B) | (A) | mismatch | X:m:B |
| I06 | () | () | () | empty | E:e:None |
| I07 | () | (A) | (A) | empty | E:e:None; C:u:A; X:u:A |
| I08 | (A,A) | (A) | (A) | invalid | E:d:A |
| I09 | (A) | (A,A) | (A) | invalid | C:d:A |
| I10 | (A) | (A) | (A,A) | invalid | X:d:A |
| I11 | (A) | (A,B) | (A) | mismatch | C:u:B |
| I12 | (A) | (A) | (A,B) | mismatch | X:u:B |
| I13 | (A) | (A,"") | (A) | invalid | C:z:"" |
| I14 | ("") | (A) | (A) | invalid | E:e:None; E:z:""; C:u:A; X:u:A |
| I15 | (A) | (A,a) | (A) | mismatch | C:u:a |
| I16 | (A) | (A) | (" A") | mismatch | X:m:A; X:u:" A" |
| I17 | (A,A,B) | (A,"",C) | (A,A,C) | invalid | E:d:A; C:z:""; C:m:B; C:u:C; X:d:A; X:m:B; X:u:C |
| I18 | (A) | (A) | ("","") | invalid | X:z:""; X:m:A |

Las identidades A/B/C son strings literales para la tabla. Añadir pruebas de
opacidad con nodeids reales sintéticos, por ejemplo
`tests/unit/test_x.py::test_y[a b]` y `tests/unit/test_x.py::test_y[a]`, y Unicode
compuesto/descompuesto distintos. No normalizarlos ni ejecutar esos paths.

Pruebas contractuales adicionales, IDs estables:

- **I19:** contenedor no tuple en cada argumento → TypeError; incluye string.
- **I20:** elemento no string en cada argumento → TypeError; incluye None/int.
- **I21:** resultados/datos inmutables, entradas intactas, salida determinista
  y orden canónico con varias identidades y códigos.
- **I22:** nodeids con espacios/parámetros, y Unicode no normalizado; sustitución
  sin igualdad exacta → mismatch. Control con el mismo string → match.

## 6. Tests que sirven para discriminar

Tests parametrizados con IDs I01–I18, una ejecución pytest por fila; I19–I22
con variantes identificadas. El expected es literal de esta tabla, no obtenido
de otro llamado a `compare_identities`, ni de un helper que reproduzca su
algoritmo. Cotejar status **y todas las findings**, no solo longitud o substring.

TDD: conservar salida roja y diff del momento. Si la primera roja es un import
ausente, llamarla bootstrap, no prueba de sensibilidad semántica. Después el
verifier comprueba en copias variantes plausibles: comparar solo tamaños,
deduplicar antes de validar, ignorar X, aceptar vacío, normalizar identidad y
devolver solo la primera causa. Es **calibración por variantes manuales**, no
G-MUT, no ejecución de mutmut y no cierre de G1b. Rechazar todo también debe
fallar con I01/I02; una implementación válida alternativa debe pasar.

El feature será gramática/contrato. Los tests parametrizados llaman la API
productiva y se vinculan por Ixx. No generar tests con el handler histórico de
inventario del ejemplo: desconoce estos steps. G-ACCEPT parse verde no prueba
su ejecución; no anunciar G-ACCEPT-MUT verde con comandos que fallan por falta
de handlers. La ruta CLI/aceptación ensamblada se completa en P06.

## 7. Compatibilidad y calidad del perímetro

- Ningún comportamiento ni archivo existente cambia; GateResult queda intacto.
- Núcleo sin IO, entorno, reloj, procesos, red, imports de WCT/pytest/frameworks.
- Anotaciones/docstrings, CC y tamaño bajo límites actuales; sin supresiones.
- Analizar el módulo nuevo expresamente: G-ARCH/COGNITIVE/MUT históricos no
  cubren por inferencia `tools/wct/evidence`.
- Cobertura del código nuevo y pruebas de variantes se reportan por alcance.
  No sumar tools a paths.source ni elevar un baseline para conseguir verde.
- No crear funciones privadas de framework extensible por usos hipotéticos.
  API mínima de §3; algoritmo y nombres privados quedan a elección del coder.

## 8. Verificación y parada del primer encargo

1. Estado/base/allowlist registrados; contrato y Gherkin revisados, sin artefactos
   previos que se puedan sobreescribir. Sin modelo/precio en el registro público.
2. Colección completa (`uv run pytest --collect-only -q`), matriz I01–I22
   ejecutada por ruta productiva, suite completa y fast. Las pruebas enfocadas
   son evidencia focal, nunca sustituto de un gate completo.
3. `git diff --check`; inspección de tipos/imports/efectos. Corrida de commit
   y ratchets según la matriz vigente, con salidas reales. Si solo integridad
   queda roja por el nuevo código protegido, reportar rutas, no autoblindar.
4. Handoff con todos los intentos, defectos, costes diferidos y limitaciones.
   No hacer commit/push/PR/bless; no implementar P02.
5. Verifier independiente examina el mismo patch congelado y hace challenge.
   El arquitecto no da GO por el autoinforme del coder.

No hay techo monetario como criterio de aceptación por instrucción del usuario.
Para una corrida de desarrollo, entregar el **primer candidato completo**; la
revisión posterior abre otra entrega con parent_id. En un lote comparativo la
cantidad de reparaciones/recursos se fija antes conforme a EVALUACION-CIEGA.
Si falta información necesaria para calcular coste, se conserva unavailable;
no impide revisar calidad, sí impide afirmar ahorro exacto.
