from fastapi import APIRouter
from utils.docs_service import get_docs_service
from config.google_oauth import SCOPES

router = APIRouter(prefix="/api/docs")

@router.post("/create")
def create_doc(
    token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    title: str = "WorkFlow.AI Document",
    content: str = "Hello Pavi! This document was created using FastAPI 💛"
):
    docs_service, drive_service = get_docs_service(
        token, refresh_token, client_id, client_secret, SCOPES
    )

    # 1. Create a blank Google Doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")

    # 2. Insert content into the Doc
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": content
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()

    # 3. Generate a shareable link (optional)
    drive_service.permissions().create(
        fileId=doc_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    link = f"https://docs.google.com/document/d/{doc_id}/edit"

    return {"doc_id": doc_id, "link": link}
