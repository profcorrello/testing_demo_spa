#!/usr/bin/env python3
"""Test script for the DOCX to HTML API."""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


class TestRootEndpoint:
    def test_root_returns_html(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "DOCX to HTML Converter API" in response.text


class TestConvertEndpoint:
    def test_convert_requires_file(self):
        response = client.post("/convert")
        assert response.status_code == 422

    def test_convert_rejects_non_docx(self):
        response = client.post(
            "/convert",
            files={"file": ("test.txt", b"content", "text/plain")}
        )
        assert response.status_code == 400
        assert "must be a .docx file" in response.text

    def test_convert_success(self, tmp_path):
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        mock_run = MagicMock()
        mock_run.text = "Hello World"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None

        mock_paragraph = MagicMock()
        mock_paragraph.text = "Hello World"
        mock_paragraph.style.name = "Normal"
        mock_paragraph.runs = [mock_run]

        mock_table = MagicMock()
        mock_table.rows = []

        mock_document = MagicMock()
        mock_document.paragraphs = [mock_paragraph]
        mock_document.tables = []
        mock_document.element.body = [
            MagicMock(tag="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
        ]

        with patch("docx_to_html.Document", return_value=mock_document):
            file_content = b"PK\x00\x00\x00\x00"
            response = client.post(
                "/convert",
                files={"file": ("test.docx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text
        assert "<p>Hello World</p>" in response.text


class TestStaticFiles:
    def test_root_includes_frontend(self):
        # container div from index.html should be present
        r = client.get("/")
        assert r.status_code == 200
        assert "<div class=\"container\">" in r.text
        assert "id=\"drop-zone\"" in r.text
        assert "/static/app.js" in r.text

    def test_css_served(self):
        r = client.get("/static/style.css")
        assert r.status_code == 200
        assert "text/css" in r.headers.get("content-type", "")

    def test_js_served(self):
        r = client.get("/static/app.js")
        assert r.status_code == 200
        # some servers return application/javascript or text/javascript
        assert "javascript" in r.headers.get("content-type", "").lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
