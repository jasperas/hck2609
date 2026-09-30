import json
from email import policy
from email.parser import BytesParser
from pathlib import Path

from pypdf import PdfReader

from hck2609.contracts import CleanData, RawData


# def clean(raw: RawData) -> CleanData:
#     """Clean and normalise raw data. Stub: strips names, drops missing rows."""
#     df = raw.dropna().copy()
#     df["name"] = df["name"].str.strip().str.lower()
#     return df


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
}


# def convert_raw(
#     raw_dir: Path = Path("data/raw"), out_dir: Path = Path("data/processed")
# ) -> list[Path]:
#     """Convert folders 01-04 of raw_dir to flat JSON files in out_dir."""
#     out_dir.mkdir(parents=True, exist_ok=True)
#     written = []
#     for folder, convert in CONVERTERS.items():
#         for path in sorted(p for p in (raw_dir / folder).iterdir() if p.is_file()):
#             out = out_dir / f"{path.stem}.json"
#             out.write_text(
#                 json.dumps(convert(path), indent=2, ensure_ascii=False, default=str),
#                 encoding="utf-8",
#             )
#             written.append(out)
#     return written
