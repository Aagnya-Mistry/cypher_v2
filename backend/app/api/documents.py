"""Upload and list annual reports.

Routes are plain `def` (not async) on purpose: Supabase and PDF calls block, and FastAPI runs
plain functions in a worker thread so the server stays responsive (v1 blocked its event loop).
"""

import hashlib
import io
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pypdf import PdfReader

from app.api.deps import CurrentUser, get_current_user
from app.core.config import get_settings
from app.models.schemas import FISCAL_YEARS, DocumentOut
from app.services.documents import DocumentRepository, NewDocument, get_document_repo

router = APIRouter(prefix="/documents", tags=["documents"])
log = logging.getLogger(__name__)


@router.get("", response_model=list[DocumentOut])
def list_documents(
    user: CurrentUser = Depends(get_current_user),
    repo: DocumentRepository = Depends(get_document_repo),
):
    return repo.list_for_user(user.id)


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    fiscal_year: str = Form(...),
    user: CurrentUser = Depends(get_current_user),
    repo: DocumentRepository = Depends(get_document_repo),
):
    company_name = " ".join(company_name.split())
    if not 2 <= len(company_name) <= 100:
        raise HTTPException(400, "Company name must be 2 to 100 characters")
    if fiscal_year not in FISCAL_YEARS:
        raise HTTPException(400, f"Fiscal year must be one of: {', '.join(FISCAL_YEARS)}")

    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    content = file.file.read(max_bytes + 1)  # read one byte past the limit to detect oversize files
    if len(content) > max_bytes:
        raise HTTPException(413, f"File is larger than {get_settings().max_upload_mb} MB")
    if not content.startswith(b"%PDF"):
        raise HTTPException(400, "This file is not a PDF")

    sha256 = hashlib.sha256(content).hexdigest()
    existing = repo.find_by_hash(user.id, sha256)
    if existing:
        raise HTTPException(409, f"You already uploaded this file (as {existing['company_name']})")

    try:
        page_count = len(PdfReader(io.BytesIO(content)).pages)
    except Exception:
        raise HTTPException(400, "This PDF could not be read (damaged or password-protected?)")

    try:
        return repo.create(
            NewDocument(
                user_id=user.id,
                company_name=company_name,
                fiscal_year=fiscal_year,
                original_filename=(file.filename or "report.pdf")[:255],
                sha256=sha256,
                size_bytes=len(content),
                page_count=page_count,
                content=content,
            )
        )
    except Exception:
        log.exception("Upload failed for user %s", user.id)  # full error goes to the server log only
        raise HTTPException(500, "Upload failed. Please try again.")
