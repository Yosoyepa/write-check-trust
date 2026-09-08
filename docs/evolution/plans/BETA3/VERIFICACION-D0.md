# Verificación documental de D0

Fecha: 2026-09-07. HEAD `8de9107184288f1aa72c9578a14913686c47ad7c`.
Esta es evidencia de **este turno de especificación**; no prueba implementación
de B3-P1, calificación del molde, cierre G1b ni resultados de modelos.

## Resultado real de fast

Comando: `uv run wct gate --tier fast`. **Exit 0**.

```text
GATE           STATUS  MS      SUMMARY
G-META-2       PASS    60      todas las reglas nombran verificadores conocidos
G-RULES-DRIFT  PASS    108     copias por proveedor sincronizadas
G-SUPPRESS     PASS    192     sin erosión por supresiones
G-DEBT         PASS    67      deuda diferida trazable
G-LINT         PASS    14      ok
G-FMT          PASS    13      ok
G-TYPE         PASS    173     ok

7 gates: 7 PASS · 0 SKIP · 0 FAIL/ERROR
```

Log auxiliar: `build/tmp/beta3-d0/fast.log`. Este tier no contiene pytest ni
mutación: no presentarlo como suite o aceptación completas. Se ejecutó sobre
código preexistente; no se escribió código que requiera verifier por PROC-005.
El futuro incremento sí exige un verifier distinto del coder.

## Gherkin y enlaces

- Cuatro bloques de GHERKIN-P1, **36 filas** (21+4+6+5). Cada bloque se copió
  a `build/tmp/beta3-d0/p1-N.feature` para lectura, sin generar tests ni steps.
- Para cada copia: `uv run --frozen wct accept parse <copia>` y
  `uv run --frozen wct accept ir-dry <copia>`: **exit 0**; ir-dry sin findings.
- Comprobación adicional de correspondencia exacta entre columnas Examples y
  placeholders utilizados. No columnas huérfanas ni valores sin parametrizar
  en los pasos variables de esos bloques.
- Sonda #35: narrativa bajo Feature produce ValueError en línea 2; el mismo
  texto convertido en comentario parsea. Solo confirma el límite actual.
- Enlaces locales del dossier revisados por existencia; fences equilibrados y
  sin espacios finales nuevos. No sustituye revisión semántica ni prueba E2E.

## Preservación y cambios

Antes de editar se fijaron hashes de **467 archivos** visibles para Git y se
guardó el diff tracked previo en `build/tmp/beta3-d0/`. Al finalizar:

- El diff tracked previo se conserva byte a byte, incluidos README de evolución
  y los tres documentos G1. Los directorios/archivos previos fuera de BETA3
  conservan sus hashes; no hubo archivos anteriores eliminados.
- Dentro de BETA3 se añadieron adendas enlazadas a **11 documentos** iniciales.
  Su texto anterior se conserva; PRD.md y PROMPT.md no cambiaron.
- Se añadieron seis documentos: D0, TRAZABILIDAD-D0, SPEC-B3-P1-evidencia,
  GHERKIN-P1, PILOTO-PREPARACION y este registro. Las adendas distinguen las
  observaciones anteriores de la revalidación actual.
- Código, tests ejecutables, governance, thresholds, workflows, pyproject,
  lock y archivos de instrucciones protegidos conservan sus bytes.
- `uv run wct integrity check`: **exit 0**, sin diagnóstico de cambios.
- `git diff --check`: **exit 0**; revisión adicional cubre documentos untracked,
  que ese comando no comprueba por sí solo.

No se ejecutaron formatters con escritura, tests, coverage, full/commit tier,
mutación, red team ni APIs de inferencia. No se ejecutó personalAssistant ni
sus servicios. Lecturas de GitHub (`gh`/git ls-remote y descarga del SBOM) no
cambiaron estado remoto. Sin commit, push, bless, cambios de tags o release.

Los JSON/logs/copias de consulta de `build/tmp/beta3-d0/` son auxiliares efímeros;
los hechos y decisiones durables están en D0/TRAZABILIDAD/PILOTO. No se atribuye
al archivo descargado del SBOM procedencia de build que su contenido no prueba.

## Pendiente por decisión, no por fallo del gate

D0 es una propuesta lista para aprobar/rechazar. El humano debe aprobar el
Gherkin y la frontera/presupuesto de P1 antes de implementación (PROC-003 y rol
specifier). G1b sigue abierto. Modelos/tarifas/monto total requieren D2; la
selección de personalAssistant y Codex para el oráculo ya fue dada por el usuario.
