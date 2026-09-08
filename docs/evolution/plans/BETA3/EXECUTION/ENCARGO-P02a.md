# Encargo preparado P02a — no iniciar sin D1

Estado: preparado para usar **después** de aprobar API, Gherkin y allowlist de
[PROPUESTA-P02a, revisión 2](PROPUESTA-P02a.md). No es autorización implícita.
El arquitecto debe registrar el SHA integrado/base y digest final del contrato
al abrir el candidato; no usar una rama mutable como identidad del encargo.

## Prompt del coder

Actúas como coder de P02a: inventario reproducible de inputs, solo lectura.
Esta entrega pertenece a B3-MA-D, no al experimento ciego R0/R1. No busques
marca/modelo/precios del coder original ni afirmes ahorro; datos ausentes son
unavailable. No llames proveedores adicionales para ejecutar este encargo.

Antes de escribir, lee AGENTS, tu rol Owns/Does Not Own, ENTREGA-v2,
MOLDE-WCT-v2, la propuesta aprobada completa y SONDA-GIT-P02a. Confirma en un
recibo: aprobación D1 realmente registrada, versión/digest del contrato, base
exacta, API, selección, errores, expected literal, variantes de IA01–IA41,
frontera de archivos, entorno, medición focal/global y paradas. Son 42 filas
Gherkin porque IA33 tiene control válido y exceso separados. No obtengas los
expected mediante una llamada al mismo algoritmo que estás probando.

Implementa exclusivamente `capture_inputs` y sus tipos/adaptadores en el
allowlist de §10. No toques P01, CLI, runner, ratchets, producto posterior,
governance, workflows, locks, reglas generadas ni contrato. No conviertas
snapshot en acreditación. P02b es dueño del workspace; P03/P06 observarán el
entorno realmente ejecutado. `ContextRef` sigue siendo caller-declared.

Aplica TDD. Casos válidos y defectos deben contrastarse por resultado observable,
no solo mocks: estado Git distinto de bytes, ignorados incluidos, outputs sin
contaminar identidad, carpetas eliminadas, Git de otra raíz, filtros antes de
status, objeto faltante sin lazy fetch, symlinks/races y límites. Conserva el
rojo real; si un contrato falla por falta de información o una sonda contradice
el diseño, detente y devuélvelo al arquitecto. No arregles el expected tú mismo.

Mapea cada variante a nodeids reales y ejecuta collect-only. Conserva nombre,
tipo Outline, pasos, encabezados, cardinalidad, IDs y celdas del Gherkin
aprobado; prueba que alterar cada campo rompe su control. El binding no permite
afirmar que el generador histórico ejecutó vocabulario P02. Los contract tests
deben llamar la API real. No implementar CLI de P06 para simular ensamblaje.

Mide módulos nuevos de tools explícitamente: los motores por defecto sobre el
ejemplo no los califican. Distingue cobertura focal/global, desafíos manuales
de mutación productiva y scope de cada gate. Preserva umbrales/baselines y la
secuencia de hardening de AGENTS. Si una herramienta no alcanza esos archivos,
decláralo y pide resolución; no reclasifiques esa ausencia como PASS.

Entrega sin commit, push, PR ni bless. Solo código/tests/feature del allowlist y
el handoff nuevo `docs/evolution/plans/BETA3/SELF-HOSTING/runs/HANDOFF-B3-MA-P02A-R0.md`.
Evidencia grande en `build/tmp/b3-ma-p02a-r0/`, creado exclusivamente: si existe,
detente, no sobrescribas otro run. No reutilices LCOV, outputs o manifests de
P01. Anota comandos, cwd/runtime, exits, log paths/hashes y custodia local-only.
Calcula el digest del candidato con la serialización de ENTREGA-v2; preserva
los diez archivos del allowlist con rutas POSIX relativas, orden lexicográfico
por bytes UTF-8, y declara esa lista antes de escribir. Por fila: SHA-256,
dos espacios ASCII, ruta, LF; manifest UTF-8 sin BOM y LF final.
No incluyas en esa identidad agregada logs ni el propio handoff.

Fast debe pasar; G-META-1 puede quedar rojo pre-bless únicamente sobre los cinco
módulos nuevos de producto autorizados. Cualquier otra ruta protegida o fallo
es un hallazgo adicional, no una excepción. No termines con una promesa de
verificación: entrega los resultados reales y los controles que no ejecutaste.

## Frontera del arquitecto y verifier

El arquitecto prepara un worktree propio del candidato después de D1 y no
escribe el fix del coder sin registrar esa asistencia. Otro verifier revisa
el digest final, solo lectura, y ejecuta la matriz sobre esos mismos bytes.
La PR se crea después de reconciliar hallazgos; bless humano y CI son puertas
posteriores. No encargar P03/P04 sobre APIs de P02 todavía variables.

Este prompt no promete coste económico ni tiempo cero, no convierte al
verifier en dueño del contrato y no modifica las aprobaciones de P02b–P10.
