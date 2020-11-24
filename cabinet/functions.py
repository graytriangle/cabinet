# -*- coding: utf-8 -*-

from flask import g, current_app
import psycopg2
import re

QUERY_ERR = u"Ошибка при выполнении запроса к БД!"
NO_NOTE = u"Запись не существует!"
EMPTY_TOPIC = u"Записей на данную тему не найдено!"
EMPTY_TOPIC_LIST = u"Список тем пуст!"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = psycopg2.connect(
            "host='%s' dbname='%s' user='%s' password='%s'"
            % (
                current_app.config["DBHOST"],
                current_app.config["DBNAME"],
                current_app.config["DBUSER"],
                current_app.config["DBPASSWORD"],
            )
        )
    return db


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


# unused since moving to python 3
def decodesql(record):
    "Converts db record (tuple) to UTF-8"
    return tuple(
        element.decode("utf-8") if type(element) is str else element
        for element in record
    )


def get_nested(pool, target=None):
    """Transform a flat list of dicts into a nested one.

    Take a result of dictfetchall and rebuild it into a list of nested dicts
    recursively.

    Keyword arguments:
    pool -- the initial flat list
    target -- a list of top-level dicts to attach children to

    """
    if not target: # on first call
        target = []
        for i in pool:
            if not i["parent"]:
                target.append(i)
                
    for item in target:
        children = []
        for old in pool:
            if old["parent"] == item["uid"]:
                children.append(old)
        if children:
            children = get_nested(pool, children)
        item["children"] = children
    return target


def sanitize_url(url, length):
    "Replaces url-unsafe characters in a string"
    "Leaves only digits, English and Russian letters and dashes"
    "Truncates it to desired length"
    url = url.lower().replace(" ", "-")
    url = re.sub("[^ЁёА-яa-zA-Z0-9\-]", "", url)
    return url[:length]
