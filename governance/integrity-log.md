# Registro de integridad

Este archivo es el rastro auditable de **F14**: todo cambio a un archivo de gobernanza
(`governance/**`, `.claude/settings.json`, `.pre-commit-config.yaml`, `.importlinter`,
`.github/workflows/**`, `pyproject.toml`) debe aparecer aquí con un aprobador humano.

## Cómo funciona el gate

`G-META-1` (`wct verify-integrity`) recalcula el hash de cada archivo protegido y lo compara
con `governance/integrity.lock`. Un mismatch **sin** una entrada correspondiente en este archivo
hace fallar el build.

Para autorizar un cambio legítimo:

```bash
wct integrity bless --reason "subir max-args a 6: el caso de uso X necesita 6 puertos" \
                    --approved-by "jandradeu"
```

Eso actualiza `integrity.lock` y añade una entrada aquí.

## Reglas

1. **`approved_by` debe ser una persona.** Una entrada con `approved_by: claude`, `agent`,
   `assistant` o similar es rechazada por el gate. Un agente puede *proponer* el cambio y
   redactar la razón; la aprobación es humana o no es aprobación.
2. **La razón debe decir por qué el umbral estaba mal, no que el gate molestaba.** "El gate
   fallaba" no es una razón; "el umbral asumía que X, y en este proyecto Y" sí.
3. **No se borran entradas.** El historial de aflojamientos es el dato más útil para saber si
   el harness está calibrado o si se está erosionando.
4. **Un cambio en `.claude/settings.json` que quite un hook** requiere además explicar qué
   cubre ese anillo y qué lo cubre ahora. `G-HOOKS-WIRED` lo verifica de todas formas.

---

## Entradas

### 2026-08-11 — semilla inicial

- **approved_by**: jandradeu
- **reason**: creación del harness. Estado inicial de todos los archivos de gobernanza.
- **files**: todos los protegidos (ver `governance/policy.yaml` → `paths.protected`)
- **thresholds**: CRAP `changed_max: 6` (ADR-003), lint `ruff` (ADR-002),
  minimalismo `lite` con 4 overrides (ADR-001)

<!-- Las entradas nuevas van ARRIBA de esta línea, más reciente primero. -->

## 2026-08-12T20:19:44.123280+00:00

- Approved by: jandradeu
- Reason: Bootstrap final del control plane y toolchain reproducible
- Commit: unborn

## 2026-08-12T20:23:46.582935+00:00

- Approved by: jandradeu
- Reason: Implementación completa autorizada: configuración final de mutation testing, prueba del valor por defecto y salida Gherkin estable
- Commit: unborn

## 2026-08-19T21:37:59.825356+00:00

- Approved by: jandradeu
- Reason: feedback piloto 2026-08-19 aprobado, ref #1: backports B1-B6, mejoras P1-P8, docs D1-D8
- Commit: unborn

## 2026-08-19T21:38:06.121544+00:00

- Approved by: jandradeu
- Reason: feedback piloto 2026-08-19 aprobado, ref #1: backports B1-B6, mejoras P1-P8, docs D1-D8
- Commit: unborn

## 2026-08-20T23:45:06.748014+00:00

- Approved by: Yosoyepa
- Reason: release público inicial como write-check-trust, ref #1: rename + feedback del piloto aplicado
- Commit: unborn

## 2026-08-21T00:27:05.568534+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #7: consolidación dependabot 2026-08
- Commit: f6fa5e256d44bc9bf6bde70b9ee4d74b900836c5

## 2026-08-21T00:50:33.726059+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #8: feedback piloto fases 22-24
- Commit: 12665d4264dd5bcd17a1db88b59a3a2d5362a8b8
