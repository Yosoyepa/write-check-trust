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
- REANCLAJE-3 (2026-09-17/18, autorización humana explícita del encargo;
  sonda en build/tmp/reanclaje2-20260918 y controles S1-S3 de
  build/tmp/reanclaje3-20260918): 17 entradas para los falsos positivos de
  la superficie P03a/R8 + operador fase 1 sobre PR #56. Categorías: (a) API
  pública consumida desde tests (vulture no escanea tests/): load_policy
  (7 llamadas), decode_pytest_journal y reconcile_pytest (162 llamadas en
  tests/unit/test_pytest_*.py); (b) campos del wire contractual de
  PROPUESTA-P03 §3 escritos por el decodificador vía kwargs del constructor
  (invisible al detector) y conservados como claims del emisor: log_sha256,
  pytest_version, pluggy_version, observer_version, runtime_profile_sha256,
  source_sha256, effective_sha256, profile_match, argument_exit,
  call_disposition, pass_eligible, deselected_property, protocol_complete,
  preflight_identities (estos cuatro últimos con lecturas directas en
  tests: 19+7+28+2). ALCANCE DEMOSTRADO: toda entrada de vulture silencia
  el nombre GLOBALMENTE en src+tools (controles S1-S3 con homónimo muerto
  ajeno oculto); se acepta solo para nombres compuestos específicos del
  contrato. RECHAZADAS en este encargo: utc, distribution y qualified
  (nombres genéricos; ocultarían homónimos ajenos futuros) y expectation
  (no es falso positivo: campo interno _ScanState escrito y nunca leído,
  pendiente de disposición). InstanceReport NO se whitelistó: era código
  muerto real, eliminado en el mismo incremento.
"""

abstract_symbols  # noqa: B018, F821 — entrada de whitelist vulture (ADR-D-02): el nombre cuenta como usado, no es código ejecutable
_.pytest_collection_finish  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_collectreport  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_internalerror  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_runtest_makereport  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
_.pytest_sessionfinish  # noqa: B018, F821 — hook pluggy invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt._Recorder
pytest_configure  # noqa: B018, F821 — hook pluggy de módulo invocado por reflexión (ADR-D-02): falso positivo sustentado en pytest_receipt

load_policy  # noqa: B018, F821 — API pública del operador (REV2 §2) consumida desde tests; vulture no escanea tests/ (REANCLAJE-3)
decode_pytest_journal  # noqa: B018, F821 — API pública del kernel P03a (PROPUESTA-P03 §2); 100+ llamadas en tests R8 (REANCLAJE-3)
reconcile_pytest  # noqa: B018, F821 — API pública del kernel P03a (PROPUESTA-P03 §2); 60+ llamadas en tests R8 (REANCLAJE-3)
log_sha256  # noqa: B018, F821 — campo wire contractual ExecutionEnd (PROPUESTA-P03 §3), escrito por el decodificador vía kwargs (REANCLAJE-3)
pytest_version  # noqa: B018, F821 — campo wire contractual SessionStart (PROPUESTA-P03 §3), claim del emisor conservado (REANCLAJE-3)
pluggy_version  # noqa: B018, F821 — campo wire contractual SessionStart (PROPUESTA-P03 §3), claim del emisor conservado (REANCLAJE-3)
observer_version  # noqa: B018, F821 — campo wire contractual SessionStart (PROPUESTA-P03 §3), claim del emisor conservado (REANCLAJE-3)
runtime_profile_sha256  # noqa: B018, F821 — campo wire contractual SessionStart (PROPUESTA-P03 §3), claim del emisor conservado (REANCLAJE-3)
source_sha256  # noqa: B018, F821 — campo wire contractual PluginClaim (PROPUESTA-P03 §3), claim del emisor conservado (REANCLAJE-3)
effective_sha256  # noqa: B018, F821 — campo wire contractual OptionsClaim (PROPUESTA-P03 §3), claim del emisor conservado (REANCLAJE-3)
profile_match  # noqa: B018, F821 — campo wire contractual OptionsClaim (PROPUESTA-P03 §3), leído en tests R8 (REANCLAJE-3)
argument_exit  # noqa: B018, F821 — campo wire contractual SessionEnd (PROPUESTA-P03 §3), conservado para cotejo de exit (REANCLAJE-3)
call_disposition  # noqa: B018, F821 — campo público TestObservation (PROPUESTA-P03 §2), 7 lecturas en tests R8 (REANCLAJE-3)
pass_eligible  # noqa: B018, F821 — campo público TestObservation (PROPUESTA-P03 §2), 28 lecturas en tests R8 (REANCLAJE-3)
deselected_property  # noqa: B018, F821 — campo público ExecutionObservation (PROPUESTA-P03 §2), inventario del productor (REANCLAJE-3)
protocol_complete  # noqa: B018, F821 — campo público ExecutionObservation (PROPUESTA-P03 §2), 19 lecturas en tests R8 (REANCLAJE-3)
preflight_identities  # noqa: B018, F821 — campo público PytestObservation (PROPUESTA-P03 §2), 2 lecturas en tests R8 (REANCLAJE-3)
