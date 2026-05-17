"""System responses schemas module."""

__all__ = ("HealthResponse", "UnhealthResponse", "VersionResponse")

from .health import HealthResponse
from .unhealth import UnhealthResponse
from .version import VersionResponse
