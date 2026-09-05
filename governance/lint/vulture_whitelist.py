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
"""

abstract_symbols  # noqa: B018, F821 — entrada de whitelist vulture (ADR-D-02): el nombre cuenta como usado, no es código ejecutable
