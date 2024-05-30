import discord
from discord.ext import commands, tasks

import hltv
import crawl_timer

import json
import random
import time

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

def timestamp(ctx):
    now = time
    print("[%s] %s requested %s" % (now.strftime('%m-%d %H:%M:%S'), ctx.message.author, ctx.message.content))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    article_reload.start()

@tasks.loop(minutes=3)
async def article_reload():
    global last_title
    new_article = hltv.article.crawl_article()
    now = time

    if new_article is None:
        print("[%s] Article returned NoneType" % now.strftime('%m-%d %H:%M:%S'))

    elif new_article == -1:
        print("[%s] Cloudflare block detected" % now.strftime('%m-%d %H:%M:%S'))
        
    elif new_article["article_title"] != last_title:
        print("[%s] New article detected - %s" % (now.strftime('%m-%d %H:%M:%S'), new_article["article_title"]))
        for guild in bot.guilds:
            for channel in guild.channels:
                if channel.id in boradcast_channels:
                    await hltv.article.broadcast_article(channel, new_article)
                    last_title = new_article["article_title"]
    
    else:
        print("[%s] There's no new article" % now.strftime('%m-%d %H:%M:%S'))

@bot.command()
async def ping(ctx):
    timestamp(ctx)
    await crawl_timer.crawl_timer(ctx)

@bot.command()
async def ongoing(ctx, arg: str = None):
    timestamp(ctx)
    match_infos = hltv.match.crawl_matches()
    await hltv.match.send_ongoing_matches(ctx, arg, match_infos)

@bot.command()
async def upcoming(ctx, arg: str = None):
    timestamp(ctx)
    match_infos = hltv.match.crawl_matches()
    await hltv.match.send_upcoming_matches(ctx, arg, match_infos)

@bot.command()
async def match(ctx, arg: str = None):
    timestamp(ctx)
    match_infos = hltv.match.crawl_matches()
    await hltv.match.send_matches(ctx, arg, match_infos)

@bot.command()
async def ranking(ctx, arg: str = None):
    timestamp(ctx)
    
    if arg is None:
        pages = hltv.ranking.return_rankings_nonetype()

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
                if page_idx < 5:
                    page_idx += 1
                    await msg.edit(embed = pages[page_idx])

            elif str(reaction) == '⏭':
                page_idx = 5
                await msg.edit(embed = pages[page_idx])

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout = 60.0, check = check)
                await msg.remove_reaction(reaction, user)
            except:
                break

        await msg.clear_reactions()

    
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