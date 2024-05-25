import hashlib
import random

from flask import render_template, request, jsonify, redirect, url_for, session
from Flagstravaganza import app, db
from Flagstravaganza.models import User, Flag
from config import salt


@app.route('/')
def index():
    if session.get("logged_in") is None:
        session["logged_in"] = False
    return render_game()


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    user = User.query.filter_by(username=username, password=hashed_password).first()
    if user:
        # Redirect to another HTML page on successful login
        session["logged_in"] = True
        return render_game()
    else:
        return render_game()


@app.route('/logout', methods=['POST'])
def logout():
    session["logged_in"] = False
    return render_game()


@app.route('/check_guess', methods=['POST'])
def check_guess():
    # Get the guessed country from the form
    guessed_country = request.form['guess'].strip().lower()

    # Get the actual country of the flag
    flag_country = request.form['flag_country'].strip().lower()

    # Check if the guess is correct
    if guessed_country == flag_country:
        # If correct, pick a new random flag
        flags = Flag.query.all()
        new_flag = random.choice(flags)
        new_flag_data = {"img_path": new_flag.img_path, "country": new_flag.country}
        result = "Correct! Here's a new flag."
        return jsonify(result=result, new_flag=new_flag_data)
    else:
        result = "Incorrect! Try again."
        return jsonify(result=result)


def render_game():
    # Retrieve all flags and countries from the database
    flags = Flag.query.all()
    countries = [flag.country for flag in flags]
    flag = random.choice(flags)
    flag_data = {"img_path": flag.img_path, "country": flag.country}

    return render_template('game.html', flag=flag_data, countries=countries, logged_in=session["logged_in"])


if __name__ == '__main__':
    app.run(debug=True)
