# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask import render_template
from flask import request
import psycopg2
import uuid
import dbsettings
from datetime import datetime

QUERY_ERR = u'Ошибка при выполнении запроса к БД!'
NO_NOTE = u'Запись не существует!'
EMPTY_TOPIC = u'Записей на данную тему не найдено!'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (dbsettings.host, dbsettings.dbname, dbsettings.user, dbsettings.password))
    return db

app = Flask(__name__)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def main_page():
    cur = get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "order by created desc;")
        main = dictfetchall(cur)

        cur.execute("select * "
            "from goals;")
        todo = dictfetchall(cur)
    finally:
        cur.close()
    return render_template('master.html', main=main, todo=get_nested(todo))

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
        return render_template('404.html', message=QUERY_ERR)
    finally:
        cur.close()
    if result:
        return render_template('master.html', data=result)
    else:
        return render_template('404.html', message=NO_NOTE)

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
        return render_template('404.html', message=QUERY_ERR)
    finally:
        cur.close()
    return render_template('post.html', record=result[0])

@app.route('/topic/<string:topic>')
def gettopic(topic):
    # show notes on given topic
    cur = get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "left join notes_topics nt on nt.note = n.uid "
            "left join topics t on nt.topic = t.uid "
            "where t.name = %s;", (topic.lower(),))
        result = dictfetchall(cur)
    except:
        return render_template('404.html', message=QUERY_ERR)
    finally:
        cur.close()
    if result:
        return render_template('master.html', data=result)
    else:
        return render_template('404.html', message=EMPTY_TOPIC)

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

def get_nested(pool, target = []):
    "Builds a new list of dicts (target) of arbitrary depth from another flat list of dicts (result of dictfetchall())"
    "Fields 'parent' and 'uid' are required"
    if not target:
        for i in pool:
            if not i['parent']:
                target.append(i)
    for item in target:
        children = []
        for old in pool:
            if old['parent'] == item['uid']:
                children.append(old)
        if children:
            children = get_nested(pool, children)
        item['children'] = children
    return target