"""Stable acceptance facade; custom mutation runners require AC1 receipts.

Runners consume WCT_ACCEPT_IR and emit WCT_ACCEPT_RECEIPT matching attempt
ID, IR hash and observed exit. Exit 1 alone is not semantic rejection.
The pytest adapter handles generated scenarios with SemanticMismatch.
"""

from tools.wct.accept.campaign import run_mutations
from tools.wct.accept.generation import generate
from tools.wct.accept.ir_checks import ir_dry
from tools.wct.accept.mutation_cases import mutations
from tools.wct.accept.parsing import STEP, parse_feature
from tools.wct.accept.verdict import accept_verdict

__all__ = [
    "STEP",
    "accept_verdict",
    "generate",
    "ir_dry",
    "mutations",
    "parse_feature",
    "run_mutations",
]
