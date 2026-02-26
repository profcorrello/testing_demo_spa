import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from docx_to_html import (
    convert_docx_to_html,
    _convert_paragraph,
    _convert_runs,
    _convert_run,
    _convert_table,
    main,
)


class TestConvertDocxToHtml:
    def test_convert_docx_to_html_file_not_found(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.docx"
        with pytest.raises(FileNotFoundError):
            convert_docx_to_html(nonexistent_file)

    def test_convert_docx_to_html_invalid_extension(self, tmp_path):
        not_docx = tmp_path / "file.txt"
        not_docx.write_text("content")
        with pytest.raises(ValueError, match="Expected .docx file"):
            convert_docx_to_html(not_docx)

    def test_convert_docx_to_html_with_paragraph(self, tmp_path, mocker):
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

        mocker.patch("docx_to_html.Document", return_value=mock_document)

        result = convert_docx_to_html(docx_file)

        assert "<!DOCTYPE html>" in result
        assert "<html lang=\"en\">" in result
        assert "<p>Hello World</p>" in result
        assert "</html>" in result

    def test_convert_docx_to_html_with_heading(self, tmp_path, mocker):
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        mock_run = MagicMock()
        mock_run.text = "Heading Text"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None

        mock_paragraph = MagicMock()
        mock_paragraph.text = "Heading Text"
        mock_paragraph.style.name = "Heading 1"
        mock_paragraph.runs = [mock_run]

        mock_document = MagicMock()
        mock_document.paragraphs = [mock_paragraph]
        mock_document.tables = []
        mock_document.element.body = [
            MagicMock(tag="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
        ]

        mocker.patch("docx_to_html.Document", return_value=mock_document)

        result = convert_docx_to_html(docx_file)

        assert "<h1>Heading Text</h1>" in result

    def test_convert_docx_to_html_with_table(self, tmp_path, mocker):
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        mock_paragraph = MagicMock()
        mock_paragraph.text = ""
        mock_paragraph.style.name = "Normal"
        mock_paragraph.runs = []

        mock_cell_header1 = MagicMock()
        mock_cell_header1.text = "Header1"
        mock_cell_header2 = MagicMock()
        mock_cell_header2.text = "Header2"
        mock_row_header = MagicMock()
        mock_row_header.cells = [mock_cell_header1, mock_cell_header2]

        mock_cell_data1 = MagicMock()
        mock_cell_data1.text = "Data1"
        mock_cell_data2 = MagicMock()
        mock_cell_data2.text = "Data2"
        mock_row_data = MagicMock()
        mock_row_data.cells = [mock_cell_data1, mock_cell_data2]

        mock_table = MagicMock()
        mock_table.rows = [mock_row_header, mock_row_data]

        mock_document = MagicMock()
        mock_document.paragraphs = [mock_paragraph]
        mock_document.tables = [mock_table]
        mock_document.element.body = [
            MagicMock(tag="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"),
            MagicMock(tag="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl"),
        ]

        mocker.patch("docx_to_html.Document", return_value=mock_document)

        result = convert_docx_to_html(docx_file)

        assert "<table>" in result
        assert "<th>Header1</th>" in result
        assert "<th>Header2</th>" in result
        assert "<td>Data1</td>" in result
        assert "<td>Data2</td>" in result


class TestConvertParagraph:
    def test_empty_paragraph(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "   "
        mock_paragraph.style = MagicMock(name="Normal")

        result = _convert_paragraph(mock_paragraph)
        assert result == ""

    def test_normal_paragraph(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Normal text"
        mock_paragraph.style.name = "Normal"

        mock_run = MagicMock()
        mock_run.text = "Normal text"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<p>Normal text</p>"

    def test_heading_1(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Heading 1"
        mock_paragraph.style.name = "Heading 1"

        mock_run = MagicMock()
        mock_run.text = "Heading 1"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<h1>Heading 1</h1>"

    def test_heading_2(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Heading 2"
        mock_paragraph.style.name = "Heading 2"

        mock_run = MagicMock()
        mock_run.text = "Heading 2"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<h2>Heading 2</h2>"

    def test_heading_out_of_range(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Heading"
        mock_paragraph.style.name = "Heading 10"

        mock_run = MagicMock()
        mock_run.text = "Heading"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<h6>Heading</h6>"

    def test_title_style(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Document Title"
        mock_paragraph.style.name = "Title"

        mock_run = MagicMock()
        mock_run.text = "Document Title"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<h1>Document Title</h1>"

    def test_bullet_list(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "List item"
        mock_paragraph.style.name = "List Bullet"

        mock_run = MagicMock()
        mock_run.text = "List item"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<ul><li>List item</li></ul>"

    def test_numbered_list(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "List item"
        mock_paragraph.style.name = "List Number"

        mock_run = MagicMock()
        mock_run.text = "List item"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<ol><li>List item</ol>"

    def test_blockquote(self):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Quote text"
        mock_paragraph.style.name = "Quote"

        mock_run = MagicMock()
        mock_run.text = "Quote text"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_paragraph(mock_paragraph)
        assert result == "<blockquote>Quote text</blockquote>"


class TestConvertRuns:
    def test_single_run(self):
        mock_paragraph = MagicMock()

        mock_run = MagicMock()
        mock_run.text = "Simple text"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None
        mock_paragraph.runs = [mock_run]

        result = _convert_runs(mock_paragraph)
        assert result == "Simple text"

    def test_multiple_runs(self):
        mock_paragraph = MagicMock()

        mock_run1 = MagicMock()
        mock_run1.text = "Hello "
        mock_run1.bold = False
        mock_run1.italic = False
        mock_run1.underline = False
        mock_run1.style = None

        mock_run2 = MagicMock()
        mock_run2.text = "World"
        mock_run2.bold = False
        mock_run2.italic = False
        mock_run2.underline = False
        mock_run2.style = None

        mock_paragraph.runs = [mock_run1, mock_run2]

        result = _convert_runs(mock_paragraph)
        assert result == "Hello World"

    def test_empty_run(self):
        mock_paragraph = MagicMock()

        mock_run = MagicMock()
        mock_run.text = ""

        mock_paragraph.runs = [mock_run]

        result = _convert_runs(mock_paragraph)
        assert result == ""


class TestConvertRun:
    def test_plain_text(self):
        mock_run = MagicMock()
        mock_run.text = "Plain text"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None

        result = _convert_run(mock_run)
        assert result == "Plain text"

    def test_bold_text(self):
        mock_run = MagicMock()
        mock_run.text = "Bold text"
        mock_run.bold = True
        mock_run.italic = False
        mock_run.underline = False
        mock_run.style = None

        result = _convert_run(mock_run)
        assert result == "<strong>Bold text</strong>"

    def test_italic_text(self):
        mock_run = MagicMock()
        mock_run.text = "Italic text"
        mock_run.bold = False
        mock_run.italic = True
        mock_run.underline = False
        mock_run.style = None

        result = _convert_run(mock_run)
        assert result == "<em>Italic text</em>"

    def test_underlined_text(self):
        mock_run = MagicMock()
        mock_run.text = "Underlined text"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = True
        mock_run.style = None

        result = _convert_run(mock_run)
        assert result == "<u>Underlined text</u>"

    def test_bold_italic_text(self):
        mock_run = MagicMock()
        mock_run.text = "Bold italic"
        mock_run.bold = True
        mock_run.italic = True
        mock_run.underline = False
        mock_run.style = None

        result = _convert_run(mock_run)
        assert result == "<strong><em>Bold italic</em></strong>"

    def test_all_formatting(self):
        mock_run = MagicMock()
        mock_run.text = "All formats"
        mock_run.bold = True
        mock_run.italic = True
        mock_run.underline = True
        mock_run.style = None

        result = _convert_run(mock_run)
        assert result == "<strong><em><u>All formats</u></em></strong>"

    def test_empty_text(self):
        mock_run = MagicMock()
        mock_run.text = ""

        result = _convert_run(mock_run)
        assert result == ""

    def test_strikethrough_style(self):
        mock_run = MagicMock()
        mock_run.text = "Strikethrough"
        mock_run.bold = False
        mock_run.italic = False
        mock_run.underline = False
        mock_style = MagicMock()
        mock_style.name = "Strike"
        mock_run.style = mock_style

        result = _convert_run(mock_run)
        assert result == "<s>Strikethrough</s>"


class TestConvertTable:
    def test_empty_table(self):
        mock_table = MagicMock()
        mock_table.rows = []

        result = _convert_table(mock_table)
        assert result == ""

    def test_table_with_header_row(self):
        mock_table = MagicMock()

        mock_cell1 = MagicMock()
        mock_cell1.text = "Col1"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Col2"

        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]

        mock_table.rows = [mock_row]

        result = _convert_table(mock_table)

        assert "<table>" in result
        assert "<th>Col1</th>" in result
        assert "<th>Col2</th>" in result
        assert "</table>" in result

    def test_table_with_data_rows(self):
        mock_table = MagicMock()

        mock_cell_h1 = MagicMock()
        mock_cell_h1.text = "Header1"
        mock_cell_h2 = MagicMock()
        mock_cell_h2.text = "Header2"
        mock_header_row = MagicMock()
        mock_header_row.cells = [mock_cell_h1, mock_cell_h2]

        mock_cell_d1 = MagicMock()
        mock_cell_d1.text = "Data1"
        mock_cell_d2 = MagicMock()
        mock_cell_d2.text = "Data2"
        mock_data_row = MagicMock()
        mock_data_row.cells = [mock_cell_d1, mock_cell_d2]

        mock_table.rows = [mock_header_row, mock_data_row]

        result = _convert_table(mock_table)

        assert "<th>Header1</th>" in result
        assert "<td>Data1</td>" in result
        assert "<td>Data2</td>" in result

    def test_table_cell_whitespace(self):
        mock_table = MagicMock()

        mock_cell = MagicMock()
        mock_cell.text = "  Text with spaces  "

        mock_row = MagicMock()
        mock_row.cells = [mock_cell]

        mock_table.rows = [mock_row]

        result = _convert_table(mock_table)
        assert "Text with spaces" in result


class TestMain:
    def test_main_success(self, tmp_path, mocker):
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        mock_paragraph = MagicMock()
        mock_paragraph.text = "Test"
        mock_paragraph.style.name = "Normal"
        mock_paragraph.runs = []

        mock_document = MagicMock()
        mock_document.paragraphs = [mock_paragraph]
        mock_document.tables = []
        mock_document.element.body = [
            MagicMock(tag="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
        ]

        mocker.patch("docx_to_html.Document", return_value=mock_document)

        result = main([str(docx_file)])
        assert result == 0

    def test_main_file_not_found(self):
        result = main(["nonexistent.docx"])
        assert result == 1

    def test_main_invalid_extension(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")

        result = main([str(txt_file)])
        assert result == 1
