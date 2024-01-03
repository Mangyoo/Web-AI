import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from indexing import Indexer

class WebCrawler:
    def __init__(self, start_url, allowed_domain, indexer):
        self.start_url = start_url
        self.allowed_domain = allowed_domain
        self.visited_urls = set()
        self.indexer = indexer

    def crawl(self, url):
        if url in self.visited_urls:
            return

        try:
            response = requests.get(url)
            if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                self.parse_page(response.text, url)
                self.visited_urls.add(url)

                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if self.is_valid_url(next_url):
                        self.crawl(next_url)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def parse_page(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.title
        title = title_tag.string.strip() if title_tag else ''
        
        content = soup.get_text().strip()
        teaser = soup.p.string
        if teaser is None:
            teaser = ""
            
        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Content: {teaser}")
        # Send information to the indexer
        self.indexer.add_document(url=url, title=title, content=content, teaser = teaser)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return (
        parsed_url.scheme in ('http', 'https') and
        parsed_url.netloc == self.allowed_domain and
        'text/html' in requests.head(url).headers.get('content-type', '')
        )   

    def run_crawler(self):
        self.crawl(self.start_url)

if __name__ == "__main__":
    # Example usage:
    indexer = Indexer("indexdir")
    crawler = WebCrawler(start_url='https://example.com', allowed_domain='example.com', indexer=indexer)
    crawler.run_crawler()

    # Commit the changes to the index after crawling is done
    indexer.commit()
