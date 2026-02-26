# DOCX to HTML Converter

Convert Word (.docx) documents to HTML 5 with support for paragraphs, headings, tables, lists, and text formatting.

## Features

- Convert .docx files to HTML 5
- Supports headings (H1-H6), paragraphs, tables, bullet/numbered lists, and blockquotes
- Preserves text formatting: bold, italic, underline, strikethrough
- Available as CLI tool or FastAPI REST API

## Dependencies

- `python-docx>=1.1.0` - For reading .docx files
- `fastapi>=0.100.0` - For the REST API
- `uvicorn>=0.23.0` - ASGI server
- `python-multipart>=0.0.6` - For file uploads
- `httpx>=0.27.0` - For API testing
- `pytest>=7.0.0` - For testing
- `pytest-mock>=3.10.0` - For mocking in tests

## Installation

```bash
pip install -r requirements.txt
```

## CLI Usage

Convert a docx file and output to stdout:

```bash
python docx_to_html.py document.docx
```

Convert a docx file and save to HTML file:

```bash
python docx_to_html.py document.docx -o output.html
```

Format output with indentation:

```bash
python docx_to_html.py document.docx --pretty
```

## API Usage

Start the API server:

```bash
python api.py
```

The API will be available at `http://localhost:8094`

### Endpoints

#### GET /

Returns usage information.

#### POST /convert

Converts a .docx file to HTML.

**Request:**

- Content-Type: `multipart/form-data`
- Body: `file` - The .docx file to convert

**Response:**

- Content-Type: `text/html`
- Returns the converted HTML document

### API Examples

Using curl:

```bash
curl -X POST -F "file=@document.docx" http://localhost:8094/convert
```

Using Python with requests:

```python
import requests

with open("document.docx", "rb") as f:
    response = requests.post(
        "http://localhost:8094/convert",
        files={"file": f}
    )

print(response.text)
```

Using httpx:

```python
import httpx

with open("document.docx", "rb") as f:
    response = httpx.post(
        "http://localhost:8094/convert",
        files={"file": f}
    )

print(response.text)
```

## Web Interface

A single‑page application is included in the `static/` folder. It provides a drag‑and‑drop interface to upload a `.docx` file, convert it via the `/convert` API, and download the resulting HTML. The backend serves the SPA at the root path and exposes the CSS/JS under `/static`.

**Features**

- Responsive layout with a bright modern look
- Light/dark theme toggle in the top‑right corner
- Drag‑and‑drop or click to select a file
- Conversion button and download link appear after processing

> **Note:** the SPA is not a standalone file; the browser must load it over HTTP from the running backend.  If you open `static/index.html` directly with `file://`, the conversion button will fail because there is no server to handle `/convert`.

Start the server:

```bash
python api.py
# or, for auto reload during development:
uvicorn api:app --reload --port 8094
```

Open your browser to `http://localhost:8094/` — the server will return the `static/index.html` page and serve assets from `/static/`.

## Testing

### Python tests

Run all tests:

```bash
pytest
```

### UI tests (Playwright)

A Playwright script exercises the single‑page app end‑to‑end.  It will start
`api.py` in the background, navigate to the root page, upload the sample
DOCX and verify that the download link appears.

1. Install Node.js (if not already available):

    ```bash
    # on Debian/Ubuntu
    sudo apt install nodejs npm
    # or use nvm, brew, etc.
    ```

2. In the project root initialise and install Playwright:

    ```bash
    npm init -y
    npm install -D playwright
    npx playwright install
    ```

3. Run the UI tests:

    ```bash
    npx playwright test tests/ui.spec.ts
    ```

The test will spin up the API server itself; you don’t need to run `python
api.py` manually when executing the Playwright script.

## Continuous Integration

A GitHub Actions workflow runs both the Python and Playwright test suites automatically on every push to the `main` branch and on pull requests.

**Workflow file:** `.github/workflows/test.yml`

**What it does:**

1. Checks out the code.
2. Sets up Python 3.11, installs dependencies from `requirements.txt`, and runs `pytest`.
3. Sets up Node.js, installs Playwright, and runs the UI tests.
4. On completion (pass or fail), uploads the Playwright HTML report as an artifact.

The workflow uses caching to speed up dependency installation and runs on `ubuntu-latest` to ensure cross\-platform compatibility.

To enable this workflow, push the `.github/workflows/test.yml` file to your repository. Once pushed, you can view the test results in the "Actions" tab on GitHub.

### Run only API tests:

```bash
pytest tests/test_api.py -v
```

Run only CLI tests:

```bash
pytest tests/test_docx_to_html.py -v
```

## Programmatic Usage

Import and use the conversion function directly:

```python
from pathlib import Path
from docx_to_html import convert_docx_to_html

html = convert_docx_to_html("document.docx")
print(html)
```

## Supported Elements

| DOCX Element | HTML Output |
|--------------|-------------|
| Heading 1-6 | `<h1>` - `<h6>` |
| Title | `<h1>` |
| Normal Paragraph | `<p>` |
| Bullet List | `<ul><li>...</li></ul>` |
| Numbered List | `<ol><li>...</li></ol>` |
| Blockquote | `<blockquote>` |
| Table | `<table>` with `<th>`/`<td>` |
| Bold | `<strong>` |
| Italic | `<em>` |
| Underline | `<u>` |
| Strikethrough | `<s>` |
