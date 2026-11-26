"""Stores uploaded reports: the PDF goes to Supabase Storage, its details to the `documents` table.

Every query is filtered by user_id taken from the verified login token, so one user can never
see or overwrite another user's documents (v1 leaked evidence between reports).
"""

from dataclasses import dataclass

from supabase import Client

from app.core.config import get_settings

COLUMNS = "id, company_name, fiscal_year, original_filename, size_bytes, page_count, status, created_at"


@dataclass
class NewDocument:
    user_id: str
    company_name: str
    fiscal_year: str
    original_filename: str
    sha256: str
    size_bytes: int
    page_count: int
    content: bytes


class DocumentRepository:
    def __init__(self, client: Client):
        self.client = client
        self.bucket = get_settings().storage_bucket

    def find_by_hash(self, user_id: str, sha256: str) -> dict | None:
        rows = (
            self.client.table("documents").select(COLUMNS)
            .eq("user_id", user_id).eq("sha256", sha256).limit(1).execute().data
        )
        return rows[0] if rows else None

    def list_for_user(self, user_id: str) -> list[dict]:
        return (
            self.client.table("documents").select(COLUMNS)
            .eq("user_id", user_id).order("created_at", desc=True).execute().data
        )

    def create(self, doc: NewDocument) -> dict:
        # The file is named by its content hash, so re-uploading the same file can't create a second copy.
        path = f"{doc.user_id}/{doc.sha256}.pdf"
        storage = self.client.storage.from_(self.bucket)
        storage.upload(path, doc.content, {"content-type": "application/pdf", "upsert": "true"})
        try:
            row = {
                "user_id": doc.user_id,
                "company_name": doc.company_name,
                "fiscal_year": doc.fiscal_year,
                "original_filename": doc.original_filename,
                "storage_path": path,
                "sha256": doc.sha256,
                "size_bytes": doc.size_bytes,
                "page_count": doc.page_count,
            }
            return self.client.table("documents").insert(row).execute().data[0]
        except Exception:
            # Don't leave an orphan file in Storage if the database insert failed.
            storage.remove([path])
            raise


def get_document_repo() -> DocumentRepository:
    from app.services.supabase_client import get_admin_client

    return DocumentRepository(get_admin_client())
