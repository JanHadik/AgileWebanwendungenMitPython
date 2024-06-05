from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

db = SQLAlchemy(app)

from Flagstravaganza.views import *

if __name__ == "__main__":
    app.run(debug=True)
