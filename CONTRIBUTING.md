# Contribuir a WCT

Gracias por tu interés. Este repositorio se gobierna a sí mismo: las mismas
reglas que el harness impone a los proyectos adoptantes se aplican a su
propio desarrollo.

## Requisitos

- Python 3.11–3.14, `uv` y Git.
- Arranque: `make bootstrap` (instala los grupos dev/quality, genera las
  reglas por proveedor e instala pre-commit).

## La regla de oro

Los códigos de salida son la ley. Antes de cada handoff:

```bash
uv run wct gate --tier fast
```

Si tu cambio altera comportamiento observable, escribe primero un test que
FALLE ante una implementación plausiblemente incorrecta (TDD), y luego el
mínimo código que lo hace pasar. La suite no acepta tests que solo verifican
su propio andamiaje (`mock.assert_called_once_with(...)` sin aseverar sobre
el valor de retorno del sistema bajo test).

## El control plane es especial

`governance/**`, `.github/workflows/**`, `pyproject.toml`, `uv.lock`,
`tools/wct/**` y demás rutas protegidas están selladas por
`governance/integrity.lock` (gate G-META-1).

- Si tu PR toca rutas protegidas, **G-META-1 llegará rojo a propósito**. No
  intentes arreglarlo editando el lock: solo el mantenedor puede ejecutar
  `wct integrity bless`, y el comando exige citar la aprobación (URL o
  referencia `#N` de PR/issue).
- No subas umbrales ni regrabes baselines para hacer pasar un gate. Si un
  umbral te parece incorrecto, ábrelo en un issue y discutámoslo con datos.

## Si trabajas con agentes de IA

Apunta al agente a `AGENTS.md`. Le está prohibido: ejecutar
`wct integrity bless`, `wct ratchet record` o `mutate update-manifest
--approved-by`; usar `git commit --no-verify`; y correr subconjuntos de la
suite (`pytest -k ...`) como evidencia de que el gate pasa. El hook
PreToolUse lo bloquea de todos modos: un hook que crashea retorna exit 2 y
nunca se interpreta como permiso.

## Commits y pull requests

- Mensajes en Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`,
  `chore:`); el pre-commit lo verifica.
- Usa la plantilla de PR y rellénala con resultados reales. Un gate que no
  corriste no cuenta como verificado: si algo falló, pégalo y explícalo.
- Para cambios de comportamiento no triviales, abre primero un issue con el
  boceto del escenario Gherkin y consigue aprobación del escenario antes de
  implementar.

## Reporte de bugs

Usa las plantillas de issue. Para fallos de gates, incluye la salida completa
del gate y de `uv run wct doctor`.
