# Fuentes y procedencia

## Fuentes internas

El diagnóstico local corresponde a la revisión
`82d686d491baeac5ea03227c7283aeaf7d84628c`, observada el 2026-09-01. Las
principales fuentes fueron:

- `README.md`, `PLAN.md`, `docs/STATUS.md` y `docs/gates.md` para las promesas
  documentadas;
- `governance/policy.yaml` y `governance/thresholds.yaml` para configuración y
  umbrales declarados;
- `tools/wct/gate/runner.py` y `tools/wct/model.py` para ejecución y semántica de
  estados;
- `tools/wct/selftest/redteam.py` y `quality/redteam/cases.yaml` para red team;
- `tools/wct/accept/pipeline.py` y `tools/wct/cli.py` para aceptación;
- `pyproject.toml` para scopes de cobertura, mutación y selección de tests;
- artefactos generados localmente bajo `build/` para cobertura y SBOM.

Los tiempos son observaciones de un único entorno; no son benchmarks de
rendimiento.

## DeepSeek Harness

Se inspeccionó un clone superficial en el commit
`4e84901e6471b79ec0338099867ebb4606d12bb5`, fechado 2026-09-01. Usar links
anclados al commit evita que una rama cambiante altere retrospectivamente la
base del análisis.

| Fuente primaria | Uso en este dossier |
|---|---|
| [Repositorio](https://github.com/deepseek-ai/deepseek-harness/tree/4e84901e6471b79ec0338099867ebb4606d12bb5) | arquitectura, estado alpha y composición por plugins |
| [Python SDK](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/python/sdk/README.md) | ejecución programática, aislamiento y resultado estructurado |
| [Política de testing](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/docs/testing.md) | mockear solo la frontera no determinista y probar la ruta real |
| [Session Snapshot](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/test-support/session-snapshot/README.md) | snapshots cerrados, normalización y record/replay |
| [LLM Replay](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/test-support/llm-replay/README.md) | replay sin claves, consumo completo y fallos guionados |
| [LLM Mock Server](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/test-support/llm-mock-server/README.md) | errores HTTP/SSE, stalls, rate limits y stress con seed |
| [Token Meter](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/llm/token-meter/README.md) | tokens facturados, caché, reasoning y presión de contexto |
| [Postmortem 0001](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/docs/postmortem/0001-acp-default-export-drops-inject.md) | 178 tests verdes y 100 % de línea no cubrieron la ruta ensamblada |
| [Postmortem 0002](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/docs/postmortem/0002-js-expression-disabled-filesystem-tools.md) | un snapshot actualizado puede aceptar una regresión semántica |
| [Safety](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/SAFETY.md) | límites de seguridad y madurez declarados por el proyecto |

DeepSeek Harness se usa como fuente de patrones, no como autoridad de calidad ni
como benchmark terminado.

## Evaluación de agentes

| Fuente primaria | Aprendizaje aplicado |
|---|---|
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | tareas sobre issues reales y ejecución reproducible en contenedores |
| [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) | revisión humana múltiple de especificación y tests |
| [Auditoría posterior de SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) | el benchmark también necesita calificación; tests estrechos, amplios o rotos distorsionan resultados |
| [Terminal-Bench / Harbor](https://github.com/harbor-framework/terminal-bench) | estabilidad del oráculo y ejecuciones repetidas antes de liberar una tarea |
| [Inspect AI](https://inspect.aisi.org.uk/) | separación modular de dataset, agente, herramientas, scorer, sandbox y logs |

No se propone instalar ninguna de estas herramientas en esta fase documental.
