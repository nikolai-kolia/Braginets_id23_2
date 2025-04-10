import requests
from bs4 import BeautifulSoup
import networkx as nx
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import argparse
import os


class WebsiteParser:
    def __init__(self, start_url, max_depth=2, output_format="graphml"):
        self.start_url = start_url
        self.max_depth = max_depth
        self.output_format = output_format
        self.graph = nx.DiGraph()
        self.visited = set()
        self.queue = deque()
        self.base_domain = urlparse(start_url).netloc
        self.progress = 0

    def is_valid_url(self, url):
        """Проверяет, является ли URL валидным для обработки"""
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def is_internal_link(self, url):
        """Проверяет, относится ли ссылка к тому же домену"""
        return urlparse(url).netloc == self.base_domain

    def normalize_url(self, url):
        """Нормализует URL, удаляя якоря и параметры запроса"""
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()

    def get_page_links(self, url):
        """Извлекает все ссылки со страницы"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            # Проверяем, что это HTML (а не изображение, PDF и т.д.)
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()

            for link in soup.find_all('a', href=True):
                href = link.get('href')
                abs_url = urljoin(url, href)
                norm_url = self.normalize_url(abs_url)

                if self.is_valid_url(norm_url) and self.is_internal_link(norm_url):
                    links.add(norm_url)

            return links

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при обработке {url}: {e}")
            return []

    def crawl_website(self):
        """Основной метод для обхода сайта и построения графа"""
        self.queue.append((self.start_url, 0))
        self.visited.add(self.start_url)
        self.graph.add_node(self.start_url)

        total_pages = 1  # Начинаем с 1 (стартовая страница)
        processed_pages = 0

        while self.queue:
            url, depth = self.queue.popleft()
            processed_pages += 1
            self.progress = int((processed_pages / total_pages) * 100)

            print(f"Обработка: {url} (глубина {depth})")

            if depth >= self.max_depth:
                continue

            links = self.get_page_links(url)
            for link in links:
                if link not in self.visited:
                    self.visited.add(link)
                    self.queue.append((link, depth + 1))
                    total_pages += 1

                self.graph.add_edge(url, link)

            # Обновляем прогресс
            self.progress = min(100, int((processed_pages / total_pages) * 100))

        return self.graph

    def save_graph(self, filename=None):
        """Сохраняет граф в указанном формате"""
        if not filename:
            domain = urlparse(self.start_url).netloc.replace('.', '_')
            filename = f"{domain}_depth{self.max_depth}.{self.output_format}"

        if self.output_format == "graphml":
            nx.write_graphml(self.graph, filename)
            print(f"Граф сохранен как {filename}")
            return filename
        else:
            raise ValueError(f"Неподдерживаемый формат: {self.output_format}")

    def print_summary(self):
        """Выводит статистику по графу"""
        print("\n--- Статистика ---")
        print(f"Всего страниц: {len(self.graph.nodes())}")
        print(f"Всего ссылок: {len(self.graph.edges())}")
        print(f"Максимальная глубина: {self.max_depth}")


def main():
    parser = argparse.ArgumentParser(description='Парсер структуры веб-сайта')
    parser.add_argument('url', help='URL сайта для парсинга')
    parser.add_argument('--depth', type=int, default=2,
                       help='Максимальная глубина обхода (по умолчанию: 2)')
    parser.add_argument('--format', choices=['graphml'], default='graphml',
                       help='Формат сохранения графа (по умолчанию: graphml)')
    parser.add_argument('--output', help='Имя выходного файла')

    args = parser.parse_args()

    print(f"Запуск парсера для: {args.url}")
    print(f"Максимальная глубина: {args.depth}")
    print(f"Формат вывода: {args.format}")

    start_time = time.time()

    parser = WebsiteParser(args.url, args.depth, args.format)
    graph = parser.crawl_website()
    output_file = parser.save_graph(args.output)
    parser.print_summary()

    end_time = time.time()
    print(f"\nВремя выполнения: {end_time - start_time:.2f} секунд")

    # Для соответствия требованиям выводим результат в формате JSON
    print("\nРезультат в формате JSON:")
    print('{')
    print(f'  "status": "completed",')
    print(f'  "progress": 100,')
    print(f'  "result": "{output_file}"')
    print('}')


if __name__ == "__main__":
    main()