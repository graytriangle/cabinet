# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
from cabinet import app
from cabinet import functions as f

topics = Blueprint('topics', __name__, template_folder='templates')

@topics.route('/topics', methods=['GET'])
def notes_load():
    result = get_topics()
    return render_template('topics.html', topics=result)

def get_topics():
    cur = f.get_db().cursor()
    sql = """\
            select uid, name 
            from topics 
            order by name;"""
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{'error': f.EMPTY_TOPIC_LIST, 'details': ''}]
    except psycopg2.Error as e: 
        f.get_db().rollback()
        result = [{'error': f.QUERY_ERR, 'details': str(e)}]
    finally:
        cur.close()
    return result