import json
from email import policy
from email.parser import BytesParser
from pathlib import Path

import frontmatter
import pandas as pd
from docx import Document
from pptx import Presentation
from pypdf import PdfReader

from hck2609.contracts import CleanData, RawData


def clean(raw: RawData) -> CleanData:
    """Clean and normalise raw data. Stub: strips names, drops missing rows."""
    df = raw.dropna().copy()
    df["name"] = df["name"].str.strip().str.lower()
    return df


def pptx_to_json(path: Path) -> dict:
    """Convert a PowerPoint file to {"type", "metadata", "body"}; one body block per slide."""
    prs = Presentation(path)
    props = prs.core_properties
    slides = []
    for number, slide in enumerate(prs.slides, start=1):
        lines = [
            paragraph.text.strip()
            for shape in slide.shapes
            if shape.has_text_frame
            for paragraph in shape.text_frame.paragraphs
            if paragraph.text.strip()
        ]
        slides.append(f"[Slide {number}]\n" + "\n".join(lines))
    return {
        "type": "powerpoint",
        "metadata": {
            "title": props.title,
            "author": props.author,
            "last_modified_by": props.last_modified_by,
            "created": props.created,
            "modified": props.modified,
            "slides": len(slides),
        },
        "body": "\n\n".join(slides),
    }


def docx_to_json(path: Path) -> dict:
    """Convert a Word document to {"type", "metadata", "body"} (paragraphs, then tables)."""
    doc = Document(path)
    props = doc.core_properties
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    cells = [
        cell.text.strip()
        for table in doc.tables
        for row in table.rows
        for cell in row.cells
        if cell.text.strip()
    ]
    return {
        "type": "word",
        "metadata": {
            "title": props.title,
            "author": props.author,
            "last_modified_by": props.last_modified_by,
            "revision": props.revision,
            "created": props.created,
            "modified": props.modified,
        },
        "body": "\n".join(paragraphs + cells),
    }


def excel_to_json(path: Path) -> dict:
    """Convert an Excel workbook to {"type", "metadata", "body"}; one body block per sheet."""
    sheets = pd.read_excel(path, sheet_name=None)
    blocks = []
    for name, df in sheets.items():
        rows = [
            " | ".join(str(v).strip() for v in row if pd.notna(v) and str(v).strip())
            for row in df.itertuples(index=False)
        ]
        blocks.append("\n".join([f"Sheet: {name}", *(r for r in rows if r)]))
    return {
        "type": "excel",
        "metadata": {
            "sheets": list(sheets),
            "rows": {name: len(df) for name, df in sheets.items()},
        },
        "body": "\n\n".join(blocks),
    }


def markdown_to_json(path: Path) -> dict:
    """Convert a Markdown file (optional YAML frontmatter) to {"type", "metadata", "body"}."""
    post = frontmatter.load(path)
    lines = [line.strip() for line in post.content.splitlines() if line.strip()]
    return {
        "type": "markdown",
        "metadata": dict(post.metadata),
        "body": "\n".join(lines),
    }


def email_to_json(path: Path) -> dict:
    """Convert an .eml file to {"type", "metadata", "body"}."""
    msg = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    body = msg.get_body(preferencelist=("plain", "html"))
    return {
        "type": "email",
        "metadata": {
            "from": msg["From"],
            "to": msg["To"],
            "cc": msg["Cc"],
            "subject": msg["Subject"],
            "date": msg["Date"],
            "message_id": msg["Message-ID"],
            "attachments": [a.get_filename() for a in msg.iter_attachments()],
        },
        "body": body.get_content() if body else "",
    }


def sharepoint_to_json(path: Path) -> dict:
    """Convert a SharePoint item export to {"type", "metadata", "body"}."""
    item = json.loads(path.read_text(encoding="utf-8"))
    body = item.pop("Content", "")
    return {"type": "sharepoint", "metadata": item, "body": body}


def teams_to_json(path: Path) -> dict:
    """Convert a Teams channel thread to {"type", "metadata", "body"}.

    The body is the list of messages, so replies and reactions stay available.
    """
    thread = json.loads(path.read_text(encoding="utf-8"))
    messages = thread.pop("messages", [])
    return {"type": "teams_thread", "metadata": thread, "body": messages}


def pdf_to_json(path: Path) -> dict:
    """Convert a PDF to {"type", "metadata", "body"} (text layer only, no OCR)."""
    reader = PdfReader(path)
    info = {k.lstrip("/"): v for k, v in (reader.metadata or {}).items()}
    return {
        "type": "pdf",
        "metadata": {**info, "pages": len(reader.pages)},
        "body": "\n\n".join(page.extract_text() for page in reader.pages),
    }


CONVERTERS = {
    "01_emails": email_to_json,
    "02_sharepoint": sharepoint_to_json,
    "03_teams_messages": teams_to_json,
    "04_pdf": pdf_to_json,
    "05_powerpoint": pptx_to_json,
    "06_word": docx_to_json,
    "07_excel": excel_to_json,
    "08_wiki_markdown": markdown_to_json,
}


def convert_raw(
    raw_dir: Path = Path("data/raw"), out_dir: Path = Path("data/processed")
) -> list[Path]:
    """Convert all raw folders (01-08) of raw_dir to flat JSON files in out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for folder, convert in CONVERTERS.items():
        for path in sorted(p for p in (raw_dir / folder).iterdir() if p.is_file()):
            out = out_dir / f"{path.stem}.json"
            out.write_text(
                json.dumps(convert(path), indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            written.append(out)
    return written
