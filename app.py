import os
from os.path import join, dirname

from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, LoginManager, login_required

app = Flask(__name__)
login = LoginManager(app)

from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('401.html'), 401

@app.route("/getall")
@login_required
def get_all():
    try:
        users = User.query.all()
        return jsonify([u.serialize() for u in users])
    except Exception as e:
        return(str(e))


@app.route("/add/form", methods=['GET', 'POST'])
@login_required
def add_user_form():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = User(
                username=username,
                email=email,
                password=User.generate_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            return "User added. user id={}".format(user.id)
        except Exception as e:
            return(str(e))
    return render_template("create_user.html")


@app.route("/doorcontrol", methods=['GET', 'POST'])
@login_required
def doorcontrol(): 
    if request.method == 'POST':
        print(request.form.data)
    return render_template("doorcontrol.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('add_user_form'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
 
        try:
            user = User.query.filter_by(email=email).first() 
            if User.verify_hash(password, user.password):
                login_user(user, remember=True)
                return redirect(url_for('add_user_form'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))
        except Exception as e:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template("login.html")


if __name__ == '__main__':
    app.run()
