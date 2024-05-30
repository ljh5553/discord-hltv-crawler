import requests
import cloudscraper
import re
from bs4 import BeautifulSoup

def scrap_website(link):
    timeout = 10
    scraper = cloudscraper.create_scraper()
    res = scraper.get(link, timeout = timeout)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def crawl_article():
    HLTV_MAIN = 'http://hltv.org'
    link = ''

    try:
        main_soup = scrap_website(HLTV_MAIN)
    except requests.exceptions.ReadTimeout:
        return -2

    if "Just a moment" in main_soup.find("title").string:
        return -1

    try:
        if main_soup.find("div", {"class" : "newsgrouping"}): # if there is live update (big events)
            main_div = main_soup.find_all("div", {"class" : "standard-box standard-list"})[1]
        else: # there is no live update (normal situation)
            main_div = main_soup.find("div", {"class" : "standard-box standard-list"})

        short_re = re.compile('short:', re.IGNORECASE)
        
        if short_re.search(main_div.find("div", {"class" : "newstext"}).string):
            link = HLTV_MAIN + main_div.find_all("a")[1].attrs["href"]
        else:
            link = HLTV_MAIN + main_div.find("a").attrs["href"]

        # link_main = HLTV_MAIN + main_div.find("a").attrs["href"]
        # link_sub = HLTV_MAIN + main_div.find_all("a")[1].attrs["href"]
    except AttributeError:
        return None
    
    try:
        article_soup = scrap_website(link)
    except requests.exceptions.ReadTimeout:
        return -2
    
    try:
        article_div = article_soup.find("article", {"class" : "newsitem standard-box"})
        title = article_div.find("h1", {"class" : "headline"}).text
        header = article_div.find("p", {"class" : "headertext"}).text
    except AttributeError:
        return None

    return {"article_title" : title, "article_header" : header, "article_url" : link}

    # if article_div.find("h1", {"class" : "headline"}) is not None: #first article is NOT short news
    #     title = article_div.find("h1", {"class" : "headline"}).text
    #     header = article_div.find("p", {"class" : "headertext"}).text
    #     return {"article_title" : title, "article_header" : header, "article_url" : link_main}
    
    # else: #first article is short news
    #     article_soup = scrap_website(link_sub)
    #     article_div = article_soup.find("article", {"class" : "newsitem standard-box"})
    #     title = article_div.find("h1", {"class" : "headline"}).text
    #     header = article_div.find("p", {"class" : "headertext"}).text
    #     return {"article_title" : title, "article_header" : header, "article_url" : link_sub}

async def broadcast_article(channel, news):
    title = str(news["article_title"])
    header = str(news["article_header"])
    link = str(news["article_url"])
    article_text = f'{"## " + title}\n{header}\n{"[HLTV link](" + link + ")"}'
    await channel.send(article_text)

if __name__ == "__main__":
    info = crawl_article()

    if info is None:
        print("info is None")
    elif info == -1:
        print("cloudflare block detected")
    elif info == -2:
        print("Page request timeout")
    else:
        print(f'title : {info["article_title"]}\nheader : {info["article_header"]}\nurl : {info["article_url"]}')