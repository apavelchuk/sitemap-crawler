import asyncio
import aiohttp
import re
import settings
from copy import copy
from urllib.parse import urlparse, ParseResult


class HtmlParser():
    """Handle raw html body."""

    def __init__(self, html):
        self.html = html

    def get_links(self):
        """Extract url links from raw html."""
        links_regexp = re.compile(r'<a.*?href="([^#"]*)')  # skipping everything after asterisk, if present
        links = [link.group(1) for link in links_regexp.finditer(self.html)]

        return links


class Crawler():
    """Responsible for concurrent urls fetch."""

    def __init__(self, url):
        valid_url = Crawler.validate_url(url)
        if not valid_url:
            raise RuntimeError('Please specify valid url.')

        self.root_url = valid_url
        self.visited_urls = set()

    @staticmethod
    def format_visited_url(url):
        # remove schema and possible "www."
        return url.netloc.replace('www.', '').rstrip('/') + '/' + url.path.strip('/')

    @staticmethod
    def validate_url(url, belongs_to=None):
        try:
            parsed_url = urlparse(url.rstrip('/'))
        except Exception:
            return False
        if parsed_url.scheme not in ('http', 'https', '') or \
                (not belongs_to and not parsed_url.netloc) or \
                (not parsed_url.netloc and not parsed_url.path):
            # skipping not http related resources (e.g. file:// etc) and empty urls
            return False

        if belongs_to:
            # make complete url out of relative/not full one
            # skip query string
            new_scheme = parsed_url.scheme if parsed_url.scheme else belongs_to.scheme
            new_netloc = parsed_url.netloc if parsed_url.netloc else belongs_to.netloc
            parsed_url = ParseResult(scheme=new_scheme,
                                     netloc=new_netloc,
                                     path=parsed_url.path,
                                     params='', query='', fragment='')

            if belongs_to.netloc.replace('www.', '') != parsed_url.netloc.replace('www.', ''):
                # given url does not belong to the root domain
                # skipping also subdomains as they can be really different resources
                #   containing their own sitemaps
                return False

        return parsed_url

    @classmethod
    async def process_url(cls, url, belongs_to, skip_urls):
        print(f'Crawling {url.geturl()}...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request('GET', url.geturl()) as response:
                    response = await response.text()
        except Exception as exc:
            print(f'[ERROR] Error when fetching {url}: {exc}')
            return set()

        new_urls = []
        for link in HtmlParser(response).get_links():
            valid_url = cls.validate_url(link, belongs_to)
            if valid_url and cls.format_visited_url(valid_url) not in skip_urls:
                new_urls.append(valid_url)

        print(f'[SUCCESS] Crawling {url.geturl()} DONE.')
        return set(new_urls[:settings.CRAWLER_MAX_LINKS_PER_URL])

    @classmethod
    async def fetch_links(cls, urls_to_visit, root_url, visited_urls):
        current_depth = 1
        while urls_to_visit and current_depth <= settings.CRAWLER_MAX_DEPTH:
            iter_urls = copy(urls_to_visit)
            urls_to_visit = set()  # will be used for new urls retreived from queued links
            fetch_tasks = []
            visited_urls |= set([cls.format_visited_url(url) for url in iter_urls])

            # gather fetch tasks
            for url in iter_urls:
                fetch_tasks.append(
                    Crawler.process_url(url, root_url, visited_urls)
                )

            # running tasks and queuing not visited urls
            for future in asyncio.as_completed(fetch_tasks):
                new_links = await future
                urls_to_visit |= new_links

            current_depth += 1

        if current_depth > settings.CRAWLER_MAX_DEPTH:
            print(f'Max depth({settings.CRAWLER_MAX_DEPTH}) was reached.')

    def get_visited_urls(self):
        return [f'{self.root_url.scheme}://www.{url}' for url in self.visited_urls]

    def crawl(self):
        ioloop = asyncio.get_event_loop()
        future = Crawler.fetch_links(set([self.root_url]), self.root_url, self.visited_urls)
        ioloop.run_until_complete(future)
        ioloop.close()
