import re
import discord

def parse_ranking_all(ranking_soup):
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
        
def extract_infos(ranking):
    result_string = f'{"* " + ranking["rank_number"] + " **" + ranking["team_name"] + "** (" + ranking["rank_point"] + "p) [Team Profile](<" + ranking["team_link"] + ">)"}\n * '
    for cnt, player in enumerate(ranking["player_infos"]):
        result_string += f'{"[" + player["player_nick"] + "](<" + player["player_link"] + ">) "}'
        if cnt != 4: result_string += "| "
    result_string += "\n"

    return result_string

def rankings_nonetype(ranking_soup):
    pages = []
    ranking_cnt = 0

    rankings = parse_ranking_all(ranking_soup)
    
    for page_number in range(6):
        embed = discord.Embed(title = "HLTV RANKING", url = "https://hltv.org/ranking/teams", color = 0xFFF300)

        for idx in range(ranking_cnt, ranking_cnt + 5):
            rank_number = rankings[idx]["rank_number"]
            team_name = rankings[idx]["team_name"]
            rank_point = rankings[idx]["rank_point"]
            player_infos = rankings[idx]["player_infos"]

            field_name = rank_number + "  " + team_name + "  (" + rank_point + "p)"
            field_value = ""
            for cnt, player_info in enumerate(player_infos):
                field_value += player_info
                if cnt != 4: field_value += " • "

            embed.add_field(name = field_name, value = field_value, inline= False)
        
        page_str = "page " + str(page_number + 1) + "/6"
        embed.set_footer(text = page_str)

        pages.append(embed)
        ranking_cnt += 5

    return pages