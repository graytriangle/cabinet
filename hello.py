# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask import render_template
from flask import request
import psycopg2
import uuid

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect("dbname=note user=postgres")
    return db

app = Flask(__name__)

@app.route('/')
def test():
    cur = get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n;")
        result = dictfetchall(cur)
    finally:
        cur.close()
    return render_template('master.html', data=result)

@app.route('/', methods=['POST'])
def my_form_post():
    postuid = request.form['uid']
    importance = request.form['importance']
    maintext = request.form['maintext']
    topic = request.form['topic']
    source = request.form['source']
    if postuid == '00000000-0000-0000-0000-000000000000':
        postuid = str(uuid.uuid4())
    cur = get_db().cursor()
    try:
        cur.execute("INSERT INTO notes (uid, maintext, important, url) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (uid) DO UPDATE SET maintext=excluded.maintext, changed=timezone('utc'::text, now()), important=excluded.important, url=excluded.url;", (postuid, maintext, importance, source))
        get_db().commit()
        if topic:
            topicsarray = topic.split(',')
            topicsarray = [i.strip() for i in topicsarray]
            topicsarray = [i for i in topicsarray if i] # removing empty strings
            try:
                for t in topicsarray:
                    cur.execute("INSERT INTO topics (name) VALUES (%s) ON CONFLICT DO NOTHING;", (t,))
                get_db().commit()
                cur.execute("DELETE FROM notes_topics WHERE note = %s;", (postuid,))
                get_db().commit()
                for t in topicsarray:
                    cur.execute("SELECT uid FROM topics WHERE name = %s;", (t,))
                    topicuid = cur.fetchone()[0]
                    cur.execute("INSERT INTO notes_topics (note, topic) VALUES (%s, %s);", (postuid, topicuid))
                get_db().commit()
            finally:
                pass
    finally:
        cur.close()
    return getpost(postuid)

@app.route('/delete', methods=['GET'])
def delete():
    uid = (request.args.get('uid', ''),)
    cur = get_db().cursor()
    try:
        cur.execute("DELETE FROM notes WHERE uid = %s::uuid;", uid)
        get_db().commit()
    finally:
        cur.close()
    return uid # getting uid back to delete post from page

@app.route('/mark', methods=['GET'])
def mark():
    uid = (request.args.get('uid', ''),)
    status = (request.args.get('status', ''),)
    cur = get_db().cursor()
    try:
        cur.execute("UPDATE notes SET important = %s WHERE uid = %s::uuid;", (status, uid))
        get_db().commit()
    finally:
        cur.close()
    return uid 

@app.route('/post/<string:post_id>') # TODO: switch to uuids; it fails for some reason
# TODO: make title hyperlink here
def show_post(post_id):
    # show the post with the given id, the id is an uuid
    cur = get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "where n.uid = %s;", (post_id,))
        result = dictfetchall(cur)
    except:
        return render_template('404.html')
    finally:
        cur.close()
    if result:
        return render_template('master.html', data=result)
    else:
        return render_template('404.html')

@app.route('/getpost', methods=['GET'])
def getpost(post_id=None):
    # get the post with the given id, the id is an uuid
    uid = request.args.get('uid')
    if not uid:
        uid = post_id
    cur = get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "where n.uid = %s;", (uid,))
        result = dictfetchall(cur)
    except:
        return render_template('master.html') # TODO: make 404 page
    finally:
        cur.close()
    return render_template('post.html', record=result[0])

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def dictfetchall(cursor):
    "Returns all rows from a cursor as a list of dicts"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], decodesql(row)))
        for row in cursor.fetchall()
    ]

def decodesql(record):
    "Converts db record (tuple) to UTF-8"
    return tuple(
        element.decode('utf-8') if type(element) is str else element for element in record
    )