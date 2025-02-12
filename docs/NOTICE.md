# NOTICE by xxrjun

**Warning:** This documentation has known limitations and issues that may affect your experience:

- **Cross-page Anchors:** Internal links (anchors) that reference headings across different pages may not function correctly. This issue can also affect the accuracy of the generated PDF.

## Build Instructions

### Install Dependencies

Before building the documentation, ensure that all required dependencies are installed. For example:

```bash
# Using Conda (optional):
conda create -n mkdocs python=3.11
conda activate mkdocs

# Install the required packages with pip:
pip install -r requirements.txt
```

### Build the Documentation and PDF

To build the documentation using [MKDocs Material](https://squidfunk.github.io/mkdocs-material/) and generate a PDF version, run:

```bash
./scripts/build_mkdocs.sh
```

### Serve Locally

To preview the documentation locally, use:

```bash
mkdocs serve
```

If you encounter any issues during the build or serve process, please consult the repository's issue tracker or contact the maintainers for further assistance.

## Features and Improvements in This Version

- [x] **Automated Updates:** Automatically fetches the latest content from the upstream repository [isocpp/CppCoreGuidelines](https://github.com/isocpp/CppCoreGuidelines) on a monthly basis.
- [x] **Optimized Documentation Structure:** The guidelines are organized into separate sections using MKDocs. (My PC struggles with a single large page..)
- [x] **PDF Generation:** The entire documentation is compiled into a single PDF using [orzih/mkdocs-with-pdf](https://github.com/orzih/mkdocs-with-pdf) for convenient offline access.
- [ ] **Code Highlight**: Improved code highlighting and syntax highlighting for better readability.
- [ ] **Anchor Fixes:** Ongoing efforts are in progress to resolve issues with broken cross-page anchors.
