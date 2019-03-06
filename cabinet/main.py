# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask import render_template
from flask import request
from flask import redirect, session, flash
from flask import url_for
import uuid
from cabinet import app
from cabinet import intentions as i
from cabinet import notes as n
from cabinet import functions as f
from cabinet import topics as t
from cabinet import appsettings
from datetime import datetime

app.register_blueprint(i.intentions)
app.register_blueprint(n.notes)
app.register_blueprint(t.topics)
app.secret_key = appsettings.secret_key

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.before_request
def before_request():
    print(request.endpoint)
    if not session.get('logged_in') and request.endpoint != 'login_page' and request.endpoint != 'login' and request.endpoint != 'static':
        return redirect(url_for('login_page'))

@app.route('/')
def main_page():
    return render_template('master.html', notes=n.get_notes(), showtypes=True, todo=i.get_current_intentions(), topics=t.get_topics())

@app.route('/login')
def login_page():
    if session.get('logged_in'):
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == appsettings.admin_login and request.form['password'] == appsettings.admin_pw:
        session['logged_in'] = True
        return redirect('/')
    else:
        flash(u'Неверные логин/пароль!')
        return login_page()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/login')

@app.route('/', methods=['POST'])
def my_form_post():
    postuid = request.form['uid']
    importance = request.form['importance']
    maintext = request.form['maintext']
    topic = request.form['topic']
    source = request.form['source']
    print('source')
    notetype = request.form['notetype']
    print('notetype')
    if postuid == '00000000-0000-0000-0000-000000000000':
        postuid = str(uuid.uuid4())
    if maintext == '<p><br></p>':
        maintext = '' # for some bizarre reason None doesn't get converted into null
    cur = f.get_db().cursor()
    try:
        cur.execute("INSERT INTO notes (uid, maintext, important, url, type) VALUES (%s, %s, %s, %s, (SELECT uid FROM notetypes WHERE name = %s)) "
            "ON CONFLICT (uid) DO UPDATE SET maintext=excluded.maintext, changed=timezone('MSK'::text, now()), "
            "important=excluded.important, url=excluded.url, type=excluded.type;", (postuid, maintext, importance, source, notetype))
        if topic:
            topicsarray = topic.split(',')
            topicsarray = [i.strip() for i in topicsarray]
            topicsarray = [i for i in topicsarray if i] # removing empty strings
            for t in topicsarray:
                cur.execute("INSERT INTO topics (name) VALUES (%s) ON CONFLICT DO NOTHING;", (t,))
            cur.execute("DELETE FROM notes_topics WHERE note = %s;", (postuid,))
            for t in topicsarray:
                cur.execute("SELECT uid FROM topics WHERE name = %s;", (t,))
                topicuid = cur.fetchone()[0]
                cur.execute("INSERT INTO notes_topics (note, topic) VALUES (%s, %s);", (postuid, topicuid))
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return n.notes_load(postuid)

@app.route('/delete', methods=['GET'])
def delete():
    uid = (request.args.get('uid', ''),)
    cur = f.get_db().cursor()
    try:
        cur.execute("DELETE FROM notes WHERE uid = %s::uuid;", uid)
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid) # getting uid back to delete post from page

@app.route('/mark', methods=['GET'])
def mark():
    uid = (request.args.get('uid', ''),)
    status = (request.args.get('status', ''),)
    cur = f.get_db().cursor()
    try:
        cur.execute("UPDATE notes SET important = %s WHERE uid = %s::uuid;", (status, uid))
        f.get_db().commit()
        print('mark set!')
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid)

# auxiliary finctions

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

