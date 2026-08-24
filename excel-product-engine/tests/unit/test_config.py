import pytest
from pydantic import ValidationError

from excel_engine.config.product_config import LocaleConfig, ProductConfig, ThemeConfig
from excel_engine.exceptions.errors import ProductConfigurationError


def test_default_product_config():
    config = ProductConfig(name="Financial OS", version="1.0.0", author="MuffinCodes")
    assert config.locale.currency == "USD"
    assert config.theme.name == "premium"


def test_invalid_version_rejected():
    with pytest.raises(ValidationError):
        ProductConfig(name="Financial OS", version="v1", author="MuffinCodes")


def test_invalid_theme_rejected():
    with pytest.raises(ValidationError):
        ThemeConfig(name="not-a-real-theme")


def test_currency_is_uppercased():
    locale = LocaleConfig(currency="inr")
    assert locale.currency == "INR"


def test_product_config_from_yaml(tmp_path):
    yaml_content = """
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
    path = tmp_path / "config.yaml"
    path.write_text(yaml_content)
    config = ProductConfig.from_yaml(path)
    assert config.name == "Financial OS"
    assert config.locale.currency == "INR"


def test_missing_yaml_file_raises(tmp_path):
    with pytest.raises(ProductConfigurationError):
        ProductConfig.from_yaml(tmp_path / "does_not_exist.yaml")


def test_yaml_missing_product_section_raises(tmp_path):
    path = tmp_path / "bad_config.yaml"
    path.write_text("locale:\n  currency: INR\n")
    with pytest.raises(ProductConfigurationError):
        ProductConfig.from_yaml(path)
