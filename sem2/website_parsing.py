# project/app/api/endpoints/website_parsing.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.website_parse import WebsiteParseRequest, WebsiteParseResponse
from celery.result import AsyncResult
from fastapi import BackgroundTasks
from app.tasks import parse_website_task
from app.api.dependencies import get_current_user

parsing_router = APIRouter()


@parsing_router.post("/parse_website", response_model=WebsiteParseResponse)
async def parse_website(
        request: WebsiteParseRequest,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(get_current_user)
):
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    if request.max_depth < 0 or request.max_depth > 5:
        raise HTTPException(status_code=400, detail="Max depth should be between 0 and 5")

    task = parse_website_task.delay(
        url=request.url,
        max_depth=request.max_depth,
        format=request.format
    )

    return {"task_id": task.id}