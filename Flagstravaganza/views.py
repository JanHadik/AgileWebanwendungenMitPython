import hashlib
import random
import time

from flask import render_template, request, jsonify, session
from sqlalchemy import desc

from Flagstravaganza import app, db, socketio
from Flagstravaganza.models import User, Flag, Highscore
from config import salt

'''
Session Variables:

session["current_flag"]
session["score"]
session["username"]
session["logged_in"]
session["image"]
'''


@app.route('/')
def index():
    set_session_variables()
    return render_game()


@app.route('/register_page', methods=['POST'])
def register_page():
    return render_template('register_form.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    confirmed_password = request.form['confirm_password']

    user = User.query.filter_by(username=username).first()

    if password != confirmed_password:
        result = "Passwords do not match"
        return render_template('register_form.html', error=result)
    elif user:
        result = "Username already exists"
        return render_template('register_form.html', error=result)
    else:
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        user = User(username, hashed_password)
        db.session.add(user)
        db.session.commit()

        time.sleep(2.5)

        return render_game()


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    user = User.query.filter_by(username=username, password=hashed_password).first()
    if user:
        session["logged_in"] = True
        session["username"] = username
        return render_game()
    else:
        return render_game()


@app.route('/logout', methods=['POST'])
def logout():
    session["logged_in"] = False
    return render_game()


@app.route('/current_score')
def current_score():
    current_score = session.get('score', 0)
    return jsonify({'current_score': current_score})


@app.route('/check_guess', methods=['POST'])
def check_guess():
    guessed_country = request.form['guess'].strip().lower()

    flag_country = session["current_flag"]

    if guessed_country.lower() == flag_country.lower():
        result = "Correct! Here's a new flag."
        session["score"] = session["score"] + 1
        socketio.emit('update_score', {'current_score': session['score']})
    else:
        if session["logged_in"]:
            curr_highscore = Highscore.query.filter_by(user=session["username"]).first()
            if curr_highscore is None:
                highscore = Highscore(session["username"], session["score"])
                db.session.add(highscore)
                db.session.commit()
            elif curr_highscore.score < session["score"]:
                db.session.query(Highscore).filter_by(user=session["username"]).delete()
                highscore = Highscore(session["username"], session["score"])
                db.session.add(highscore)
                db.session.commit()
        session["score"] = 0
        socketio.emit('update_score', {'current_score': session['score']})
        result = "Incorrect! The correct answer was " + flag_country + "."

    return jsonify(result=result, new_flag=get_new_flag())


def set_session_variables():
    session["logged_in"] = False
    session["score"] = 0
    session["username"] = ""
    session["current_flag"] = ""
    return


def get_new_flag():
    flags = Flag.query.all()
    new_flag = random.choice(flags)
    new_flag_data = {"img_path": "/flag_images/"+new_flag.img_path, "country": new_flag.country}
    session["current_flag"] = new_flag.country
    return new_flag_data


def render_game():
    flags = Flag.query.all()
    countries = [flag.country for flag in flags]
    flag_data = get_new_flag()

    highest_scores = Highscore.query.order_by(desc(Highscore.score)).limit(7).all()

    default_highscore = Highscore(score=0, user="N/A")

    while len(highest_scores) < 7:
        highest_scores.append(default_highscore)

    user_highscore = None
    if session["logged_in"]:
        user = User.query.filter_by(username=session["username"]).first()
        if user:
            user_highscore = Highscore.query.filter_by(user=user.username).first()

    return render_template('game.html', flag=flag_data, countries=countries, logged_in=session["logged_in"],
                           highest_scores=highest_scores, user_highscore=user_highscore, username=session["username"])


if __name__ == '__main__':
    app.run(debug=True)
