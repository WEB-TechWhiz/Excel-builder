"""Engine-wide runtime settings (as opposed to per-product configuration).

Loaded from environment variables (via python-dotenv) with sane defaults.
Keep this deliberately small — most configuration belongs in
``ProductConfig``, not here.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class EngineSettings(BaseModel):
    """Process-wide settings, independent of any single product."""

    output_dir: Path = Field(default=Path("output"))
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    @classmethod
    def from_env(cls) -> EngineSettings:
        return cls(
            output_dir=Path(os.getenv("EXCEL_ENGINE_OUTPUT_DIR", "output")),
            log_level=os.getenv("EXCEL_ENGINE_LOG_LEVEL", "INFO"),
            debug=os.getenv("EXCEL_ENGINE_DEBUG", "false").strip().lower() == "true",
        )


settings = EngineSettings.from_env()
