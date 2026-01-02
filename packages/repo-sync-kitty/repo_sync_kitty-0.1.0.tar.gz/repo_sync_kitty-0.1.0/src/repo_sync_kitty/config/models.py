"""Pydantic models for manifest configuration."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class RemoteConfig(BaseModel):
    """Configuration for a remote git forge."""

    name: str
    base_url: str
    branch: str | None = None
    parallelism: int | None = None
    timeout: int | None = None


class ProjectConfig(BaseModel):
    """Configuration for a single project/repository."""

    slug: str  # Set by loader if not provided (derived from path)
    path: Path
    remote: str | None = None
    branch: str | None = None
    status: Literal["active", "archived", "deleted"] = "active"


class CommonConfig(BaseModel):
    """Common/default configuration values."""

    root_path: Path
    branch: str = "main"
    remote: str
    parallelism: int = Field(default=4, ge=1, le=32)
    log_level: str = "info"
    timeout: int = Field(default=300, ge=1)
    ignore_extra: list[str] = Field(default_factory=list)


class Manifest(BaseModel):
    """Top-level manifest model."""

    common: CommonConfig
    remotes: list[RemoteConfig] = Field(default_factory=list)
    projects: list[ProjectConfig] = Field(default_factory=list)
