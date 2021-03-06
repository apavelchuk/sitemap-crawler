# Sitemap Crawler

Crawls given website and builds its sitemap xml file.
Makes use of python3.6/asyncio networking library to fetch urls concurrently.

General algorithm is similar to BFS: firstly we discover links of the initial url 
(marking initial one as visited), on the next level we fetch links for all the retrieved urls 
on the previous level (without going deep immediately) etc.

In order to use the script you would need to install requirements from the provided text file:  
```pip3 install -r requirements.txt```
  
You can run the crawler with:  
```python3 build_sitemap.py https://www.sitemaps.org/```  
And expect file **sitemap_sitemaps_org.xml** to be generated.

A few things to notice:
 * Some restrictions were put in place in order not to overwhelm the target site: max amount of levels for crawler to go 
    and max number of links to process on each page. You can change it **settings.py**.
 * The output xml complies with the Sitemap protocol (https://www.sitemaps.org/)
