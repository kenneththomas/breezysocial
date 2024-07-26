from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
import os
import datetime
import random
import sqlite3
import time
sys.path.append('../')
sys.path.append('../simulate_tools')
import mt_tweet
from simulate_tools.poast import poast, get_profile_picture, get_all_users, like_poast, verify_user

app = Flask(__name__, static_folder='../../static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////CRABBER_DATABASE.db'
app.config['SECRET_KEY'] = 'replace-with-a-secure-random-key'
app.config['SESSION_COOKIE_NAME'] = 'admin_session'
db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    latest_tweet = None
    profile_picture = None
    username = None  # Initialize username
    postid = None
    likes = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        tweet = request.form.get('tweet')
        replyid = request.form.get('reply_id')
        likes = request.form.get('likes')
        isreply = False
        # if replyid is int, then set isreply to replyid
        if replyid.isdigit():
            isreply = replyid

        #use gpt to generate the tweet
        gpt_toggle = request.form.get('gpt_toggle')
        if gpt_toggle:
            print("Checkbox is checked")
            tweet = mt_tweet.npctweet_v2(username, tweet)
        
        postid = poast(username, tweet, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%m:%S.%f"), isreply)
        flash("Tweet posted!")
        # if likes is int, then like the post
        if likes.isdigit():
            like_resource(username, postid, int(likes))
        # Get profile picture
        profile_picture = get_profile_picture(username)
        print('debug profile_picture', profile_picture)
        latest_tweet = tweet

    return render_template('index.html', latest_tweet=latest_tweet, profile_picture=profile_picture, username=username, postid=postid)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        display_name = request.form.get('display_name')
        bio = request.form.get('bio')
        avatar_url = request.form.get('avatar_url')
        verify_account = request.form.get('verify_account')
        
        print(f'username: {username} display_name: {display_name} bio: {bio} avatar_url: {avatar_url}')

        create_user(username, display_name, bio, avatar_url)
        
        if verify_account == 'on':
            verify_user(username)

        return render_template('create_account.html', username=username, display_name=display_name, bio=bio, avatar_url=avatar_url)

    return render_template('create_account.html')  # Render account creation page if method is GET.


def create_user(username,displayname,description, avatar_url=None):

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

    if avatar_url:
        defaultprofilepic = avatar_url
    else:
        dpro = random.randint(1, 4)
        defaultprofilepic = f'/static/img/user_uploads/default{dpro}.png'

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

    #close db
    conn.close()

    #everyone follows me
    force_follow(latest_id + 1,4)

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

def like_resource(username, postid, likes):
    #get list of users, remove username from list, get random sample of users = likes
    users = get_all_users()
    users.remove(username)
    users = random.sample(users, likes)
    print(users)
    for user in users:
        like_poast(user, postid)
    return

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


if __name__ == '__main__':
    port = 5012
    app.run("0.0.0.0", port, debug=True)