"""Whitelist de vulture: símbolos usados vía reflexión, invisibles al análisis.

Procedencia: ADR-D-02 (redime F11-b), autorización delegada del arquitecto,
2026-09-05. La sonda sobre main midió exactamente 1 falso positivo en todo
el repo a confianza 60; esta lista replica esa evidencia y nada más.
Convención de vulture: cada nombre referenciado aquí cuenta como usado en
el código escaneado. Ampliarla exige una sonda que mida el falso positivo.

Entradas:

- abstract_symbols — campo del dataclass PackageMetric
  (tools/wct/archmetrics/analyzer.py) consumido vía dataclasses.asdict();
  vulture no ve el acceso reflexivo.
- pytest_collection_finish, pytest_collectreport, pytest_internalerror,
  pytest_runtest_makereport, pytest_sessionfinish — hooks de pluggy en
  tools/wct/accept/pytest_receipt.py (métodos de _Recorder) que pytest
  invoca por nombre durante la sesión; vulture solo exime el prefijo
  pytest_* en archivos que matchean sus patrones de test (core.py,
  _is_test_file) y pytest_receipt.py no matchea. Evidencia: las entradas
  canónicas de --make-whitelist eliminan los 6 hallazgos, y los hooks se
  ejercen en tests/unit/test_accept_pytest.py y en la campaña de
  aceptación real del paquete.
- pytest_configure — hook de nivel de módulo que pytest invoca por nombre
  al cargar el plugin (PYTEST_PLUGINS o -p); mismo mecanismo, evidencia y
  motivo que los hooks anteriores.
"""

abstract_symbols  # noqa: B018, F821 — entrada de whitelist vulture (ADR-D-02): el nombre cuenta como usado, no es código ejecutable
_.pytest_collection_finish  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_collectreport  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_internalerror  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_runtest_makereport  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_sessionfinish  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
pytest_configure  # noqa: B018, F821 — hook pluggy de módulo invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt
