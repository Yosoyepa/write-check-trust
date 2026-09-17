# Beta.3 — cierre parcial y reanudación acotada

Estado: PAUSADO por petición humana. No GO de release, bless, commit o push.
El usuario pide cerrar lo posible y continuar después: una beta debe aportar
una evolución útil, no alcanzar perfección. El arquitecto reconoce que amplió
demasiado la calificación y sus investigaciones respecto a ese objetivo.

## Entrega conservada

- Worktree: build/tmp/beta3-acceptance-engine; rama codex/beta3-acceptance-engine.
- Base/HEAD: 932c835ac0eeb75010ec7a1071315b1c51f78eb6. Cambios sin commit.
- AC1 implementado: baseline antes de mutantes, recibos vinculados al IR,
  distinción de desacuerdo semántico/error instrumental y transporte acotado.
- Refuerzos de tests revisados e incorporados: estados/causas, parser,
  configuración real del observer, escenarios ausentes, entorno privado,
  UTF-8 independiente del locale y control de lectura de recibo sobredimensionado.
- Fuentes/fixtures/feature: 18 rutas permanecen idénticas a source-review-2.
- Manifiesto final de 23 rutas: build/tmp/b3-ma-ac1-r0/candidate-r4-final.sha256,
  SHA256 d28c8991424c085ffb62e2713a053e03b27e8d8fe882dec3f278c391d7e06f9c.
- El trabajo ajeno del checkout principal y el candidato P02a no se incorporaron.

## Verificación y límites

El verifier ejecutó en el checkout real fast: 7 PASS, cero SKIP/FAIL, exit 0;
colección global: 599 tests, exit 0. No confundir colección con suite ejecutada.
En la copia revisada ejecutó 217 pruebas focales/ratchets; el último control de
memoria se verificó después por separado. No afirmar una suite global verde
ni una corrida conjunta de 218 por sumar esas ejecuciones.

Durante la incorporación, un hunk ambiguo reubicó un test preexistente sin
cambiar su cuerpo; el hash lo detectó. Se corrigió mediante sustitución exacta
del archivo revisado. El fast/collect anterior vio los mismos tests, en otro
orden; no se atribuye retroactivamente esa ejecución a los bytes finales.
candidate-r4.sha256 conserva el primer traslado; candidate-r4-final.sha256
identifica el orden exacto finalmente corregido. git diff --check pasa.

La copia auxiliar omitió inicialmente reglas generadas/fixtures quality; esos
fallos de preparación se distinguen de defectos del producto. El control de
memoria usa un fixture de 8 MiB y un separador diagnóstico de 4 MiB: detecta
read(None), no modifica policy ni demuestra una cota universal para toda IO.

## Campaña detenida, sin maquillar resultados

Se interrumpió mediante SIGINT el proceso validado de la copia
build/tmp/ac1-mutation-r2.hObK4N, sobre R3, por cierre de sesión humano.
Resultados brutos: 1.481 IDs = 1.319 exit 1 + 112 exit 0 + 50 null.
Es parcial: no G-MUT aprobado, no cero residuos y no resultado de R4.
Mutmut devuelve exit 0 al gestionar la interrupción; no significa éxito.
La receta serial corrigió los problemas instrumentales de las dos tentativas
anteriores, pero no se infiere un resultado completo de lo que falta ejecutar.
El proceso principal terminó; el hijo de timeout observado acabó naturalmente.
No quedan esos procesos activos. No se eliminó evidencia ni se lanzó otra campaña.

Logs, metas, árbol generado y manifiestos permanecen bajo build/tmp. Son
evidencia local, no custodia externa garantizada. Las revisiones parciales
por módulo preservan sus reservas y no conceden excepciones automáticas.

## Próxima sesión: suficiente para una beta

1. Acordar un alcance mínimo de cierre, sin añadir features nuevas. Separar
   bloqueos funcionales/seguridad de diferencias cosméticas y equivalencias.
2. Resolver únicamente los bloqueos que impidan ese alcance; no repetir toda
   investigación ni reiniciar campañas pesadas sin justificar qué decisión
   habilitan y acotar su duración antes de ejecutarlas.
3. Revisar la admisión de residuos con el criterio vigente y, si hiciera falta,
   pedir decisión humana explícita. Esta pausa no baja umbrales ni aprueba
   equivalencias, especialmente las 54 de P02a para otro incremento.
4. AC2 (operadores tipados) y FI1 (aislamiento de fixtures) siguen como propuestas,
   no implementaciones. Decidir si son imprescindibles para beta.3 o trabajo
   posterior; no convertir automáticamente cada oportunidad en bloqueante.
5. Solo con diff acotado y criterio de aceptación resuelto: PR revisable,
   bless humano cuando corresponda y verificación proporcional al riesgo.

No se afirma todavía mejora causal por modelo económico, ahorro de inferencia
ni automejora autónoma. Hay mejoras concretas de implementación/pruebas y
hallazgos útiles; la evaluación económica sigue sin datos de modelo/coste.

### Prompt breve para reanudar

Lee este cierre y los contratos existentes. Propón primero el mínimo necesario
para cerrar beta.3 como evolución utilizable. No abras otra auditoría general
ni nuevas features. Conserva los bytes/evidencias, prioriza fallos funcionales
y de seguridad, separa equivalencias y cosmética, y acota por adelantado la
verificación. No reinicies mutación exhaustiva ni cambies umbrales sin una
decisión explícita. Presenta el diff mínimo y los riesgos aceptables antes de
PR/bless; no declares completa una comprobación parcial.
