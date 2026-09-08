# Decisión de arquitectura — piloto de instrumento, no excepción de gate

2026-09-08. Bajo la delegación vigente de contratos y planificación, se aprueba
exclusivamente el piloto de cuatro casos de
[PROPUESTA-P02a-ACEPTACION-SEMANTICA.md](PROPUESTA-P02a-ACEPTACION-SEMANTICA.md),
SHA-256 `83ef6ddf026035a6be28ca05b3859f3deeb7d398441fb5b29f023481a00477d0`.

IA01/02/17/36, positivos alternativos y controles defectuosos declarados,
20 mutaciones históricas clasificadas y negativos semánticos adicionales.
Instrumento y evidencias únicamente en directorio nuevo exclusivo bajo
`build/tmp/b3-ma-p02a-semantic-preflight-<id>/` del candidato. Dos scripts como
máximo (`runner.py`, `controls.py`), stdlib y runtime existente, sin instalaciones.
No se aprueba la expansión a 42 casos ni se modifica el candidato de 17 archivos.

Antes de ejecutar: revisión independiente de la propuesta sin bloqueantes;
comprobar identidad del candidato y procedencia de imports, conservar hashes
del instrumento y controles sanos. Hacer las correcciones del instrumento
en nuevas revisiones identificadas, sin atribuir un rojo antiguo al código nuevo.

Límites operativos del piloto: ejecución secuencial, 30 segundos máximos por
intento y 180 segundos para la campaña inicial. Timeout se registra como
instrumento inválido, nunca killed; terminar/recolectar el proceso y no
continuar silenciosamente. Estos topes son contención del piloto, no promesa
de rendimiento ni modificación de límites productivos.

Mantener separados: desacuerdo semántico observado, rechazo del vocabulario,
supervivencia, error de instrumentación y control deliberadamente defectuoso.
Un profile inválido que preserva invalid_spec no se fabrica como kill.
No contar tests fijos o cotejos de hash como ejecución de filas mutadas.

La revisión posterior será de un agente distinto del autor. El piloto solo
resuelve viabilidad y clasificación del instrumento. No concede una excepción
de aceptación, no equivale a G-ACCEPT-MUT PASS y no habilita aún CRAP/DRY/full.
Bless y publicación siguen bajo autorización humana separada.
