#!/usr/bin/env python3
"""Sync README.md content to __init__.py docstring."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
README = ROOT / "README.md"
INIT_PY = ROOT / "python" / "hwpers" / "__init__.py"

# Sections to include in docstring (exclude API Reference tables and License)
EXCLUDE_SECTIONS = ["API Reference", "Documentation", "License"]


def extract_guide_content(readme_content: str) -> str:
    """Extract guide content from README, excluding API reference tables."""
    lines = readme_content.split("\n")
    result = []
    skip = False

    for line in lines:
        # Check for section headers
        if line.startswith("## "):
            section_name = line[3:].strip()
            skip = section_name in EXCLUDE_SECTIONS

        if not skip:
            result.append(line)

    return "\n".join(result).strip()


def update_init_py():
    """Update __init__.py with README content."""
    readme_content = README.read_text(encoding="utf-8")
    guide_content = extract_guide_content(readme_content)

    init_content = INIT_PY.read_text(encoding="utf-8")

    # Find the docstring and imports
    match = re.search(r'^""".*?"""', init_content, re.DOTALL)
    if not match:
        print("Error: Could not find docstring in __init__.py")
        return False

    # Replace docstring with new content
    new_docstring = f'"""\n{guide_content}\n"""'
    new_content = init_content[:match.start()] + new_docstring + init_content[match.end():]

    INIT_PY.write_text(new_content, encoding="utf-8")
    print(f"Updated {INIT_PY}")
    return True


if __name__ == "__main__":
    update_init_py()
