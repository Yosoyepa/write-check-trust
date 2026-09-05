# ADR-G1-04 — Completitud y causa del inventario (G1b): diseño propuesto y requisitos bloqueantes

Estado: **aceptado como DIRECCIÓN** (yosoyepa, 2026-09-05); implementación
BLOQUEADA tras los gates de SPEC-G1b-1 — nada de este ADR queda
implementado ni medido por esa aceptación. Trazabilidad:
REVIEW-G1 §4, §7, D4; ANALYSIS §7.

## Problemas que G1b ataca (y G1a declara abiertos)

1. **Causa de los killed**: exit 1 (aserción que falla) y exit 3 (error
   interno de pytest) colapsan a `killed` en el reporte textual. G1a lo
   declara; G1b debe distinguir al menos "error interno" de "kill sano".
2. **Inventario esperado vs recibido**: `results` recorre los metas que
   encuentre (`load` tolera FileNotFoundError); perder UN meta entre fases
   deja killed sueltos sin denominador. G1a detecta solo vacío total.
3. **Pérdida parcial, IDs duplicados, truncados, resultados ajenos**,
   cambios concurrentes sobre `mutants/`.
4. **Versión soportada**: el contrato medido es de la 3.7.0 instalada; no
   se atribuye a `mutmut>=3.2` ni a futuras.

## Diseño propuesto (mínimo que satisface el contrato medido)

- **Lector versionado del artefacto del motor** (`.meta`): acceso
  EXPLÍCITO y versionado — assert de las claves/tipos esperadas
  (`exit_code_by_key: dict[str, int|None]`, `hash_by_function_name`, …);
  cualquier divergencia de esquema → ERROR "versión/esquema no soportado",
  nunca dependencia accidental de rutas o line numbers. Con él:
  - exit crudo por mutante → 3 ≠ 1: exit-3 cuenta como "kill por error
    interno" (clase propia, no PASS pleno; política exacta a aprobar).
  - conjunto esperado = llaves presentes tras la fase run; recibido =
    lo impreso por `results --all true`; divergencia → ERROR (RG06).
- **Identidad de corrida y versión**: diagnóstico con versión de mutmut,
  scope efectivo y marca de corrida; soporte declarado: 3.7.0 exacta;
  otra versión → advertencia y, para el lector, bloqueo (RG10).
- **Concurrencia**: sin locking del motor; el adaptador garantiza
  aislamiento o rechazo visible (workspace por corrida o detección de
  divergencia esperado/recibido), nunca mezcla (RG11). Symlinks: sin
  escritura/borrado fuera de la raíz de la corrida.
- **No prometer causalidad completa**: exit 1 tampoco identifica la
  aserción relevante; la atribución total (qué test mató, y si es
  relevante) tiene alcance propio (borde G2) y NO se incluye en G1b.

## Requisitos que BLOQUEAN la liberación de G1b

Ninguno está implementado ni medido a la fecha de este dossier:

- **RG05** discriminación exit 1/3 demostrada (lector versionado o
  interfaz pública equivalente; preferir la mínima).
- **RG06** pérdida parcial detectada (denominador independiente) — o el
  requisito declarado ABIERTO por el humano con el límite visible.
- **RG11** concurrencia/symlinks: aislamiento o rechazo visible.
- **RG12** presupuesto emparejado (≥3 repeticiones, mediana/rango, mismo
  entorno/scope/tests/versiones; suite, coverage, redteam y gate por
  separado) aprobado por el humano ANTES de obligar repetición completa
  en tiers.
- **RG13** invalidación por cambio solo de tests/config/asociación (la
  repetición literal re-ejecuta; queda demostrar que ninguna vía de
  resultado anterior sobrevive a ella, incluidos stats/otros caches).
- Previo: G1a fusionada; ADR-G1-02 y este ADR aprobados; Gherkin de G1b
  aprobado por el humano (el borrador de GHERKIN-G1.md NO es aprobación).

## Alternativas consideradas

- Interfaz pública que preserve causa (no existe en 3.7.0; `results`
  colapsa por diseño).
- Instrumentar los resultados de tests por mutante ( heavyweight; borde
  con G2; costo propio).
- Extender el lector versionado a duraciones/asociaciones: solo si un
  requisito medido lo pide (YAGNI; H0 puede necesitarlo con su propio ADR).
