# P02a R3 — puerta humana, no GO de hardening todavía

Dictamen del arquitecto: **no autorizar bless ni declarar beta.3 cerrada**.
El candidato resolvió los hallazgos técnicos revisados, pero la regla vigente
de cero supervivientes impide avanzar sin la decisión humana descrita abajo.
No se cambió governance ni se filtraron resultados.

## Identidad y evolución observadas

Worktree de producto: `build/tmp/beta3-p02a-candidate`, rama
`codex/beta3-p02a-inputs`, base `b414ba63f0de06477da7ef445e4ccec7624fb578`.
Diecisiete archivos de producto/tests/feature sin commit, manifiesto R3:
`e4b25b2b16183de4da325f2c1264a53a1d5590e1eda1e1943635d1e3eb080570`.
El handoff está fuera del manifiesto y conserva el historial de asistencia.

| Campaña | Identidad abreviada | Generados | Killed | Survived bruto | Timeout |
|---|---|---:|---:|---:|---:|
| Inicial | 5a5fe9dc | 1552 | 1295 | 257 | 0 |
| R1 | 451a1256 | 1564 | 1468 | 96 | 0 |
| R2 | ffe546c2 | 1564 | 1506 | 57 | 1 |
| R3 | e4b25b2b | 1564 | 1510 | 54 | 0 |

El arquitecto cotejó independientemente el AST generado y resultados R3:
1564 identidades únicas, cero faltantes/extras; estados1/0:1510/54. También
cotejó los17 hashes actuales y comprobó que las doce fuentes permanecen
idénticas a R1. R1→R2 cambió tres tests y R2→R3 solo el test de filesystem.
No llamar a esos refuerzos decenas de defectos nuevos de producto corregidos.

Las campañas fueron ejecutadas por el coder; la revisión independiente y
los cotejos del arquitecto no se presentan como nuevas campañas. No hay
comparación causal de modelos ni medición económica disponible. La primera
campaña y R1 tampoco tienen exactamente el mismo denominador.

## Qué mejoró y qué sigue sin acreditarse

Se corrigieron validación que copiaba valores antes de comprobar sus tipos
y errores secundarios de filesystem sin normalizar. Tests posteriores
reforzaron JSON literal completo, códigos exactos, límites independientes,
lecturas multibloque, caches/profundidad, RootBinding, contexto y causas de
excepciones. Las revisiones preservan los rojos anteriores al fix.

El timeout R2 fue conservado como tal, no como killed o flake. R3 aisló el
caso FIFO en un hijo con plazo2s y kill/recolección, sin cambiar fuentes. El
coder informó una sonda específica posterior al full: original1PASS;
mutante `_open__mutmut_7`,1FAIL por plazo del test, antes del watchdog mutmut.
No es fallo del candidato original ni permiso para reintentar silenciosamente.

La última ejecución focal del coder fue 261 PASS; colección 666 total. Fast 7/7,
lint y tipos sobre 12 fuentes reportados verdes. El verifier independiente
repitió colección (666, exit 0), focales (261 PASS) y fast (7 PASS, cero SKIP
o FAIL); comprobó 17/17 hashes antes/después y 12/12 imports de la candidata.
Su dictamen es favorable pre-hardening, no GO. No sustituir estos datos por
un full global que no se corrió. Aceptación mutada, LCOV/CRAP/DRY finales, matriz global y
calificación postintegración **siguen pendientes**. No se afirma que el único
rojo actual sea G-META-1 sin ejecutar esa batería sobre el incremento final.

## Adjudicación propuesta de los54 supervivientes

Inventario por ID, hash de fuente, delta y motivo:
[P02a-ADJUDICACION-R3.json](P02a-ADJUDICACION-R3.json).
El arquitecto comprobó que su conjunto coincide exactamente con los54
supervivientes R3, sin extras/faltantes. Las fuentes son las mismas que la
revisión independiente de equivalencias; no se transfirieron solo nombres.

- **47 E:** equivalencia semántica del perfil revisada independientemente;
  ejemplos: selección del encoder False/None, aliasUTF-8 y último componente
  de rsplit. Se conservaron los contraargumentos y límites de runtime.
- **7 D:** no son bytes idénticos. Seis modifican texto de TypeError sin
  dejar de identificar el argumento; el contrato no fija ese texto literal.
  El séptimo difiere en scheduling por un select adicional tras EOF. La
  revisión independiente comprobó pipes reales y progreso con EpollSelector:
  no pierde bytes, ni evade límite/recolección. No se prometía batching exacto
  o éxito a nanosegundos del deadline. El arquitecto acepta esas interpretaciones
  contractuales, **no** un filtro automático de sus supervivientes.
- **0 R/U/I en el cierre R3:** no quedan gaps no equivalentes, desconocidos
  ni errores del instrumento dentro de esta clasificación. Esto no demuestra
  ausencia universal de defectos ni satisface por sí solo cero raw.

La aplicación de una excepción a E/D todavía requiere permiso humano.
[La propuesta de política](PROPUESTA-ADJUDICACION-MUTACION.md) está publicada
para revisión, no activada por haber fusionado documentación.

## Decisión que se solicita

Autorizar **solo para la calificación focal P02a** la adjudicación explícita
de estos54 IDs sobre los bytes/runtime referenciados:47E+7D. Conservar54
supervivientes brutos en todo informe; nunca convertirlos en killed ni
publicar cero raw. Cualquier nuevo survivor, cambio de fuente/operador/runtime
o supuesto contractual debe revisarse nuevamente. Los demás gates y sus
umbrales, el bless y la publicación no cambian.

Si se autoriza, continúa aceptación→LCOV/CRAP→DRY y verificación global con
revisor separado; después se prepara la PR exacta de producto y su puerta de
bless humana. P02b y P03a tienen contratos preparados, no productos completos.
Si no se autoriza, se conserva el bloqueo actual: no se modifica código sano
para ocultar operadores ni se construyen tests cosméticos para fabricar0.

## Custodia y documentación integrada

Las campañas, logs y manifest original permanecen en
`build/tmp/b3-ma-p02a-r0/` del candidato. Son custodia local; no se promete
backup externo ni se deben borrar. El JSON por54 IDs preserva en Git los
deltas y razones sujetos a revisión, pero no reemplaza todos los logs.

PR49: squash `d7ba1e7b780453725647d1ec3f25057fe8778257`; CI PR
`34184286145` y main `34184588095` success. PR50 documental: squash
`0498e54ce81ccb5803aa8c4c6261e43769ed0c40`; CI PR `34185832920` y main
`34186286036` success.
Se aprobó el contrato puro P03a, no la adjudicación humana ni su producto.
El árbol original del usuario se preservó sin checkout/stash; digest del
diff tracked conservado `f604fe3876cfce5a87391d29f5aeda2e902b712fa2ba1288260555958893d0cd`.
