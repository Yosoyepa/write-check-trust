# DoD — PR-C: Definitions of Done por unidad de aceptación

## Reparto entre coders (frontera disjunta)

- **Coder-R1 — framework + engines**: `tools/wct/selftest/redteam.py`,
  `tools/wct/selftest/fixtures_engine.py`,
  `quality/redteam/cases-engine.yaml`, `quality/redteam/cases.yaml`
  (cirugía de recorte), `tests/unit/test_redteam_engine.py`.
- **Coder-R2 — tool gates**: `tools/wct/selftest/fixtures_tools.py`,
  `quality/redteam/cases-tool.yaml`, `tests/unit/test_redteam_tools.py`.
- Shared NO-editado por nadie más. La lógica de SKIP vive en el runner de R1;
  R2 solo declara `tool:`.

## DoD-F1 — framework y 10 casos engine (R1)

1. `wct selftest redteam` despacha por arnés y su resumen muestra conteos
   separados (gate-engine/gate-tool/hook/heuristic) + skips listados.
2. Los 10 casos engine cazan su defecto con el **motor productivo importado**
   (misma API que su gate) — test parametrizado en verde, rojo-primero
   documentado.
3. Invariario de modos (≥2 por F1–F15) validado sobre la UNIÓN de archivos;
   archivos ausentes tolerados (worktree verde sin cases-tool.yaml).
4. `cases.yaml` reducido a 8 casos (4 hook + 4 heuristic con razón in situ);
   reconocedores muertos eliminados de `_reject` (los que quedan: solo los de
   los residuos).
5. Cada caso en su tmpdir: sin estado compartido (test explícito).
6. Baseline de runtime capturada (paso 0.2) y delta reportado.

## DoD-F2 — 12 casos tool (R2)

1. Los 12 casos invocan la función de gate productiva sobre su fixture
   (REGISTRY o función interna — documentada por caso en paso 0.3).
2. Con herramienta presente: caza verificada (test parametrizado; si el
   entorno de test carece de la herramienta, el test se declara skip-if-absent
   — el caso se verifica igual en CI con quality group y la verificación
   final del arquitecto).
3. Con herramienta ausente (which falseado): **SKIP visible** con la
   herramienta nombrada — no incrementa failures ni rechazados (test).
4. Ningún caso tool "pasa" porque el gate SKIPee: SKIP ≠ rechazado.

## DoD-F3 — residuos declarados (R1, con ADR-C-02)

1. Los 4 residuos llevan `harness: heuristic` + comentario de razón y ruta
   de redención (ADR-C-02) en el YAML.
2. El resumen los cuenta como "heuristic (declarados)" — distinguibles de
   los productivos.
3. Ningún reconocedor muerto sobrevive en `_reject` (solo los 4 residuales).

## DoD por commit / revisión / merge

- **Commit**: conventional + byline `By coder.` + hooks sin `--no-verify` +
  suite verde en estados intermedios.
- **Revisión de arquitecto**: diff completo leído; DoD-F1/F2/F3 verificados
  INDEPENDIENTEMENTE; toda propuesta resuelta con razón escrita; falsos
  negativos reales (caso rojo por motor que no caza) evaluados como
  hallazgo del instrumento — no se aceptan fixtures "ajustados para pasar"
  sin declaración.
- **Merge**: el de [VERIFICATION.md](VERIFICATION.md) — incluye presupuesto
  de runtime dentro de lo aprobado y `30/30` reinterpretado honestamente.
