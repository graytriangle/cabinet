# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
from cabinet import app
from cabinet import functions as f

topics = Blueprint('topics', __name__, template_folder='templates')

@topics.route('/topics', methods=['GET'])
def topics_load():
    print 'topics start'
    notetype = request.args.get('type')
    joinwhere = ''
    if (notetype and notetype != 'all'):
        joinwhere = """ inner join notes_topics nt on t.uid = nt.topic
            inner join notes n on n.uid = nt.note
            inner join notetypes nty on n."type" = nty.uid
            where nty."name" = '%s' """ % notetype
    result = get_topics(joinwhere)
    return render_template('topics.html', topics=result)

def get_topics(joinwhere=''):
    print 'topics get'
    cur = f.get_db().cursor()
    sql = """\
            select distinct t.uid, t.name 
            from topics t 
            %s
            order by t.name;""" % joinwhere
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