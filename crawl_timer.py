import time
from hltv import match

async def crawl_timer(ctx):
    start_time = time.perf_counter()
    temp = match.crawl_matches()
    end_time = time.perf_counter()
    msg = f"pong!\nMatch crawling time : {int(round((end_time - start_time) * 1000))}ms"
    await ctx.send(msg)
    
if __name__ == "__main__":
    crawl_timer()