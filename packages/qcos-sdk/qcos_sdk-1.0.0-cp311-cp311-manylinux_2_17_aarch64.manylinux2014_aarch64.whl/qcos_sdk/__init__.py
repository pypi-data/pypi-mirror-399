"""QCOS SDK - Quantum Circuit Optimization Service"""
__version__ = "1.0.0"
__author__ = "SoftQuantus"

from .client import QCOSClient, AsyncQCOSClient
from .models import OptimizeRequest, OptimizeResult, JobStatus

# Licensing support (optional - requires quantumlock-sdk)
try:
    from .licensing import (
        QCOSLicense,
        LicenseError,
        FeatureNotLicensed,
        LicenseExpired,
        require_license,
        require_feature,
        Features,
    )
    _HAS_LICENSING = True
except ImportError:
    _HAS_LICENSING = False
    QCOSLicense = None
    LicenseError = None
    FeatureNotLicensed = None
    LicenseExpired = None
    require_license = None
    require_feature = None
    Features = None

__all__ = [
    "QCOSClient",
    "AsyncQCOSClient",
    "OptimizeRequest",
    "OptimizeResult",
    "JobStatus",
    # Licensing
    "QCOSLicense",
    "LicenseError",
    "FeatureNotLicensed",
    "LicenseExpired",
    "require_license",
    "require_feature",
    "Features",
]
