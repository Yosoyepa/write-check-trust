# D1-P02b — contrato autorizado, dependencia de implementación pendiente

El arquitecto, bajo la delegación humana registrada en [D1](DECISION-D1.md),
aprueba API, tipos, errores, lifecycle, matriz/Gherkin y allowlist P02b después
del challenge de `verifier`. No es GO de producto ni bless.

## Paquete exacto

| Documento | SHA-256 |
|---|---|
| [PROPUESTA-P02b.md](PROPUESTA-P02b.md) | `8561047c0f7d1e9d0ce0077ffe347002aea802626b7c746a7c61c46330ccc004` |
| [SONDA-P02b.md](SONDA-P02b.md) | `ac1c936a29d9a3a234f37b8e8a18abdaecb1de8569619bb6a8cb1f9f9151b889` |
| [PROTOCOLO-P03-PREFLIGHT.md](PROTOCOLO-P03-PREFLIGHT.md) | `16a4d72b0d795a1ea6aaff37aa308185a84b90428f03cb07966b8f360bbef760` |

Gherkin: 24 familias, variantes/nodeids literales de §7.1 y sus controles
positivos; cuatro variantes adicionales de margen al publicar. Allowlist de
§8: cinco módulos, cuatro archivos de tests y una feature; diez rutas exactas.
Su identidad final usa esas diez rutas POSIX relativas ordenadas por bytes
UTF-8 y la serialización ENTREGA-v2, no un digest de logs o documentación.

## Decisiones y razones

- Mantener los cuatro slots: journal único del supervisor por execution ID,
  log combinado con offsets, base coverage y LCOV privados. El multiplexado
  fue ensayado y sus capturas cotejadas por reviewer distinto. El log no es
  canal de decisión ni conserva identidad stdout/stderr de cada byte.
- Padre existente `root/build/tmp`, no creado implícitamente por P02b. P06
  deberá preparar esa precondición con reglas explícitas.
- P02b no elimina nada; conserva ambos nombres del terminal propio. Simplifica
  fallos/custodia y evita una limpieza innecesaria dentro de esta pieza.
- Margen de publicación previo a efectos: entradas +2 y bytes +2*envoltura.
  Un finish válido no debe incumplir check por sus propias escrituras. Este
  defecto fue detectado por challenge documental, no por gate productivo.
- `check` vincula owner/inputs; no autentica payload terminal. P04/P06 deben
  validar bytes/refs/semántica contra TerminalRef conservado fuera del archivo.
- Cualquier basetemp de P03 irá bajo artifacts/ o logs/, nunca en el nivel
  raíz cerrado del workspace. No hace falta otro slot público reservado.
- Precisión transferida desde P02a: WorkspaceError es excepción Python normal,
  no dataclass frozen. La inmutabilidad de los tipos de salida de §3 aplica
  a WorkspaceRef, ArtifactLocation y TerminalRef; no a traceback/context de
  la excepción ni al lease operativo. Se conservan code/path/errno. Ver
  [motivo reproducido](DECISION-P02a-EXCEPCION.md); no repetir el mismo fallo
  de contrato en la siguiente pieza.

Esto aprueba las ubicaciones de P03, **no** su protocolo, hooks privados,
schema, selección de plugins o implementación. Esas decisiones requieren un
contrato específico calificado. Ningún worktree se presenta como sandbox.

## Genealogía de evidencia

La sonda conserva el hash histórico `7cccea9c…` y luego `04749059…` del contrato:
esta última revisión precisó par permanente, st_size y mapa de variantes.
P03 inspeccionó `13ae6e67…`; los cuatro slots no cambiaron desde ese corte.
La revisión autorizada `8561047c…` añadió el margen aritmético y cuatro casos.
No se atribuye a esos cambios una nueva corrida del producto inexistente.
El verifier cotejó los hashes de las sondas y recomendó aprobación de este
paquete final; el arquitecto repitió mecanismos P02b por separado, con el
alcance declarado en [seguimiento](SEGUIMIENTO-P02.md).

## Puerta de inicio y entrega

El coder P02b **no inicia todavía**: debe recibir P02a estable y revisada,
base integrada exacta, hashes/API disponibles y recibo de entendimiento.
No escribir contra una rama mutable del otro coder. Su handoff adicional será
`docs/evolution/plans/BETA3/SELF-HOSTING/runs/HANDOFF-B3-MA-P02B-R0.md`;
evidencia nueva exclusiva en `build/tmp/b3-ma-p02b-r0/`, sin sobrescribir un run.
No existen todavía esos resultados ni un candidato P02b aprobado.

Sin commit/push/bless por el coder; el coordinador sigue integración revisada
por PR. Preservar positivos, rojos, variantes y límites, verificación focal
de las cinco fuentes y gates globales diferenciados. Cambiar partición/API
requiere nueva decisión previa. Bless y publicación siguen siendo humanos.
