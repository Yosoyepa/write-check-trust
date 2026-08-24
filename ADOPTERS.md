# Adopters

Proyectos que usan WCT como harness de calidad. Si adoptas el template,
envía un PR agregándote — basta una línea con el caso de uso (no se requiere
exponer repos privados).

| Adoptador | Uso | Evidencia |
|---|---|---|
| **personalAssistant** (piloto, repo privado) | Harness vendido (`tools/wct/`) gobernando desarrollo agéntico: 34+ gates, mutación diferencial, hooks fail-closed en 15+ fases de feedback | Encontró y reportó el deadlock del Stop hook (→ v0.4.0), el dolor del sync vendido (→ `wct adopt lock/check/sync`), y el falso positivo de gitleaks; su suite: 1199+ tests verdes bajo el harness |

## Cómo adoptar

```bash
wct adopt <ruta>                        # inventario y recomendación
wct adopt lock --source <clon-upstream> # acopla tu vendido al SHA exacto
wct adopt check --source <clon> --ref main
wct adopt sync  --source <clon> --ref <tag>
```

El acoplamiento es por **hash de commit** (patrón cruft), no por versión:
el semver del template describe el contrato del CLI/gates, tu repo decide
cuándo moverse de commit.
