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
    matches = matches_div.find_all("a", {"class" : "hotmatch-box a-reset"})

    for match in matches:

        hltv_re = re.compile(r"HLTV")

        title_temp = match.attrs["title"]
        if hltv_re.search(title_temp):
            title_temp_list = title_temp.split("-")
            del title_temp_list[0]
            title = "-".join(title_temp_list).strip()
        else:
            title = title_temp
            
        
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

def extract_infos(match, time_flag : bool):
    if time_flag:
        event = str(match["match_title"])
        team1 = str(match["match_team1"])
        team2 = str(match["match_team2"])
        time = str(match["match_time"])
        url = str(match["match_url"])
        stars = str(match["match_stars"])

        return f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"Start time (KST) : " + time}\n{"[Match Page](" + url + ")"}\n\n'

    else:
        event = str(match["match_title"])
        team1 = str(match["match_team1"])
        team2 = str(match["match_team2"])
        url = str(match["match_url"])
        stars = str(match["match_stars"])

        return f'{"**" + event + "**"}\n{"* " + team1 + " vs. " + team2 + " " + stars}\n{"[Match Page](" + url + ")"}\n\n'

def check_arg_type(arg):
    if arg is None: return "none"
    elif isinstance(arg, str) and arg.isdigit():
        if int(arg) > 0 and int(arg) < 6: return "int_valid"
        else: return "int_invalid"
    elif arg == "*": return "*"
    elif isinstance(arg, str): 
        return "str"
    else: return "error"

async def send_ongoing_matches(ctx, arg, matches):
    ongoings = []
    msg = ""
    arg_type = check_arg_type(arg)

    for match in matches:
        if match["match_time"] == "ONGOING":
            ongoings.append(match)
    
    if not ongoings:
        msg = "There's no ongoing match"
        await ctx.send(msg)
        return

    if arg_type == "none" or arg_type == "int_valid":

        if arg is None: arg = 5
        else : arg = int(arg)

        for cnt, ongoing in enumerate(ongoings):
            if cnt >= arg: break
            msg += extract_infos(ongoing, False)

        await ctx.send(msg)
        return
    
    elif arg_type == "*":

        star_matches = star_filter(ongoings)

        for cnt, ongoing in enumerate(star_matches):
            if cnt >= 5: break
            msg += extract_infos(ongoing, False)
        
        await ctx.send(msg)
        return
    
    else:
        msg = "The given argument is not in right format. It should be number up to 5 or *"
        await ctx.send(msg)
        return

async def send_upcoming_matches(ctx, arg, matches):
    upcomings = []
    msg = ""
    arg_type = check_arg_type(arg)

    for match in matches:
        if match["match_time"] != "ONGOING":
            upcomings.append(match)
    
    if not upcomings:
        msg = "There's no upcoming match"
        await ctx.send(msg)
        return
        
    if arg_type == "none" or arg_type == "int_valid":

        if arg is None: arg = 5
        else : arg = int(arg)

        for cnt, upcoming in enumerate(upcomings):
            if cnt >= arg: break
            msg += extract_infos(upcoming, True)

        await ctx.send(msg)
        return
        
    elif arg_type == "*":

        star_matches = star_filter(upcomings)

        for cnt, upcoming in enumerate(star_matches):
            if cnt >= 5: break
            msg += extract_infos(upcoming, True)

        await ctx.send(msg)
        return
    
    else:
        msg = "The given argument is not in right format. It should be number up to 5 or *"
        await ctx.send(msg)
        return

async def send_matches(ctx, arg, matches):
    msg = ""
    arg_type = check_arg_type(arg)

    if not matches:
        msg = "There's no upcoming match"
        await ctx.send(msg)
        return

    if arg_type == "none" or arg_type == "int_valid":
 
        if arg is None: arg = 5
        else : arg = int(arg)

        for cnt, match in enumerate(matches):
            if cnt >= arg: break
            msg += extract_infos(match, True)

        await ctx.send(msg)
        return
    
    elif arg_type == "*":
        star_matches = star_filter(matches)
        
        for cnt, match in enumerate(star_matches):

            if cnt >= 5: break
            msg += extract_infos(match, True)
        
        await ctx.send(msg)
        return
    
    else:
        msg = "The given argument is not in right format. It should be number up to 5 or *"
        await ctx.send(msg)
        return

if __name__ == "__main__":
    print(crawl_matches())