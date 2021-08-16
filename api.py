from flask import json, redirect, request, render_template, jsonify, Blueprint, session, g
from models import User, Post
from db_connect import db
from flask_bcrypt import Bcrypt

board = Blueprint('board', __name__)
bcrypt = Bcrypt()


@board.before_app_request
def load_logged_in_user():
    """This function will be run before each request.
    Checks if session['login'] is populated,
    and stores user info as global variable, which can be used by html.
    """
    user_id = session.get("login")
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.query(User).filter(User.id == user_id).first()


@board.route("/", methods=['GET'])
def home():
    if session.get('login') is None:
        return redirect('/login')
    else:
        return redirect('/post')


@board.route("/post", methods=["GET", "POST"])
def post():
    if session.get('login') is not None:
        if request.method == 'GET':
            data = Post.query.order_by(Post.created_at.desc()).all()
            return render_template("index.html", post_list=data)
        else:
            # POST
            content = request.form['content']
            author = request.form['author']

            post = Post(author, content)
            db.session.add(post)
            db.session.commit()
            return jsonify({"result": "success"})
    else:
        return redirect("/")


@board.route("/post", methods=["DELETE"])
def delete_post():
    post_id = request.form['id']
    requesting_userId = request.form['author']

    post = Post.query.filter(
        Post.id == post_id, Post.author == requesting_userId).first()

    if post is not None:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "fail"})


@board.route("/post", methods=["PATCH"])
def update_post():
    post_id = request.form['id']
    post_content = request.form['content']
    requesting_user = User.query.filter(User.id == session['login']).first()

    post = Post.query.filter(Post.id == post_id, Post.author ==
                             requesting_user.user_id).first()
    post.content = post_content

    db.session.commit()
    return jsonify({"result": "success"})


@board.route("/join", methods=['GET', 'POST'])
def join():
    # Only accessible if not logged in already.
    if session.get('login') is None:
        if request.method == "GET":
            return render_template("join.html")
        else:
            user_id = request.form['user_id']
            user_pw = request.form['user_pw']
            pw_hash = bcrypt.generate_password_hash(user_pw)

            user = User(user_id, pw_hash)
            db.session.add(user)
            db.session.commit()
            return jsonify({"result": "success"})
    else:
        return redirect('/')


@board.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('login') is None:
        if request.method == "GET":
            return render_template("login.html")
        else:
            user_id = request.form['user_id']
            user_pw = request.form['user_pw']

            user = User.query.filter(User.user_id == user_id).first()
            if user is not None:
                if bcrypt.check_password_hash(user.user_pw, user_pw):
                    session['login'] = user.id
                    return jsonify({'result': 'success'})
                # password does not match
                else:
                    return jsonify({'result': 'fail'})
            # user does not exist
            else:
                return jsonify({'result': 'fail'})
    else:
        return redirect('/')


@board.route("/logout")
def logout():
    session['login'] = None
    return redirect("/")
