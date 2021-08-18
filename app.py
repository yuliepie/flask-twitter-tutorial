import pymysql
from flask import Flask, render_template
from api import board
import os
from db_connect import db  # import SQLAlchemy object
from flask_bcrypt import Bcrypt


BASEDIR = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.register_blueprint(board)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    BASEDIR, "app.sqlite"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "asodfajsdofijac"

db.init_app(app)
bcrypt = Bcrypt(app)  # for password hashing


if __name__ == "__main__":
    app.run(debug=True)
