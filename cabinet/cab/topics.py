# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
from cabinet import functions as f
from cabinet import auth as a
from flask_login import login_required

topics = Blueprint(
    "topics",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/cab/static",
    subdomain="cabinet",
)


@topics.before_request
@login_required
@a.requires_permission("admin")
def before_request():
    """Request admin permission to access any endpoint from this blueprint."""
    pass


@topics.route("/topics", methods=["GET"])
def topics_load():
    notetype = request.args.get("type")
    joinwhere = ""
    if notetype and notetype == "people":
        result = get_peoplenames()
        return render_template("topics.html", topics=result)
    else:
        if notetype and notetype != "all":
            joinwhere = (
                """ left join notes n on n.uid = nt.note
                left join notetypes nty on n."type" = nty.uid
                where nty."name" = '%s' """
                % notetype
            )
        result = get_topics(joinwhere)
        return render_template("topics.html", topics=result)


@topics.route("/topics/delete", methods=["GET"])
def topics_delete():
    uid = (request.args.get("uid", ""),)
    cur = f.get_db().cursor()
    try:
        cur.execute("DELETE FROM topics WHERE uid = %s::uuid;", uid)
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid)  # getting uid back to delete post from page


def get_topics(joinwhere=""):
    cur = f.get_db().cursor()
    sql = (
        """\
            select distinct t.uid, t.name, count(nt.uid) as count
            from topics t 
            left join notes_topics nt on t.uid = nt.topic
            %s
            group by t.uid, t.name, nt.uid
            order by t.name;"""
        % joinwhere
    )
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{"error": f.EMPTY_TOPIC_LIST, "details": ""}]
    except psycopg2.Error as e:
        f.get_db().rollback()
        result = [{"error": f.QUERY_ERR, "details": str(e)}]
    finally:
        cur.close()
    return result


def get_peoplenames():
    cur = f.get_db().cursor()
    sql = """\
            select uid, name, 1 as count
            from people;"""
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{"error": f.EMPTY_TOPIC_LIST, "details": ""}]
    except psycopg2.Error as e:
        f.get_db().rollback()
        result = [{"error": f.QUERY_ERR, "details": str(e)}]
    finally:
        cur.close()
    return result
