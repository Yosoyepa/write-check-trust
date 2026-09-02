# SPEC-003 — Ledger de evidencia, artefactos y replay

- Estado: propuesta
- Naturaleza: contrato lógico; storage y formato quedan abiertos

## Objetivo

Preservar una cadena de evidencia suficiente para reconstruir qué ocurrió,
detectar cherry-picking, reproducir integración sin API y separar datos exactos,
estimados o ausentes.

## Modelo de ledger

El ledger es append-only a nivel lógico. Una corrección agrega un evento que
supersede otro; no reescribe el original. Cada registro contiene:

| Campo | Obligación |
|---|---|
| event id y run id | únicos |
| sequence y timestamp monotónico | ordenables |
| wall-clock timestamp/timezone | auditables |
| event type/version | schema explícito |
| actor/producer/version | provenance |
| payload hash | integridad |
| parent/causal refs | trayectoria |
| visibility | agent-visible, evaluator-only o public |
| sensitivity | clasificación de datos |
| exactness | exact, provider-reported, estimated, derived, unavailable |
| supersedes | si corrige una observación anterior |

## Taxonomía mínima de eventos

- run assigned/started/terminated;
- environment materialized/verified/teardown;
- prompt/context delivered;
- model request/response/usage;
- tool requested/started/completed/failed;
- file/tree/patch checkpoint;
- gate started/result/artifact;
- repair iteration started/ended;
- budget warning/exhausted;
- retry/rate limit/stream error;
- oracle mounted/started/result/unmounted;
- reviewer verdict/adjudication;
- artifact sealed;
- deviation/exclusion/rerun;
- replay started/completed/diverged.

El contenido de reasoning privado no es requisito. El ledger captura uso y
eventos permitidos, respetando políticas del provider y privacidad.

## Manifiesto de artefactos

| Artefacto | Metadatos mínimos |
|---|---|
| task package | id/version/hash/provenance |
| base repository | commit/tree/remote permitido |
| environment | image digest, OS/arch, lock y toolchain |
| prompt/context | hash y clasificación; contenido según acceso |
| treatment config | perfil, reglas, capabilities y digest |
| event stream | schema, count, first/last id y hash |
| patch/final tree | base, final, files y hash |
| gate evidence | claim, value, threshold, scope, tool, artifact hashes |
| oracle package | id/hash/custodio; contenido privado |
| oracle result | requisitos, criticidad, logs redacted y hash |
| usage/cost | unidades, source, exactness y price-table ref |
| replay bundle | source session, normalizations y script refs |

Un run solo está “cerrado” cuando el manifiesto enumera tanto artefactos
presentes como ausencias justificadas.

## Normalización permitida

Para replay/snapshot pueden normalizarse exclusivamente campos no semánticos
declarados, por ejemplo:

- ids aleatorios de sesión;
- paths de workspace reemplazados por tokens estables;
- timestamps cuando no afectan budgets/ordering;
- puertos efímeros;
- cabeceras de request no funcionales y secretos redacted.

No se normalizan:

- orden causal de tool calls;
- comandos, argumentos o archivos relevantes;
- estados de gate/oracle;
- tokens/costo sin conservar el original;
- errores, retries o timeouts;
- contenido que determine el resultado.

Cada regla de normalización tiene versión y fixture que demuestra que no borra un
fallo conocido.

## Contrato de replay

Un replay válido:

1. parte del mismo task/environment manifest o sustituto compatible declarado;
2. no usa credenciales del provider;
3. entrega respuestas en el orden grabado;
4. falla ante request extra, faltante o incompatible;
5. prueba throw, hang, retry y streams parciales cuando estén en el corpus;
6. consume el guion completo;
7. compara árbol cerrado, eventos críticos e invariantes semánticos;
8. informa campos normalizados y divergencias;
9. no se presenta como nueva muestra de calidad del modelo.

## Snapshot más invariantes

El snapshot detecta drift estructural. Las invariantes independientes deciden
corrección. Para cada snapshot debe existir al menos una afirmación semántica que
no se regenere automáticamente, como:

- herramienta habilitada ejecuta con resultado esperado;
- gate defectuoso bloquea;
- archivo no autorizado no aparece;
- `UNKNOWN_TOOL` no sustituye una tool call válida;
- timeout conserva evidencia y no produce `PASS`;
- oracle privado nunca aparece en contexto visible.

Refresh requiere diff, rationale y reejecución de invariantes. No se acepta
“actualizar el golden” como explicación suficiente.

## Integridad y chain of custody

- Hashes se calculan al producir y al consumir.
- Artefactos derivados referencian inputs y versión del transformador.
- El run registra commit de WCT, runtime, adapter y configuración.
- El custodio del oracle y el ejecutor del tratamiento son roles separables.
- Un rerun crea otro run id enlazado; nunca reemplaza al original.
- Exportación/redacción produce un paquete derivado con mapa de omisiones.
- Clock skew y secuencias incompletas aparecen en validity.

## Privacidad y retención

Clasificaciones mínimas: pública, interna, confidencial de repositorio, secreta y
holdout. Secretos nunca son payload persistido; solo puede registrarse que una
credencial estuvo disponible. Retención y acceso se definen por clase. La
publicación usa artefactos derivados y conserva hashes del original bajo custodia.

## Evals del ledger

| Caso adversarial | Resultado esperado |
|---|---|
| borrar un run fallido | discontinuidad o manifest mismatch detectable |
| cambiar el patch después del oracle | hashes no coinciden y run inválido |
| reportar tokens estimados como exactos | conformance falla |
| omitir un retry | secuencia/costo no reconcilia |
| replay no consume última respuesta | replay falla |
| normalizar un error semántico | fixture de normalización falla |
| refresh acepta regresión | invariante independiente falla |
| export redacted se presenta como original | provenance inválida |
| artifact de otro commit | ref/hash no corresponde al run |

## Queries mínimas que el producto debe responder

- ¿Qué vio el agente antes de cada reparación?
- ¿Qué gate falló primero y cuántas veces se repitió?
- ¿Cuánto costó el run incluyendo fallos y retries?
- ¿Qué artefacto sustenta cada `PASS`?
- ¿Cuál fue la primera divergencia entre dos brazos?
- ¿Qué runs fueron excluidos, quién y por qué?
- ¿Puede reproducirse la integración sin API?
- ¿Qué dato es estimado o no está disponible?
- ¿El oracle corresponde al mismo patch que se reporta?

## Criterio de conformidad

Un paquete es auditable cuando un verificador puede responder todas las queries
anteriores sin acceso a estado mutable del ejecutor. Es reproducible cuando,
además, puede materializar entorno y replay con resultados e invariantes
esperados. Los dos términos no son sinónimos.
