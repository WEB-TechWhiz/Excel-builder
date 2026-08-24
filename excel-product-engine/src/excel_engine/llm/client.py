"""OpenAI LLM client for generating validated Excel WorkbookSpec objects.

This is the only module in the engine that makes an external LLM API call.

The client converts a plain-English workbook request into a validated
WorkbookSpec using OpenAI structured outputs.

Required environment variable:
    OPENAI_API_KEY

Optional environment variable:
    EXCEL_ENGINE_LLM_MODEL

Example .env:
    OPENAI_API_KEY=your_openai_api_key
    EXCEL_ENGINE_LLM_MODEL=gpt-5.4
"""

from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI

from excel_engine.exceptions.errors import ProductConfigurationError
from excel_engine.llm.schema import WorkbookSpec
from excel_engine.logging_config import get_logger


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

# client.py location:
#
# <project_root>/
#     src/
#         excel_engine/
#             llm/
#                 client.py
#
# parents[0] -> llm
# parents[1] -> excel_engine
# parents[2] -> src
# parents[3] -> project_root

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


def _load_environment() -> None:
    """Load variables from the project-root .env file.

    Environment variables that already exist in the operating system are
    intentionally not overwritten.
    """

    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise ProductConfigurationError(
            "python-dotenv is not installed. Run: "
            "python -m pip install python-dotenv"
        ) from exc

    load_dotenv(ENV_FILE, override=False)


_load_environment()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logger = get_logger("llm.client")

DEFAULT_MODEL = "gpt-5.4"


SYSTEM_PROMPT = """
You turn a plain-English request for an Excel workbook into a structured
WorkbookSpec.

You never write Python code.

You never create or modify an Excel file directly.

Your only job is to produce a valid WorkbookSpec that the Excel engine can
use to build the workbook.

Rules:

1. Every KPI's source_sheet must exactly match the name of one of the tables
   defined in the workbook.

2. Every KPI's source_column must exactly match one of the column headers
   defined for its source table.

3. Only use these aggregation functions:
   - SUM
   - AVERAGE
   - COUNT
   - COUNTA
   - MAX
   - MIN

4. Keep the number of tables reasonable.

5. Keep table column counts reasonable.

6. Keep KPI counts reasonable.

7. Use meaningful, professional table and column names.

8. Choose a currency symbol based on the user's request.

9. If the user does not specify a currency, default to "$".

10. Do not invent unnecessary data fields.

11. Make the workbook specification practical for a real business user.

12. Return only information that belongs in the WorkbookSpec schema.
""".strip()


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Get the OpenAI API key from the environment."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ProductConfigurationError(
            "OPENAI_API_KEY is not set. "
            f"Add it to your .env file: {ENV_FILE}"
        )

    api_key = api_key.strip()

    if not api_key:
        raise ProductConfigurationError(
            "OPENAI_API_KEY is empty."
        )

    return api_key


def _get_model(model: str | None = None) -> str:
    """Resolve the OpenAI model.

    Priority:
        1. Explicit function argument
        2. EXCEL_ENGINE_LLM_MODEL environment variable
        3. DEFAULT_MODEL
    """

    resolved_model = (
        model
        or os.getenv("EXCEL_ENGINE_LLM_MODEL")
        or DEFAULT_MODEL
    )

    resolved_model = resolved_model.strip()

    if not resolved_model:
        raise ProductConfigurationError(
            "EXCEL_ENGINE_LLM_MODEL cannot be empty."
        )

    return resolved_model


# ---------------------------------------------------------------------------
# OpenAI client
# ---------------------------------------------------------------------------

def _create_client() -> OpenAI:
    """Create the OpenAI client."""

    api_key = _get_api_key()

    try:
        return OpenAI(api_key=api_key)
    except Exception as exc:
        raise ProductConfigurationError(
            f"Failed to initialize OpenAI client: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Workbook specification generation
# ---------------------------------------------------------------------------

def get_workbook_spec(
    prompt: str,
    model: str | None = None,
) -> WorkbookSpec:
    """Generate a validated WorkbookSpec using OpenAI.

    Args:
        prompt:
            Plain-English description of the Excel workbook.

        model:
            Optional OpenAI model override.

    Returns:
        A validated WorkbookSpec.

    Raises:
        ProductConfigurationError:
            If configuration, API communication, or response validation fails.
    """

    if not prompt or not prompt.strip():
        raise ProductConfigurationError(
            "Workbook prompt cannot be empty."
        )

    client = _create_client()
    resolved_model = _get_model(model)

    logger.info(
        "Requesting workbook spec from %s for prompt: %r",
        resolved_model,
        prompt,
    )

    try:
        response = client.responses.parse(
            model=resolved_model,
            instructions=SYSTEM_PROMPT,
            input=prompt,
            text_format=WorkbookSpec,
        )

    except Exception as exc:
        logger.exception("OpenAI API request failed.")

        raise ProductConfigurationError(
            f"OpenAI API request failed: {exc}"
        ) from exc

    # -----------------------------------------------------------------------
    # Structured output validation
    # -----------------------------------------------------------------------

    parsed = response.output_parsed

    if parsed is None:
        raise ProductConfigurationError(
            "OpenAI did not return a structured WorkbookSpec."
        )

    if not isinstance(parsed, WorkbookSpec):
        try:
            return WorkbookSpec.model_validate(parsed)
        except Exception as exc:
            raise ProductConfigurationError(
                f"OpenAI returned an invalid WorkbookSpec: {exc}"
            ) from exc

    return parsed