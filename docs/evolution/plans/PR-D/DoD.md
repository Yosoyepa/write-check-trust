# DoD — PR-D: Definitions of Done por unidad de aceptación

## Reparto entre coders (frontera disjunta)

- **Coder-D1 — perfil y resumen**: `tools/wct/gate/runner.py` (metadatos
  del constructor + REGISTRY scopes), `tools/wct/report/overview.py`,
  `tools/wct/report/render.py`, `tests/unit/test_report_profile.py`.
- **Coder-D2 — redenciones**: `governance/thresholds.yaml`,
  `governance/lint/vulture_whitelist.py` (nuevo),
  `tools/wct/gate/checks.py` (solo `dead_code_command`),
  `tools/wct/accept/pipeline.py` (+consumidores mapeados del IR),
  `tests/acceptance/generated/test_acceptance.py` (solo regenerado por
  herramienta), `pyproject.toml` ([tool.ruff] extend),
  `quality/redteam/cases.yaml`, `quality/redteam/cases-tool.yaml`,
  `tools/wct/selftest/fixtures_tools.py`,
  `tools/wct/selftest/redteam.py` (solo eliminación del reconocedor
  `unused`), `tests/unit/test_redteam_tools.py`, tests nuevos de accept.
- Shared: nadie edita lo del otro. El arquitecto aterriza features/ y
  docs/ del dossier.

## DoD-F1 — perfil de capacidades (D1)

1. Todo gate con herramienta externa expone `tools` desde el constructor
   (test: ningún gate "de herramienta" queda sin metadata).
2. `wct report` incluye `capabilities` con presencia efectiva, scope y
   tiers por gate, en orden estable, JSON auditable.
3. `render.text_report` con SKIPs añade la línea de capacidades no
   verificadas; sin SKIPs la salida es byte-idéntica a la actual.
4. Los scopes declarados fueron verificados contra los comandos reales
   (paso 0.1 documentado).

## DoD-F2 — F11-b redimido (D2)

1. Sonda re-verificada en el handoff: exactamente 1 FP a confianza 60.
2. `dead_code_command` añade `--whitelist` solo con clave declarada.
3. vulture 60 + whitelist sobre el repo real: **0 hallazgos**, baseline
   intacta (sin `ratchet record`).
4. F11-b cazado por el gate productivo en el parametrizado (9 tool
   cases); reconocedor `unused` eliminado; resumen del red team:
   `30/30 · 13 gate-engine · 9 gate-tool · 4 hook · 4 heuristic`.
5. Feature de residuos actualizado (F11-b fuera; quedan 4).

## DoD-F3 — artefacto relativo (D2)

1. Consumidores de `ir["source"]` mapeados y resueltos contra root.
2. Test de dos roots → artefactos byte-idénticos.
3. Artefacto regenerado SOLO con la herramienta; diff = solo la ruta.

## DoD-F4 — ruff extend (D2)

1. Test rojo-primero: ruff desnudo sobre un archivo limpio pasa (antes
   fallaba con I001).
2. Sin regresión: el comando con `--config` (G-LINT) idéntico.

## DoD por commit / revisión / merge

- **Commit**: conventional + byline `By coder.` + hooks sin
  `--no-verify` + suite verde en estados intermedios.
- **Revisión de arquitecto**: diffs completos leídos; DoD-F1..F4
  verificados independientemente; toda propuesta resuelta con razón
  escrita; hallazgos inesperados (más FPs de vulture, diffs extraños del
  artefacto) evaluados como hallazgos, no commiteados.
- **Merge**: matriz de VERIFICATION.md con salida real + presupuesto de
  runtime del tier fast sin regresión + G-META-1 como único rojo
  pre-bless.
