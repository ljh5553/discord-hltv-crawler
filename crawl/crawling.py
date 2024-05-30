import re
import cloudscraper
from bs4 import BeautifulSoup

class CloudflareException(Exception):
    def __init__(self):
        super().__init__("Cloudflare blocking detected")

def scrap_website(link, timeout):
    scraper = cloudscraper.create_scraper()
    res = scraper.get(link, timeout = timeout)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    if "Just a moment" in soup.find("title").string:
        raise CloudflareException
    return soup

def parse_newsdetail(main_soup, HLTV_MAIN):
    if main_soup.find("div", {"class" : "newsgrouping"}): # if there is live update (big events)
        main_div = main_soup.find_all("div", {"class" : "standard-box standard-list"})[1]
    else: # there is no live update (normal situation)
        main_div = main_soup.find("div", {"class" : "standard-box standard-list"})

    if scrap_website(HLTV_MAIN + main_div.find("a").attrs["href"], 10).find("h1", {"class" : "headline"}) is None:
        return HLTV_MAIN + main_div.find_all("a")[1].attrs["href"]
    else:
        return HLTV_MAIN + main_div.find("a").attrs["href"]