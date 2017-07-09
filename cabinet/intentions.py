from flask import Blueprint
from flask import request
import psycopg2
from cabinet import app
from cabinet import functions as f

intentions = Blueprint('intentions', __name__, template_folder='templates')

@intentions.route('/intent/check', methods=['GET'])
def intent_check():
    uid = request.args.get('uid', '')
    status = request.args.get('status', '')
    print uid
    print status
    cur = f.get_db().cursor()
    try:
        cur.execute("SELECT recurrent FROM intentions WHERE uid = %s::uuid;", (uid,))
        recurrent = cur.fetchone()[0]
        cur.execute("SELECT frequency FROM intentions WHERE uid = %s::uuid;", (uid,))
        frequency = cur.fetchone()[0]
        if recurrent:
            if status == 'true':
                cur.execute("UPDATE intentions SET oldstartdate = startdate WHERE uid = %s::uuid;", (uid,))
                # set startdate to next 4:00 AM
                cur.execute("UPDATE intentions SET startdate = date_trunc('day', LOCALTIMESTAMP + interval '20 hours') + interval '4 hours' WHERE uid = %s::uuid;", (uid,))
            else:
                cur.execute("UPDATE intentions SET startdate = oldstartdate WHERE uid = %s::uuid;", (uid,))
        else:
            if status == 'true':
                cur.execute("UPDATE intentions SET finished = LOCALTIMESTAMP WHERE uid = %s::uuid;", (uid,))
            else:
                cur.execute("UPDATE intentions SET finished = NULL WHERE uid = %s::uuid;", (uid,))
        f.get_db().commit()
    finally:
        cur.close()
    return uid 

@app.route('/intent/delete', methods=['GET'])
def intent_delete():
    uid = (request.args.get('uid', ''),)
    cur = f.get_db().cursor()
    try:
        cur.execute("DELETE FROM intentions WHERE uid = %s::uuid;", uid)
        f.get_db().commit()
    finally:
        cur.close()
    return uid # getting uid back to delete post from page