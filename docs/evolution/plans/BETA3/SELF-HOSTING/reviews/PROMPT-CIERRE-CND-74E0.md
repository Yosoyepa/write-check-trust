# Prompt de cierre documental — CND-74E0

Basado en [REVIEW-CND-74E0](REVIEW-CND-74E0.md). Preparado, no ejecutado.
Su envío por el usuario autoriza solamente completar el expediente de P01;
no autoriza cambios de producto ni acciones remotas.

---

El arquitecto revisó CND-74E0 y lo considera técnicamente conforme al contrato
SH-P01 en su alcance aprobado. No hagas otro refactor. Conserva el modelo
oculto, el candidato padre, el hijo y sus artefactos. No empieces P02 ni
implementes propuestas del harness. Sin commit, push, PR, bless o publicación.

Lee el acta en:
`/home/jandradeu/Documents/well_code_template/docs/evolution/plans/BETA3/SELF-HOSTING/reviews/REVIEW-CND-74E0.md`.

1. Verifica que los cuatro archivos de CND-74E0 conservan el manifest
   `909e58a71e9477ccc25822823f8b3615225b68fec713cf03e22be4ccabc09cb4`, con
   la serialización ya acordada. Si cambiaron, reporta el drift y detente;
   este dictamen no cubre otros bytes.
2. Crea una **addenda nueva** bajo SELF-HOSTING/runs que cite
   SHR-27687E/CND-74E0 y el acta. No reescribas los registros previos ni los
   documentos normativos. No cambies producto, tests, feature o gobernanza.
3. Corrige la certeza de la explicación del digest de R0: aporta los bytes
   y comando originales que producen `de207e0d…`, o registra explícitamente
   «causa histórica no confirmada». Con las rutas absolutas y orden indicados
   el reviewer obtiene `01a1c071…`, no el hash histórico. No inventes otra causa.
   La identidad correcta de CND-74E0 no está cuestionada.
4. Registra que tú corriste `--require coverage-total` (1/1) y que el reviewer
   ejecutó `--require all` (10/10), con referencia a su captura. No atribuyas
   esa segunda corrida a tu sesión ni regeneres evidencia para ocultar la
   omisión. Distingue LCOV focal nuevo del reviewer y global entregado por ti.
5. Conserva la limitación del binding: detecta inventarios extra/duplicados,
   pero no prueba todos los pasos ni su ejecución. El feature actual sí fue
   cotejado verbatim. Es seguimiento separado del arquitecto, no permiso para
   cambiarlo ni condición para otra reparación de producto de este candidato.
6. Presenta la lista exacta para una futura PR: los cuatro archivos P01 y
   únicamente el expediente de evidencia que el humano elija incluir; deja
   fuera documentación ajena. Los artefactos grandes siguen en build/tmp,
   con referencias y hashes; su custodia externa aún no debe darse por hecha.

Entrega la addenda y la frontera propuesta para revisión humana. Mantén
G-META-1 pre-bless declarado sobre las dos rutas nuevas de producto; no ejecutes
update-manifest, no inventes un número de PR ni una aprobación de yosoyepa.
Para CI de un futuro SHA habrá que producir nuevamente el LCOV global antes
de consumir ratchets y verificar el diff exacto aprobado.

La autorización de crear PR, commit/push y el bless humano será otra decisión.
Esta pieza conforme no significa beta.3 terminada ni demuestra todavía ahorro
del modelo: preserva R0, R1 y la asistencia para la evaluación económica posterior.

---
