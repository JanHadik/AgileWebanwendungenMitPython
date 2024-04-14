from flask import Flask, render_template, request, jsonify
from flag_list import FLAGS
import random

app = Flask(__name__)

@app.route('/')
def index():
    # Pick a random flag
    flag = random.choice(FLAGS)
    return render_template('index.html', flag=flag)


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
    app.run(debug=True,host='0.0.0.0', port=80)
