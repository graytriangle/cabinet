# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
import uuid
from cabinet import functions as f
from cabinet import auth as a
from cabinet.cab import intentions as i
from cabinet.cab import topics as t
from cabinet.cab import notes as n
from flask_login import login_required

main = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/cab/static",
    subdomain="cabinet",
)


@main.before_request
@login_required
@a.requires_permission("admin")
def before_request():
    """Request admin permission to access any endpoint from this blueprint."""
    pass


@main.route("/")
def main_page():
    """Render main page."""
    return render_template(
        "master.html",
        notes=n.get_notes(),
        showtypes=True,
        todo=i.get_current_intentions(),
        topics=t.get_topics(),
    )


@main.route("/", methods=["POST"])
def my_form_post():
    """Add a new note or modify an existing one."""
    postuid = request.form["uid"]
    importance = request.form["importance"]
    maintext = request.form["maintext"]
    topic = request.form["topic"]
    source = request.form["source"]
    print("source")
    notetype = request.form["notetype"]
    print("notetype")
    if postuid == "00000000-0000-0000-0000-000000000000":
        postuid = str(uuid.uuid4())
    if maintext == "<p><br></p>":
        maintext = ""  # for some bizarre reason None doesn't get converted into null
    cur = f.get_db().cursor()
    try:
        cur.execute(
            "INSERT INTO notes (uid, maintext, important, url, type) "
            "VALUES (%s, %s, %s, %s, (SELECT uid FROM notetypes WHERE name = %s)) "
            "ON CONFLICT (uid) DO UPDATE SET maintext=excluded.maintext, changed=timezone('MSK'::text, now()), "
            "important=excluded.important, url=excluded.url, type=excluded.type;",
            (postuid, maintext, importance, source, notetype),
        )
        if topic:
            topicsarray = topic.split(",")
            topicsarray = [i.strip() for i in topicsarray]
            topicsarray = [i for i in topicsarray if i]  # removing empty strings
            for t in topicsarray:
                cur.execute(
                    "INSERT INTO topics (name) VALUES (%s) ON CONFLICT DO NOTHING;",
                    (t,),
                )
            cur.execute("DELETE FROM notes_topics WHERE note = %s;", (postuid,))
            for t in topicsarray:
                cur.execute("SELECT uid FROM topics WHERE name = %s;", (t,))
                topicuid = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO notes_topics (note, topic) VALUES (%s, %s);",
                    (postuid, topicuid),
                )
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return n.notes_load(postuid)


@main.route("/delete", methods=["GET"])
def delete():
    """Add a new note or modify an existing one."""
    uid = (request.args.get("uid", ""),)
    cur = f.get_db().cursor()
    try:
        cur.execute("DELETE FROM notes WHERE uid = %s::uuid;", uid)
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid)  # getting uid back to delete post from page


@main.route("/mark", methods=["GET"])
def mark():
    uid = (request.args.get("uid", ""),)
    status = (request.args.get("status", ""),)
    cur = f.get_db().cursor()
    try:
        cur.execute(
            "UPDATE notes SET important = %s WHERE uid = %s::uuid;", (status, uid)
        )
        f.get_db().commit()
        print("mark set!")
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid)
