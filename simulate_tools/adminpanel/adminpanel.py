from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
# able to load modules from parent directory
import sys
sys.path.append('../')
sys.path.append('../simulate_tools')
from simulate_tools.poast import poast, get_profile_picture, get_all_users, like_poast
import datetime
import random
import mt_tweet
import user_creator

app = Flask(__name__, static_folder='../../static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////CRABBER_DATABASE.db'
app.config['SECRET_KEY'] = 'replace-with-a-secure-random-key'
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
        
        postid = poast(username, tweet, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"), isreply)
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
        
        print(f'username: {username} display_name: {display_name} bio: {bio}')

        user_creator.create_user(username, display_name, bio)
        return redirect(url_for('index'))  # Redirect to home page (or a different page) after account creation.

    return render_template('create_account.html')  # Render account creation page if method is GET.

def like_resource(username, postid, likes):
    #get list of users, remove username from list, get random sample of users = likes
    users = get_all_users()
    users.remove(username)
    users = random.sample(users, likes)
    print(users)
    for user in users:
        like_poast(user, postid)
    return


if __name__ == '__main__':
    app.run(debug=True)
