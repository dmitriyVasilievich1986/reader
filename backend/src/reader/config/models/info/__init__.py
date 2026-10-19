"""Application information configuration models.

This module provides configuration models for application metadata, including
API server, CORS and filesystem path settings. It aggregates the submodels into
a single ``Info`` model.
"""

__all__ = ("Info",)

from pydantic import BaseModel, Field

from reader import __version__ as app_version

from .api import APIInfo
from .cors import CORSInfo
from .paths import PathsInfo


class Info(BaseModel):
    """Application information and configuration container.

    This model aggregates application metadata together with API server, CORS
    and filesystem path settings. It is the central configuration model for
    application-level settings.

    Attributes:
        name (str): Name of the application. Defaults to ``"Reader"``.
        description (str): Short description of the application. Defaults to
            ``"The application for reading books"``.
        version (str): Version of the application. Defaults to the installed
            package version (``reader.__version__``).
        api_info (APIInfo): API server settings.
        cors_info (CORSInfo): Cross-Origin Resource Sharing settings.
        paths_info (PathsInfo): Filesystem paths used by the application.

    """

    name: str = Field("Reader", description="The name of the application")
    description: str = Field("The application for reading books", description="The description of the application")
    version: str = Field(app_version, description="The version of the application")

    api_info: APIInfo = Field(..., description="The API information")
    cors_info: CORSInfo = Field(..., description="The CORS information")
    paths_info: PathsInfo = Field(..., description="The paths information")
