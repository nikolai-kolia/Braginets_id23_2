# project/app/tasks.py
from celery import shared_task
from app.services.website_parser import crawl_website, graph_to_graphml
import os
import uuid
from app.core.config import Settings


@shared_task(bind=True)
def parse_website_task(self, url: str, max_depth: int, format: str):
    try:
        graph = crawl_website(url, max_depth)

        if format == "graphml":
            filename = f"graph_{uuid.uuid4()}.graphml"
            filepath = os.path.join(Settings.DATA_DIR, filename)
            os.makedirs(Settings.DATA_DIR, exist_ok=True)
            graph_to_graphml(graph, filepath)

            with open(filepath, "r") as f:
                graph_content = f.read()

            return {
                "status": "completed",
                "filepath": filepath,
                "content": graph_content
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }