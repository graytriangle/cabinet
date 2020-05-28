# -*- coding: utf-8 -*-
from cabinet import functions as f
from flask_login import UserMixin
from . import login_manager

users = {}

class CabinetUser(UserMixin):
    def __init__(self):
        self.id = None
        self.name = None
        self.login = None

    @classmethod
    def get_by_field(cls, field, value):
        cur = f.get_db().cursor()
        cur.execute("SELECT uid, name, login, password FROM users WHERE {} = %s;".format(field), (value,))
        dbuser = cur.fetchone()
        appuser = CabinetUser()
        if not dbuser:
            return None
        appuser.id, appuser.name, appuser.login, appuser.password = dbuser[0], dbuser[1], dbuser[2], dbuser[3]
        if (appuser.id not in users):
            users[appuser.id] = appuser
        return appuser

    @classmethod
    def create(cls, login, password):
        cur = f.get_db().cursor()
        cur.execute("INSERT into users (login, password) VALUES (%s, %s);", (login,password))
        f.get_db().commit()


@login_manager.user_loader
def load_user(user_id):
    if (user_id in users):
        return users[user_id]
    else:
        return CabinetUser.get_by_field("uid", user_id)
