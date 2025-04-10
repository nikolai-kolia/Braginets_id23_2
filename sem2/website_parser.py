# project/app/services/website_parser.py
import requests
from bs4 import BeautifulSoup
import networkx as nx
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, Optional
from celery import current_task
import time


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def is_internal_url(base_url: str, url: str) -> bool:
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    return url_domain == base_domain

def crawl_website(
    url: str,
    max_depth: int = 2,
    current_depth: int = 0,
    visited: Optional[Set[str]] = None,
    graph: Optional[nx.DiGraph] = None
) -> nx.DiGraph:
    if visited is None:
        visited = set()
    if graph is None:
        graph = nx.DiGraph()

    if current_depth > max_depth or url in visited:
        return graph

    try:
        # Обновляем статус задачи в Celery
        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "progress": int((current_depth / max_depth) * 100),
                    "current_url": url
                }
            )

        visited.add(url)
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        # Проверяем, что это HTML (а не изображение, PDF и т.д.)
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return graph

        soup = BeautifulSoup(response.text, "html.parser")
        graph.add_node(url, title=soup.title.string if soup.title else "")

        for link in soup.find_all("a", href=True):
            href = link.get("href")
            abs_url = urljoin(url, href)

            # Очищаем URL от якорей и параметров
            abs_url = urlparse(abs_url)
            abs_url = abs_url._replace(fragment="", query="")
            abs_url = abs_url.geturl()

            if is_valid_url(abs_url) and is_internal_url(url, abs_url):
                graph.add_edge(url, abs_url)
                if abs_url not in visited:
                    crawl_website(
                        abs_url,
                        max_depth,
                        current_depth + 1,
                        visited,
                        graph
                    )

    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")
        graph.add_node(url, error=str(e))

    return graph

def graph_to_graphml(graph: nx.DiGraph, filepath: str) -> str:
    nx.write_graphml(graph, filepath)
    return filepath