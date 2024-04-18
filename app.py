from flask import Flask, render_template, request, jsonify, redirect, url_for
from flag_list import FLAGS
import random

app = Flask(__name__)

users = {'1': '1', 'user2': 'password2'}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username] == password:
        # Redirect to another HTML page on successful login
        return redirect(url_for('game'))
    else:
        return 'Invalid username or password. Please try again.'

@app.route('/game')
def game():
    flag = random.choice(FLAGS)
    return render_template('game.html', flag=flag)

@app.route('/check_guess', methods=['POST'])
def check_guess():
    # Get the guessed country from the form
    guessed_country = request.form['guess'].strip().lower()

    # Get the actual country of the flag
    flag_country = request.form['flag_country'].strip().lower()

    # Check if the guess is correct
    if guessed_country == flag_country:
        # If correct, pick a new random flag
        new_flag = random.choice(FLAGS)
        result = "Correct! Here's a new flag."
        return jsonify(result=result, new_flag=new_flag)
    else:
        result = "Incorrect! Try again."
        return jsonify(result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
