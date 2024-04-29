import requests
from bs4 import BeautifulSoup

def crawl_article():
    HLTV_MAIN = 'https://hltv.org'

    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    res = requests.get(HLTV_MAIN, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    if soup.find("div", {"class" : "newsgrouping"}): # if there is live update (big events)
        main_div = soup.find_all("div", {"class" : "standard-box standard-list"})[1]
    else: # there is no live update (normal situation)
        main_div = soup.find("div", {"class" : "standard-box standard-list"})
    link = main_div.find("a").attrs["href"]

    url = HLTV_MAIN + link
    res = requests.get(url, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    try:
        article_div = soup.find("article", {"class" : "newsitem standard-box"})
        title = article_div.find("h1", {"class" : "headline"}).text
        header = article_div.find("p", {"class" : "headertext"}).text
    except AttributeError:
        return None

    return {"article_title" : title, "article_header" : header, "article_url" : url}

async def broadcast_article(channel, news):
    title = str(news["article_title"])
    header = str(news["article_header"])
    link = str(news["article_url"])
    article_text = f'{"## " + title}\n{header}\n{"[HLTV link](" + link + ")"}'
    await channel.send(article_text)

if __name__ == "__main__":
    info = crawl_article()
    print(f'title : {info["article_title"]}\nheader : {info["article_header"]}\nurl : {info["article_url"]}')