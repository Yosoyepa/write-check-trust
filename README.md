<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/wct-banner-dark.svg">
    <img src="docs/assets/wct-banner-light.svg" alt="WCT — Write, Check, Trust">
  </picture>
</p>

<p align="center">
  <strong>Controles ejecutables para desarrollo asistido por IA.</strong><br>
  Especifica el cambio. Verifica la evidencia. Conserva el control humano.
</p>

<p align="center">
  <a href="https://github.com/Yosoyepa/write-check-trust/releases"><img src="https://img.shields.io/badge/canal-beta-f59e0b" alt="Canal beta; consultar versiones publicadas"></a>
  <a href="https://github.com/Yosoyepa/write-check-trust/actions/workflows/quality.yml"><img src="https://github.com/Yosoyepa/write-check-trust/actions/workflows/quality.yml/badge.svg" alt="CI de calidad"></a>
  <a href="https://github.com/Yosoyepa/write-check-trust/actions/workflows/full-hardening.yml"><img src="https://github.com/Yosoyepa/write-check-trust/actions/workflows/full-hardening.yml/badge.svg" alt="CI de hardening completo"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Yosoyepa/write-check-trust?color=blue" alt="Licencia MIT"></a>
</p>

**Write, Check, Trust (WCT)** es un template y un arnés de calidad para
proyectos Python. Convierte reglas de desarrollo en verificaciones
ejecutables: arquitectura, tests, cobertura, mutación, seguridad e integridad
del propio sistema de control.

Es agnóstico al proveedor del agente: las instrucciones orientan el trabajo;
los comandos, sus resultados y la revisión humana determinan qué se acepta.
Puedes usarlo como punto de partida o integrar el arnés en un repositorio
existente.

**Esta revisión corresponde a `1.0.0-beta.2`** (`wct 1.0.0b2`). El código
de una rama no implica una release publicada: consulta
[Releases](https://github.com/Yosoyepa/write-check-trust/releases) para elegir
una versión distribuida y [RELEASES.md](RELEASES.md) para la política de madurez.

[Inicio rápido](#inicio-rápido) · [Novedades de beta.2](#qué-cambia-en-beta2) ·
[Verificación](#elige-la-verificación-adecuada) ·
[Adopción](#adopción-en-un-proyecto-existente) · [Documentación](#documentación)

<p align="center">
  <img src="docs/assets/demo-gate.gif" alt="Demo: wct gate --tier fast en verde, y en rojo cuando el agente deja un import sin uso y formato roto" width="820">
</p>

<p align="center"><em>Demostración del tier fast: el mismo control pasa en un árbol válido y bloquea un cambio con errores de lint y formato. No representa la batería completa de release.</em></p>

## Qué aporta WCT

| Necesidad | Cómo la aborda |
|---|---|
| Reglas consistentes entre agentes | `governance/` define la política; las instrucciones por proveedor se generan y se comprueba su sincronización. |
| Tests que detecten cambios de comportamiento | Análisis de aserciones, cobertura y mutación diferencial sobre el alcance configurado. |
| Evitar que la deuda crezca | Ratchets: baselines que impiden retrocesos en las métricas medidas. |
| Detectar cambios en los propios controles | Lock de integridad y aprobación humana para rutas protegidas. |
| Revisiones trazables | Escenarios Gherkin, evidencia de comandos y separación entre autor y verificador. |
| Actualizar el arnés integrado en otro proyecto | `adopt lock/check/sync`: referencia por SHA, detección de divergencias y propuesta de parche. |

WCT está pensado para equipos que quieren hacer revisable el trabajo de los
agentes. **No demuestra corrección total ni sustituye el criterio técnico.**
Usarlo con modelos económicos es un caso de uso, no una mejora de calidad o
coste demostrada mediante un benchmark de modelos.

## Inicio rápido

Requiere Git, Make, `uv` y Python. El paquete declara compatibilidad con
Python **3.11–3.14**; la CI del template está configurada con **3.12**.

Para explorar el estado actual del proyecto:

```bash
git clone https://github.com/Yosoyepa/write-check-trust.git
cd write-check-trust
make bootstrap
uv run wct doctor
uv run wct gate --tier commit
```

Para una adopción reproducible, selecciona un tag publicado o un SHA revisado
antes de ejecutar `make bootstrap`. El ejemplo anterior clona la rama por
defecto, no una versión inmutable.

`make bootstrap` instala los grupos dev/quality, genera instrucciones e
instala los hooks de Git. Solo crea el lock de integridad si no existe;
**no aprueba ni bendice cambios en un lock existente**.

> [!TIP]
> Usa `uv run wct`, no `wct` a secas. Así ejecutas el arnés del entorno del
> proyecto y evitas colisiones con otros programas del sistema.

Si un control falla, lee su causa antes de modificar código o configuración.
Los diagnósticos de instalación están en
[el kit de verificación](docs/STATUS.md) y el [runbook](docs/runbook.md).

## Qué cambia en beta.2

- **Ratchets exigibles.** `--require` bloquea cuando falta una medición
  requerida y conserva las comparaciones de las demás métricas. El modo
  sin requisitos explícitos mantiene su comportamiento histórico.
- **Cobertura producida y consumida en CI.** El workflow genera LCOV sin
  property tests, exige cobertura total y docstrings, y ejecuta property
  en un paso separado. Once tests protegen el contrato de esos pasos.
- **Honestidad de tests antes del merge.** `G-INTROVERT` pasa al tier
  `commit`; el escape observado en #37/#38 tiene una regresión en la suite.
- **Mutación y red team con evidencia productiva.** El veredicto de
  mutación clasifica los resultados que recibe del motor. Los 30 casos
  del corpus adversarial usan motores productivos o hooks, sin casos
  declarados como heurísticos.
- **Alcance de la verificación más explícito.** El reporte distingue qué
  controla el arnés y sobre qué rutas, en lugar de tratar cada verde
  como evidencia de cobertura universal.

Consulta el [CHANGELOG y la guía beta.1 → beta.2](CHANGELOG.md).
Un proyecto antes verde puede encontrar nuevos bloqueos: diagnostica si
se trata de un defecto real, una configuración incompleta o una limitación
del analizador. No relajes umbrales para obtener verde.

## Elige la verificación adecuada

| Tier | Uso | Controles en beta.2 |
|---|---|---:|
| `fast` | Feedback corto de reglas, lint, formato y tipos | 7 |
| `commit` | Verificación habitual antes de entregar: incluye tests unit/integration e integridad | 21 |
| `pr` | Comprobaciones adicionales para preparar una PR, incluidas cobertura diferencial y aceptación mutada | 27 |
| `full` | Hardening ampliado, mutación y controles para calificar una release | 34 |

```bash
uv run wct gate --tier fast
uv run wct gate --tier commit
uv run wct gate --tier pr
```

`full` y `pr` son extensiones de `commit`, no una escalera acumulativa:
**full no incluye todos los controles de pr**. El tier `pr` tampoco
sustituye la secuencia completa del workflow, incluido el ratchet exigible.
El inventario ejecutable vive en [TIERS](tools/wct/gate/runner.py);
el detalle por control está en el [catálogo](docs/gates.md).

El hook de pre-commit corre `fast`; la CI de calidad corre `commit` y sus
pasos adicionales. Un resultado `SKIP` no acredita una comprobación
ejecutada. Los errores del arnés bloquean: no son un permiso para continuar.

### Ratchets con mediciones actuales

Desde la raíz del proyecto, esta es la cadena de cobertura de beta.2:

```bash
uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property" &&
uv run wct ratchet check --require coverage-total,docstring-coverage &&
uv run pytest -q tests/property
```

El encadenamiento con `&&` detiene la secuencia si falla un comando.
El primero produce el artefacto; el segundo
exige las mediciones y compara los ratchets; el tercero ejecuta property
sin incorporarlo a cobertura. En CI, los pasos dependen del éxito previo.

`--require all` exige el inventario explícito de diez métricas. **No prueba
por sí solo la frescura ni la completitud del LCOV**: la procedencia depende
del checkout limpio y de la ejecución exitosa del productor en esa corrida.

### Qué se mide y dónde

Alcances del template incluido; no asumas que un gate cubre todo el repositorio:

| Control | Alcance configurado |
|---|---|
| Cobertura | `src/` y `tools/wct/`; property excluido de la medición |
| Mutación diferencial | Código de ejemplo en `src/example`; no mutación general de `tools/wct/` |
| Gherkin (`G-ACCEPT`) | Parseo y validación estructural de features; no ejecución automática de todos sus escenarios |
| Aceptación mutada por defecto | `features/example.feature` y su ejecutor de ejemplo |
| Red team | 30 adversarios conocidos; resultado del corpus, no garantía sobre ataques no incluidos |

Para una suite completa y el flujo de hardening:

```bash
uv run pytest -q
uv run wct selftest redteam
make harden
```

`make harden` ejecuta mutación → aceptación mutada → tier full, deteniéndose
ante un fallo. No reemplaza la [matriz de release](docs/evolution/plans/RELEASE-BETA2/PLAN.md):
faltan, entre otras evidencias, el smoke desde clon limpio y el orden aleatorio.

## Adopción en un proyecto existente

Empieza con un inventario de solo lectura:

```bash
uv run wct adopt ../mi-proyecto
```

Después define las capas y rutas del proyecto, instala las herramientas y
mide sus propios baselines. **No copies los baselines verdes del ejemplo
a un sistema legacy.** El código nuevo se verifica con el perfil estricto;
la deuda existente se gestiona con ratchets y decisiones explícitas.

Para proyectos que ya integran el arnés y tienen `.wct-upstream.json`,
desde la raíz del proyecto adoptante:

```bash
uv run wct adopt check --source ../write-check-trust --ref HEAD
uv run wct adopt sync --source ../write-check-trust --ref HEAD
```

La ruta identifica tu clon upstream. `HEAD` significa el commit actual de
ese clon; usa un tag publicado o SHA revisado para una actualización concreta.
`check` muestra divergencias y candidatos a conflicto. `sync` escribe una
**propuesta de parche**, no aplica la actualización a los archivos integrados.
El registro inicial se hace con `adopt lock`; consulta
`uv run wct adopt --help` y los [adoptadores documentados](ADOPTERS.md).

## Gobernanza y revisión

Las instrucciones orientan; los verificadores aportan evidencia. La política
vive en `governance/`, y las copias por proveedor se generan con
`wct rules build`. La arquitectura de ejemplo sigue:
`entrypoints → adapters → application → domain`.

Un flujo de trabajo recomendado es especificar el cambio, escribir tests
que detecten una implementación incorrecta, implementar, revisar la evidencia
con un verificador independiente y someter la PR a CI.

> [!IMPORTANT]
> Cambiar rutas protegidas requiere aprobación humana y bless con referencia
> a la aprobación. Un bless registra una decisión sobre el plano de control;
> no arregla un test fallido ni autoriza por sí solo una release. Los agentes
> no deben ejecutarlo en nombre del mantenedor.

No edites las instrucciones generadas ni los manifiestos a mano. Los pasos
operativos, hooks y válvulas anti-deadlock están en el
[runbook](docs/runbook.md); pasar una válvula nunca convierte un árbol rojo
en verde.

## Límites y madurez

- **Beta, no GA.** La política exige evidencia adicional de adopción,
  continuidad y estabilidad antes de declarar `1.0.0` estable.
- **Análisis estáticos con límites.** DRY, métricas arquitectónicas e
  introvert requieren interpretación. Un test por subprocess puede ser
  legítimo aunque el analizador no trace sus aserciones al SUT.
- **Mutación sin promesas adicionales.** Un delta vacío no demuestra
  ejecución de mutantes. Las mejoras de frescura, completitud y aislamiento
  de [G1b](docs/evolution/plans/G1/README.md) no se consideran entregadas.
- **Aceptación acotada.** El parser no acepta todavía narrativa libre
  bajo `Feature:`; se usan comentarios ([#35](https://github.com/Yosoyepa/write-check-trust/issues/35)).
- **Sin garantía universal.** Los gates no prueban requisitos omitidos,
  usabilidad, rendimiento real ni seguridad completa. Tampoco se ha probado
  un aumento causal de calidad o ahorro de modelos atribuible a WCT.

## Documentación

| Para… | Empieza aquí |
|---|---|
| Ver cambios y actualizar desde beta.1 | [CHANGELOG](CHANGELOG.md) |
| Entender el estado y derivarlo con comandos | [Estado del proyecto](docs/STATUS.md) |
| Consultar controles y arquitectura | [Gates](docs/gates.md) · [Arquitectura](docs/architecture.md) |
| Operar integridad, ratchets y hooks | [Runbook del mantenedor](docs/runbook.md) |
| Consultar versiones y madurez | [Política de releases](RELEASES.md) · [Releases publicadas](https://github.com/Yosoyepa/write-check-trust/releases) |
| Explorar decisiones e investigación | [Índice de documentación](docs/README.md) · [Investigación](RESEARCH.md) |

## Contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md) y el
[código de conducta](CODE_OF_CONDUCT.md). Para un falso positivo, incluye
comando, versión, configuración relevante y una reproducción mínima.
Reporta vulnerabilidades mediante el canal privado de [SECURITY.md](SECURITY.md).

## Licencia

[MIT](LICENSE) © 2026 Write, Check, Trust contributors.
Avisos de terceros: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
