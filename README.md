# Discord HLTV crawler
Discord bot for getting match, ranking, news from [HLTV.org](https://HLTV.org)

---

# Index
1. Structure of the project
2. Requested libraries
3. How to install & run
4. Features & Commands
5. FAQ
---

## 1. Structure of the project
 The project is written in python 3.12.3 or higher. I not guaruntee proper running on lower version of python.

 There are 3 big parts in this project. Python code **main.py** is the main access point of the program. This file contains core bot features like initializing bot, commands of the bot etc. Folder **crawl** contains webpage crwaling code using by cloudscraper and basic parsing code using by beautifulsoup. This folder(although it has only one file yet) gets HLTV.org's main and ranking pages and send over to main.py. Folder **hltv** contains python codes which parse actual information to corresponding user's command. It parses useful information on pre-crwaled page and filters parsed data by user's request.

 When you running the program, it brings personal settings in **config.json**. **config.json** has basic bot information like bot token and channels to be broadcast news. Then, the program initializes bot's settings and becomes online status. For every 3 minutes and 6 hours, bot crawls HLTV's main page and ranking page, and store HTML data on its memory. When bot find that news' title is different from pre-saved title, it replaces the title to new one and send news' information to all configured chatting servers. If user requests some information via command, program will call corresponding function from **hltv**. Code identifies parameter of the command and parsing data from pre-saved HLTV's main page and send results to chatting channel. This is a rough sketch how this project works.

## 2. Required libraries
 This program is using [Discord.py](https://github.com/Rapptz/discord.py), [requests](https://github.com/psf/requests), [cloudscraper](https://github.com/VeNoMouS/cloudscraper), [BeautifulSoup](https://github.com/wention/BeautifulSoup4).

## 3. How to install & run
 To run this bot on your own environment, i recommend having your own server to service 24/7. I run bot on Raspberry Pi 4b and it has no problem to deal with it.

 You need to create and set your bot on discord developer portal. Here's [short tutorial of discord offical document](https://discord.com/developers/docs/quick-start/getting-started#step-1-creating-an-app). At *Adding scopes and bot permissions* part, check **Administrator** in General permissions.

 1. Download source code from [here](https://github.com/ljh5553/discord-hltv-crawler/releases).
 2. Set your bot's token in **config.json**.
 3. Download requested libraries by ```pip install discord.py requests cloudscraper beautifulsoup4``` in cmd
 4. Go to project's root folder and run ```python main.py```
 5. Done! If you want to set auto news broadcasting, type ```!newschannel``` in chat. It will automatically add the channel as news broadcasting.
 
## 4. Features & Commands
 The bot automatically sends news information on pre-selected channel. And provide match and ranking information to user's request by command.

 * ```!ping```
    
    Returns time elapsed to crawl HLTV's main page

 * ```!match [ * | team name | event name | integer ]```
    
    Returns all match information. Parameter * filters HLTV recommend matches only. Parameter one word searches name of the team or event. Parameter integer limits search result.

 * ```!ongoing [ * | team name | event name | integer ]```
    
    Returns ongoing match information. Parameter * filters HLTV recommend matches only. Parameter one word searches name of the team or event. Parameter integer limits search result.

 * ```!upcoming [ * | team name | event name | integer ]```
    
    Returns upcoming match information. Parameter * filters HLTV recommend matches only. Parameter one word searches name of the team or event. Parameter integer limits search result.

 * ```!ranking [ team name | player name | integer ]```
    
    Returns HLTV ranking information. Parameter one word searches name of the event or player. Parameter integer limits search result.

 * ```!newschannel```
    
    Set or remove the channel as news broadcasting channel. If HLTV has new article, bot detects and sends news' information to all broadcasting channels.

 * ```!choose [ option1 (option2 option3 ...) ]```
    
    Select one of options randomly.

 * ```!faze```
    
    Returns FaZe team logo image.

 * ```!github```
    
    Returns bot's github link.

## 5. FAQ

 > Q. Program is dead while running.
 >
 > A. There is a critical flaw by HTTP connection pool exception. It occurs when you run this bot for long time(i estimate it is about 5 days). I really did lots of googling to fix this. But i am sorry, i am too shit to fix this error. I suggest you to restart regularly by using scheduler.
