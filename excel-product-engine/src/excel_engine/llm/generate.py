"""End-to-end: a plain-English prompt in, a saved .xlsx path out.

    python -m excel_engine.llm.generate "Make me a sales tracker with total revenue"
"""

from __future__ import annotations

import sys
from pathlib import Path

from excel_engine.llm.builder import build_from_spec
from excel_engine.llm.client import get_workbook_spec
from excel_engine.logging_config import get_logger

logger = get_logger("llm.generate")


def generate_workbook(
    prompt: str, output_dir: str | Path = "output", model: str | None = None
) -> Path:
    """The full pipeline: prompt -> Claude -> validated spec -> real workbook -> disk."""
    spec = get_workbook_spec(prompt, model=model)
    workbook = build_from_spec(spec)
    filename = spec.product_name.strip().lower().replace(" ", "_") + ".xlsx"
    path = workbook.save(Path(output_dir) / filename)
    logger.info("Generated %s from prompt %r", path, prompt)
    return path


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m excel_engine.llm.generate "your prompt here"')
        raise SystemExit(1)
    prompt = " ".join(sys.argv[1:])
    path = generate_workbook(prompt)
    print(f"Saved: {path}")


if __name__ == "__main__":
    main()
