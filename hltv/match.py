import datetime
import discord
import re

def parse_matches(main_soup):
    match_infos = []
    matches = main_soup.find_all("a", {"class" : "hotmatch-box a-reset"})

    hltv_re = re.compile(r"HLTV|playing")

    for match in matches:
        hltv_re = re.compile(r"HLTV|playing")
        hltvconfirmed_re = re.compile(r"hltv-confirmed")

        if hltvconfirmed_re.search(match.attrs["href"]):
            continue

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
        
        time = "ongoing"
        time_div = match.find("div", {"class" : "middleExtra"})
        if time_div:
            unixtime = time_div.attrs["data-unix"]
            time = datetime.datetime.fromtimestamp(int(unixtime) // 1000).strftime('%m/%d %H:%M')
        
        url = "https://hltv.org" + match.attrs["href"]

        stars_div = match.find("div", {"class" : re.compile(r'^teambox match')})
        stars_n = int(stars_div.attrs["stars"])
        stars = ""
        if stars_n != 0:
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
        if "*" in str(match["match_stars"]):
            only_stars.append(match)
    return only_stars

def ongoing_filter(matches):
    ongoings = []
    for match in matches:
        if match["match_time"] == "ongoing":
            ongoings.append(match)
    return ongoings

def upcoming_filter(matches):
    upcomings = []
    for match in matches:
        if match["match_time"] != "ongoing":
            upcomings.append(match)
    return upcomings

def search_filter(matches, arg):
    search_results = []
    arg_re = re.compile(arg, re.IGNORECASE)
    for match in matches:
        if arg_re.search(match["match_title"]) or arg_re.search(match["match_team1"]) or arg_re.search(match["match_team2"]):
            search_results.append(match)
    return search_results

def modify_length(matches, num):
    if len(matches) <= num or num <= 0: return matches
    return matches[:num]

def check_cmdtype(cmdtype, match_infos):
    embed_infos = {}

    if cmdtype == "match":
        embed_infos["title"] = "CS2 Matches"
        embed_infos["desc"] = "Ongoing and upcoming CS2 matches from HLTV.org"
        embed_infos["color"] = 0xffffff
    
    elif cmdtype == "ongoing":
        embed_infos["title"] = "Ongoing CS2 Matches"
        embed_infos["desc"] = "Ongoing CS2 matches from HLTV.org"
        embed_infos["color"] = 0x00ddff
        match_infos = ongoing_filter(match_infos)

    elif cmdtype == "upcoming":
        embed_infos["title"] = "Upcoming CS2 Matches"
        embed_infos["desc"] = "Upcoming CS2 matches from HLTV.org"
        embed_infos["color"] = 0xb7ff00
        match_infos = upcoming_filter(match_infos)

    return embed_infos, match_infos

def emptylist(embed_infos):
    embed = discord.Embed(title = embed_infos["title"], description = embed_infos["desc"], url = "https://www.hltv.org/matches", color = embed_infos["color"])
    embed.add_field(name = "No match was found for the conditions", value = "", inline = False)
    return embed
    
def get_matches(match_infos, cmdtype : str, arg = None):
    pages = []
    embed_infos = {}
    matches_cnt = 0

    embed_infos, match_infos = check_cmdtype(cmdtype, match_infos)

    if arg is None : pass
    elif arg.isdigit() : match_infos = modify_length(match_infos, int(arg))
    elif arg == "*" : match_infos = star_filter(match_infos)
    elif arg.isalnum() : match_infos = search_filter(match_infos, arg)
    else : return None

    if not match_infos:
        return emptylist(embed_infos)

    match_infos_len = len(match_infos)
    pages_len = ((match_infos_len - 1) // 5) + 1

    for page_number in range(pages_len):
        embed = discord.Embed(title = embed_infos["title"], description = embed_infos["desc"], url = "https://www.hltv.org/matches", color = embed_infos["color"])
 
        for idx in range(matches_cnt, matches_cnt + 5):
            if idx >= match_infos_len: break
            
            title = match_infos[idx]["match_title"]
            team1 = match_infos[idx]["match_team1"]
            team2 = match_infos[idx]["match_team2"]
            time = match_infos[idx]["match_time"]
            url = match_infos[idx]["match_url"]
            stars = match_infos[idx]["match_stars"]

            field_name = "%s %s vs. %s - %s" % (stars, team1, team2, title)
            field_value = "%s - [%s](%s)" % (time,"Matchpage", url)

            embed.add_field(name = field_name, value = field_value, inline = False)
        
        now = datetime.datetime.now()
        page_str = "page %s/%s - updated %s" % (str(page_number + 1), pages_len, now.strftime('%m/%d %H:%M'))
        embed.set_footer(text = page_str)

        pages.append(embed)
        matches_cnt += 5
    
    return pages