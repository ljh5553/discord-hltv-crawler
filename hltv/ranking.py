import re
import discord
import datetime

def parse_rankings(ranking_soup):
    ranking_infos = []
    rankings = ranking_soup.find_all("div", {"class" : "ranked-team standard-box"})
    
    for ranking in rankings:
        player_infos = []

        rank_number = ranking.find("span", {"class" : "position"}).string
        team_name = ranking.find("span", {"class" : "name"}).string
        rank_point = re.sub(r"[^0-9]", "", ranking.find("span", {"class" : "points"}).string)

        players = ranking.find_all("td", {"class" : "player-holder"})
        for player in players:
            player_nick = player.find("div", {"class" : "nick"}).contents[1]
            player_infos.append(player_nick)

        ranking_infos.append({"rank_number" : rank_number,
                              "team_name" : team_name,
                              "rank_point" : rank_point,
                              "player_infos" : player_infos})
        
    return ranking_infos

def search_filter(rankings, arg):
    search_results = []
    arg_re = re.compile(arg, re.IGNORECASE)
    for ranking in rankings:
        if arg_re.search(ranking["team_name"]):
            search_results.append(ranking)
            continue
        for player_nick in ranking["player_infos"]:
            if arg_re.search(player_nick):
                search_results.append(ranking)
                break
    return search_results

def modify_length(rankings, arg):
    if isinstance(arg, int):
        if len(rankings) <= arg or arg <= 0 : return rankings
        return rankings[:arg]
    
    start, end = list(map(int, arg.split("~")))
    if start <= 0 or end >= len(rankings) : return rankings
    return rankings[(start - 1):end]

def emptylist(embed_infos):
    embed = discord.Embed(title = embed_infos["title"], url = "https://hltv.org/ranking/teams", color = embed_infos["color"])
    embed.add_field(name = "No ranking information was found for the conditions", value = "", inline = False)
    return embed

def get_rankings(ranking_infos, arg = None):
    pages = []
    embed_infos = {}
    ranking_cnt = 0

    if arg is None : pass
    elif re.search(r'^[0-9]+~[0-9]+$', arg): ranking_infos = modify_length(ranking_infos, arg)
    elif arg.isdigit() : ranking_infos = modify_length(ranking_infos, int(arg))
    elif arg.isalnum() : ranking_infos = search_filter(ranking_infos, arg)
    else : return None

    embed_infos["title"] = "HLTV RANKING"
    embed_infos["color"] = 0xFFF300

    if not ranking_infos:
        return emptylist(embed_infos)
    
    ranking_infos_len = len(ranking_infos)
    pages_len = ((ranking_infos_len - 1) // 5) + 1

    for page_number in range(pages_len):
        embed = discord.Embed(title = embed_infos["title"], url = "https://hltv.org/ranking/teams", color = embed_infos["color"])

        for idx in range(ranking_cnt, ranking_cnt + 5):
            if idx >= ranking_infos_len: break

            rank_number = ranking_infos[idx]["rank_number"]
            team_name = ranking_infos[idx]["team_name"]
            rank_point = ranking_infos[idx]["rank_point"]
            player_infos = ranking_infos[idx]["player_infos"]

            field_name = "%s %s (%sp)" % (rank_number, team_name, rank_point)
            field_value = ""
            player_infos_len = len(player_infos)
            for cnt, player_info in enumerate(player_infos):
                field_value += player_info
                if cnt != (player_infos_len - 1) : field_value += " • "

            embed.add_field(name = field_name, value = field_value, inline= False)
        
        now = datetime.datetime.now()
        page_str = "page %s/%s - updated %s" % (str(page_number + 1), pages_len, now.strftime('%m/%d %H:%M'))
        embed.set_footer(text = page_str)

        pages.append(embed)
        ranking_cnt += 5

    return pages