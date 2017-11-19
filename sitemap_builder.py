from crawler import Crawler


XML_SITEMAP_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset> 
"""
XML_SITEMAP_ITEM_TEMPLATE = """<url><loc>{url}</loc></url>"""


class SitemapBuilder():
    """Build sitemap into xml file."""

    xml_sitemap = None

    @classmethod
    def get_instance(cls):
        """Entry point to work with Sitemap Builder."""
        if not getattr(cls, 'instance', None):
            cls.instance = cls()
        return cls.instance

    def build(self, url):
        """Use Crawler service to crawl and return urls."""
        crawler = Crawler(url)
        crawler.crawl()
        xml_urls = sorted(crawler.get_visited_urls())

        xml_urls = "\n".join([XML_SITEMAP_ITEM_TEMPLATE.format(url=url) for url in xml_urls])
        self.xml_sitemap = XML_SITEMAP_TEMPLATE.format(body=xml_urls)

    def write_to_file(self, file_name):
        if not self.xml_sitemap:
            print(f'No prepared sitemap to write to "{file_name}".')

        with open(file_name, 'wb') as fp:
            fp.write(self.xml_sitemap.encode('utf-8'))
        print(f'Sitemap was successfully saved to "{file_name}".')
