import cloudscraper
import re
from bs4 import BeautifulSoup

def scrap_website(link):
    scraper = cloudscraper.create_scraper()
    res = scraper.get(link)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def crawl_ranking():
    HLTV_MAIN = 'http://hltv.org'
    HLTV_RANKING = 'http://hltv.org/ranking/teams'

    ranking_infos = []

    ranking_soup = scrap_website(HLTV_RANKING)
    rankings = ranking_soup.find_all("div", {"class" : "ranked-team standard-box"})
    
    for ranking in rankings:
        player_infos = []

        rank_number = ranking.find("span", {"class" : "position"}).string
        team_name = ranking.find("span", {"class" : "name"}).string
        rank_point = re.sub(r"[^0-9]", "", ranking.find("span", {"class" : "points"}).string)

        players = ranking.find_all("td", {"class" : "player-holder"})
        for player in players:
            player_nick = player.find("div", {"class" : "nick"}).contents[1]
            player_link = HLTV_MAIN + player.find("a").attrs["href"]
            player_infos.append({"player_nick" : player_nick, "player_link" : player_link})

        team_link = HLTV_MAIN + ranking.find("a", {"class" : "moreLink"}).attrs["href"]
        
        ranking_infos.append({"rank_number" : rank_number,
                              "team_name" : team_name,
                              "rank_point" : rank_point,
                              "player_infos" : player_infos,
                              "team_link" : team_link})
        
    return ranking_infos
        
def extract_infos(ranking):
    result_string = f'{"* " + ranking["rank_number"] + " **" + ranking["team_name"] + "** (" + ranking["rank_point"] + "p) [Team Profile](<" + ranking["team_link"] + ">)"}\n * '
    for cnt, player in enumerate(ranking["player_infos"]):
        result_string += f'{"[" + player["player_nick"] + "](<" + player["player_link"] + ">) "}'
        if cnt != 4: result_string += "| "
    result_string += "\n"

    return result_string

def check_arg_type(arg):
    if arg is None: return "none"
    elif isinstance(arg, str) and arg.isdigit():
        if int(arg) > 0 and int(arg) < 31: return "int_valid"
        else: return "int_invalid"
    elif isinstance(arg, str): 
        return "str"
    else: return "error"

async def send_rankings(ctx, arg):
    msg = "### HLTV RANKING\n"
    arg_type = check_arg_type(arg)

    if arg_type == "none":
        rankings = crawl_ranking()

        for cnt, ranking in enumerate(rankings):
            if cnt >= 5: break
            msg += extract_infos(ranking)

    await ctx.send(msg)
    return

if __name__ == "__main__":
    rankings = crawl_ranking()
    for ranking in rankings:
        print(extract_infos(ranking))