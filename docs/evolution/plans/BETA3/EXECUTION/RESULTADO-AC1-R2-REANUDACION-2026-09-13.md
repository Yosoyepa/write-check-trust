# AC1/R2 — composición preservada y calificación acotada (2026-09-13)

**Estado:** preservación pendiente; **no GO** de AC1, beta.3, bless, merge, tag ni publicación.

Este registro distingue la composición trazable de los bytes revisados de una calificación completa. R2 queda aceptado solamente como reparación de baseline. AC1 **no está acreditado**: el primer lote de mutación de fuentes tiene supervivientes. P03a fase 1 permanece fuera de alcance.

## Identidad y composición

- Rama aislada: `codex/beta3-ac1-r2-integration`.
- Base y `HEAD` inicial: `932c835ac0eeb75010ec7a1071315b1c51f78eb6` (`origin/main`). No se modificó el checkout principal.
- Mapa de procedencia: `build/tmp/ac1-r2-composition/evidence/composition-source-map.tsv`, SHA-256 `6d3b89fc795b9d86532a164cfd111c27ebd94e9538e07de2a07c34d7f637a912`; 39 entradas de archivo (34 funcionales AC1+R2 y 5 documentos contractuales/handoffs).
- Sellos comprobados antes de componer: AC1 `d28c8991424c085ffb62e2713a053e03b27e8d8fe882dec3f278c391d7e06f9c` (23/23); base compuesta AC1 `3dfbeb35065c6e45b15a02622c57a16fd78c5980ef34675ddb6c527bfbc00213` (553/553); delta R2 `496df51cba525373769c3118a8331294b020ec48ea058d0d1c5870376810a4c0` (12/12).
- Excluidos expresamente: P03a fase 1 (aunque su sello `c23d72736448ea5c3e97bb732d5a47bd4664cea2587bb38983a1913cc0bea20e` verificó 23/23), documentación beta.3 no necesaria, `README`/G1/POST-PR36/REVIEW-G1 y `build/tmp` histórico.

## Controles que sí se ejecutaron

Con runtime existente, `PATH`, `TMPDIR` y `PYTEST_DEBUG_TEMPROOT` privados precreados:

- Colección normativa: 640 tests, exit 0.
- Baseline no-property: 639 passed, 1 deselected, exit 0; property separada: 1 passed, exit 0.
- Orden aleatorio con `pytest-randomly==5.0.0`: para semillas `20260910`, `1234`, `987654321` y `42`, cada corrida no-property dio 639 passed/1 deselected y la property separada 1 passed. No se observó flake.
- Preflight del lote de mutación: 114 focales passed, imports de los cuatro módulos resueltos exclusivamente al workspace. El manifiesto de entradas, SHA-256 `29785105c94f8fcd94817233c14926f53fe4d47176bf4b4ea083914804ccc094`, coincidió antes y después.

Las dos recetas inválidas iniciales se mantienen separadas de estos resultados: una carecía de `runtime/bin` en `PATH`; la otra usaba un `TMPDIR` inexistente y reprodujo el fallo de Semgrep. No se atribuyen a producto ni se reutilizan como baseline.

## Mutación de código AC1: hallazgo que detiene la cadena

El lote congelado contiene `receipt.py`, `receipt_validation.py`, `verdict.py` y `verdict_validation.py`, con sus dos pruebas normativas. Se ejecutó una única campaña serial (`--max-children 1`) con presupuesto de 1.800 s:

```text
timeout --signal=INT --kill-after=30s 1800s mutmut run --max-children 1 '*'
```

Terminó en 44,896 s con exit crudo 0, pero ese exit **no es un PASS**. `mutmut results --all true` registró 498 resultados: **468 killed y 30 survived**, sin otra clase de resultado. Por tanto, el lote queda en **FAIL-survivors-stop**.

La procedencia del instrumento sí quedó reconciliada: el inventario AST independiente y los hashes instrumentados son 23/23 funciones; la distribución es 4/7/5/7 entre los cuatro módulos y existen 791 asociaciones test→función. Los 498 sitios pertenecen exclusivamente a esos cuatro archivos.

Los 30 supervivientes se agrupan así:

1. `receipt.py` (2): límite de lectura `RECEIPT_LIMIT + 1 → + 2` y el alias de codec `utf-8 → UTF-8`.
2. `verdict.py` (12): tres cambios de `zip(strict=True)` y nueve cambios de textos/selector de mensajes de inventario y resultado.
3. `verdict_validation.py` (16): cambios de mensajes de validación de identidad, estado, exit, cabecera y baseline.
4. `receipt_validation.py` (0).

El límite de lectura es un hueco funcional a resolver con un recibo JSON válido de tamaño exacto `RECEIPT_LIMIT + 1`. Los cambios de mensajes deben recibir aserciones exactas si esos diagnósticos son contrato observable. El alias UTF-8 y `zip(strict=...)` bajo la precondición ya impuesta por `_inventory` son candidatos a equivalencia/redundancia, **no equivalencias aprobadas**: requieren decisión humana explícita o una simplificación de código revisable; no se concedió excepción.

Conforme al orden obligatorio, no se ejecutaron mutación de aceptación, cobertura/CRAP, DRY ni tier full después de este hallazgo. Tampoco se modificó producto para ocultarlo.

## Gate e integridad posteriores a la documentación

- `wct gate --tier fast`: **7 PASS, 0 SKIP, 0 FAIL/ERROR**, exit 0 en 2,642 s. Log SHA-256 `47021d32099e5477edee7473f263adf248b3413024ca577710d1f4d717a9194e`.
- `wct integrity check`: exit 1 por el drift esperado de 20 rutas protegidas de `tools/wct/**` (4 modificadas y 16 nuevas). Log SHA-256 `4bdb49e1997831017640c2f10e7b5e6dee65bbdd5ab6e46fd42c61d3bf33f4a4`. Es un hallazgo declarado, no una autorización: no se ejecutó `bless`, no se modificó el lock y sigue pendiente revisión humana sobre un diff/PR real.

## Evidencia local

Toda la evidencia vive bajo `build/tmp`; no se afirma custodia externa:

| Artefacto | SHA-256 |
|---|---|
| Plan de campaña | `66dbf02f234fc18739a7c674464a103f2f6d971f158590d805ced9ad2444c991` |
| Preflight (114 PASS) | `a01789168ddd55d902a5368c94e3f8ad1a2c0de5bfb06bb55ec5db41e2a57622` |
| Log crudo de campaña | `ad6893d982a08fb4c922569c3be8e1a8ed95b180c16e21e27a67dd608de09c91` |
| Resultados completos | `38434d37bb900f7d0d691e708d2c00695e62879a420fa893b8c2e7fce72a3248` |
| Diffs de supervivientes | `0376c4949bf66ea832422ca8d415a36638965bb0af532be66f1a53e58c22824c` |
| Reconciliación | `b73a4d529ac7a245cd65306fa7a68c5a9f460deae29667a6d00f1d48644832c4` |

El manifiesto JSON contiguo enumera las identidades, resultados y referencias completas para una PR revisable.

## Próxima decisión necesaria

Antes de cualquier nueva campaña o avance de la cadena, una persona debe decidir el contrato de los diagnósticos y adjudicar los dos grupos potencialmente equivalentes. Si se autoriza una reparación, debe ser mínima, incluir pruebas discriminantes y volver a ejecutar únicamente la secuencia exigida desde mutación de código. La versión sigue siendo `1.0.0-beta.2`; cualquier convención/tag de beta.3 requiere decisión humana independiente. No hay comando de bless en este registro.
