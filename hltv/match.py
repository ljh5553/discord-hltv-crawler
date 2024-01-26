import requests
import datetime
from bs4 import BeautifulSoup

def crawl_matches():
    HLTV_MAIN = 'https://hltv.org'

    match_infos = []

    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    res = requests.get(HLTV_MAIN, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    matches_div = soup.find("div", {"class" : "top-border-hide"})
    matches = matches_div.find_all("a", {"class" : "hotmatch-box a-reset"})
    for match in matches:
        title = match.attrs["title"].split("-")[-1].strip()
        
        team1 = team2 = "TBA"
        if match.select(".team"):
            team1 = match.select(".team")[0].text
            team2 = match.select(".team")[1].text
        
        time = "ONGOING"
        time_div = match.find("div", {"class" : "middleExtra"})
        if time_div:
            unixtime = time_div.attrs["data-unix"]
            time = datetime.datetime.fromtimestamp(int(unixtime) // 1000)
        
        url = HLTV_MAIN + match.attrs["href"]

        match_infos.append({"match_title" : title,
                            "match_team1" : team1,
                            "match_team2" : team2,
                            "match_time" : time,
                            "match_url" : url
                            })
    
    return match_infos
        
async def send_ongoing_matches(ctx, matches):
    ongoings = []
    msg = ""

    for match in matches:
        if match["match_time"] == "ONGOING":
            ongoings.append(match)

    print(ongoings)
    
    if ongoings:
        for ongoing in ongoings:
            event = str(ongoing["match_title"])
            team1 = str(ongoing["match_team1"])
            team2 = str(ongoing["match_team2"])
            url = str(ongoing["match_url"])

            #testmsg = f'{"**Event : " + event + "**"}\n{team1 + " VS. " + team2}\n{"[Match Page](" + url + ")"}\n\n'
            #print(testmsg)
            msg += f'{"**" + event + "**"}\n{"* " + team1 + " VS. " + team2}\n{"[Match Page](" + url + ")"}\n\n'
        
    else:
        msg = "No ongoing match"

    await ctx.send(msg)

async def send_matches(ctx, cnt, matches):
    msg = ""

    if not matches:
        await ctx.send("There's no upcoming match")
    
    else:
        if cnt == None or cnt > 5: cnt = 5
        i = 0
        
        for match in matches:

            if i < cnt:
                i += 1
            else:
                break

            event = str(match["match_title"])
            team1 = str(match["match_team1"])
            team2 = str(match["match_team2"])
            time = str(match["match_time"])
            url = str(match["match_url"])

            msg += f'{"**" + event + "**"}\n{"* " + team1 + " VS. " + team2}\n{"Start time (KST) : " + time}\n{"[Match Page](" + url + ")"}\n\n'

        await ctx.send(msg)

if __name__ == "__main__":
    print(crawl_matches())