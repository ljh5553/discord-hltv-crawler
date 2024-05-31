import discord
from discord.ext import commands, tasks

import hltv
import crawl
import crawl_timer

import json
import random
import time
import traceback

import requests.exceptions
import urllib3.exceptions

main_soup = None
ranking_soup = None
news_soup = None
news_link = ""
last_title = ""
TOKEN = ""
boradcast_channels = []
timeout = 10

with open("config.json") as f:
    json_obj = json.load(f)
    TOKEN = json_obj["token"]
    boradcast_channels = json_obj["channels"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def timestamp(ctx):
    now = time
    print("[%s] %s requested %s" % (now.strftime('%m-%d %H:%M:%S'), ctx.message.author, ctx.message.content))

def printlog(msg):
    now = time
    print("[%s] %s" % (now.strftime('%m-%d %H:%M:%S'), msg))

async def send_unknownerror(ctx):
    await ctx.send("Unknown error occurred. Please try again")

async def multipage_embed(ctx, pages):
    if pages is None:
        await ctx.send("Invalid parameter. Please try again")
        return
    
    if isinstance(pages, discord.Embed):
        await ctx.send(embed = pages)
        return
    
    pages_len = len(pages)

    msg = await ctx.send(embed = pages[0])
    await msg.add_reaction('⏮')
    await msg.add_reaction('◀')
    await msg.add_reaction('▶')
    await msg.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author
    
    page_idx = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            page_idx = 0
            await msg.edit(embed = pages[page_idx])

        elif str(reaction) == '◀':
            if page_idx > 0:
                page_idx -= 1
                await msg.edit(embed = pages[page_idx])
                
        elif str(reaction) == '▶':
            if page_idx < (pages_len - 1):
                page_idx += 1
                await msg.edit(embed = pages[page_idx])

        elif str(reaction) == '⏭':
            page_idx = (pages_len - 1)
            await msg.edit(embed = pages[page_idx])

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout = 60.0, check = check)
            await msg.remove_reaction(reaction, user)
        except:
            break

    await msg.clear_reactions()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    crawl_hltv.start()
    crawl_ranking.start()
    article_reload.start()

@tasks.loop(minutes = 3)
async def crawl_hltv():
    global main_soup
    global news_soup
    global news_link
    HLTV_MAIN = "http://hltv.org"

    try:
        main_soup = crawl.crawling.scrap_website(HLTV_MAIN, timeout)
        news_link = crawl.crawling.parse_newsdetail(main_soup, HLTV_MAIN)
        news_soup = crawl.crawling.scrap_website(news_link, timeout)
        printlog("Successfully crawled main page")
        crawl_hltv.change_interval(minutes = 3)
    except AttributeError:
        printlog("Exception AttributeError occurred while crawling main pages. Retrying in 3 min...")
    except crawl.crawling.CloudflareException:
        printlog("Exception CloudflareException occurred while crawling main pages. Retrying in 5 min...")
        crawl_hltv.change_interval(minutes = 5)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, urllib3.exceptions.ReadTimeoutError, urllib3.exceptions.TimeoutError, TimeoutError):
        printlog("Connection timeout occurred while crawling main pages. Retrying in 3 min...")
    except:
        printlog("Exception occurred while crawling main pages. Retrying in 3 min...")
        traceback.print_exc()

@tasks.loop(hours = 6)
async def crawl_ranking():
    global ranking_soup
    HLTV_RANKING = "http://hltv.org/ranking/teams"

    try:
        ranking_soup = crawl.crawling.scrap_website(HLTV_RANKING, timeout)
        printlog("Successfully crawled ranking page")
        crawl_ranking.change_interval(hours = 6)
    except AttributeError:
        printlog("Exception AttributeError occurred while crawling ranking pages. Retrying in 3 min...")
        crawl_ranking.change_interval(minutes = 3)
    except crawl.crawling.CloudflareException:
        printlog("Exception CloudflareException occurred while crawling ranking pages. Retrying in 5 min...")
        crawl_ranking.change_interval(minutes = 5)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, urllib3.exceptions.ReadTimeoutError, urllib3.exceptions.TimeoutError, TimeoutError):
        printlog("Connection timeout occurred while crawling ranking pages. Retrying in 3 min...")
        crawl_ranking.change_interval(minutes = 3)
    except:
        printlog("Exception occurred while crawling ranking pages. Retrying in 3 min...")
        crawl_ranking.change_interval(minutes = 3)
        traceback.print_exc()

@tasks.loop(minutes = 3)
async def article_reload():
    global last_title
    try:
        new_article = hltv.article.parse_news(news_soup)

        if new_article["article_title"] != last_title:
            printlog("New article - %s" % new_article["article_title"])
            for guild in bot.guilds:
                for channel in guild.channels:
                    if channel.id in boradcast_channels:
                        await hltv.article.broadcast_article(channel, new_article, news_link)
                        last_title = new_article["article_title"]
    except AttributeError:
        printlog("Exception AttributeError occurred while reloading article")
    except UnboundLocalError:
        printlog("Exception UnboundLocalError occurred while reloading article")
    except:
        printlog("Exception occurred while reloading article")

@bot.command()
async def ping(ctx):
    timestamp(ctx)
    await crawl_timer.crawl_timer(ctx)

@bot.command(aliases = ["ongoing", "upcoming"])
async def match(ctx, arg: str = None):
    timestamp(ctx)
    try:
        match_infos = hltv.match.parse_matches(main_soup)
        pages = hltv.match.get_matches(match_infos, ctx.invoked_with, arg)
        await multipage_embed(ctx, pages)
    except AttributeError:
        printlog("Exception AttributeError occurred while loading matches")
        await send_unknownerror(ctx)
    except UnboundLocalError:
        printlog("Exception UnboundLocalError occurred while loading matches")
        await send_unknownerror(ctx)
    except:
        printlog("Exception occurred while loading matches")
        traceback.print_exc()
        await send_unknownerror(ctx)

@bot.command()
async def ranking(ctx, arg: str = None):
    timestamp(ctx)
    try:
        ranking_infos = hltv.ranking.parse_rankings(ranking_soup)
        pages = hltv.ranking.get_rankings(ranking_infos, arg)
        await multipage_embed(ctx, pages)
    except AttributeError:
        printlog("Exception AttributeError occurred while loading rankings")
        await send_unknownerror(ctx)

@bot.command()
async def choose(ctx, *choices: str):
    timestamp(ctx)
    await ctx.send(random.choice(choices))

@bot.command()
async def faze(ctx):
    timestamp(ctx)
    await ctx.send(file=discord.File("faze.png"))

@bot.command()
async def github(ctx):
    timestamp(ctx)
    await ctx.send("github : https://github.com/ljh5553/discord-hltv-crawler")

bot.run(TOKEN)