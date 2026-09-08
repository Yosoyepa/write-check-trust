# Gobernanza y contratos del negocio de WCT

Estado: especificación de proceso y producto; **no cambia governance/**.
La gobernanza ejecutable actual conserva su autoridad. Promover estas reglas
a YAML/gates requerirá un diff y aprobación propios, después de calibrarlas.

## 1. Autoridad y separación

| Objeto / acción | Responsable y permiso | Límite |
|---|---|---|
| Requisito, contrato, molde y scope | Arquitecto propone; `yosoyepa` aprueba la pieza | El coder reporta ambigüedad, no modifica el expected |
| Implementación y tests de desarrollo | Coder, solo allowlist de la pieza | Sin cambios al calificador, baselines, workflows, locks o modelo |
| Pruebas/oráculo de evaluación | Verifier o custodio separado del coder; challenge del arquitecto/humano | No copiar holdout al workspace ni usar expected calculado por el SUT |
| Revisión semántica | Arquitecto ciego al modelo | Autor de la especificación no es independiente de sus propios supuestos; necesita challenge |
| Ejecución verificadora | Verifier sin escritura en el candidato | No editar el fix que verifica; mismo diff/hash en todo el dictamen |
| Modelo, routing y recibos privados | Usuario/custodio | Solo él abre el cegamiento tras congelar calidad |
| Promoción, bless, commit/PR, release | Usuario decide cada frontera | Bless no valida comportamiento ni autoriza un diff posterior |

El prompt concreto prevalece sobre el DoD genérico del rol coder: **en P01 se
entrega sin commit/push/PR ni bless**. Se conserva así el circuito de revisión
humana solicitado; no se usa un texto genérico del rol para publicar por cuenta
propia. PROC-005 se cumple con un verifier distinto cuando haya implementación.

## 2. Reglas del dominio de confianza

| ID | Contrato | Consumidor / comprobación prevista | Motivo |
|---|---|---|---|
| SH-C01 | Una obligación se identifica, no se representa solo por un número | P01; sustitución con N constante | 10/10 puede describir diez obligaciones equivocadas |
| SH-C02 | Sin obligaciones válidas, sin acreditación | P01/P05; vacío y faltantes | Evitar verde vacuo |
| SH-C03 | `match` de identidades no significa tests pasados | P03/P05; setup/call/teardown | Coincidencia de nombres no observa conducta |
| SH-C04 | Required es aditivo: no apaga otros rojos | P04/P06 y tests históricos de ratchet | Evitar selección interesada del indicador |
| SH-C05 | Artefacto consumido pertenece a esta ejecución, inputs y productor | P02/P04; viejo, ajeno, truncado, cambio de inputs | Hash/presencia aislados no prueban frescura |
| SH-C06 | Compatibilidad histórica se preserva; evidencia nueva vive aparte | P06; seis campos, bytes fijos, exits | No romper adoptadores ni reetiquetar PASS histórico |
| SH-C07 | El candidato no aprueba sus cambios de controles | Custodia/Qn, scope y diff exacto | El juez no se modifica para aprobar al acusado |
| SH-C08 | Una capacidad desconocida/no soportada no se infiere de otra | Perfil P1/P05; mutación/arquitectura no acreditadas | Evitar sumar badges hasta inventar garantías |
| SH-C09 | Toda causa relevante permanece aunque otra sea prioritaria | P01/P05; error y fallo simultáneos | Diagnóstico no debe ocultar el defecto original |
| SH-C10 | Cada fila de aceptación comprometida tiene identidad y evidencia de ejecución | P03/P06; borrar una fila ejecutada | Parsear o generar un escenario no lo ejecuta |
| SH-C11 | No se asume equivalencia entre versiones/roots/lotes | P02 y ledger; diffs, deps, policy, tests, runner | Mismo HEAD o nombre no implica mismos inputs |
| SH-C12 | Un molde declara scope, aristas, tolerancias y limitaciones efectivamente consumidas | P07/P08; variar un campo cambia un veredicto | Campos decorativos e instrucciones sin enforcement no son contrato ejecutable |
| SH-C13 | Lo válido también debe pasar; rechazar todo es un defecto | Calificador; controles positivos y otra solución válida | Optimizar detección sin precisión inutiliza el harness |
| SH-C14 | Datos y logs no son instrucciones ejecutables | Adaptadores/contexto; sin shell/eval; escaping | Un diagnóstico o input puede ser malicioso |
| SH-C15 | El coste incluye intentos fallidos y reparaciones | Custodio/ledger; cobertura de recibos | Un éxito barato aparente puede ocultar muchos intentos |
| SH-C16 | Un hallazgo nuevo no cambia el pasado | Versiones/Qn y registro de feedback | Evitar mover el criterio según el resultado |

No registrar estos IDs como `verified_by` actuales: sus consumidores son
**futuros** salvo las comprobaciones históricas expresamente citadas.

## 3. Freeze y expectativas sin bucle de bootstrap

Hay tres freezes, no un hash mágico:

1. **Antes del coder:** contrato de comportamiento, casos/filas, alcance,
   criterios, Wn/Qn y permisos. Es el denominador semántico, no los bytes de un
   archivo que el coder todavía no ha escrito.
2. **Antes de verificar un candidato:** patch y bytes completos del candidato,
   revisión de bindings caso→nodeid, tests esperados del perfil, configuraciones
   y herramientas. La colección ayuda a proponer bindings, pero el custodio
   los coteja con el contrato; no usa observed como expected autoritativo.
3. **Antes de publicar dictamen:** outputs/resultados completos y sus digests,
   mismas entradas al inicio/fin. Una reparación produce otro candidate_id.

El digest de la implementación cambia legítimamente entre candidatos; el
contrato no. Para una comparación entre brazos, la tarea y el oráculo son los
mismos; los tests particulares del coder pueden tener otros nombres y se
puntúan contra el mismo comportamiento. No exigir que dos soluciones válidas
tengan idéntica estructura de tests privados.

En la cadena P1, por el contrario, los expected tests del **perfil de ese
candidato** se fijan antes de su productor y sí se comparan exactamente con
colección/ejecución. Separar esos dos denominadores evita imponer al control
los nombres de la implementación del tratamiento.

## 4. Estados y promoción

Proceso: `specified → authorized → implementing → candidate-frozen → reviewed`
`→ human-approved → integrated → qualified-for-next-piece`.

`needs-fix`, `blocked` e `inconclusive` son salidas válidas. Un fallo del entorno
no se cambia a PASS. La señal técnica del producto P1 tiene otra máquina:
`invalid > incomplete > rejected > accredited`; conservar todas las razones.
La pieza P01 tiene estados propios menores; no es el cierre de P1.

Todo verde de checks en el candidato se rotula `candidate-reported` hasta la
revisión independiente. Wn+1 se usa en nuevas tareas solo con calificación,
regresiones y límites registrados; **no se actualiza durante un lote emparejado**.

## 5. Integridad y bless en un repo que se cambia a sí mismo

Cambiar `tools/wct/**` hará que integridad detecte drift protegido. Ese resultado
permanece FAIL pre-bless: no se edita el lock, no se desactiva G-META-1 y no se
describe como 21/21. El verifier coteja que el diff corresponde exactamente al
allowlist autorizado y que el propio motor de integridad no cambió.

La autorización de implementar permite ese diff, **no** bendecirlo. Si el
drift incluye cualquier ruta no autorizada, hay un bloqueo adicional. Otros
gates rojos se diagnostican; no se excusan por «pre-bless». Fast debe pasar
antes del handoff o el estado rojo se declara conforme a PROC-001/012.

Cuando el usuario decida bless, revisar sus artefactos, SHA y razón; ejecutar
otra vez los checks sobre los bytes finales. Una nueva corrección de código
después de revisión invalida el dictamen previo sobre ese diff. No automatizar
bless ni usar identidades humanas sin esa autorización concreta.

## 6. Límites reales de aislamiento y seguridad

- Coder trabaja sin claves del custodio, datos productivos, credenciales de
  publicación ni acceso autorizado a holdout; red solo si su tarea lo exige.
- Worktrees evitan colisiones Git, no lectura del resto del disco. Permisos,
  usuario distinto/contenedor/host y montaje de solo lectura deben probarse
  para afirmar aislamiento. Este dossier **no los instala**.
- Ejecutar un patch es ejecutar código no confiable. El scorer debe controlar
  su proceso, inventario y salidas desde fuera; un test privado importado en el
  mismo proceso del candidato no es inaccesible para código hostil.
- Hasta calificar esa frontera, informar «revisión separada cooperativa», no
  seguridad contra un agente malicioso ni holdout técnicamente secreto.
- Prohibido seguir symlinks o borrar rutas ajenas para limpiar evidencias.
  P02 define directorios exclusivos bajo `build/tmp/`; no reciclar uno existente.

## 7. Cambiar una regla sin sobreajustar

Hallazgo reproducible → clasificar causa (código/contrato/instrumento/entorno)
→ control válido + defecto → propuesta de regla → medición de falsos positivos
y coste → revisión → versión nueva. Si es un falso positivo, no reformular el
código solo para engañar al detector. Si una regla debe cambiar, se tramita con
autorización; un ratchet no se eleva silenciosamente.

El propietario de triage es `yosoyepa`; el arquitecto mantiene propuestas. Los
IDs SH-* son identificadores locales, **no issues creados**. Si se difiere
trabajo en código, aplicar owner/issue real de PROC-009 antes de fusionar.
