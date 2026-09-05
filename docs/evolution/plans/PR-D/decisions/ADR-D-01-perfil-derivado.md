# ADR-D-01 — El perfil de capacidades se DERIVA del constructor del gate

Estado: aceptado (arquitecto con autoría delegada, 2026-09-05).
Contexto: [ANALYSIS.md](../ANALYSIS.md) §1.

## Decisión

Cada gate expone sus metadatos desde donde YA viven: `dynamic()` conoce el
ejecutable (lo resuelve con `shutil.which`); los sitios de construcción en
`REGISTRY` declaran su `scope` (tupla de rutas que escanea). Los
metadatos viajan estampados en el objeto gate y `wct report` los agrega
con presencia efectiva (`shutil.which` en tiempo de reporte) y tiers
(`TIERS`). Nadie duplica el dato.

## Alternativas consideradas

- **(a) Tabla `GATE_CAPABILITIES` declarada en governance/policy.yaml con
  doctor de conformidad (patrón PR-B)**: rechazada para este caso — PR-B
  dio autoridad de CONFIG a valores que los gates LEEN de config. El
  scope no se lee de config: es lo que el comando del gate ES. Declararlo
  en YAML crea una segunda copia sin autoridad semántica, y su drift es
  exactamente lo que el perfil quiere eliminar.
- **(b) Tabla paralela en runner.py junto a REGISTRY**: viable pero
  duplica el constructor — el `executable` ya vive en `dynamic()`;
  separarlo invita a que diverjan.
- **(c) Solo documentar scopes en docs/gates.md**: rechazado — la prosa
  no es derivable ni auditable (regla del STATUS.md: gana el comando; el
  perfil HACE derivable lo que el comando sabe).

## Consecuencias

- El perfil es evidencia de una sola fuente: si un gate cambia de
  herramienta o scope, el perfil cambia con él o truena en construcción.
- `Gate` sigue siendo un callable; el stamping se encapsula en un helper
  tipado `gate_info(gate)` con test que fija "todo gate con herramienta
  externa expone tools".
- Los scopes se reportan; configurarlos desde policy queda como decisión
  futura si aparece un caso real que lo exija.
