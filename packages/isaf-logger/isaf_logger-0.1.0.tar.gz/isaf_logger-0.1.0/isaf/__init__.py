"""
ISAF Logger - Instruction Stack Audit Framework

Automatic compliance logging for AI systems. Captures the complete
instruction stack (Layers 6-8) for regulatory compliance with
EU AI Act, NIST AI RMF, and ISO/IEC 42001.

Usage:
    import isaf
    
    isaf.init()
    
    @isaf.log_objective(name="cross_entropy_loss")
    def train(model, data):
        ...
    
    @isaf.log_data(source="internal", version="1.0")
    def load_data():
        ...
    
    lineage = isaf.get_lineage()
    isaf.export("compliance_report.json")
"""

__version__ = "0.1.0"
__author__ = "HAIEC Lab"
__email__ = "contact@haiec.com"

from isaf.core.session import (
    init,
    get_lineage,
    export,
    verify_lineage,
    get_session
)

from isaf.decorators import (
    log_objective,
    log_data,
    log_framework,
    log_all
)

__all__ = [
    "init",
    "get_lineage",
    "export",
    "verify_lineage",
    "get_session",
    "log_objective",
    "log_data",
    "log_framework",
    "log_all",
    "__version__"
]
