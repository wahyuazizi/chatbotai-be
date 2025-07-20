from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.rag_service import rag_service
from app.utils.security import has_role

router = APIRouter()

class IngestRequest(BaseModel):
    file_paths: Optional[List[str]] = Field(None, description="List of local file paths to ingest.")
    urls: Optional[List[str]] = Field(None, description="List of URLs to ingest.")

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_data(request: IngestRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(has_role(["admin"]))):
    """
    Endpoint to ingest data from files and URLs into the vector store.
    This process runs in the background.
    """
    if not request.file_paths and not request.urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'file_paths' or 'urls' must be provided."
        )

    # Run the ingestion in the background to avoid blocking the API
    background_tasks.add_task(rag_service.ingest_data, file_paths=request.file_paths, urls=request.urls)

    return {"message": "Data ingestion started in the background."}
