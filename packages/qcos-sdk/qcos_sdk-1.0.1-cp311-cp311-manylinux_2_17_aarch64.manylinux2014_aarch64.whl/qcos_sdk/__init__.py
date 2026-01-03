"""QCOS SDK - Quantum Circuit Optimization Service"""
__version__ = "v1.0.1"
__author__ = "SoftQuantus"

from .client import QCOSClient, AsyncQCOSClient
from .models import OptimizeRequest, OptimizeResult, JobStatus

try:
    from .licensing import QCOSLicense, require_license, require_feature
    _HAS_LICENSING = True
except ImportError:
    _HAS_LICENSING = False

__all__ = ["QCOSClient", "AsyncQCOSClient", "OptimizeRequest", "OptimizeResult", "JobStatus"]
