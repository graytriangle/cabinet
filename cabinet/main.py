# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask import render_template
from flask import request
import uuid
from cabinet import app
from cabinet import intentions as i
from cabinet import notes as n
from cabinet import functions as f
from datetime import datetime

app.register_blueprint(i.intentions)
app.register_blueprint(n.notes)

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def main_page():
    cur = f.get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "order by created desc;")
        main = f.dictfetchall(cur)

    finally:
        cur.close()
    return render_template('master.html', notes=n.get_notes(), showtypes=True, todo=i.get_current_intentions())

@app.route('/', methods=['POST'])
def my_form_post():
    postuid = request.form['uid']
    importance = request.form['importance']
    maintext = request.form['maintext']
    topic = request.form['topic']
    source = request.form['source']
    if postuid == '00000000-0000-0000-0000-000000000000':
        postuid = str(uuid.uuid4())
    cur = f.get_db().cursor()
    try:
        cur.execute("INSERT INTO notes (uid, maintext, important, url) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (uid) DO UPDATE SET maintext=excluded.maintext, changed=timezone('MSK'::text, now()), important=excluded.important, url=excluded.url;", (postuid, maintext, importance, source))
        f.get_db().commit()
        if topic:
            topicsarray = topic.split(',')
            topicsarray = [i.strip() for i in topicsarray]
            topicsarray = [i for i in topicsarray if i] # removing empty strings
            try:
                for t in topicsarray:
                    cur.execute("INSERT INTO topics (name) VALUES (%s) ON CONFLICT DO NOTHING;", (t,))
                f.get_db().commit()
                cur.execute("DELETE FROM notes_topics WHERE note = %s;", (postuid,))
                f.get_db().commit()
                for t in topicsarray:
                    cur.execute("SELECT uid FROM topics WHERE name = %s;", (t,))
                    topicuid = cur.fetchone()[0]
                    cur.execute("INSERT INTO notes_topics (note, topic) VALUES (%s, %s);", (postuid, topicuid))
                f.get_db().commit()
            finally:
                pass
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
    finally:
        cur.close()
    return uid # getting uid back to delete post from page

@app.route('/mark', methods=['GET'])
def mark():
    uid = (request.args.get('uid', ''),)
    status = (request.args.get('status', ''),)
    cur = f.get_db().cursor()
    try:
        cur.execute("UPDATE notes SET important = %s WHERE uid = %s::uuid;", (status, uid))
        f.get_db().commit()
    finally:
        cur.close()
    return uid 

# auxiliary finctions

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

