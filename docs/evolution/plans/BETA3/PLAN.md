# Plan de evolución a v1.0.0-beta.3

> Secuencia inmediata refinada por el encargo de automejora:
> [SH-P01–P10](SELF-HOSTING/PIEZAS.md). P01 es solo reconciliación de identidades
> dentro de P1a; no autoriza ni acredita la cadena completa. Evaluación de
> calidad ciega al modelo, datos monetarios posteriores y WCT como primer repo:
> [protocolo vigente](SELF-HOSTING/EVALUACION-CIEGA.md). Las puertas de cambios
> protegidos, integración y release del plan siguiente permanecen.

> D0 especificado para decisión en [D0](D0.md), pendiente de aprobación humana.
> B3-P1 se recorta a [una cadena tests/cobertura](specs/SPEC-B3-P1-evidencia.md)
> y se divide en P1a/b/c. P2 espera contrato P1 aprobado y cadena calificada.
> [Preparación del piloto](PILOTO-PREPARACION.md) incorpora la selección humana
> de personalAssistant y Codex; [verificación actual](VERIFICACION-D0.md).

Estado: **propuesta de alcance y secuencia**, 2026-09-07. Sin implementación,
bump, gasto de API, publicación ni cambios de gobernanza autorizados.
La aprobación de esta dirección no sustituye las puertas de cada incremento.

## 1. Orden recomendado

La secuencia útil es: reconciliar el estado → contrato/evidencia → molde mínimo
→ adopción/contexto → medir calidad/coste → calificar/publicar. No esperar a
tener un catálogo de arquitecturas para aprender si una sola aporta valor.

| Incremento / PR candidata | Alcance revisable | Salida obligatoria | Dependencia |
|---|---|---|---|
| B3-P0 Preparación | Aceptar/rechazar ADRs y escenarios; reconciliar beta.2, #12/#35/#33 y deuda local | tabla de decisiones, responsables, presupuesto técnico y primer diff previsto | ninguna |
| B3-P1 Evidencia mínima | envoltura de ejecución/capacidades seleccionadas; preservar GateResult y modo histórico | E01–E07 y controles válidos por ruta real; limits explícitos para capacidades restantes | diseño aprobado |
| B3-P2 Molde mínimo | schema/instancia, clasificación total y plan efectivo; compilación a consumidores existentes | M01–M10/M15–M16; equivalencia de dos layouts; sin hardcodes `example` en capacidades seleccionadas | P1, ADR-01/04 |
| B3-P3 Adopción y compatibilidad | inventario/mapeo/diff revisable, deuda por identidad, perfil beta.2 | M11–M14; no escritura durante plan; migración/reversión ensayadas | P2 |
| B3-P4 Contexto y contratos | paquete de tarea/diagnóstico; manifiesto de aceptación de features nuevas y contract tests del puerto | E08–E14; ruta ensamblada; cambio de firma/semántica detectado | P1–P3 |
| B3-P5 Piloto | runner opcional mínimo, scorer aislado, corpus, preflight y comparación | ledger íntegro, costes, resultados/intervalos y claims admitidos/rechazados | instrumentos calificados; presupuesto API aprobado |
| B3-P6 Release | docs/migración/bump protegidos, calificación de SHA final, prerelease/artefactos | GO de producto distinto de GO de ahorro; verificación remota del canal | features comprometidas listas, revisión humana |

Estas etiquetas no son números de PR de GitHub. Una fila puede partirse si el
diff deja de ser pequeño; por ejemplo, schema/plan antes que integración de
gates, o corpus antes que corridas. No abrir seis PRs dependientes para tenerlas
en progreso sin decisiones previas.

### Carril G1b: límite que no se resuelve con documentación nueva

Antes de utilizar mutación como claim fresco/completo, retomar
[SPEC-G1b-1](../G1/specs/SPEC-G1b-1.md) y
[su investigación local](../G1/INVESTIGACION-G1b.md). Hace falta:

1. Igualdad de identidades del inventario esperado/reportado, no N=N.
2. Matriz RG13 dentro del workspace propuesto, incluido cuerpo de test con
   nombre conservado y selección/source_paths propias.
3. Symlinks dentro de `mutants/src`, fallo parcial y pertenencia de artefactos.
4. Concurrencia con árboles distintos y política observable de exclusividad.
5. Presupuesto emparejado a escala relevante; causa del killed con evidencia
   suficiente o limitación expresa si el motor no permite observarla.

No sumar `tools/` a paths.source como atajo: seleccionar funciones/fixtures,
verificar soportes del motor y autorizar cambios protegidos primero. La mutación
del compilador/mapeo nuevo es candidata de alto valor para medir selectivamente.

Este carril puede investigar mientras se diseña el molde. Si queda abierto,
los contratos y el piloto deben fijar un perfil limitado que no exija mutación
acreditada. Eso permite estudiar utilidad arquitectónica/semántica, pero **no**
anunciar «validación completa» ni que beta.3 cerró G1b. Si producto exige ese
claim para beta.3, G1b pasa a ser bloqueo de release: decisión en Puerta D0.

## 2. Puertas y autoridad

| Puerta | Qué decide el humano | Qué NO autoriza |
|---|---|---|
| D0 Dirección | un molde hexagonal Python, alcance MVP, ADRs propuestos, si mutación acreditada es obligatoria para beta.3 | cambios protegidos o inferencias |
| D1 Implementación por incremento | Gherkin concreto, diff/frontera, compatibilidad y presupuesto técnico | implementación de los demás incrementos, bless automático |
| D2 Experimento | repos/corpus, modelos, precios, tope de gasto, oráculos y análisis preregistrado | publicación de claims positivos no sustentados |
| D3 Release | SHA calificado, matriz completa, notas/limits, tag y prerelease | mover un tag previo ni presentar beta como GA |

Cada PR de implementación sigue especificación aprobada → TDD → coder →
verifier distinto sin permiso de escritura (PROC-005) → gates → revisión humana.
Si toca archivos protegidos, el bless es posterior a revisar el diff exacto;
no es permiso para corregir la implementación sobre la marcha ni garantiza CI.

## 3. Presupuestos: medir primero, no estimar desde historias

### Producto y gates

Para cada motor afectado, comparar beta.2/candidato en el mismo host, snapshots
y locks fijados. Mínimo inicial de planificación: cinco pares alternados por
fixture, frío/caliente separado; reportar mediana, rango y N. Para colas/p95
ampliar muestra, sin atribuir estabilidad al percentil de cinco observaciones.

Medir por separado: compilación del molde, escaneo, cobertura, mutación,
colección/tests, contexto y tiempo hasta primer resultado completo. Distinguir
tiempo del bootstrap, primer verde y cada reparación. Las ejecuciones de beta.2
de ~1–4 minutos en otros informes no son presupuesto emparejado de beta.3.

Antes de D1 el propietario fija techo de latencia/CPU/memoria y tamaño de
contexto del incremento. No usar esos techos para rebajar coverage, suprimir
tests o omitir herramientas requeridas. Si no se cumplen, reducir scope de
feature y revisar el plan, no falsear completitud.

### Experimento

El piloto propone 144 runs más 4 de preflight separados; **ninguno autorizado
por esta propuesta**. Presupuesto superior: suma de los topes por run, compute,
costes de oráculo y revisión, más reintentos de infraestructura limitados por
regla explícita. Los costes exactos se cotizan al aprobar model IDs/tarifas.

Primero calificar fixtures sin claves y obtener un preflight autorizado pequeño.
Escalar solo si accounting/aislamiento funcionan y el coste observado cabe en
el techo total. Un stop de presupuesto conserva artefactos y no reinicia contadores.

## 4. DoD por incremento

- [ ] Gherkin aprobado y mapa requisito → test → resultado → evidencia.
- [ ] Compatibilidad del CLI/formato existente comprobada; funciones nuevas con
  contrato separado cuando cambian semántica.
- [ ] Tests relevantes nacieron rojos ante un defecto plausible; controles buenos
  y negativos independientes del generador de expectativas.
- [ ] Colección de tests comprobada y cero vacuidad de unidades exigidas.
- [ ] Verifier independiente revisó el diff final y sus limitaciones.
- [ ] `git diff --check`, fast, commit y ratchets; full/otros según el impacto
  aprobado. No presentar una suite parcial como gate completo.
- [ ] Orden aleatorio con versión/semillas/alcance registrado; no omitir una
  dependencia de orden porque el orden habitual pasa.
- [ ] Mismas configuraciones/inputs/artefactos soportan la evidencia declarada.
- [ ] Presupuesto medido; errores, skips y flakes registrados, sin relajar ratchets.
- [ ] Usuario revisó cambios protegidos y bless cuando corresponda; staging exacto.
- [ ] CI y post-merge sobre SHA final; hallazgos restantes con owner/issue reales
  antes de diferir trabajo en implementación.

## 5. Contrato de salida beta.3

### Funcionalidad y adopción

- [ ] Pack hexagonal Python versionado y calificado para las capacidades anunciadas.
- [ ] Dos layouts equivalentes, un caso brownfield y una ruta de puerto/CLI real.
- [ ] Instancia mal configurada, vacía, contradictoria o fuera del MVP no acredita conformidad.
- [ ] Perfil beta.2 de compatibilidad, migración/reversión y cambios de comportamiento documentados.
- [ ] Mapeo, política y scopes efectivos no divergen entre instrucciones, motores y reportes.
- [ ] B3-01/B3-04 publican evidencia/limits sin proclamar cierre de los 34 gates.
- [ ] G1b resuelto si se exige ese claim; de otro modo límite publicado y perfil
  congelado que no lo presenta como acreditado.

### Medición

- [ ] Corpus/runner/oráculo calificados; piloto completo o desviaciones visibles.
- [ ] Costes incluyen fallos, retries y revisión; no hay claim de ahorro sin soporte.
- [ ] Diferencias por tarea/repo, incertidumbre y escalamientos informados.
- [ ] Si falta presupuesto de piloto, volver a D0 a recortar la promesa de beta.3;
  no declarar «piloto completado» ni ahorro por tener la infraestructura.

### Publicación

- [ ] SHA final congelado después de code/docs/bump; no calificar un SHA y etiquetar otro.
- [ ] Gates pesados y smoke de adopción del SHA final con presupuesto aprobado.
- [ ] SBOM/evidencias y manifiesto con SHA/digests; sin secretos o holdout público.
- [ ] Notas beta.2→beta.3 separan entregado, experimental y diferido.
- [ ] Tras autorización: tag inmutable `v1.0.0-beta.3`, smoke del tag y release.
- [ ] Consulta remota verifica `isPrerelease: true`, `isDraft: false`, tag al SHA
  aprobado, assets correctos y no promoción indebida a Latest estable.
- [ ] El estado remoto se comprueba incluso si el comando de publicación salió 0.

La discrepancia beta.2 `isPrerelease:false` se puede corregir con autorización
específica sin mover su tag. No se ha corregido en este turno. La existencia de
un asset no acredita su correspondencia: verificar su contenido/manifiesto.

## 6. Backlog fuera de esta beta y criterios de entrada

| Candidato | Por qué no entra ahora | Qué lo desbloquea |
|---|---|---|
| Otros lenguajes | motores y semántica no equivalentes | contrato de capacidades por lenguaje y adopción real |
| Composición libre de arquitecturas | interacciones y coste de soporte sin medir | dos packs útiles y prueba de conflictos/inter-contextos |
| Model routing automático | riesgo de aprobar/escalar con señal insuficiente | curva coste/calidad por tarea y presupuesto/autoridad explícitos |
| Catálogo de scaffolds/marketplace | no valida comportamiento y añade cadena de suministro | demanda y valor medidos del primer molde |
| Mutación de todo el harness | coste/invalidation/causa no acreditados para todo tools | G1b y presupuesto selectivo con alto valor discriminador |
| Leaderboard/fine-tuning | riesgo de contaminación y optimización del indicador | corpus gobernado, confirmatorio y evidencia externa |
| Dedup por cuota | puede añadir abstracciones sin valor | hotspot concreto y mejora preservando comportamiento |

Owner de triage propuesto: `yosoyepa`. D0 asignará responsables reales y decidirá
qué issues abrir; no se inventan referencias remotas. Lo no seleccionado no es
trabajo autorizado y no debe aparecer como implementación implícita en el prompt.
