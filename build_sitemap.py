import sys
from urllib.parse import urlparse

from sitemap_builder import SitemapBuilder


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('Please specify the url to create sitemap from.')
        exit(1)

    url = sys.argv[1]
    sitemap_builder = SitemapBuilder.get_instance()
    try:
        sitemap_xml = sitemap_builder.build(url)
    except Exception as exc:
        # @TODO: introduce crawler/builder specific exceptions
        print(f'Something went wrong: {exc}')
        exit(1)

    out_file_name = 'sitemap_{}.xml'.format(urlparse(url).netloc.replace('www.', '').replace('.', '_'))
    sitemap_builder.write_to_file(out_file_name)
