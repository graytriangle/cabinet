# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
from cabinet import functions as f
from cabinet import auth as a
from flask_login import login_required

intentions = Blueprint(
    "intentions",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/cab/static",
    subdomain="cabinet",
)


@intentions.before_request
@login_required
@a.requires_permission("admin")
def before_request():
    """Request admin permission to access any endpoint from this blueprint."""
    pass


##################
# VIEW FUNCTIONS #
##################


@intentions.route("/intent/check", methods=["GET"])
def intent_check():
    uid = request.args.get("uid", "")
    status = request.args.get("status", "")
    print(uid)
    print(status)
    cur = f.get_db().cursor()
    try:
        cur.execute("SELECT recurrent FROM intentions WHERE uid = %s::uuid;", (uid,))
        recurrent = cur.fetchone()[0]
        cur.execute("SELECT frequency FROM intentions WHERE uid = %s::uuid;", (uid,))
        frequency = cur.fetchone()[0]
        if recurrent:
            if status == "true":
                cur.execute(
                    "UPDATE intentions SET oldstartdate = startdate WHERE uid = %s::uuid;",
                    (uid,),
                )
                # set startdate to next 4:00 AM
                cur.execute(
                    "UPDATE intentions "
                    "SET startdate = date_trunc('day', timezone('MSK'::text, now()) + interval '20 hours') "
                    "+ interval '4 hours' "
                    "WHERE uid = %s::uuid;",
                    (uid,),
                )
            else:
                cur.execute(
                    "UPDATE intentions SET startdate = oldstartdate WHERE uid = %s::uuid;",
                    (uid,),
                )
        else:
            if status == "true":
                cur.execute(
                    "UPDATE intentions SET finished = timezone('MSK'::text, now()) WHERE uid = %s::uuid;",
                    (uid,),
                )
            else:
                cur.execute(
                    "UPDATE intentions SET finished = NULL WHERE uid = %s::uuid;",
                    (uid,),
                )
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid)


@intentions.route("/intent/delete", methods=["GET"])
def intent_delete():
    uid = (request.args.get("uid", ""),)
    cur = f.get_db().cursor()
    try:
        cur.execute("DELETE FROM intentions WHERE uid = %s::uuid;", uid)
        f.get_db().commit()
    # no exception handling; simple alert about "500 server error"
    finally:
        cur.close()
    return str(uid)


@intentions.route("/intent/reload", methods=["GET"])
def intent_reload():
    # get the intentions tree
    all = request.args.get("all")
    if all == "true":
        return render_template("todo.html", todo=get_all_intentions())
    else:
        return render_template("todo.html", todo=get_current_intentions())


###################
# OTHER FUNCTIONS #
###################


def get_current_intentions():
    cur = f.get_db().cursor()
    try:
        cur.execute(
            "select "
            "uid, name, description, important, recurrent, parent, created, "
            # for recurrent intentions that didn't reach their reminder we set "finished"
            # to mark them as completed
            "case when (recurrent = 't' and timezone('MSK'::text, now()) < "
            "(startdate + (frequency * INTERVAL '1 day') - (reminder * INTERVAL '1 day'))) "
            "then startdate else finished end as finished, "
            "startdate, frequency, reminder, oldstartdate "
            "FROM public.intentions where "
            # non-recurrent intentions that are either not completed or completed less than 5 days ago
            "(recurrent = 'f' and coalesce(finished, timezone('MSK'::text, now())) >= "
            "(timezone('MSK'::text, now()) - '2 day'::interval)) OR "
            # recurrent intentions that were completed recently (less than 5 days ago)
            "(recurrent = 't' and timezone('MSK'::text, now()) < (startdate + '2 day'::interval)) OR "
            # recurrent intentions that should be completed in the near future (reminder reached)
            "(recurrent = 't' and timezone('MSK'::text, now()) > "
            "(startdate + (frequency * INTERVAL '1 day') - (reminder * INTERVAL '1 day')));"
        )
        todo = f.dictfetchall(cur)
        result = f.get_nested(todo)
    except psycopg2.Error as e:
        f.get_db().rollback()
        result = [{"error": str(e)}]
    finally:
        cur.close()
    return result


def get_all_intentions():
    cur = f.get_db().cursor()
    try:
        cur.execute(
            "select "
            "uid, name, description, important, recurrent, parent, created, "
            "case when (recurrent = 't' and timezone('MSK'::text, now()) < "
            "(startdate + (frequency * INTERVAL '1 day') - (reminder * INTERVAL '1 day'))) "
            "then startdate else finished end as finished, "
            "startdate, frequency, reminder, oldstartdate "
            "FROM public.intentions ;"
        )
        todo = f.dictfetchall(cur)
        result = f.get_nested(todo)
    except psycopg2.Error as e:
        f.get_db().rollback()
        result = [{"error": str(e)}]
    finally:
        cur.close()
    return result
