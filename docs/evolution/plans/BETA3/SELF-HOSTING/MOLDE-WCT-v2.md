# wct-harness-local/2 — Pieza, ensamblaje y certificado limitado

Fecha: 2026-09-07. Molde documental de desarrollo para los próximos contratos,
no un pack compilable ni una nueva distribución de carpetas. Hereda la
Dependency Rule y los límites de [v1](MOLDE-WCT.md), añadiendo
[sh-delivery/2](ENTREGA-v2.md). No altera P01 ni los gates instalados.

## La pieza no es solo código con forma correcta

Una pieza entregable contiene **contrato + implementación + comprobaciones
discriminantes + evidencia identificable + límites**. Sus interfaces deben
encajar y su comportamiento debe contrastarse con expectativas independientes.
Ni la arquitectura ni un conjunto finito de tests garantizan ausencia de bugs.

| Responsabilidad | Puede depender de | No puede hacer | Prueba de encaje |
|---|---|---|---|
| Kernel puro de identidades P01 | stdlib, valores explícitos | Leer disco/procesos/reloj/config; afirmar éxito de tests | Igualdad exacta no vacua, precedencia, findings completos |
| Snapshot/workspace P02, futuro | Entradas explícitas y adaptador de filesystem | Elegir obligaciones desde resultados; tratar worktree como sandbox de seguridad | Inventario independiente, serialización, posesión y límites de rutas |
| Colección/terminales P03, futuro | Runner y contratos de snapshot | Confundir colección con ejecución o skip con éxito | Colección y terminal por identidad/fase, errores parciales visibles |
| Artefactos/cierre P04/P05, futuros | Resultados explícitos de piezas anteriores | Inferir frescura por presencia ni permitir «rechazar todo» | Cadena productora real, control válido y cada causa inválida |
| Entrada opt-in P06, futura | Ensamblaje y adaptadores anteriores | Cambiar salida legacy sin contrato | argv/exit/salida y ruta productiva completa |

Las rutas futuras de [PIEZAS](PIEZAS.md) son candidatas, no permiso de crearlas
todas. No construir una interfaz de un solo implementador sin frontera real
de IO. Cuando se apruebe una pieza, su contrato fija API, errores, consumidor,
diff y escenarios; el coder no decide por omisión.

## Hoja de fabricación exigida por pieza

| Sección del contrato | Criterio de entrada/salida |
|---|---|
| Intención | Qué obligación satisface y qué afirmación queda prohibida |
| Material de entrada | Tipos, procedencia, confianza, validación y límites de tamaño/rutas |
| Geometría de encaje | API, estados/errores, orden y consumidor real; compatibilidad observable |
| Tolerancias | CRAP, cobertura, complejidad, duplicación y scopes reales, sin bajar umbrales |
| Matriz de defectos | Positivos, defectos plausibles, adversarios y aserciones que los distinguen |
| Trazabilidad | Identidades de bytes y contexto, comando/actor/resultado y custody status |
| Promoción | Revisión separada y aprobación del diff; bless y release no implícitos |

No entregar un certificado que diga solo «todo verde». Debe decir qué pieza,
versión y bytes se compararon, contra qué contrato, quién midió qué y qué no
se probó. La frontera declarada de un gate forma parte de su interpretación.

## Límites aprendidos que el siguiente contrato debe explicitar

- Identidades no son conteos; un ID sustituido a N constante se detecta.
- `match` de P01 no prueba que expected sea independiente ni que haya ocurrido
  ejecución. Esa procedencia es obligación de sus futuros callers.
- Una cobertura completa de `tools/wct` no asegura CRAP aceptable ni tests
  semánticamente fuertes; se miden esas dimensiones aparte.
- Los bindings deben comprobar exactamente los campos que anuncian proteger;
  el texto del escenario y sus terminales no se deducen de una tabla de filas.
- Serialización de hashes es parte del protocolo, no un detalle del cwd.
- Workspace privado significa posesión operativa declarada; seguridad frente
  al mismo UID, carreras y symlinks requieren diseño y comprobaciones propios.

## Evolución del molde, no movimiento retrospectivo de la meta

R0/R1 se puntúan con v1. El siguiente lote congela v2 antes del primer intento.
El feedback nuevo propone una revisión numerada para el siguiente lote o una
corrección explícita del instrumento que reevalúe todos los afectados. Registrar
escapes, vueltas por defecto y tiempo humano; no atribuir una mejora de calidad
al modelo o al molde sin comparación adecuada y costes de todos los intentos.
