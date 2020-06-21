# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask import render_template
from flask import request
from flask import redirect, session, flash
from flask import url_for
import uuid
from cabinet import app
from cabinet import functions as f
from cabinet import auth as a
from cabinet.errors import errornames
from datetime import datetime
from cabinet.atw import atw
from cabinet.cab import intentions as i
from cabinet.cab import notes as n
from cabinet.cab import topics as t
from cabinet.cab import main as m
from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import pbkdf2_sha512
from werkzeug.exceptions import HTTPException

app.register_blueprint(m.main, url_prefix='/')
app.register_blueprint(i.intentions, url_prefix='/')
app.register_blueprint(n.notes, url_prefix='/')
app.register_blueprint(t.topics, url_prefix='/')
app.register_blueprint(atw.atw, url_prefix='/')
app.config.from_pyfile('cabinet.cfg')

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# @app.before_request
# def before_request():
#     print(request.endpoint)
#     if not session.get('logged_in') and request.endpoint != 'login_page' and request.endpoint != 'login' and request.endpoint != 'static':
#         return redirect(url_for('login_page'))

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return redirect(url_for("error_page", code=code, origin=request.referrer))

@app.route('/error/<int:code>')
def error_page(code):
    # check if code is valid in case someone entered the url manually
    try:
        errornames[str(code)]
    except:
        return redirect(url_for("error_page", code=404))
    # get the origin
    if ("origin" in request.args):
        origin_url = request.args.get('origin')
    else:
        origin_url = "https://" + app.config['SERVER_NAME']
    return render_template('error.html', code=str(code), message=errornames[str(code)] + "!", origin=origin_url), code

# lobby page
@app.route('/')
def lobby_page():
    return render_template('lobby.html')

@app.route('/signup', methods=['GET'])
def signup_page(): 
    # redirect if logged in or forbidden to register
    if current_user.is_authenticated or (not app.config['REG_OPEN']):
        return redirect('/')
    else:
        flash(u'Введите данные и нажмите Enter')
        if request.args.get('error'):
            flash(u'Слишком много запросов!')
        return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    # redirect if logged in or forbidden to register
    if current_user.is_authenticated or (not app.config['REG_OPEN']):
        return redirect('/')
    else:
        user = a.CabinetUser.get_by_field("login", request.form['username'])
        if (user):
            flash(u'Этот пользователь уже существует!')
            return signup_page()
        else:
            a.CabinetUser.create(request.form['username'], pbkdf2_sha512.hash(request.form['password']))
            user = a.CabinetUser.get_by_field("login", request.form['username'])
            login_user(user)
            return redirect('/')

@app.route('/login', methods=['GET'])
def login_page():
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect('/')
    else:
        flash(u'Введите данные и нажмите Enter')
        if request.args.get('error'):
            flash(u'Слишком много запросов!')
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect('/')
    else:
        user = a.CabinetUser.get_by_field("login", request.form['username'])
        if (user and pbkdf2_sha512.verify(request.form['password'], user.password)):
            login_user(user)
            # we take the full url for redirect or use default '/' url in its absence
            dest_url = request.args.get('next')
            if not dest_url:
                return redirect('/')
            return redirect(dest_url)
        else:
            flash(u'Неверные логин/пароль!')
            return login_page()

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

# auxiliary functions

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

