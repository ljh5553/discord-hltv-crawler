import discord
from discord.ext import commands, tasks

import hltv
import crawl_timer

import json
import random

last_title = ""
TOKEN = ""
boradcast_channels = []

with open("config.json") as f:

    json_obj = json.load(f)
    TOKEN = json_obj["token"]
    boradcast_channels = json_obj["channels"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    article_reload.start()

@tasks.loop(minutes=1)
async def article_reload():
    global last_title
    new_article = hltv.article.crawl_article()

    if new_article["article_title"] != last_title:
        print("NEW ARTICLE DETECTED. - %s" % new_article["article_title"])
        for guild in bot.guilds:
            for channel in guild.channels:
                if channel.id in boradcast_channels:
                    await hltv.article.broadcast_article(channel, new_article)
                    last_title = new_article["article_title"]
    
    else:
        print("THERE'S NO NEW ARTICLE")

@bot.command()
async def ping(ctx):
    await crawl_timer.crawl_timer(ctx)

@bot.command()
async def ongoing(ctx, arg: str = None):
    match_infos = hltv.match.crawl_matches()
    await hltv.match.send_ongoing_matches(ctx, arg, match_infos)

@bot.command()
async def upcoming(ctx, arg: str = None):
    match_infos = hltv.match.crawl_matches()
    await hltv.match.send_upcoming_matches(ctx, arg, match_infos)

@bot.command()
async def match(ctx, arg: str = None):
    match_infos = hltv.match.crawl_matches()
    await hltv.match.send_matches(ctx, arg, match_infos)

@bot.command()
async def choose(ctx, *choices: str):
    await ctx.send(random.choice(choices))

@bot.command()
async def faze(ctx):
    await ctx.send(file=discord.File("faze.png"))

@bot.command()
async def github(ctx):
    await ctx.send("github : https://github.com/ljh5553/discord-hltv-crawler")

bot.run(TOKEN)