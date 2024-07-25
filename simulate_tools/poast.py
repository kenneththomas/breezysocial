import sqlite3
import os
import sys
import time
import datetime
import random

def poast(username, content, timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),reply=False):

    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get id from table crab where username=username
    c.execute("SELECT id FROM crab WHERE username=?", (username,))
    user_id = c.fetchone()
    user_id = user_id[0]

    #get latest id from poasts table, increment by 1
    c.execute("SELECT id FROM molt ORDER BY id DESC LIMIT 1")
    id = c.fetchone()
    id = id[0] + 1

    #delete temp table if it exists
    c.execute("DROP TABLE IF EXISTS temp")

    #copy id 29 from table molts as an example and save to temp table
    c.execute("CREATE TABLE temp AS SELECT * FROM molt WHERE id=29")

    source = 'BreezySocial iOS'

    #update temp table where id=29 to id = id, user_id = user_id, content = content, timestamp = timestamp
    c.execute("UPDATE temp SET id=?, author_id=?, content=?, timestamp=?, source=?", (id, user_id, content, timestamp, source))

    #if reply is an integer, update temp table is_reply = 1 and original_molt_id = reply
    if int(reply):
        print('DEBUG: detected reply')
        c.execute("UPDATE temp SET is_reply=1, original_molt_id=? WHERE id=?", (reply, id))

    #insert temp table into poasts table
    c.execute("INSERT INTO molt SELECT * FROM temp")

    #delete temp table
    c.execute("DROP TABLE temp")

    #commit changes
    conn.commit()

    #close db
    conn.close()

    print(f'poast {id} from {username} at {timestamp} with content {content}')

    return id

#example usage
#poast('caoimhe', 'my first poast!')

def like_poast(username, poast_id):

    #current timestamp UTC, format 2023-07-10 14:35:42.042890
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get user_id from table crab where username=username
    c.execute("SELECT id FROM crab WHERE username=?", (username,))
    user_id = c.fetchone()
    user_id = user_id[0]

    #get latest id from likes table, increment by 1
    c.execute("SELECT id FROM like ORDER BY id DESC LIMIT 1")
    id = c.fetchone()
    id = id[0] + 1

    #add to table likes id = id, crab_id = user_id, molt_id = poast_id
    c.execute("INSERT INTO like VALUES (?, ?, ?)", (id, user_id, poast_id))


    #get latest id from notifications table, increment by 1
    c.execute("SELECT id FROM notification ORDER BY id DESC LIMIT 1")
    nid = c.fetchone()
    nid = nid[0] + 1

    # get poast author id
    c.execute("SELECT author_id FROM molt WHERE id=?", (poast_id,))
    poast_author_id = int(c.fetchone()[0])

    #delete temp table if it exists
    c.execute("DROP TABLE IF EXISTS temp")

    #copy id 8 from notification table as an example and save to temp table
    c.execute("CREATE TABLE temp AS SELECT * FROM notification WHERE id=8")

    #update temp table where id=8 to id = nid, recipient_id = user_id, sender_id = user_id, type = like, timestamp = timestamp
    c.execute("UPDATE temp SET id=?, recipient_id=?, sender_id=?, type=?, timestamp=?, molt_id=?", (nid, poast_author_id, user_id, 'like', timestamp, poast_id))

    #insert temp table into notification table
    c.execute("INSERT INTO notification SELECT * FROM temp")

    #delete temp table
    c.execute("DROP TABLE temp")

    #commit changes
    conn.commit()

    #close db
    conn.close()

def get_latest_id(cursor, table):
    cursor.execute(f"SELECT id FROM {table} ORDER BY id DESC LIMIT 1")
    latest_id = cursor.fetchone()[0]
    return latest_id

def get_next_id(cursor,table):
    latest_id = get_latest_id(cursor,table)
    next_id = latest_id + 1
    return next_id

def name_to_id(cursor,username):
    cursor.execute("SELECT id FROM crab WHERE username=?", (username,))
    user_id = cursor.fetchone()
    user_id = user_id[0]
    return user_id

def id_to_name(cursor,user_id):
    cursor.execute("SELECT username FROM crab WHERE id=?", (user_id,))
    username = cursor.fetchone()
    username = username[0]
    return username

def follow(cursor,sourceuser,targetuser):
    #get latest id from following table, increment by 1
    next_id = get_next_id(cursor,'following')
    
    #get sourceuser id
    sourceuser_id = name_to_id(cursor,sourceuser)

    #get targetuser id
    targetuser_id = name_to_id(cursor,targetuser)

    #insert into following table id = next_id, follower_id = sourceuser_id, following_id = targetuser_id
    cursor.execute("INSERT INTO following VALUES (?, ?, ?)", (next_id, sourceuser_id, targetuser_id))

    #get latest id from notifications table, increment by 1
    nid = get_next_id(cursor,'notification')

    #current timestamp UTC, format 2023-07-10 14:35:42.042890
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    #delete temp table if it exists
    cursor.execute("DROP TABLE IF EXISTS temp")

    #copy id 2 from notification table as an example and save to temp table
    cursor.execute("CREATE TABLE temp AS SELECT * FROM notification WHERE id=2")

    #update temp table where id=2 to id = nid, recipient_id = targetuser_id, sender_id = sourceuser_id, type = follow, timestamp = timestamp
    cursor.execute("UPDATE temp SET id=?, recipient_id=?, sender_id=?, type=?, timestamp=?", (nid, targetuser_id, sourceuser_id, 'follow', timestamp))

    #insert temp table into notification table
    cursor.execute("INSERT INTO notification SELECT * FROM temp")

    #delete temp table
    cursor.execute("DROP TABLE temp")

    return True

def test_follow():
    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    follow(c,'caoimhe','snowdays')

    #commit changes
    conn.commit()

    #close db
    conn.close()

def unfollow(cursor,sourceuser,targetuser):
    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get sourceuser id
    sourceuser_id = name_to_id(cursor,sourceuser)

    #get targetuser id
    targetuser_id = name_to_id(cursor,targetuser)

    #delete from following table where follower_id = sourceuser_id and following_id = targetuser_id
    cursor.execute("DELETE FROM following WHERE follower_id=? AND following_id=?", (sourceuser_id, targetuser_id))

    return True

def verify_user(username):
    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #update crab table set verified = 1 where username = username
    c.execute("UPDATE crab SET verified=1 WHERE username=?", (username,))

    #commit changes
    conn.commit()

    #close db
    conn.close()

    #post from seto
    poast('seto',f'@{username} is now verified.')

    return True

#get profile picture from crab table
def get_profile_picture(username):
    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get profile picture from crab table
    c.execute("SELECT avatar FROM crab WHERE username=?", (username,))
    profile_picture = c.fetchone()
    profile_picture = profile_picture[0]

    #close db
    conn.close()

    return profile_picture

# get python list of all usernames
def get_all_users():
    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get all usernames from crab table
    c.execute("SELECT username FROM crab")
    usernames = c.fetchall()
    usernames = [i[0] for i in usernames]

    #close db
    conn.close()

    return usernames
    