from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
INDEX = ROOT / "index.qmd"

readme_text = README.read_text(encoding="utf-8")

# Remove the first line of the README (if any)
lines = readme_text.splitlines(keepends=True)
if lines:
    readme_text = "".join(lines[1:])
else:
    readme_text = ""

# Insert exactly one blank line before a top-level list block when the preceding line is not blank.
readme_text = re.sub(r"([^\n])\n(?=(?:-\s))", r"\1\n\n", readme_text)

# Preserve YAML front matter from existing index.qmd (if present)
index_txt = INDEX.read_text(encoding="utf-8")
yaml_block = ""
if index_txt.startswith("---"):
    parts = index_txt.split("---", 2)
    if len(parts) >= 3:
        yaml_block = f"---{parts[1]}---\n\n"

new_content = yaml_block + readme_text.rstrip() + "\n"
INDEX.write_text(new_content, encoding="utf-8")
