#!/usr/bin/env python3
"""
This script reads CppCoreGuidelines.md, splits its content into chapters
based on level‑1 headings (# ), writes the first chapter to docs/index.md
and subsequent chapters to separate Markdown files in docs/,
updates the mkdocs.yml file with navigation (if not already present), fixes image/link paths (copying
local images to docs/src/), processes header anchors, and creates a NOTICE file.
"""

import os
import re
import shutil

def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug:
      - Lowercase letters
      - Spaces become hyphens
      - Remove non-alphanumeric characters (except hyphens)
    """
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text

def copy_and_update_image(match, base_dir: str) -> str:
    """
    Callback for image links: if the image link is relative,
    copy the image file from base_dir to docs/src/ and update the URL.
    """
    prefix = match.group(1)
    path = match.group(2).strip()
    suffix = match.group(3)
    
    if path.startswith("http") or path.startswith("/"):
        return match.group(0)
    
    normalized = re.sub(r'^(?:\./|\.\./)+', '', path)
    source_path = os.path.join(base_dir, normalized)
    if not os.path.exists(source_path):
        print(f"WARNING: Image file '{source_path}' not found.")
        return match.group(0)
    
    dest_dir = os.path.join("docs", "src")
    os.makedirs(dest_dir, exist_ok=True)
    
    dest_path = os.path.join(dest_dir, os.path.basename(source_path))
    try:
        shutil.copy2(source_path, dest_path)
    except Exception as e:
        print(f"ERROR copying '{source_path}' to '{dest_path}': {e}")
        return match.group(0)
    
    new_link = f"src/{os.path.basename(source_path)}"
    return f"{prefix}{new_link}{suffix}"

def fix_links_and_images(content: str, base_dir: str) -> str:
    """
    Fix image and link paths in the Markdown content so that they work correctly
    when the files are moved to the docs/ directory.
    
    1. For image links that start with "./", copy the image to docs/src/ and update the link.
    2. For internal anchor links of the form (/#xxx), remove the extra "/" so that it becomes (#xxx).
    """
    content = re.sub(
        r'(!\[[^\]]*\]\()([^\s\)]+)([^\)]*\))',
        lambda m: copy_and_update_image(m, base_dir),
        content
    )
    content = re.sub(r'\(\s*/#', r'(#', content)
    return content

def process_heading_line(line: str) -> str:
    """
    Process a header line that may contain an HTML anchor.
    For example, convert:
      "# <a name="S-introduction"></a>Introduction"
    to:
      "# Introduction {#S-introduction}"
    If the header has no visible text after removing the anchor tag,
    use the anchor's name as the header text.
    """
    m = re.match(r'^(#{1,6}\s+)(<a\s+name="([^"]+)"></a>)(.*)', line)
    if m:
        header_prefix = m.group(1)
        anchor_name = m.group(3)
        rest = m.group(4).strip()
        if not rest:
            rest = anchor_name
        return f"{header_prefix}{rest} {{#{anchor_name}}}"
    else:
        return line

def split_markdown(input_file: str = 'CppCoreGuidelines.md', output_dir: str = 'docs') -> list:
    """
    Reads the input file, fixes links/images, splits the file into chapters based on
    level-1 headings (# ), processes header lines to ensure proper anchor IDs, and writes
    each chapter to a separate Markdown file in the output directory.
    
    The first chapter is written to docs/index.md (Home page), and subsequent chapters
    are written to separate files.
    
    Returns a list of tuples (title, filename) for navigation (excluding the Home page).
    """
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found!")
        return []

    base_dir = os.path.dirname(os.path.abspath(input_file))
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content = fix_links_and_images(content, base_dir)
    chapters = re.split(r'(?=^#\s)', content, flags=re.MULTILINE)
    nav_items = []
    first = True

    for chapter in chapters:
        chapter = chapter.strip()
        if not chapter:
            continue

        chapter_lines = chapter.splitlines()
        if chapter_lines:
            chapter_lines[0] = process_heading_line(chapter_lines[0])
            chapter = "\n".join(chapter_lines)

        m = re.match(r'^#{1,6}\s+(.*)', chapter_lines[0])
        if m:
            full_heading = m.group(1).strip()
            title = re.sub(r'\s*\{\#.*\}$', '', full_heading).strip()
        else:
            title = "Untitled"

        if first:
            index_path = os.path.join(output_dir, "index.md")
            with open(index_path, 'w', encoding='utf-8') as out:
                out.write(chapter + "\n")
            print(f"Created Home page: {title} -> {index_path}")
            first = False
        else:
            filename = f"{slugify(title)}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as out:
                out.write(chapter + "\n")
            nav_items.append((title, filename))
            print(f"Created chapter: {title} -> {filepath}")

    return nav_items

def update_mkdocs_config(nav_items, config_file: str = 'mkdocs.yml'):
    """
    Generate the mkdocs.yml configuration file with the following settings only if it doesn't exist:
      - site_name: C++ Core Guidelines
      - repo_url: https://github.com/xxrjun/CppCoreGuidelines
      - repo_name: xxrjun/CppCoreGuidelines
      - theme: material with the specified palette and features.
      - markdown_extensions: include toc, pymdownx.highlight (with custom settings),
        pymdownx.inlinehilite, pymdownx.snippets, and pymdownx.superfences.
      - plugins: search and open-in-new-tab.
      - nav: "Home" (index.md), "NOTICE" (NOTICE.md), followed by the chapter pages.
    If the configuration file already exists, the function will not overwrite it.
    """
    if os.path.exists(config_file):
        print(f"MkDocs config already exists at {config_file}. Skipping creation.")
        return

    lines = []
    lines.append("site_name: C++ Core Guidelines")
    lines.append("repo_url: https://github.com/xxrjun/CppCoreGuidelines")
    lines.append("repo_name: xxrjun/CppCoreGuidelines")
    lines.append("theme:")
    lines.append("  name: material")
    lines.append("  palette:")
    lines.append("    - scheme: default")
    lines.append("      primary: indigo")
    lines.append("      accent: indigo")
    lines.append("      toggle:")
    lines.append("        icon: material/brightness-7")
    lines.append("        name: Switch to dark mode")
    lines.append("    - scheme: slate")
    lines.append("      primary: indigo")
    lines.append("      accent: indigo")
    lines.append("      toggle:")
    lines.append("        icon: material/brightness-4")
    lines.append("        name: Switch to light mode")
    lines.append("  features:")
    lines.append("    - content.code.copy")
    lines.append("")
    lines.append("markdown_extensions:")
    lines.append("  - toc:")
    lines.append("      permalink: true")
    lines.append("      toc_depth: 3")
    lines.append("  - pymdownx.highlight:")
    lines.append("      anchor_linenums: true")
    lines.append("      line_spans: __span")
    lines.append("      pygments_lang_class: true")
    lines.append("  - pymdownx.inlinehilite")
    lines.append("  - pymdownx.snippets")
    lines.append("  - pymdownx.superfences")
    lines.append("")
    lines.append("plugins:")
    lines.append("  - search")
    lines.append("  - open-in-new-tab")
    lines.append("  - with-pdf:")
    lines.append("")
    lines.append("nav:")
    lines.append("  - Home: index.md")
    lines.append("  - NOTICE: NOTICE.md")
    # Append each chapter as an independent top-level navigation item.
    for title, filename in nav_items:
        lines.append(f"  - '{title}': {filename}")

    config_content = "\n".join(lines) + "\n"

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print(f"Updated MkDocs config: {config_file}")

def update_index_md():
    """
    Update docs/index.md: fix internal links and ensure it begins with the
    heading "C++ Core Guidelines".
    """
    index_file = "docs/index.md"
    heading = "# C++ Core Guidelines"
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = fix_links_and_images(content, os.getcwd())
        if not content.lstrip().startswith(heading):
            content = heading + "\n\n" + content
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated docs/index.md with heading and fixed internal links.")
    else:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(heading + "\n\nWelcome to C++ Core Guidelines!")
        print("Created docs/index.md with heading 'C++ Core Guidelines'.")

def create_notice_md():
    """
    Create a NOTICE file (docs/NOTICE.md) in English if it does not exist.
    This file warns users about known issues, such as cross-page anchor failures and PDF generation problems,
    and includes build instructions for MKDocs + PDF.
    """
    notice_file = "docs/NOTICE.md"
    if os.path.exists(notice_file):
        print(f"NOTICE file already exists at {notice_file}. Skipping creation.")
        return

    notice_content = (
        "# NOTICE\n\n"
        "WARNING: This documentation is known to have issues:\n\n"
        "- **Cross-page anchors may fail:** Internal links (anchors) that reference headings across different pages might not work as expected. PDF generation may also be affected.\n\n"
        "## Build Instructions\n\n"
        "To build the documentation with MKDocs and generate a PDF, run the following command:\n\n"
        "```bash\n"
        "./scripts/build_mkdocs.sh\n"
        "```\n\n"
        "Please consult the repository issues or contact the maintainers for further assistance.\n"
    )
    with open(notice_file, 'w', encoding='utf-8') as f:
        f.write(notice_content)
    print(f"Created NOTICE file at {notice_file}")

def main():
    nav_items = split_markdown()
    if nav_items:
        update_mkdocs_config(nav_items)
    else:
        print("No chapters found; MkDocs config was not updated.")
    update_index_md()
    create_notice_md()

if __name__ == "__main__":
    main()
