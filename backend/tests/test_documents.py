"""Upload rules, tested with a fake in-memory store instead of Supabase."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.documents import get_document_repo
from tests.utils import auth_header

def _one_page_pdf() -> bytes:
    import io

    from pypdf import PdfWriter

    w = PdfWriter()
    w.add_blank_page(width=10, height=10)
    buf = io.BytesIO()
    w.write(buf)
    return buf.getvalue()


TINY_PDF = _one_page_pdf()


class FakeRepo:
    def __init__(self):
        self.rows = []

    def find_by_hash(self, user_id, sha256):
        return next((r for r in self.rows if r["user_id"] == user_id and r["sha256"] == sha256), None)

    def list_for_user(self, user_id):
        return [r for r in self.rows if r["user_id"] == user_id]

    def create(self, doc):
        row = {
            "id": f"doc-{len(self.rows) + 1}", "user_id": doc.user_id, "company_name": doc.company_name,
            "fiscal_year": doc.fiscal_year, "original_filename": doc.original_filename, "sha256": doc.sha256,
            "size_bytes": doc.size_bytes, "page_count": doc.page_count, "status": "uploaded",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.rows.append(row)
        return row


@pytest.fixture
def repo():
    fake = FakeRepo()
    app.dependency_overrides[get_document_repo] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


client = TestClient(app)


def upload(content=TINY_PDF, company="Tata Consultancy Services", fy="FY2024-25", headers=None):
    return client.post(
        "/api/documents",
        files={"file": ("report.pdf", content, "application/pdf")},
        data={"company_name": company, "fiscal_year": fy},
        headers=auth_header() if headers is None else headers,
    )


def test_upload_and_list(repo):
    r = upload()
    assert r.status_code == 201
    body = r.json()
    assert body["company_name"] == "Tata Consultancy Services"
    assert body["page_count"] == 1
    assert "sha256" not in body and "user_id" not in body  # internal fields stay internal

    listed = client.get("/api/documents", headers=auth_header()).json()
    assert [d["id"] for d in listed] == [body["id"]]


def test_login_required(repo):
    assert upload(headers={}).status_code == 401
    assert client.get("/api/documents").status_code == 401


def test_duplicate_file_rejected(repo):
    assert upload().status_code == 201
    r = upload(company="Same file again")
    assert r.status_code == 409
    assert len(repo.rows) == 1


def test_same_file_allowed_for_different_users(repo):
    assert upload().status_code == 201
    assert upload(headers=auth_header(sub="other-user")).status_code == 201


def test_users_only_see_their_own_documents(repo):
    upload()
    assert client.get("/api/documents", headers=auth_header(sub="other-user")).json() == []


@pytest.mark.parametrize(
    "kwargs, status",
    [
        ({"content": b"<html>blocked</html>"}, 400),  # not a PDF
        ({"content": b"%PDF-1.4 garbage"}, 400),       # looks like a PDF but can't be read
        ({"company": " "}, 400),                        # empty company name
        ({"fy": "FY1999-00"}, 400),                     # unknown fiscal year
    ],
)
def test_bad_uploads_rejected(repo, kwargs, status):
    assert upload(**kwargs).status_code == status
    assert repo.rows == []


def test_too_large_rejected(repo, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "max_upload_mb", 0)
    r = upload()
    assert r.status_code == 413
