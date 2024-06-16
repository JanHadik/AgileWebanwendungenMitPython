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

    session["logged_in"] = False
    session["game_over"] = False
    session["score"] = 0
    session["end_score"] = 0
    session["username"] = ""
    session["current_flag"] = ""
    session["correct_answer"] = ""
'''


@app.route('/')
def index():
    set_session_variables()
    return render_game()


@app.route('/lost')
def lost():
    session["game_over"] = False
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

        session["logged_in"] = True
        session["username"] = username
        session["score"] = 0

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
        session["score"] = 0
        return render_game()
    else:
        return render_game()


@app.route('/logout', methods=['POST'])
def logout():
    session["logged_in"] = False
    session["score"] = 0
    return render_game()


@app.route('/current_score')
def current_score():
    current_score = session.get('score', 0)
    return jsonify({'current_score': current_score})


@app.route('/check_guess', methods=['POST'])
def check_guess():
    guessed_country = request.form['guess']
    flag_country = session["current_flag"]

    if guessed_country.lower() == flag_country.lower():
        session["score"] += 1
        socketio.emit('update_score', {'current_score': session['score']})
        session["game_over"] = False
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
        socketio.emit('update_score', {'current_score': session['score']})
        session["end_score"] = session["score"]
        session["correct_answer"] = session["current_flag"]
        session["score"] = 0
        session["game_over"] = True
    return render_game()


def set_session_variables():
    if session.get("logged_in") is not True:
        session["logged_in"] = False
        session["game_over"] = False
        session["score"] = 0
        session["end_score"] = 0
        session["username"] = ""
        session["current_flag"] = ""
        session["correct_answer"] = ""


def get_new_flag():
    flags = Flag.query.all()
    new_flag = random.choice(flags)
    session["current_flag"] = new_flag.country
    return {"img_path": "/flag_images/" + new_flag.img_path, "country": new_flag.country}


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
                           highest_scores=highest_scores, user_highscore=user_highscore, username=session["username"],
                           game_over=session["game_over"], end_score=session["end_score"],
                           correct_answer=session["correct_answer"])


if __name__ == '__main__':
    app.run(debug=True)
