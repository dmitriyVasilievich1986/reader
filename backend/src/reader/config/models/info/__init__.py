"""Application information configuration models.

This module provides configuration models for application metadata, including
API settings and CORS configuration. It aggregates information from various
submodules to create a unified Info model.
"""

__all__ = ("Info",)

from reader import __version__ as app_version
from pydantic import BaseModel, Field

from .api import APIInfo
from .cors import CORSInfo
from .paths import PathsInfo


class Info(BaseModel):
    """Application information and configuration container.

    This model aggregates various configuration settings including application
    metadata, API settings, and CORS configuration. It serves as the central
    configuration model for application-level settings.

    Attributes:
        name: The name of the application. Defaults to "Reader".
        version: The version of the application, automatically loaded from
            the package version.
        api_info: Configuration settings for the API server.
        cors_info: Configuration settings for Cross-Origin Resource Sharing.

    """

    name: str = Field("Reader", description="The name of the application")
    description: str = Field("The application for reading books", description="The description of the application")
    version: str = Field(app_version, description="The version of the application")

    api_info: APIInfo = Field(description="The API information", default_factory=APIInfo)  # type: ignore[arg-type]
    cors_info: CORSInfo = Field(description="The CORS information", default_factory=CORSInfo)  # type: ignore[arg-type]
    paths_info: PathsInfo = Field(description="The paths information", default_factory=PathsInfo)  # type: ignore[arg-type]
