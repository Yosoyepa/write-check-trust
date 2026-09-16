# Anexo — Diagnóstico de G-DEPS y G-DEAD (2026-09-15)

Anexo del registro `GS2-REVALIDACION-Y-PREPARACION-CIERRE-2026-09-15.md`.
Frente B, **solo diagnóstico**, sobre clon congelado del corte
`bdb7db31e3ad5e68adb01fc2b62364fab5858db0`. **Ninguna reparación fue
aplicada**: gobernanza, `pyproject.toml`, `src/` y `tools/` quedaron intactos
(`git diff bdb7db3 -- governance pyproject.toml tools src` vacío; clon limpio).
Runtime designado (sin sync/install): venv de integración — deptry 0.25.1,
vulture 2.16. Los dos comandos y sus salidas fueron reejecutados de forma
independiente con resultado byte-idéntico (ver registro §1.7).

## 1. G-DEPS

Comando exacto del registro productivo (`tools/wct/gate/runner.py:376-388`),
cwd = raíz del clon:

```
deptry src tools --known-first-party example --known-first-party tools
```

Resultado: **exit 1** (158-171 ms), `Scanning 88 files...` y 1 hallazgo.

| ID | Ruta:símbolo | Salida | Clasificación |
|---|---|---|---|
| F-DEPS-1 | `tools/wct/accept/pytest_receipt.py:11` (`import pytest`) | `DEP004 'pytest' imported but declared as a dev dependency` | **Defecto real de declaración/empaquetado** (ARCH-009 / SEC-004) |

Mecanismo y descarte de artefacto de runtime:

- `pytest` vive solo en `[dependency-groups] dev`; el módulo se empaqueta en
  `tools` (`[tool.hatch.build.targets.wheel] packages = ["tools", …]`) y se
  carga por reflexión (`PYTEST_PLUGINS` en `campaign.py:29-33`;
  `-p tools.wct.accept.pytest_receipt` en `tests/unit/test_accept_pytest.py:303`);
  sin pytest instalado el módulo no es importable (`@pytest.hookimpl`).
- Sonda de reparación (no aplicada): `[project.optional-dependencies]` con
  `accept = ["pytest>=8.3"]` → `Success! No dependency issues found.` (exit 0).
- Reparación mínima propuesta: añadir esa sección a `pyproject.toml`, conservar
  `pytest>=8.3` en dev y correr `uv lock` (G-AUDIT usa `uv export --frozen`).
- **Autorización humana requerida**: `pyproject.toml` y `uv.lock` son rutas
  protegidas (SEC-005). No es dependencia nueva: es reclasificación de una ya
  usada y declarada como dev.
- Descartado: `[tool.deptry] per_rule_ignores` (supresión), mover el plugin a
  `tests/` (rompe `-p tools.wct.accept.pytest_receipt`), import perezoso (los
  decoradores corren al importar el módulo).

## 2. G-DEAD

Comando exacto (`tools/wct/gate/checks.py:144-162` +
`governance/thresholds.yaml:202-213`; whitelist como path posicional porque
vulture 2.16 no tiene `--whitelist`), cwd = raíz del clon:

```
vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60
```

Resultado: **exit 3** (268-276 ms), 7 hallazgos.

| # | Ruta:línea | Símbolo | Clasificación |
|---|---|---|---|
| F-DEAD-1..5 | `tools/wct/accept/pytest_receipt.py:28/37/42/46/82` | hooks `pytest_collection_finish`, `pytest_collectreport`, `pytest_internalerror`, `pytest_runtest_makereport`, `pytest_sessionfinish` | **Falso positivo sustentado** (pluggy invoca por reflexión) |
| F-DEAD-6 | `tools/wct/accept/pytest_receipt.py:103` | `pytest_configure` | **Falso positivo sustentado** (ídem) |
| F-DEAD-7 | `tools/wct/accept/process.py:10` | `BinaryIO` "unused import" | **Falso positivo sustentado** (literal en `cast("BinaryIO", …)`, líneas 38-39) |

Mecanismo F-DEAD-1..6: pluggy/pytest invoca los hooks por nombre; vulture solo
exime `pytest_*` en archivos que matchean sus patrones de test, y
`tools/wct/accept/pytest_receipt.py` no matchea. La whitelist canónica
(`--make-whitelist`) emite exactamente las 6 entradas y, añadida como sonda,
los 6 hallazgos desaparecen.

Mecanismo F-DEAD-7: vulture no evalúa literales string; `ruff` y `mypy` sí los
resuelven (verdes sobre el original y sobre la sonda sin comillas).

Reparaciones mínimas propuestas (no aplicadas):

1. Ampliar `governance/lint/vulture_whitelist.py` con las 6 entradas canónicas
   con `# noqa: B018, F821` justificado (ADR-D-02); no sube el ratchet de
   G-SUPPRESS (solo escanea `src`+`tests`).
2. Para F-DEAD-7, opción preferida sin allowlist: descomillar los dos `cast` en
   `tools/wct/accept/process.py:38-39` (ruff y mypy verdes en la sonda).
   Fallback: entrada de whitelist de `BinaryIO`.

**Autorización humana requerida**: `governance/**` y `tools/wct/**` son rutas
protegidas; ADR-D-02 exige sonda del falso positivo (provista). Aplicar la
whitelist **no cierra G-META-1**: el drift del manifiesto de 20 rutas
protegidas (E9) se secuencia aparte con su propia revisión humana y bless.

Verificación posterior propuesta: los dos comandos → exit 0, y
`ruff check --config governance/lint/ruff.toml governance/lint/vulture_whitelist.py`
→ exit 0 (probado sobre copia).

## 3. Preexistencia y presupuesto

- `git diff c6be7ee bdb7db3` sobre `process.py`, `pytest_receipt.py`,
  `vulture_whitelist.py`, `thresholds.yaml` y `pyproject.toml`: **vacío** → no
  son regresiones del corte.
- Presupuesto B: **3164 ms de 300 000 ms** (17 comandos, `presupuesto-B.tsv`);
  la reejecución independiente sumó 426 ms adicionales fuera de ese presupuesto.
- Evidencia cruda (local, temporal): `build/tmp/gs2-coord.vdQDdj/subB/raw/`
  (`gdeps.txt` sha256 `3d494f90…`, `gdead.txt` sha256 `bee76537…`, sondas y
  versiones). La custodia durable de las conclusiones es este anexo.
