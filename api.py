#!/usr/bin/env python3
"""FastAPI application for converting docx files to HTML."""

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from docx_to_html import convert_docx_to_html

app = FastAPI(title="DOCX to HTML Converter")

# serve frontend static files from the `static` directory at root
from fastapi.staticfiles import StaticFiles

# serve frontend assets from /static; API endpoints remain at root paths
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/convert", response_class=HTMLResponse)
async def convert_docx(file: UploadFile = File(...)):
    """Convert a .docx file to HTML.
    
    Upload a .docx file and receive the converted HTML.
    """
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="File must be a .docx file")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)
    
    try:
        html = convert_docx_to_html(tmp_path)
        return html
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Return the SPA entrypoint from the static assets."""
    # reading the file ensures the latest version is served; the static mount
    # will still provide CSS/JS under /static
    index_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(index_path.read_text())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8094)
