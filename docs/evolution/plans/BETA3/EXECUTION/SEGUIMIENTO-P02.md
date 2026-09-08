# Seguimiento P02 — observaciones durante desarrollo

Registro del arquitecto. No es dictamen de producto ni primer candidato
completo. Cohorte B3-MA-D, consumo/coste unavailable. No reevalúa P01.

## Integración documental observada

- PR46 fusionada como `f6d395556ba9c97763811ab629c39b6aee9d1c13`:
  CI PR `34179918298` success y CI main `34180242693` success.
  Incluye D1 delegada; no bless del arquitecto.
- PR47 fusionada como `bb567a6b24dd28293e90ee5134ae9e5a06ac3356`:
  CI PR `34180657683` success. Solo las tres aclaraciones de P02a;
  CI de main `34180932959` observada después también success.

## Feedback temprano, no tasas de éxito

| Observación | Atribución y efecto |
|---|---|
| Git 86 sitios antes de completar adaptador; selección compartida 32 | Coder pidió partición antes de crear extras; arquitecto reprodujo 86, verifier desafió cohesión y exigió única fuente pura. Acta autoriza 17 rutas, sin relajar umbral |
| Mínimos required ambiguos para caller/API | Consulta del coder antes de expected; arquitecto aclaró responsabilidad P06 conservando selección exhaustiva P02a. No es detección de gate |
| Mutación default mide ejemplo | Inspección de herramienta, autorización focal aislada y evidencia separada. La campaña todavía no se acredita por haberla autorizado |
| Helpers IO escritos antes de tests | Desviación declarada por coder durante desarrollo; debe enumerar helpers/momento en handoff. No reconstruir rojo retroactivo ni afirmar TDD íntegro |
| CC 11 y 7 en borrador | Medición focal reportada por coder; exige refactor antes de entrega. No equivale a detección de G-CRAP sobre tools ni a incumplimiento final resuelto |
| Binding por segundo coder | 14 tests focales y 12 alteraciones reportadas por ese actor; no API ni ejecución de familias IA. Principal integra después y verifier revisará bytes finales |
| Edición durante repetición de una prueba | Coder declaró edición antes de terminar session93200; `api-races-red.txt` no califica identidad congelada. Conserva corrida anterior74063 y repite después sin edición concurrente. No se atribuye frescura a un nombre de log |
| Conteo manual de fixture IA33 incorrecto | Arquitecto revisó preparación: nueve archivos, seis directorios y frontera `.git` = 16 entradas, no 15. Se autoriza literal16 con lista independiente, no conteo derivado del SUT |
| Control IA41 clonado sin índice preparado | Coder observó D/?? para igual path; preparar índice del clon completo mediante read-tree HEAD, sin cambiar negativo ni API. Rechazo de duplicados se conserva; no se proclama soporte de todos los estados Git válidos |

Los cambios anteriores son asistencia/decisiones durante desarrollo. No contar
varios coders, módulos, sondas o reparaciones de borrador como tareas
independientes exitosas. El primer candidato completo se congelará cuando se
entregue; solo después procede dictamen R0 y tasa de primera aceptación.

### Pruebas FS adicionales antes de la primera entrega

El segundo coder recibió un archivo de tests exclusivo, sin editar producto.
Sobre dependencias congeladas reportó 33 PASS y tres defectos reproducidos:
symlink de directorio entre stat/open diagnosticado como io_error; descriptor
no cerrado si fstat falla después de abrirlo; enumeración que consume más de
N+1 antes de bloquear. El último había sido señalado primero por lectura del
arquitecto; los otros dos surgieron de los tests adicionales. No atribuirlos a
gates históricos ni a un verifier final que todavía no revisó el candidato.

Preservó también un fallo del instrumento: AF_UNIX con path demasiado largo,
corregido mediante bind relativo en la fixture. No es defecto del producto.
Entregó 37 nodeids; la corrida anterior ejercitó 36. El positivo exacto del
límite se añadió después y estaba pendiente de ejecución con las correcciones.
Evidencia local: `build/tmp/b3-ma-p02a-fs-tests/` del candidato. Hash del archivo
al devolver ownership: `6e0cd99e5a5a0760118dab7398eac86de6acd33d4b74d2c385e386234e1bd9dc`.

## Reproducción propia de mecanismo P02b

El arquitecto leyó el script de sonda completo y ejecutó otra corrida exclusiva:

```text
cwd: worktree documental beta3-execution.uW30FJ
uv run --no-sync python build/tmp/p02b-preflight-LQDdmh/probe.py build/tmp/p02b-architect-Q66yMa
runtime: Python 3.13.14, Linux 7.1.13, glibc 2.43
exit: 0
```

Con runtime compartido de P01 explícito y PYTHONPATH documental. Observó un
ganador de mkdir, ELOOP/ENOTDIR en enlaces, identidad distinta del reemplazo,
descriptores no heredables a exec (flag, no nueva sonda exec), link EEXIST sin
overwrite, errores inducidos postlink con terminal intacto, SIGKILL propio
con parcial y sin terminal, parser/IR de 24 filas sin findings. No ejecutó el
script followup ni implementaciones P02a/P02b para esa comprobación.

Artefactos de esta repetición en `build/tmp/p02b-architect-Q66yMa`, local-only;
stdout conservado en la salida de herramienta de esta sesión, no log durable
independiente. No volver a ejecutar sobre ese directorio ni borrar la única
copia. La sonda prueba mecanismos locales, no el lifecycle de la API futura.
