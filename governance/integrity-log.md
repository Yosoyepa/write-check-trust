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

## 2026-08-21T03:33:13.917661+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #8: feedback piloto fases 22-24
- Commit: 6ea228481e8e9927ac660823ec5bc96519fcc16a

## 2026-08-21T18:01:59.715640+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #9: tier pr + reviviendo gates muertos
- Commit: 7017aabdc36a857ca7bf1c34cfe18059b4cf1b5d

## 2026-08-21T18:15:49.027189+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #10: hardening CI para colaboradores
- Commit: 59b4e6d2fb6c13a9d484c355c494cc33f7076c80

## 2026-08-21T19:52:15.181328+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #11: release v0.2.0
- Commit: 052fe97d12b8932836261db2a7b7e72896475ddb

## 2026-08-22T18:48:58.497703+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #13: gates de tamaño/cognitiva/supresiones y fix G-DRY-TOK
- Commit: fab7c6008f2138377226bdf0ff92d0aeab57c646

## 2026-08-23T18:40:24.249988+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #14: release 0.3.0 (hotspots, CI hardening, split runner, ratchets)
- Commit: 8b70814c119f6464510eec948dd88aa38814a7a9

## 2026-08-23T18:48:09.768277+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #15: G-DRY-TOK entra al tier full
- Commit: 23455ffcec5d529aabdc23cd2abb89e1624fb9cc

## 2026-08-23T18:55:43.586742+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #16: dedup del patrón subprocess que G-DRY-TOK cazó en CI
- Commit: 191f83198a51bfea12dfbc11d008cd202dc12600

## 2026-08-23T20:19:53.178387+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #17: escape anti-deadlock del Stop hook
- Commit: aef252a6be0424719aae0bb05a2a76261021b056

## 2026-08-24T00:47:38.349770+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #21: fase beta-1 metricas estructurales (G-WIRE, G-LCOM, G-DRY-TPL)
- Commit: 4231366784a696b22e445d22870d337a1064efbe

## 2026-08-24T00:57:09.660135+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #22: release 0.5.0 tras beta-1
- Commit: ca3d673bf28fa19ac0ea0da271a9964c5cec020c

## 2026-08-24T01:36:05.371528+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #23: adopt lifecycle lock/check/sync (beta-2)
- Commit: e81753055e3fdfe51809a7eb23566a10f0d7d25d

## 2026-08-24T01:50:17.386984+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #24: declarar beta 1.0.0-beta.1
- Commit: be151317d7668d1583a7f53f79e56623ea652acd
