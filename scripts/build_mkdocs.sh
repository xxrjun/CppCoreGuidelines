#!/bin/bash
set -e

echo "=== Splitting markdown into chapters ==="
python scripts/python/split_md_for_mkdocs.py

echo "=== Building MkDocs site (with PDF generation) ==="
mkdocs build

echo "Documentation site and PDF generated successfully."

cp site/pdf/document.pdf ./CppCoreGuidelines.pdf
