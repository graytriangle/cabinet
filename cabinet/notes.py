# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
from cabinet import app
from cabinet import functions as f
from cabinet import intentions as i

notes = Blueprint('notes', __name__, template_folder='templates')

##################
# VIEW FUNCTIONS #
##################

@notes.route('/note/<string:post_id>') # TODO: switch to uuids; it fails for some reason
def show_post(post_id):
    # show the post with the given id, the id is an uuid
    # you can also return single post with ajax, see below
    try:
        result = get_notes('', " where n.uid = '%s' " % post_id)
        if not result:
            result = {}
        return render_template('master.html', notes=result, showtypes=True, todo=i.get_current_intentions(), message=f.NO_NOTE)
    except psycopg2.Error as e:
        return render_template('master.html', notes={}, showtypes=True, todo=i.get_current_intentions(), message=f.QUERY_ERR, details=str(e))
        # return render_template('404.html', message=f.QUERY_ERR, details=str(e))

@notes.route('/notes', methods=['GET'])
def notes_load(post_id=None):
    # get the intentions tree
    notetype = request.args.get('type')
    notetopic = request.args.get('topic')
    noteuid = request.args.get('uid')
    print noteuid
    if not noteuid:
        noteuid = post_id # for getting a particular post after submitting
    where = "where 1=1 "
    join = " "
    showtypes = True
    cur = f.get_db().cursor()
    if (notetype and notetype != 'all'):
        where += " and nt.name = '%s' " % notetype
        showtypes = False
    if (notetopic):
        join = """ left join notes_topics nto on nto.note = n.uid
                left join topics t on nto.topic = t.uid """
        where += " and t.name = '%s' " % notetopic.lower()
    if (noteuid):
        where += " and n.uid = '%s' " % noteuid
    print where
    try:
        result = get_notes(join, where)
        if result:
            return render_template('notes.html', notes=result, showtypes=showtypes)
        else:
            return render_template('404.html', message=f.NO_NOTE)
    except psycopg2.Error as e:
        f.get_db().rollback()
        return render_template('404.html', message=f.QUERY_ERR, details=str(e))

###################
# OTHER FUNCTIONS #
###################

def get_notes(join='', where=''):
    cur = f.get_db().cursor()
    sql = """\
            select n.*, 
            (select string_agg(name, ',') from topics t 
            left join notes_topics nt on nt.topic = t.uid 
            where nt.note = n.uid) topics, 
            nt.name as typename 
            from notes n 
            left join notetypes nt on n.type = nt.uid
            %s
            %s
            order by created desc;""" % (join, where)
    try:
        cur.execute(sql)
        notes = f.dictfetchall(cur)
    except psycopg2.Error as e: 
        f.get_db().rollback()
        raise
    finally:
        cur.close()
    return notes