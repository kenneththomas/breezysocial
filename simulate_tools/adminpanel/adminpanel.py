from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
# able to load modules from parent directory
import sys
sys.path.append('../')
sys.path.append('../simulate_tools')
from simulate_tools.poast import poast, get_profile_picture
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////CRABBER_DATABASE.db'
app.config['SECRET_KEY'] = 'replace-with-a-secure-random-key'
db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        tweet = request.form.get('tweet')
        poast(username, tweet, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"))
        flash("Tweet posted!")
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

#