import sqlite3
import os
import sys
import time
import datetime
import random

def force_follow(follower_id,following_id):
    #current timestamp UTC, format 2023-07-10 14:35:42.042890
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    #open db ../CRABBER_DATABASE.db
    conn = sqlite3.connect('../CRABBER_DATABASE.db')
    c = conn.cursor()

    #get latest id from following table, increment by 1
    c.execute("SELECT id FROM following ORDER BY id DESC LIMIT 1")
    id = c.fetchone()
    id = id[0] + 1

    #insert into following table id = id, follower_id = follower_id, following_id = following_id
    c.execute("INSERT INTO following VALUES (?, ?, ?)", (id, follower_id, following_id))

    #get latest id from notifications table, increment by 1
    c.execute("SELECT id FROM notification ORDER BY id DESC LIMIT 1")
    nid = c.fetchone()
    nid = nid[0] + 1

    #delete temp table if it exists
    c.execute("DROP TABLE IF EXISTS temp")

    #copy id 29 from notification table as an example and save to temp table
    c.execute("CREATE TABLE temp AS SELECT * FROM notification WHERE id=29")
    c.execute("UPDATE temp SET id=?, recipient_id=?, sender_id=?, type=?, timestamp=?", (nid, following_id, follower_id, 'follow', timestamp))

    #insert temp table into notification table
    c.execute("INSERT INTO notification SELECT * FROM temp")

    #delete temp table
    c.execute("DROP TABLE temp")
    
    #commit changes
    conn.commit()

    #close db
    conn.close()

    return

#example usage
#force_follow(6,4)
