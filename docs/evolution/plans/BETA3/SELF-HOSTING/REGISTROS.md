# Plantillas de registro — no resultados de inferencia

Ninguna plantilla rellena `PASS`, coste 0, aprobación, modelo o hash inventado.
Los valores no observables se marcan `unavailable` con causa. Estos registros
son el plano experimental/manual, **no el schema JSON de evidencia P1**.
No crear por adelantado carpetas con resultados exitosos simulados.

## 1. Ficha pública de tarea, antes de implementar

| Campo | Contenido requerido |
|---|---|
| task_id / contract_version | p. ej. SH-P01 y sh-p01/1; IDs de la SPEC, no un issue remoto |
| run_id / coder_blind_id | asignados por operador, sin modelo/precio |
| mode | SH-D desarrollo o SH-E comparación; nunca inferido después |
| approval_ref | mensaje/fecha de aprobación del contrato/frontera, no aprobación fabricada por coder |
| subject_base | SHA completo + patch/documentos adicionales por digest |
| treatment_ref / evaluator_ref | Wn/Qn y capacidades; custodio puede ocultar brazo a reviewer |
| writable_paths / forbidden_paths | allowlist exacta y límites de producto/registro |
| contract_cases | IDs semánticos exigidos; bindings se revisan al existir tests |
| visible_feedback | qué checks/revisión puede usar y oportunidades de reparación |
| observed_limits | recursos de runtime, tiempo/calls si están fijados; sin techo monetario exigido aquí |
| custody | quién conserva modelo/recibos/oráculo y qué aislamiento existe de verdad |

La entrega documental incluye una [línea base](EVIDENCE.md), no una ficha de
inferencia iniciada. Un working tree con documentos sin commit se identifica
con base + digests; HEAD solo no captura ese contexto.

## 2. Registro append-only de intentos del coder

Un archivo nuevo `runs/<run-id>-<candidate-id>.md` por entrega; `parent_id` si
repara una previa. El operador asigna IDs seguros antes de escribir. No
sobreescribir intentos anteriores ni esconder el patch inicial tras un squash.

```text
task_id:
contract_version:
run_id:
coder_blind_id:
candidate_id:
parent_candidate_id: none | <id>
mode: SH-D | SH-E
base_sha:
context_digest:
candidate_manifest_digest:
started_at / ended_at / timezone:
changed_files: [cada archivo nuevo/modificado/borrado, con digest]
attempts: [ciclos TDD, correcciones, outputs y tiempos, incluidos fallidos]
checks: [argv, cwd, inicio/fin, exit, alcance, output_path, output_digest]
case_bindings: [Ixx -> nodeid(s) realmente coleccionados -> resultado]
red_evidence: [bootstrap o fallo semántico, causa y artefacto]
deviations: [o ninguna observada; no omitir por benignas]
unverified: [capacidades/checks no ejecutados y razón]
incidents: [flake, timeout, cancelación, estado anterior y reintento]
usage_custody: recibos privados con operador | unavailable y motivo
assistance: ninguna | diagnóstico | arreglo propuesto/escrito por arquitecto
git_actions: no commit / no push / no bless / no PR
next_action: revisión independiente; no autoaprobación
```

No pegar variables de entorno completas, API keys, reasoning privado ni
respuestas crudas con marca/modelo en el handoff del reviewer. El operador
redacta metadatos que rompan el cegamiento, conservando original privado.
Un string `command` sirve para leer; `argv` conserva límites de argumentos.

## 3. Registro privado de consumo (solo custodio)

Una fila por generación/solicitud, vinculada con run/candidate/intento y rol:

- ID local de solicitud y generation ID; timestamps y estado/cancelación;
- modelo solicitado/servido, proveedor/fallback/routing y configuración;
- raw usage/recibo y su procedencia; prompt/completion tokens, detalles
  disponibles, coste/unidad, impuestos/créditos/ajustes si se conocen;
- origen: respuesta final, consulta posterior o export; claves desconocidas
  preservadas en crudo, sin confundirlas con campos normalizados;
- relación con retry y si es una nueva inferencia facturable;
- referencia de precio/fecha para estimaciones, separadas de importe facturado;
- rol coder/architect/verifier y asistencia, para no imputarlo todo al coder.

Registrar además cuántas solicitudes esperaba el cliente. Si solo se conservan
las respuestas exitosas, su suma **no** acredita coste completo. Si no hay
acceso a ese inventario, declarar incompletitud y no fabricar denominador.

No enviar claves al arquitecto. Al final puede bastar un export redacted con
IDs ciegos, importes, unidades y cobertura de recibos. Las specs de OpenRouter
ayudan a interpretar, pero no sustituyen historial de uso perdido.

## 4. Acta del arquitecto/verifier, antes del coste

```text
review_id / reviewer_id / fecha:
task_id / candidate_id / contract_version:
candidate_manifest_digest / evaluator_digest:
blindness: modelo oculto | revelación accidental y alcance
independence: roles separados / mismo modelo / mismo host / otras limitaciones
criteria: [dimensión, satisface|defecto|no-evaluable, evidencia]
findings: [id, severidad, expected, actual, reproducción, control válido]
scope_check: [allowlist y resultado real de integridad pre/post-bless]
commands_run: [argv, exit, alcance, outputs]
not_run:
verdict: CONFORME_AL_CONTRATO | REQUIERE_CORRECCION | INCONCLUSO
reason:
quality_frozen_at:
next_authority_required:
```

El dictamen del arquitecto y la corrida del verifier son entradas distintas.
No atribuir una revisión «independiente» que nadie ejecutó. Un fichero de acta
es editable: la custodia/versionado externo y su historial deben comprobarse
para afirmar que el coder no puede reescribirlo.

## 5. Ficha de mejora del harness, después de un hallazgo

```text
proposal_id / finding_id / owner:
affected_contract / Wn / Qn:
failure_class:
why_existing_control_missed_or_rejected:
minimal_reproduction / positive_control:
generalized_rule_and_consumer:
new_validation_cases_not_used_in_design:
known_false_positives / limitations:
measured_or_unavailable_runtime_and_review_cost:
compatibility_and_scope:
requires_protected_change: yes | no
decision: candidate | investigate | reject | approve-for-next-lot
external_issue: not-created | <real reference>
```

Nada de «cerrado» sin prueba ni IDs inventados de GitHub. Una propuesta que
resulta de un holdout abierto se versiona para el lote siguiente; conservar el
dictamen original permite medir cuántos escapes costó aprender esa regla.
