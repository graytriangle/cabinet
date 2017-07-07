from flask import Blueprint
from flask import request
import psycopg2

intentions = Blueprint('intentions', __name__, template_folder='templates')

@intentions.route('/intent/check', methods=['GET'])
def mark():
    uid = (request.args.get('uid', ''),)
    status = (request.args.get('status', ''),)
    cur = get_db().cursor()
    try:
        cur.execute("SELECT recurrent FROM intentions WHERE uid = %s::uuid;", (uid,))
        recurrent = cur.fetchone()[0]
        if recurrent:
        	cur.execute("UPDATE intentions SET startdate = date_trunc('day', LOCALTIMESTAMP + interval '20 hours') + interval '4 hours' WHERE uid = %s::uuid;", (uid,))
        else:
        	if status:
        		cur.execute("UPDATE intentions SET finished = now() - interval '4 hours' WHERE uid = %s::uuid;", (uid,))
        	else:
        		cur.execute("UPDATE intentions SET finished = NULL WHERE uid = %s::uuid;", (uid,))
        get_db().commit()
    finally:
        cur.close()
    return uid 

@app.route('/intent/delete', methods=['GET'])
def goal_delete():
    uid = (request.args.get('uid', ''),)
    cur = get_db().cursor()
    try:
        cur.execute("DELETE FROM intentions WHERE uid = %s::uuid;", uid)
        get_db().commit()
    finally:
        cur.close()
    return uid # getting uid back to delete post from page