# Registro de ratchets

Un **ratchet** es un gate cuyo umbral es "el valor de la última vez, o mejor". Es el mecanismo
que permite adoptar el harness en un repo existente sin bloquearlo el primer día, y a la vez
impedir que la calidad degrade.

Los valores vivos están en `governance/baselines/*.json`.

## Reglas

1. **Solo CI en `main` escribe baselines** (`wct ratchet update`). Nunca un agente en su turno:
   si el agente pudiera actualizar el baseline, el ratchet no restringiría nada.
2. **Un ratchet nunca empeora automáticamente.** Empeorarlo requiere:
   ```bash
   wct ratchet raise --metric suppressions --to 52 \
                     --reason "migración de la librería X trae 5 type-ignore mientras upstream tipa" \
                     --approved-by "jandradeu"
   ```
   y deja una entrada aquí.
3. **`wct report` muestra la trayectoria de cada ratchet.** Un ratchet estancado durante N
   commits es visible, que es la única defensa real contra el estancamiento.
4. **PROC-008**: si un ratchet te bloquea, mejora la métrica. No subas el umbral.

## Por qué esto importa

Un ratchet que se sube cuando molesta es un baseline, y un baseline que solo sube es una métrica
decorativa. La diferencia entre un harness que funciona y uno que da la sensación de funcionar
está casi enteramente en este archivo.

---

## Entradas

### 2026-08-11 — semilla inicial

- **approved_by**: jandradeu
- **reason**: proyecto greenfield. Todos los ratchets arrancan en su mejor valor posible
  (0 supresiones, 0 clusters DRY, 0 código muerto, 0 tests introvertidos, 0 paquetes en zonas
  de dolor/inutilidad). Cobertura y docstrings arrancan en 0 y suben con el primer run de CI.
- **métricas**: las 9 de `governance/baselines/`

<!-- Las entradas nuevas van ARRIBA de esta línea, más reciente primero. -->

## 2026-09-02T13:15:10.087572+00:00

- Approved by: yosoyepa
- Reason: re-baseline por cambio de scope en PR #29: 100 era src/example (61 stmts, seed); real con src+tools/wct = 74.49 %
- Metrics: coverage-total

## 2026-09-02T13:20:54.657564+00:00

- Approved by: yosoyepa
- Reason: re-baseline por cambio de scope en PR #29, corrige registro previo con SHA corto para G-SECRET: real con src+tools/wct = 74 %
- Metrics: coverage-total

## 2026-09-02T13:32:27.692903+00:00

- Approved by: yosoyepa
- Reason: re-baseline por cambio de scope en PR #29, piso preciso truncado (74.51 medido, no 75 redondeado): real con src+tools/wct
- Metrics: coverage-total

## 2026-09-05T12:27:38.016845+00:00

- Approved by: yosoyepa
- Reason: aprobado en PR #32: registra 17 clusters (deuda preexistente 16 en main desde 2026-08-23 + 2 de fixtures PR-D - 1 disuelto por la particion de runner.py); deduplicacion archivada como PR propio
- Metrics: dry-template-clusters
