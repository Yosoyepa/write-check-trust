# Propuesta — piloto de aceptación semántica P02a

Estado: **para revisión; no autoriza implementación ni campaña**. Specifier:
`/root/p02a_binding`. Único cambio: este documento. No cambia los 17 archivos,
governance, runner general, P03, adjudicaciones ni bless.

## Decisión solicitada y bloqueo

Aprobar posteriormente un instrumento de evidencia pequeño, fuera del candidato,
que consuma IR original/mutado y llame capture_inputs. No construir todavía
un framework ni prometer cobertura completa de 42 filas.

Se leyeron completos skills/wct-acceptance/SKILL.md, ENCARGO-P02a.md y
tests/unit/test_evidence_inputs.py; se inspeccionaron parser, generador,
mutador, handler históricos, las 42 filas y API. La ruta histórica de la skill
no alcanza este vocabulario: generated lee WCT_ACCEPT_IR pero ejecuta handlers
del ejemplo; el binding P02a no lee esa variable. El baseline fallido lo
documenta el arquitecto en [HALLAZGO-P02a-ACEPTACION](HALLAZGO-P02a-ACEPTACION.md);
no es corrida propia del specifier.

**No prometer 210 kills semánticos** (42 filas × cinco columnas):

| Columna mutada | Tratamiento honesto |
|---|---|
| case | Los 42 IDs desconocidos no tienen receta: rechazo de selección, no kill del SUT |
| profile | Pasarlo realmente al InputSpec; un caso ya inválido puede conservar legítimamente invalid_spec |
| result | Contrastar resultado observado; token fuera de ok/error es rechazo de oráculo, no defecto productivo detectado |
| field | Los 42 selectores desconocidos son rechazo de lenguaje, incluso si hubo llamada API |
| expected | Contrastar literal recibido con proyección observada; separar literal inválido de desacuerdo semántico |

IA17 con profile inválido puede seguir devolviendo invalid_spec; IA36 puede
seguir rechazando antes de IO. Son hipótesis para el piloto, no resultados.
Conservar los 210 IDs brutos. No fabricar diferencias, ocultar supervivientes
ni trasladar automáticamente una excepción de mutación de fuentes a aceptación.
Si el cierre exige cero supervivientes históricos, permanece bloqueado hasta
decisión explícita sobre operadores/contrato/criterio. Este piloto no la concede.

## Piloto falsable de cuatro casos

Allowlist solicitada: directorio NUEVO exclusivo
`build/tmp/b3-ma-p02a-semantic-preflight-<id>/`, solo runner.py, controls.py,
IRs, recibos/logs y fixtures. Congelar runtime y hashes del instrumento y del
manifiesto vigente17; no usar el inventario histórico10 del encargo.

El runner recibe siempre WCT_ACCEPT_IR, también para original. No fallback,
_ROWS, hash-binding ni test fijo como oráculo. Por fila: case elige estímulo,
fixture produce InputSpec con profile recibido, llamada productiva retorna
snapshot/excepción, field selecciona proyección, result/expected se comparan.
No rellenar valores constantes por case ni obtener expected del SUT.

Casos y recetas:
- IA01: fixture abc; SHA literal aprobado contra InputFile real.
- IA02: dos capturas abc→abd; comparar digest observado.
- IA17: required ../outside; llamar API y observar invalid_spec.
- IA36: contexto None; excepción API y centinela de entrada a IO.

Reusar conceptualmente preparación input_repo/_git con stdlib y tipos públicos;
no ejecutar fixtures pytest por APIs privadas ni importar tests para llamar
sus aserciones. No extraer helpers del candidato. InputSpec/ContextRef actuales
no validan en constructor: IA17/36 sí pueden entrar a capture_inputs. Si un
constructor rechazara antes, registrar api_entered=false: acredita solo esa
frontera, no la captura, y requiere revisión antes de cubrir la fila.

Controles antes de mutar:
1. Los cuatro originales pasan con recibos API y observaciones reales.
2. IA01 con bytes alternativos y SHA literal independiente concordante pasa;
   los mismos bytes con SHA original fallan DESPUÉS de API. IA01 con profile
   inválido y oráculo error/code/invalid_spec pasa por excepción real. No se
   alteran el feature normativo ni sus expected para estos controles separados.
3. En procesos SOLO de control, dobles de llamada None, snapshot constante
   de una captura previa y error constante fallan en casos discriminantes
   (IA01/02, sanos y errores distintos). No exigir fallo de cada doble en cada
   fila. Son pruebas del instrumento, no kills ni ejecuciones del producto.
4. Generar las cinco mutaciones históricas de cada caso: 20 IRs preservados.
   Añadir expected válido pero incorrecto para IA01/02 y case conocido
   alternativo. Registrar supervivencias y su causa sin reclasificarlas.
5. Import, señal, timeout, crash o recibo truncado son instrumento inválido.
   Unknown handler/field nunca killed semántico. Éxito exige exit y recibo
   completo concordantes, no texto stdout.

Booleanos true/false exactos; campos ausentes no son false por default.
code proviene de InputCaptureError; TypeError no se convierte en un código
inventado. IA36 combina excepción y ausencia de IO, no solo mock assertion.

## Brechas para llegar a 42

| Familias | Recetas disponibles y trabajo pendiente |
|---|---|
| IA01–14,28–30,35,37,40 | Tests API de bytes/Git, inclusiones, orden/EOL/modo, exclusiones y comparaciones; falta devolver observaciones dinámicas en lugar del test fijo |
| IA15–18,31–32,36,38–39,41 | Errores de config/ruta/Git; preservar llamada API, causas y efectos; IA41 clone local y objetos sin incremento |
| IA19–22 | Variantes symlink/ancestro/exclusión/FIFO/socket; tests de helper FS no acreditan por sí solos integración API |
| IA23–27 | Races/fault injection: envolver frontera y delegar original, confirmar estímulo, restaurar estado; nunca sustituir respuesta productiva |
| IA33a/b | Límites exacto/+1 independientes: entries16 y bytes literales; manifest exige vector literal, no len(snapshot SUT) como origen del umbral esperado |
| IA34 | Tests actuales de timeout/salida son de proceso helper; falta montar Git de fixture que alcance frontera desde capture_inputs. Si no es viable, declarar hueco |

Después del piloto se diseña mapa fila→variante→receta→proyección; este cuadro
no demuestra cobertura42. bytes_source=worktree debe inferirse por hash real
contra payloads worktree/index/HEAD distintos, no etiqueta fija. partial_snapshot
es ausencia de retorno junto a excepción, no default vacío. Comparaciones
proceden de capturas reales. Límites reducidos no acreditan estrés máximo.

## Receta, presupuesto y puertas

Reusar parse_feature/mutations; run_mutations no distingue causas de exit ni
conserva diagnósticos suficientes para esta acreditación. Piloto: cuatro casos,
controles y 20 mutantes, proceso nuevo y fixture propia por intento. Medir
duración, llamadas y bytes/logs y aprobar topes antes de ampliación; no instalar
dependencias ni invocar proveedores. TMPDIR/basetemp exclusivamente build/tmp.

Si se aprueba expansión: baseline42 y proceso por mutante/fila, preservando IR
completo; cotejar que una sola celda cambió sirve para seleccionar trabajo,
no rechazar su valor. Son 210 procesos con variantes, no 8820 filas del IR
completo repetido. No adoptar toda la campaña in-process sin probar limpieza
de cwd/env/parches/hijos. No hay estimación empírica hecha en esta tarea.

Recibos: hashes candidato/instrumento/IR, runtime/cwd/argv, case/variante,
API entrada/retorno/excepción, observado/literal, categoría, exit/duración,
logs/hash. Preservar intentos, custodia local-only, verifier distinto del autor.

Si vive fuera17, el digest puede mantenerse pero la evidencia nueva requiere
revisión. Si necesita cambios de API/tests/feature, parar y renovar allowlist,
digest y revisión; adjudicaciones afectadas por nuevos bytes se reevaluarán.
No heredar conformidad por nombre de candidato.

Éxito del piloto: viabilidad de consumo dinámico IR y observación API en cuatro
casos, no cobertura42, gate verde ni cadena P03/P06. No se ejecutaron pilotos
ni campañas en esta tarea documental. La semántica completa y el conflicto210
siguen pendientes: no se introduce una exención implícita.
