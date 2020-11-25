# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
from cabinet import functions as f
from cabinet import auth as a
from cabinet.cab import intentions as i
from cabinet.cab import topics as t
from flask_login import login_required

notes = Blueprint(
    "notes",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/cab/static",
    subdomain="cabinet",
)


@notes.before_request
@login_required
@a.requires_permission("admin")
def before_request():
    """Request admin permission to access any endpoint from this blueprint."""
    pass


##################
# VIEW FUNCTIONS #
##################


@notes.route(
    "/note/<string:post_id>"
)  # TODO: switch to uuids; it fails for some reason
def show_post(post_id):
    """Render main page with a single post loaded.

    Keyword arguments:
    post_id : string -- uuid of the post
    """
    result = get_notes("", " where n.uid = '%s' " % post_id)
    return render_template(
        "master.html",
        notes=result,
        showtypes=True,
        todo=i.get_current_intentions(),
        topics=t.get_topics(),
    )


@notes.route("/notes", methods=["GET"])
def notes_load(post_id=None):
    notetype = request.args.get("type")
    notetopic = request.args.get("topic")
    noteuid = request.args.get("uid")
    print(noteuid)
    if not noteuid:
        noteuid = post_id  # for getting a particular post after submitting
    where = "where 1=1 "
    join = " "
    showtypes = True
    # if we get a batch of notes through a type switch
    if notetype and notetype == "people":
        if notetopic:
            where += " and name = '%s' " % notetopic
        result = get_people(where)
        return render_template("people.html", notes=result)
    else:
        if notetype and notetype != "all":
            where += " and nt.name = '%s' " % notetype
            showtypes = False
        if notetopic:
            join = """ left join notes_topics nto on nto.note = n.uid
                    left join topics t on nto.topic = t.uid """
            where += " and t.name = '%s' " % notetopic.lower()
        if noteuid:
            where += " and n.uid = '%s' " % noteuid
        result = get_notes(join, where)
        return render_template("notes.html", notes=result, showtypes=showtypes)


###################
# OTHER FUNCTIONS #
###################


def get_notes(join="", where=""):
    cur = f.get_db().cursor()
    sql = """\
            select n.*, 
            (select string_agg(name, ',') from topics t 
            left join notes_topics nt on nt.topic = t.uid 
            where nt.note = n.uid) topics, 
            nt.name as typename,
            nt.fullname as fullname
            from notes n 
            left join notetypes nt on n.type = nt.uid
            %s
            %s
            order by created desc;""" % (
        join,
        where,
    )
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{"error": f.NO_NOTE, "details": ""}]
    except psycopg2.Error as e:
        f.get_db().rollback()
        result = [{"error": f.QUERY_ERR, "details": str(e)}]
    finally:
        cur.close()
    return result


def get_people(where=""):
    cur = f.get_db().cursor()
    sql = """\
            select *
            from people
            %s;
            """ % (
        where
    )
    try:
        print(sql)
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{"error": f.NO_NOTE, "details": ""}]
    except psycopg2.Error as e:
        f.get_db().rollback()
        result = [{"error": f.QUERY_ERR, "details": str(e)}]
    finally:
        cur.close()
    return result
