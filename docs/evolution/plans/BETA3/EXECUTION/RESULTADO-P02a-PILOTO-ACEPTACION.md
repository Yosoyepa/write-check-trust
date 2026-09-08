# Piloto P02a — evidencia y siguiente decisión de aceptación

2026-09-08. Estado: piloto ejecutado por coder; no aprobación de aceptación
completa ni de release. Candidato de 17 archivos intacto:
`e4b25b2b16183de4da325f2c1264a53a1d5590e1eda1e1943635d1e3eb080570`.

## Qué se ejecutó

Directorio exclusivo del candidato:
`build/tmp/b3-ma-p02a-semantic-preflight-r0/`.

- `runner.py`: `1c0516d089e8055b719bc2e65f669b3bdd8408ee77a579c2f5140f288706f735`.
- `controls.py`: `a3357b74830ff8258513ab5f14e6b4701f58fc143f711003d6f90c1685556c5f`.
- Cuatro casos: IA01, IA02, IA17, IA36. Catorce controles (incluidos los
  cuatro originales) y veinte mutaciones históricas; driver exit 0.
- Los 14 controles coincidieron con su categoría prevista. Los negativos
  deliberados dieron desacuerdo; no se presentan como ejecuciones sanas.
- Tiempo del coder: 6.82 s acumulando intentos; no presupuesto comparativo
  ni predicción para las 42 filas completas. Cero timeouts/errores registrados.

El arquitecto leyó ambos scripts completos, cotejó resultados por intento
y volvió a comprobar los 17 hashes. El verifier repitió los scripts
byte-idénticos en `build/tmp/b3-ma-p02a-semantic-verifier-lnWBAP/` del candidato:
exit 0, 34/34 intentos válidos, cero timeout/instrument_error; los mismos
14 controles (7 match y 7 desacuerdos previstos) y las mismas categorías
de los veinte históricos. Plan e inventario fueron byte-idénticos al coder;
12 imports con procedencia correcta y 17 hashes verificados antes/después.
Veredicto: apto como factibilidad acotada, no aprobación de gate.

## Clasificación bruta de los veinte históricos

| Resultado | Número | Qué acredita |
|---|---:|---|
| Desacuerdo semántico | 2 | Profile alterado en IA01/02 cambia el resultado de la API |
| Supervivencia | 2 | Profile alterado en IA17/36 mantiene legítimamente el rechazo esperado |
| Rechazo de selección | 4 | Case desconocido; no hay ejecución semántica de ese caso |
| Rechazo de lenguaje | 8 | Result o field desconocidos, no defecto detectado del SUT |
| Rechazo de literal/oráculo | 4 | Expected mal formado; no confundir con literal válido pero incorrecto |

Los supervivientes son IDs históricos 81 y 181 del inventario preservado:
IA17 y IA36, columna profile, `beta3-p1` → `beta3-p1__mutated`.
IA17 produce InputCaptureError con código invalid_spec; IA36 produce TypeError
sin llamadas os.open/os.stat observadas durante la API. En ambos, el perfil
recibido llegó al InputSpec y se invocó la API.
No se modificaron fuentes para distinguir errores contractualmente iguales.

El arquitecto también ejecutó una sonda separada directa de la API, sin el
runner del piloto: para ambos perfiles obtuvo `InputCaptureError invalid_spec`
en IA17 y `TypeError context` en IA36 (cuatro llamadas, proceso exit 0).
La validación de argumentos precede a validate_root/open_root en el código
productivo. Esta sonda no se suma a los veinte mutantes ni repite las fixtures Git.

Existen controles adicionales con expected bien formado pero incorrecto:
SHA válido erróneo y booleano false en IA02, que sí producen desacuerdo tras
API real. Un case alternativo conocido ejecuta dos capturas de IA02 mediante
el mismo mecanismo de selección. No se usó el binding fijo como oráculo.

Límites del instrumento: el centinela observa os.open/os.stat, no cualquier
IO imaginable. Tampoco está preparado para clasificar uniformemente una
proyección ausente como error del instrumento: hoy puede producir desacuerdo.
No reutilizarlo para las 42 filas sin corregir y probar esa frontera. Los
rechazos de case ocurren antes de la API; los de lenguaje/oráculo después
de observar, sin que esa llamada los transforme en kills semánticos.

No llamar a este resultado «18 kills semánticos» ni descontar los dos
supervivientes. El CLI histórico podría sumar los 18 exits no cero como killed;
el piloto demuestra por qué esa agregación no acredita lo que se pretende medir.

## Recomendación del arquitecto: incremento separado, no más excepciones tácitas

Antes de continuar el hardening, revisar explícitamente el contrato del
instrumento de aceptación y su consumidor productivo:

1. Exigir baseline sano y procedencia/completitud comprobadas antes de mutar.
2. Separar fallos del instrumento y del lenguaje de desacuerdos observables.
   Un crash, import fallido, timeout o handler ausente bloquea; nunca killed.
3. Definir operadores conscientes del esquema y valores alternativos
   ejecutables; conservar inventarios anteriores sin reetiquetarlos.
4. Cuando una mutación válida preserve el comportamiento contractual,
   mantener supervivencia bruta y revisión explícita, sin forzar tests cosméticos.
5. Probar el motor con controles deliberadamente averiados y varias recetas,
   no solo la pieza con la que se está desarrollando el instrumento.

Esta recomendación no aplica una política nueva ni autoriza modificar el
motor protegido. La autorización humana de 54 supervivientes de fuentes sigue
limitada a aquel inventario: no cubre los supervivientes de aceptación ni
suprime la obligación de resolverlos. Bless/publicación no están autorizados.

## Lo que permanece pendiente

Aceptación semántica completa de 42 filas y variantes, integración de timeout
Git desde la API (IA34), límites independientes (IA33, incluida salida Git),
criterio de calificación de aceptación, LCOV/ratchets recientes, CRAP, DRY y
matriz global/full. No se avanzó esas etapas con un verde ficticio.

Evidencia en custodia local bajo build/tmp: IRs, inventario histórico completo,
plan, hashes de instrumento, stdout/stderr, recibos y resultados. No hay
garantía de backup externo. Coste de inferencia sigue unavailable; no se
atribuye causalmente este aprendizaje a un modelo barato ni a una comparación
sin WCT.
