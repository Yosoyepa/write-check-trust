"""Límites fijos, catálogo de códigos y constantes del wire (§2-§4)."""

import re

MAX_JOURNAL_BYTES = 2 * 1024 * 1024

MIN_JOURNAL_BYTES = 1

LINE_MAX_BYTES = 65536

STRING_MAX_BYTES = 4096

C0_LIMIT = 0x20

DEL_CHAR = 0x7F

_EVENT_VECTOR_FIELDS = 5

_XFAIL_FIELDS = 3

_EXIT_ABS_MAX = 255

_SIGNAL_MAX = 64

MAX_DEPTH = 8

SEQ_MAX = 2**63 - 1

SCHEMA_VERSION = 1

RECORD_TYPE = "wct-pytest-journal"

HEADER_KEYS = frozenset({"schema_version", "record_type", "run_id", "executions"})

DECODER_FINDING_CODES = frozenset(
    {
        "limit_exceeded",
        "invalid_encoding",
        "truncated_line",
        "invalid_json",
        "noncanonical_json",
        "unknown_schema",
        "unknown_field",
        "invalid_field",
        "unknown_event",
        "foreign_reference",
        "sequence_error",
    }
)

_RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")

_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00$")
