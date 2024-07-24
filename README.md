# Discord HLTV crawler
Discord bot for getting match, ranking, news from [HLTV.org](HLTV.org)

---

# Index
1. Structure of the project
2. Requested libraries & dependencies
3. How to install & run
4. FAQ

---

## 1. Structure of the project
 The project is written in python 3.12.3 or higher. I not guaruntee proper running on lower version of python.

 There are 3 big parts in this project. Python code **main.py** is the main access point of the program. This file contains core bot features like initializing bot, commands of the bot etc. Folder **crawl** contains webpage crwaling code using by cloudscraper and basic parsing code using by beautifulsoup. This folder(although it has only one file yet) gets HLTV.org's main and ranking pages and send over to main.py. Folder **hltv** contains python codes which parse actual information to corresponding user's command. It parses useful information on pre-crwaled page and filters parsed data by user's request.

 When you running the program, it brings personal settings in **config.json**. **config.json** has basic bot information like bot token and channels to be broadcast news. Then, the program initializes bot's settings and becomes online status. For every 3 minutes and 6 hours, bot crawls HLTV's main page and ranking page, and save HTML data on its memory. When bot find that news' title is different from pre-saved title, it replaces the title to new one and send news' information to all configured chatting servers. If user requests some information via command, program will call corresponding function from **hltv**. Code identifies parameter of the command and parsing data from pre-saved HLTV's main page and send results to chatting channel. This is a rough sketch how this project works.

## 2. Requested libraries & dependencies
 This program using [Discord.py](https://github.com/Rapptz/discord.py), [cloudscraper](https://github.com/VeNoMouS/cloudscraper), [BeautifulSoup](https://github.com/wention/BeautifulSoup4).

## 3. How to install & run

## 4. FAQ

 > Q. Program is dead while running.
 >
 >A. There is a critical flaw by HTTP connection pool exception. It occurs when you run this bot for long time(i estimate it is about 5 days). I really did a lot of googling to fix this. But i am sorry, i am too shit to fix this error.