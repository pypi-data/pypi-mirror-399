import os
import re
import glob

reference_dir = "docs/reference"

# Find all HTML files in the reference directory, excluding index.html and vignettes
html_files = [
    f
    for f in glob.glob(os.path.join(reference_dir, "*.html"))
    if not f.endswith("index.html") and "vignette" not in f.lower()
]


def convert_table_to_dl(match: re.Match) -> str:
    table_html = match.group(0)
    tbody_match = re.search(r"<tbody>(.*?)</tbody>", table_html, re.DOTALL)
    if not tbody_match:
        return table_html

    tbody = tbody_match.group(1)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tbody, flags=re.DOTALL)
    items = []
    for row in rows:
        cols = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.DOTALL)
        cols = [c.strip() for c in cols]
        if len(cols) == 4:
            name, type_, desc, default = cols
            dt = f"<dt><strong>{name}</strong></dt>"
            dd = f"<dd><code>{type_}</code> — {desc} (default: {default})</dd>"
            items.append(f"{dt}\n{dd}")
        elif len(cols) == 3:
            name, type_, desc = cols
            dt = f"<dt><strong>{name}</strong></dt>"
            dd = f"<dd><code>{type_}</code> — {desc}</dd>"
            items.append(f"{dt}\n{dd}")
        elif len(cols) == 2:
            type_, desc = cols
            dd = f"<dd><code>{type_}</code> — {desc}</dd>"
            items.append(dd)

    if not items:
        return table_html

    dl_content = "\n".join(items)
    return (
        '<dl style="border: 1.5px solid #b3c7e6; background: #f8fbff; '
        'border-radius: 6px; padding: 1em; margin: 1em 0;">'
        f"{dl_content}"
        "</dl>"
    )


table_pattern = r'<table[^>]*class="[^"]*caption-top[^"]*table[^"]*"[^>]*>.*?</table>'


def fix_dd_bullets_in_content(content: str) -> str:
    """
    Convert lists inside <dd>...</dd> into proper <ul><li> items.
    Handles:
      - newline-separated lists where lines start with '-' (multiline)
      - collapsed inline lists like 'columns: - x: ... - y: ...'
    """

    def repl(match: re.Match) -> str:
        inner = match.group(1)

        # 1) Multiline lists: lines starting with '-'
        if re.search(r"^\s*-\s+", inner, flags=re.MULTILINE):
            # extract list items
            items = re.findall(r"^\s*-\s*(.+)", inner, flags=re.MULTILINE)
            # remove those list lines from the inner content
            new_inner = re.sub(r"^\s*-\s*.+\n?", "", inner, flags=re.MULTILINE).rstrip()
            ul = (
                "<ul>"
                + "".join(f"<li>{it.strip()}</li>" for it in items if it.strip())
                + "</ul>"
            )
            # if there's remaining prefix text, keep it before the list
            if new_inner:
                # ensure spacing and preserve existing markup
                return f"<dd>{new_inner} {ul}</dd>"
            return f"<dd>{ul}</dd>"

        # 2) Collapsed inline list (no leading line breaks), look for "colon then dash" or "- item" patterns
        if " - " in inner:
            # try to find a prefix ending with a colon
            m = re.search(r":\s*-\s*", inner)
            if m:
                prefix = inner[: m.start() + 1]  # include colon
                items_part = inner[m.end() :]
            else:
                # fallback: split before the first " - "
                parts = re.split(r"\s*-\s*", inner, maxsplit=1)
                if len(parts) == 1:
                    return f"<dd>{inner}</dd>"
                prefix = parts[0]
                items_part = parts[1]

            # capture each "- item" (non-greedy) so that "x: x-coords" stays together
            raw_items = re.findall(
                r"-\s*(.*?)(?=(?:\s*-\s|$))", "-" + items_part, flags=re.DOTALL
            )
            items = [it.strip() for it in raw_items if it.strip()]
            if not items:
                return f"<dd>{inner}</dd>"

            ul = "<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>"
            new_inner = prefix.rstrip() + " " + ul
            return f"<dd>{new_inner}</dd>"

        # nothing to change
        return f"<dd>{inner}</dd>"

    return re.sub(r"<dd>(.*?)</dd>", repl, content, flags=re.DOTALL)


# Process each HTML file
for html_file in html_files:
    if not os.path.exists(html_file):
        continue
    with open(html_file, "r", encoding="utf-8") as fh:
        content = fh.read()

    # 1) convert caption-top tables into dl blocks
    content = re.sub(table_pattern, convert_table_to_dl, content, flags=re.DOTALL)

    # 2) fix any lists that ended up inside <dd> blocks
    content = fix_dd_bullets_in_content(content)

    with open(html_file, "w", encoding="utf-8") as fh:
        fh.write(content)

    print(f"Processed: {html_file}")

if html_files:
    print("Post-render complete: tables converted and <dd> lists fixed.")
else:
    print(f"No HTML files found in {reference_dir}")
