# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask import render_template
from flask import request
import uuid
from cabinet import app
from cabinet import intentions
from cabinet import functions as f
from datetime import datetime

QUERY_ERR = u'Ошибка при выполнении запроса к БД!'
NO_NOTE = u'Запись не существует!'
EMPTY_TOPIC = u'Записей на данную тему не найдено!'

app.register_blueprint(intentions.intentions)

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
    return render_template('master.html', main=main, todo=get_intentions())

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
            "ON CONFLICT (uid) DO UPDATE SET maintext=excluded.maintext, changed=LOCALTIMESTAMP, important=excluded.important, url=excluded.url;", (postuid, maintext, importance, source))
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
    return getpost(postuid)

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

@app.route('/post/<string:post_id>') # TODO: switch to uuids; it fails for some reason
def show_post(post_id):
    # show the post with the given id, the id is an uuid
    cur = f.get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "where n.uid = %s;", (post_id,))
        result = f.dictfetchall(cur)
    except:
        return render_template('404.html', message=QUERY_ERR)
    finally:
        cur.close()
    if result:
        return render_template('master.html', main=result, todo=get_intentions())
    else:
        return render_template('404.html', message=NO_NOTE)

@app.route('/getpost', methods=['GET'])
def getpost(post_id=None):
    # get the post with the given id, the id is an uuid
    uid = request.args.get('uid')
    if not uid:
        uid = post_id
    cur = f.get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "where n.uid = %s;", (uid,))
        result = f.dictfetchall(cur)
    except:
        return render_template('404.html', message=QUERY_ERR)
    finally:
        cur.close()
    return render_template('post.html', record=result[0])

@app.route('/topic/<string:topic>')
def gettopic(topic):
    # show notes on given topic
    cur = f.get_db().cursor()
    try:
        cur.execute("select n.*, "
            "(select string_agg(name, ',') from topics t "
            "left join notes_topics nt on nt.topic = t.uid "
            "where nt.note = n.uid) topics "
            "from notes n "
            "left join notes_topics nt on nt.note = n.uid "
            "left join topics t on nt.topic = t.uid "
            "where t.name = %s;", (topic.lower(),))
        result = f.dictfetchall(cur)
    except:
        return render_template('404.html', message=QUERY_ERR)
    finally:
        cur.close()
    if result:
        print result
        return render_template('master.html', main=result, todo=get_intentions())
    else:
        return render_template('404.html', message=EMPTY_TOPIC)

# auxiliary finctions

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_intentions():
    cur = f.get_db().cursor()
    try:
        cur.execute("select * from intentions "
            "where coalesce(finished, LOCALTIMESTAMP) "
            "> (LOCALTIMESTAMP - '5 day'::interval);")
        todo = f.dictfetchall(cur)
    finally:
        cur.close()
    return f.get_nested(todo)