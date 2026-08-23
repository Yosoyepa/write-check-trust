# Runbook del mantenedor

> [!WARNING]
> Procedimientos que requieren al humano como autoridad de aprobación. Ninguno
> es ejecutable por el agente: el hook PreToolUse los bloquea.

## Bless con baseline incluido

El gate G-SECRET lee `.secrets.baseline` sin reescribirlo (filtrado de solo
lectura), así que una corrida normal de gates no ensucia la ruta. Solo la
regeneración manual — `detect-secrets scan` con `--baseline`, sea desde el
skill de seguridad o desde reglas propias del proyecto — reescribe el archivo,
y como es una ruta protegida eso exige bless. Si el baseline cambió, inclúyelo
desde el inicio, en UNA sola línea (los backslashes de continuación no
sobreviven al copy-paste):

```bash
git add .secrets.baseline governance/ && uv run wct integrity bless --approved-by "nombre" --reason "aprobado en PR #N: explicación concreta"
```

El `--reason` debe citar la evidencia de aprobación: URL de PR/comentario o
referencia `#N`. Una frase en prosa no prueba nada y el comando la rechaza.

## Manifiesto de mutación y bless atómico

`wct mutate update-manifest` regenera el manifiesto diferencial (las funciones
se identifican por fingerprint semántico `archivo::qualname`, no por línea).
Con aprobación humana regenera también el lock en el mismo paso, así G-META-1
nunca observa un manifiesto fresco con un lock desfasado:

```bash
uv run wct mutate update-manifest --approved-by "nombre" --reason "aprobado en PR #N: motivo"
```

## Dependabot en bloque

> [!TIP]
> Para un grupo de PRs de dependencias atascadas: una sola rama con los
> cambios + `uv lock` + un único bless resuelve todas con el coste de una.
> Cierra las PRs individuales haciendo referencia a la consolidada.

Las PRs de Dependabot que toquen `pyproject.toml`, `uv.lock` o
`.github/workflows/**` llegan con G-META-1 rojo **por diseño** hasta el bless:
es el harness exigiendo que un humano revise el cambio del plano de control.
La configuración vive en `.github/dependabot.yml` (ecosistemas `uv` y
`github-actions`, grupos de minor+patch).

## Ratchets

Si un ratchet bloquea, mejora la métrica; no subas el umbral. Registrar un
nuevo piso exige evidencia de aprobación y queda asentado en
`governance/ratchet-log.md`:

```bash
uv run wct ratchet record --approved-by "nombre" --reason "aprobado en PR #N: motivo"
```

## Tests flaky

Registra cada flake en cuanto aparezca — nombre del test, corrida (job y
fecha) y si pasó al reintentar. Un flake sin registro es deuda invisible que
erosiona la confianza en CI. Con esos datos se decide después entre un
presupuesto de reintentos acotado o aislar el test; ninguna de las dos
decisiones se toma en caliente.

## Stop hook y anti-deadlock

El Stop hook corre el tier `commit` y bloquea el cierre del turno si falla.
Ese contrato presume que el agente que cierra es autor del estado del árbol.
Un rol de solo lectura (verificador, resumidor) que hereda un árbol rojo
ajeno no puede cumplirlo jamás: cada intento de cierre rebota, y el agente
entra en loop (hallado en el piloto durante la integración de wct 0.3.0).

Dos válvulas:

1. `WCT_HOOK_ROLE=observer` en el entorno del agente observador: el stop
   imprime `WCT WARN (observer): ...` y deja pasar. Resérvalo para roles sin
   permiso de escritura; un coder con esta variable se autoexime del gate.
2. Cortacircuitos global, sin configuración: la tercera bloqueada consecutiva
   del mismo evento pasa con `WCT WARN (DEADLOCK GUARD)`. La racha vive en
   `build/hooks/guard-streak.json` y se reinicia con un stop verde.

Un stop que pasa por una válvula no es un árbol verde: es un agente que puede
entregar. El aviso obliga a declarar el árbol rojo en el handoff, y la CI de
PR sigue siendo la frontera dura.

## Webhooks

`wct webhook` emite un envelope JSON v1 firmado con HMAC-SHA256. La URL y el
secreto solo se leen del entorno; HTTP se rechaza salvo localhost:

```bash
export WCT_WEBHOOK_URL=https://quality.example/hooks/wct
export WCT_WEBHOOK_SECRET='obtenido-desde-el-secret-store'
uv run wct webhook gate.completed --data '{"tier":"commit","status":"PASS"}'
```

El contrato está en `governance/adapters/webhook.schema.json`. El harness no
envía webhooks automáticamente hasta que el proyecto configure un receptor.

## CI

- `quality.yml`: tras `uv sync --frozen` corre `wct integrity check` (una PR
  que toque rutas protegidas sin bless falla en CI, no solo en local), commit
  tier, aceptación mutada y red-team.
- `full-hardening.yml`: tier completo semanalmente y bajo demanda.
- Los avisos de integridad siguen la semántica de runner limpio: una ruta
  protegida ausente y NO versionada es `aviso`; una ruta versionada eliminada
  es bloqueante; sin git, fail-closed.
