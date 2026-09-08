# Integración de P01 y entrada vigente de self-hosting

Fecha: 2026-09-07. Candidato **CND-74E0**, hijo de CND-80B8. El humano ha
autorizado incorporar las aclaraciones a especificaciones/moldes y hacer
commit/push. **Bless reservado al humano; merge y release no ejecutados.**

## 1. Dictamen y alcance que se integra

P01 es el kernel puro de reconciliación exacta/no vacua de tres inventarios.
No es un runner ni certifica ejecución, éxito, frescura, completitud de mutación
o ahorro. [R0](reviews/REVIEW-CND-80B8.md) conserva su no conformidad;
[R1](reviews/REVIEW-CND-74E0.md) conserva su conformidad técnica bajo
`sh-p01/1`. La [adenda](runs/ADENDA-E61F-CND-74E0.md) corrige la explicación
del hash histórico y atribuye correctamente el 1/1 del coder y el 10/10 del
reviewer. No se borra ninguno de los resultados.

Los cuatro archivos de producto/tests/feature siguen congelados, con
manifiesto agregado
`909e58a71e9477ccc25822823f8b3615225b68fec713cf03e22be4ccabc09cb4`.
Orden y serialización exactos: [ENTREGA-v2 §6](ENTREGA-v2.md#6-identidad-de-candidato-sin-ambigüedad-de-rutas).
El SHA Git de integración incluirá documentación además de esos bytes;
no es el digest del candidato ni una autorización de bless.

## 2. Cambio de proceso solicitado

Leer primero [ADR-SH-02](ADR-SH-02.md),
[ENTREGA-v2](ENTREGA-v2.md), [MOLDE-WCT-v2](MOLDE-WCT-v2.md) y
[PROMPT-CODER-v2](PROMPT-CODER-v2.md). Son reglas documentales prospectivas:
recepción del contrato, scopes reales, tests discriminantes, binding explícito,
manifiestos reproducibles, atribución y custodia. No se han implementado nuevos
gates/compilador/ledger ni modificado la gobernanza protegida.

Se publican los 38 documentos BETA3 de contexto y expediente para que sus
dependencias internas sean consultables. Salvo avisos iniciales en los dos
README de entrada, se preservan sus bytes. Los estados, cifras y comandos
históricos se leen en la fecha y fase que declaran: no son aprobaciones
nuevas ni estado remoto actualizado. Los prompts anteriores no son el encargo
siguiente. Los planes de producto/experimento siguen sujetos a sus puertas.

Los antecedentes de G1, POST-PR36 y REVIEW-G1 no forman parte de esta PR.
Las referencias históricas a investigación local no publicada se consideran
contexto local, no prerequisitos normativos nuevos de P01; no se incorpora
documentación ajena solo para convertir todos los enlaces en enlaces públicos.

## 3. Verificación de esta integración

Comprobaciones propias del integrador antes de commit, en el worktree
`build/tmp/sh-p01-CND-74E0`, Python 3.13.14. Entorno reutilizado del worktree
padre, `uv run --no-sync` y `PYTHONPATH` dirigido al hijo; no se instalaron
dependencias. CI usa Python 3.12 y se comprobará por separado.

| Comprobación | Resultado observado |
|---|---|
| Identidad y Gherkin | Cuatro hashes y agregado `909e58a7…` intactos; feature byte-idéntica al bloque aprobado |
| Documentos previos | 36 idénticos; dos README con aviso antepuesto y resto íntegro |
| Colección | 405 tests collected, exit 0 |
| Fast | 7 PASS, 0 SKIP, exit 0 |
| Commit | 20 PASS, 0 SKIP, 1 FAIL: G-META-1; G-TEST PASS, 94.475 s |
| Integridad directa | Solo `nuevo protegido: tools/wct/evidence/__init__.py` y `identities.py`, exit 1 |
| DRY por defecto / pieza explícita | 3 / 9 unidades respectivamente; sin candidatos ni errores en ambos; no son el mismo scope |
| Cobertura global sin property | 404 passed, 1 deselected, 118.76 s, exit 0 |
| Ratchets tras ese productor | `--require all`: medidas 10 de 10 exigibles, exit 0 |
| Property separada | 1 passed, 404 deselected, 0.45 s, exit 0 |
| Red team | 30/30 rechazados; 13 engine, 13 tool, 4 hook, 0 heuristic, 0 SKIP |
| Frontera documental | 47 rutas exactas, sin sobrantes/faltantes; fences/whitespace sin defectos |
| Enlaces locales | 174 referencias comprobadas: 171 resuelven y 3 referencias históricas remiten a G1b no publicado, según §2 |

LCOV global nuevo consumido: `1edc351fdb9646e475cd33b77c2322f1a7b711524220a8d73fdd159400b18af5`.
La corrida global y su consumidor fueron secuenciales, sin cambios a producto,
tests/config entre ambos. Capturas nuevas bajo
`build/tmp/sh-p01-integration.mBS59X/`. La observación de tiempos es individual,
no un presupuesto emparejado ni demostración de coste del modelo.

No se repitieron aquí full/pr, mutmut, orden aleatorio, SBOM ni la campaña
manual del reviewer: sus resultados/límites anteriores están en el acta R1.
Tampoco se presenta la suma 404+1 como una nueva corrida única de `pytest -q`.

CI se revisará sobre el SHA efectivamente publicado. Antes del bless se espera
G-META-1 rojo por las dos rutas nuevas de `tools/wct/evidence`; debe comprobarse
en el log real. «Esperado» no exime investigar cualquier otro rojo. Un bless
no garantiza de antemano que el resto de CI pase.

## 4. Custodia y límites de reproducción

Expediente textual R0/R1, actas y adenda quedan en Git. Capturas originales,
LCOV y desafíos grandes conservan su ubicación bajo `build/tmp`, referenciada
con hashes en las actas. Estado de custodia de esos originales: **local-only**,
sin réplica durable externa acreditada. No se autoriza limpiar worktrees ni
artefactos; no afirmar replay completo a partir del Markdown publicado.

Antes de regenerar cobertura se preservó el LCOV global histórico R1 en
`build/tmp/sh-p01-integration.mBS59X/lcov-global-R1-original.info`, con SHA-256
`cdccbe33f605aae94ca052d56f355c4effc3e19f80d6a12f56d1d75363ae45e0`,
idéntico al original. La ruta mutable `build/coverage/lcov.info` del candidato
ahora contiene la corrida nueva de §3; no usarla para reproducir R1 histórico.

El arquitecto revisó código de otro coder, pero también definió su contrato:
no es independencia de supuestos ni un ensayo causal del efecto de WCT.
Asistencia y reparaciones siguen registradas; modelo y telemetría de coste
permanecen ciegos/unavailable. Ninguna cifra de coste por tarea está acreditada.

## 5. Secuencia y siguiente pieza

1. Publicar candidato en su rama/PR con staging de §6 y hooks activos.
2. Humano revisa el diff y ejecuta bless, citando número real de PR y SHA
   revisado. El agente no ejecuta `update-manifest --approved-by`.
3. Revisar artefactos regenerados; commit/push explícitos de los cambios
   esperados de integridad, repetir 21/21 y esperar CI completa del SHA nuevo.
   Otro cambio de producto exige nueva revisión; no encadenar re-bless.
4. Con revisión/CI verdes, pedir o confirmar autorización de merge; repetir
   comprobaciones sobre el SHA integrado con cobertura recién producida.
5. Preparar contrato de **P02** conforme al último apartado de
   [PROMPT-CODER-v2](PROMPT-CODER-v2.md). API/Gherkin/allowlist aún no están
   cerrados; hasta aprobarlos, no encargar implementación al coder.
6. Beta.3 mantiene las puertas de ensamblaje, evaluación y release de
   [PIEZAS](PIEZAS.md). Este commit no hace bump ni crea tag/prerelease.

## 6. Allowlist exacta de esta integración pre-bless

**47 archivos: 4 de producto/tests/feature y 43 documentos.**
No añadir otros por glob/directorio. El manifiesto de producto de §1 excluye
deliberadamente documentación: su hash no debe reutilizarse para estos 47 archivos.
Git identificará el conjunto integrado. Los artefactos del bless tienen otra
revisión/lista y no están autorizados a editarse manualmente.

```text
docs/evolution/plans/BETA3/D0.md
docs/evolution/plans/BETA3/EVALS.md
docs/evolution/plans/BETA3/GHERKIN-P1.md
docs/evolution/plans/BETA3/GHERKIN.md
docs/evolution/plans/BETA3/PILOTO-PREPARACION.md
docs/evolution/plans/BETA3/PLAN.md
docs/evolution/plans/BETA3/PRD.md
docs/evolution/plans/BETA3/PROMPT.md
docs/evolution/plans/BETA3/README.md
docs/evolution/plans/BETA3/RESEARCH.md
docs/evolution/plans/BETA3/SELF-HOSTING/ADR-SH-01.md
docs/evolution/plans/BETA3/SELF-HOSTING/ADR-SH-02.md
docs/evolution/plans/BETA3/SELF-HOSTING/ENTREGA-v2.md
docs/evolution/plans/BETA3/SELF-HOSTING/EVALUACION-CIEGA.md
docs/evolution/plans/BETA3/SELF-HOSTING/EVIDENCE.md
docs/evolution/plans/BETA3/SELF-HOSTING/GHERKIN-P01.md
docs/evolution/plans/BETA3/SELF-HOSTING/GOBERNANZA.md
docs/evolution/plans/BETA3/SELF-HOSTING/INTEGRACION-P01.md
docs/evolution/plans/BETA3/SELF-HOSTING/MOLDE-WCT-v2.md
docs/evolution/plans/BETA3/SELF-HOSTING/MOLDE-WCT.md
docs/evolution/plans/BETA3/SELF-HOSTING/P01-IDENTIDADES.md
docs/evolution/plans/BETA3/SELF-HOSTING/PIEZAS.md
docs/evolution/plans/BETA3/SELF-HOSTING/PROMPT-CODER-v2.md
docs/evolution/plans/BETA3/SELF-HOSTING/PROMPT-CODER.md
docs/evolution/plans/BETA3/SELF-HOSTING/README.md
docs/evolution/plans/BETA3/SELF-HOSTING/REGISTROS.md
docs/evolution/plans/BETA3/SELF-HOSTING/REVISION-Y-FEEDBACK.md
docs/evolution/plans/BETA3/SELF-HOSTING/reviews/PROMPT-CIERRE-CND-74E0.md
docs/evolution/plans/BETA3/SELF-HOSTING/reviews/PROMPT-CND-80B8-R1.md
docs/evolution/plans/BETA3/SELF-HOSTING/reviews/REVIEW-CND-74E0.md
docs/evolution/plans/BETA3/SELF-HOSTING/reviews/REVIEW-CND-80B8.md
docs/evolution/plans/BETA3/SELF-HOSTING/runs/ADENDA-E61F-CND-74E0.md
docs/evolution/plans/BETA3/SELF-HOSTING/runs/SHR-015D6C-CND-80B8.md
docs/evolution/plans/BETA3/SELF-HOSTING/runs/SHR-27687E-CND-74E0.md
docs/evolution/plans/BETA3/TRAZABILIDAD-D0.md
docs/evolution/plans/BETA3/VERIFICACION-D0.md
docs/evolution/plans/BETA3/decisions/ADR-B3-01-moldes.md
docs/evolution/plans/BETA3/decisions/ADR-B3-02-confianza.md
docs/evolution/plans/BETA3/decisions/ADR-B3-03-evaluacion.md
docs/evolution/plans/BETA3/decisions/ADR-B3-04-adopcion.md
docs/evolution/plans/BETA3/specs/SPEC-B3-01-moldes.md
docs/evolution/plans/BETA3/specs/SPEC-B3-02-evidencia-contexto.md
docs/evolution/plans/BETA3/specs/SPEC-B3-P1-evidencia.md
features/wct-evidence-identities-001.feature
tests/unit/test_evidence_identities.py
tools/wct/evidence/__init__.py
tools/wct/evidence/identities.py
```

Exclusiones expresas: README raíz, `docs/evolution/README.md`,
`docs/evolution/plans/G1/**`, `POST-PR36/**`, `REVIEW-G1/**`, `.nodeterm/**`,
`build/tmp/**`, governance, workflows, pyproject y uv.lock. Los prefijos cortos
POST-PR36/REVIEW-G1 se refieren a sus directorios bajo docs/evolution/plans.
La ruta física del worktree en build/tmp no convierte sus archivos relativos
de producto en artefactos publicables de build/tmp.
