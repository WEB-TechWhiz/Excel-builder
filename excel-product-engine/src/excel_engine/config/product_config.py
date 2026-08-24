"""Strongly-typed product configuration.

Every product (Financial OS, Business Dashboard, CRM, ...) is described
by a ``ProductConfig`` instance. The engine only ever depends on this
shape — it never knows about "Financial OS" by name. Product packages
build a ``ProductConfig`` and hand it to the engine.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

from excel_engine.config.themes import AVAILABLE_THEMES, is_valid_theme
from excel_engine.exceptions.errors import ProductConfigurationError


class LocaleConfig(BaseModel):
    currency: str = Field(default="USD", description="ISO 4217 currency code, e.g. INR, USD.")
    language: str = Field(default="en")
    date_format: str = Field(default="DD/MM/YYYY")

    @field_validator("currency")
    @classmethod
    def _uppercase_currency(cls, v: str) -> str:
        return v.upper()


class ThemeConfig(BaseModel):
    name: str = Field(default="premium")

    @field_validator("name")
    @classmethod
    def _validate_theme_name(cls, v: str) -> str:
        if not is_valid_theme(v):
            raise ValueError(f"Unknown theme {v!r}. Available themes: {AVAILABLE_THEMES}")
        return v


class ProductConfig(BaseModel):
    """The full, validated configuration for a single product build."""

    name: str
    version: str
    author: str
    locale: LocaleConfig = Field(default_factory=LocaleConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"version must be semantic (X.Y.Z), got {v!r}")
        return v

    @classmethod
    def from_yaml(cls, path: str | Path) -> ProductConfig:
        """Load a ProductConfig from a YAML file shaped like:

            product:
              name: Financial OS
              version: 1.0.0
              author: MuffinCodes
            locale:
              currency: INR
              language: en
              date_format: DD/MM/YYYY
            theme:
              name: premium
        """
        path = Path(path)
        if not path.exists():
            raise ProductConfigurationError(f"Config file not found: {path}")

        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

        product = raw.get("product")
        if not product:
            raise ProductConfigurationError(f"{path} is missing a top-level 'product:' section")

        try:
            return cls(
                name=product["name"],
                version=product["version"],
                author=product["author"],
                locale=LocaleConfig(**raw.get("locale", {})),
                theme=ThemeConfig(**raw.get("theme", {})),
            )
        except KeyError as exc:
            raise ProductConfigurationError(f"Missing required product field: {exc}") from exc
