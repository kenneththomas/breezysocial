import ai_resources
import random
import sqlite3
import time
import poast
import datetime
import personality



def npctweet_v2(npcaccount,subject):

    gpttype = 'gpt-4o'

    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()


    forcesubject = True
    
    #current time
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    #get current time
    now = datetime.datetime.now()
    days = random.randint(0,365)
    hours = random.randint(0,23)
    minutes = random.randint(0,59)
    seconds = random.randint(0,59)
    microseconds = random.randint(0,999999)



    localtime = time.localtime()
    
    print(f'will tweet as {npcaccount} at {timestamp}')

    #get name, location, description of npc
    c.execute("SELECT display_name, location, description FROM crab WHERE username=?", (npcaccount,))
    npc = c.fetchone()
    name = npc[0]
    location = npc[1]
    description = npc[2]


    npcinfo = f'The time is {localtime} Name: {name} Bio: {description} Location: {location}.'

    if forcesubject:
        npcinfo = npcinfo + f'Post Subject: {subject}.'

    if npcaccount in personality.p:
        npcinfo = npcinfo + f' {personality.p[npcaccount]}'

    print(npcinfo)

    #get the latest molt id
    c.execute("SELECT id FROM molt ORDER BY id DESC LIMIT 1")
    molt_id = c.fetchone()
    molt_id = molt_id[0] + 1

    #get tweet from gpt
    tweetprompt = 'Generate a tweet roleplaying as the following. Do not use hashtags. Do not mention MBTI/Enneagram. Do not simply restate the prompt. Do not prepose the tweet with \"Just (x)\"'
    #tweetprompt = 'Roleplay as the following person and let me know your thoughts on the subject (1-3 sentences). Do not use hashtags. Do not mention MBTI/Enneagram. Do not start by saying who you are. Do not simply restate the prompt.'

    tweet = ai_resources.chatgpt([{"role": "system", "content": f"{tweetprompt}"},{"role": "user", "content": f"{npcinfo}"}],gpttype)

    #if tweet begins with a quotation, remove all quotation marks
    if tweet[0] == '\"':
        tweet = tweet.replace('\"','')

    #poast
    #poast.poast(npcaccount,tweet,timestamp)

    #close db
    conn.close()
    return tweet
