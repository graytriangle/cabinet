# -*- coding: utf-8 -*-

from flask import g
import psycopg2
from cabinet import dbsettings

QUERY_ERR = u'Ошибка при выполнении запроса к БД!'
NO_NOTE = u'Запись не существует!'
EMPTY_TOPIC = u'Записей на данную тему не найдено!'
EMPTY_TOPIC_LIST = u'Список тем пуст!'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (dbsettings.host, dbsettings.dbname, dbsettings.user, dbsettings.password))
    return db

def dictfetchall(cursor):
    "Returns all rows from a cursor as a list of dicts"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], decodesql(row)))
        for row in cursor.fetchall()
    ]

def decodesql(record):
    "Converts db record (tuple) to UTF-8"
    return tuple(
        element.decode('utf-8') if type(element) is str else element for element in record
    )

def get_nested(pool, target = []):
    "Builds a new list of dicts (target) of arbitrary depth from another flat list of dicts (result of dictfetchall())"
    "Fields 'parent' and 'uid' are required"
    if not target:
        for i in pool:
            if not i['parent']:
                target.append(i)
    for item in target:
        children = []
        for old in pool:
            if old['parent'] == item['uid']:
                children.append(old)
        if children:
            children = get_nested(pool, children)
        item['children'] = children
    return target