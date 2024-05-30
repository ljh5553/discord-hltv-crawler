def parse_news(news_soup):
    title = news_soup.find("h1", {"class" : "headline"}).text
    header = news_soup.find("p", {"class" : "headertext"}).text

    return {"article_title" : title, "article_header" : header}

async def broadcast_article(channel, news, news_link):
    title = news["article_title"]
    header = news["article_header"]
    link = news_link
    article_text = f'{"## " + title}\n{header}\n{"[HLTV link](<" + link + ">)"}'
    await channel.send(article_text)