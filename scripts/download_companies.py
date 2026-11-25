"""Download, file and verify the FY 2024-25 company documents listed in data/companies/manifest.csv.

Exchange sites (BSE/NSE) block automated downloads, so URLs are collected by hand in a browser
and pasted into the manifest. If a URL also refuses scripts, download it in the browser and save
it at the path this script prints; the verify step still checks it.

Usage:  python scripts/download_companies.py            (download missing files, then verify all)
        python scripts/download_companies.py --verify   (verify only, no downloads)
"""

import csv
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
COMPANIES_DIR = ROOT / "data" / "companies"
MANIFEST = COMPANIES_DIR / "manifest.csv"

FILENAMES = {
    "annual_report": "annual_report_FY25.pdf",
    "secretarial_compliance": "secretarial_compliance_FY25.pdf",
}
MAX_BYTES = 150 * 1024 * 1024  # large-cap annual reports can run 50-100 MB
PAGES_TO_READ = 6              # the year is almost always stated on the first few pages
USER_AGENT = "Mozilla/5.0 (research download script)"


def check_financial_year(text: str, doc_type: str) -> tuple[bool, str]:
    """Decide whether a document is for FY 2024-25 (1 Apr 2024 - 31 Mar 2025).

    `text` is the extracted text of the first few pages, lower-cased, with whitespace collapsed
    to single spaces. `doc_type` is "annual_report" or "secretarial_compliance".
    Return (True, reason) if it is FY 2024-25, else (False, reason). The reason is printed.
    """
    # TODO(human)
    raise NotImplementedError


def target_path(company: str, doc_type: str) -> Path:
    return COMPANIES_DIR / company / FILENAMES[doc_type]


def download(url: str, dest: Path) -> str:
    """Download url to dest atomically. Returns a status string."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        return f"too large (> {MAX_BYTES // (1024 * 1024)} MB), skipped"
    if not data.startswith(b"%PDF"):
        return "not a PDF (site probably returned an HTML/blocked page); download it in your browser"

    dest.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file in the same folder, then rename: a crash never leaves half a PDF behind.
    fd, tmp = tempfile.mkstemp(dir=dest.parent, suffix=".part")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.replace(tmp, dest)
    return f"downloaded ({len(data) / 1e6:.1f} MB)"


def verify(path: Path, doc_type: str) -> tuple[bool, str]:
    try:
        reader = PdfReader(path)
        pages = reader.pages[:PAGES_TO_READ]
        text = " ".join((p.extract_text() or "") for p in pages)
    except Exception as e:  # corrupt or encrypted PDF
        return False, f"could not read PDF: {type(e).__name__}"
    text = " ".join(text.lower().split())
    if not text:
        return False, "no text on first pages (scanned PDF? needs OCR)"
    return check_financial_year(text, doc_type)


def main() -> int:
    verify_only = "--verify" in sys.argv
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    problems = 0
    for row in rows:
        company, doc_type, url = row["company"], row["doc_type"], (row["url"] or "").strip()
        dest = target_path(company, doc_type)
        label = f"{company:<15} {doc_type:<24}"

        if not dest.exists():
            if verify_only or not url:
                print(f"{label} MISSING  -> add a URL, or save the PDF at {dest.relative_to(ROOT)}")
                problems += 1
                continue
            try:
                status = download(url, dest)
            except Exception as e:
                status = f"download failed: {type(e).__name__}"
            if not dest.exists():
                print(f"{label} FAILED   -> {status}. Save it manually at {dest.relative_to(ROOT)}")
                problems += 1
                continue
            print(f"{label} {status}")

        ok, reason = verify(dest, doc_type)
        print(f"{label} {'OK      ' if ok else 'CHECK   '} -> {reason}")
        problems += 0 if ok else 1

    print(f"\n{len(rows) - problems}/{len(rows)} documents ready.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
