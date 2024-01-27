import requests
import datetime
import re
from bs4 import BeautifulSoup

def crawl_matches():
    HLTV_MAIN = 'https://hltv.org'

    match_infos = []

    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    res = requests.get(HLTV_MAIN, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    matches_div = soup.find("div", {"class" : "top-border-hide"})
    #print(matches_div)
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

        stars_div = match.find("div", {"class" : re.compile(r'^teambox match')})

        stars_n = int(stars_div.attrs["stars"])
        stars = ""
        if stars_n == 0: pass
        else :
            for i in range(stars_n): stars += "*"


        match_infos.append({"match_title" : title,
                            "match_team1" : team1,
                            "match_team2" : team2,
                            "match_time" : time,
                            "match_url" : url,
                            "match_stars" : stars
                            })
    
    return match_infos

def star_filter(matches):
    only_stars = []

    for match in matches:
        if  "*" in str(match["match_stars"]):
            only_stars.append(match)

    return only_stars

async def send_ongoing_matches(ctx, arg, matches):
    ongoings = []
    msg = ""

    for match in matches:
        if match["match_time"] == "ONGOING":
            ongoings.append(match)
    
    if ongoings:

        if arg is None or arg.isdecimal():
            cnt = 0
        
            if arg is None: arg = 5
            else : arg = int(arg)

            for ongoing in ongoings:

                if cnt < arg:
                    cnt += 1
                else:
                    break

                event = str(ongoing["match_title"])
                team1 = str(ongoing["match_team1"])
                team2 = str(ongoing["match_team2"])
                url = str(ongoing["match_url"])
                stars = str(ongoing["match_stars"])

                msg += f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"[Match Page](" + url + ")"}\n\n'
        
        elif arg == "*":
            cnt = 0

            star_matches = star_filter(ongoings)
            for ongoing in star_matches:

                if cnt < 5:
                    cnt += 1
                else:
                    break

                event = str(ongoing["match_title"])
                team1 = str(ongoing["match_team1"])
                team2 = str(ongoing["match_team2"])
                url = str(ongoing["match_url"])
                stars = str(ongoing["match_stars"])

                msg += f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"[Match Page](" + url + ")"}\n\n'

        else:
            msg += "The given argument is not in right format. It should be number up to 5 or *"

    else:
        msg = "There's no ongoing match"

    await ctx.send(msg)

async def send_upcoming_matches(ctx, arg, matches):
    upcomings = []
    msg = ""

    for match in matches:
        if match["match_time"] != "ONGOING":
            upcomings.append(match)
    
    if upcomings:
        
        if arg is None or arg.isdecimal():
            cnt = 0
        
            if arg is None: arg = 5
            else : arg = int(arg)

            for upcoming in upcomings:

                if cnt < arg:
                    cnt += 1
                else:
                    break

                event = str(upcoming["match_title"])
                team1 = str(upcoming["match_team1"])
                team2 = str(upcoming["match_team2"])
                time = str(upcoming["match_time"])
                url = str(upcoming["match_url"])
                stars = str(upcoming["match_stars"])

                msg += f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"Start time (KST) : " + time}\n{"[Match Page](" + url + ")"}\n\n'
            
        elif arg == "*":
            cnt = 0

            star_matches = star_filter(upcomings)
            for upcoming in star_matches:

                if cnt < 5:
                    cnt += 1
                else:
                    break

                event = str(upcoming["match_title"])
                team1 = str(upcoming["match_team1"])
                team2 = str(upcoming["match_team2"])
                time = str(upcoming["match_time"])
                url = str(upcoming["match_url"])
                stars = str(upcoming["match_stars"])

                msg += f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"Start time (KST) : " + time}\n{"[Match Page](" + url + ")"}\n\n'
        
        else:
            msg += "The given argument is not in right format. It should be number up to 5 or *"

    else:
        msg += "There's no upcoming match"

    await ctx.send(msg)

async def send_matches(ctx, arg, matches):
    msg = ""

    if not matches:
        await ctx.send("There's no upcoming match")
        return

    if arg is None or arg.isdecimal():
        cnt = 0
        
        if arg is None: arg = 5
        else : arg = int(arg)

        for match in matches:

            if cnt < arg and cnt < 5:
                cnt += 1
            else:
                break

            event = str(match["match_title"])
            team1 = str(match["match_team1"])
            team2 = str(match["match_team2"])
            time = str(match["match_time"])
            url = str(match["match_url"])
            stars = str(match["match_stars"])

            msg += f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"Start time (KST) : " + time}\n{"[Match Page](" + url + ")"}\n\n'
    
    elif arg == "*":
        cnt = 0

        star_matches = star_filter(matches)
        
        for match in star_matches:

            if cnt < 5:
                cnt += 1
            else:
                break

            event = str(match["match_title"])
            team1 = str(match["match_team1"])
            team2 = str(match["match_team2"])
            time = str(match["match_time"])
            url = str(match["match_url"])
            stars = str(match["match_stars"])

            msg += f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"Start time (KST) : " + time}\n{"[Match Page](" + url + ")"}\n\n'
    
    else:
        msg += "The given argument is not in right format. It should be number up to 5 or *"
    
    await ctx.send(msg)

if __name__ == "__main__":
    print(crawl_matches())