#manually add users to CRABBER_DATABASE.db sqlite

import sqlite3
import os
import sys
import time
import datetime
import random
import force_follow

#generate random username
def random_username():
    username = "guest"
    for i in range(0, 10):
        username += chr(random.randint(97, 122))
    return username

def generate_default_personality():
    #MBTI
    mbti = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']
    #randomly select one
    mbti = random.choice(mbti)

    #random enneagram (ex: 3w4)
    enneagram = str(random.randint(1,9)) + 'w' + str(random.randint(1,9))

    return f'npc MBTI: {mbti} Enneagram: {enneagram}'

def create_user(username=random_username(),displayname=random_username(),description=f'{generate_default_personality()}'):

    #connect to database
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get id #5 from table crab
    c.execute("SELECT * FROM crab WHERE id=5")
    print(c.fetchone())

    email = username + "@localhost.com"

    #get the latest id from table crab
    c.execute("SELECT id FROM crab ORDER BY id DESC LIMIT 1")
    latest_id = c.fetchone()[0]

    #drop temp table if it exists
    c.execute("DROP TABLE IF EXISTS temp")
    
    #create temp table
    c.execute("CREATE TABLE temp AS SELECT * FROM crab WHERE id=5")

    #random integer 1-5
    dpro = random.randint(1, 4)
    defaultprofilepic = f'/static/img/user_uploads/default{dpro}.png'

    defaultprofilepic = f'/static/img/user_uploads/{username}.png'

    #update temp table where id=5 to latest id + 1, set username and email
    c.execute("UPDATE temp SET id=?, username=?, email=?, display_name=?, avatar=?", (latest_id + 1, username, email, displayname,defaultprofilepic))

    #update description
    #todo consolidate this with the above update
    c.execute("UPDATE temp SET description=?", (description,))

    #print temp table
    print('DEBUG TEMP TABLE')
    c.execute("SELECT * FROM temp")
    print(c.fetchone())

    #insert temp table into crab table
    c.execute("INSERT INTO crab SELECT * FROM temp")

    #delete temp table
    c.execute("DROP TABLE temp")

    #commit changes
    conn.commit()

    print(f'new user created: @{username} {email}')

    #print the new user
    c.execute("SELECT * FROM crab WHERE id=?", (latest_id + 1,))
    print(c.fetchone())

    #get latest id from following table, increment by 1
    c.execute("SELECT id FROM following ORDER BY id DESC LIMIT 1")
    follower_latest_id = c.fetchone()[0] + 1

    #insert into following table id = follower_latest_id, follower_id = latest_id + 1, following_id = 4
    c.execute("INSERT INTO following VALUES (?, ?, ?)", (follower_latest_id, latest_id + 1, 4))

    #add notification
    #get latest id from notification table, increment by 1
    c.execute("SELECT id FROM notification ORDER BY id DESC LIMIT 1")
    notification_latest_id = c.fetchone()[0] + 1

    #current timestamp UTC, format 2023-07-10 14:35:42.042890
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    #copy id 29 from notification table as an example and save to temp table
    c.execute("CREATE TABLE temp AS SELECT * FROM notification WHERE id=29")
    # set id to notification_latest_id, set recipient_id to 4, sender_id to latest_id + 1, set type to follow, timestamp to current timestamp
    c.execute("UPDATE temp SET id=?, recipient_id=?, sender_id=?, type=?, timestamp=?", (notification_latest_id, 4, latest_id + 1, 'follow', timestamp))

    #insert temp table into notification table
    c.execute("INSERT INTO notification SELECT * FROM temp")

    #delete temp table
    c.execute("DROP TABLE temp")

    #commit changes
    conn.commit()
    
    #close db
    conn.close()