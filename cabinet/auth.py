# -*- coding: utf-8 -*-
from cabinet import functions as f
from flask_login import UserMixin
from . import login_manager
import functools
from flask_login import current_user
from flask import current_app, redirect, url_for, flash, request
import uuid
from werkzeug.exceptions import Forbidden

users = {}

class CabinetUser(UserMixin):
    def __init__(self):
        self.id = None
        self.name = None
        self.login = None
        self.permissions = []

    @classmethod
    def get_by_field(cls, field, value):
        cur = f.get_db().cursor()
        cur.execute("SELECT u.uid, u.name, u.login, u.password, string_agg(p.name, ',') FROM users u "
            "LEFT JOIN users_permissions up on u.uid = up.userid "
            "LEFT JOIN permissions p on p.uid = up.permissionid "
            "WHERE u.{} = %s "
            "GROUP BY u.uid; ".format(field), (value,))
        dbuser = cur.fetchone()
        appuser = CabinetUser()
        if not dbuser:
            return None
        appuser.id, appuser.name, appuser.login, appuser.password, appuser.permissions = \
            dbuser[0], dbuser[1], dbuser[2], dbuser[3], dbuser[4].split(',') if dbuser[4] else None
        if (appuser.id not in users):
            users[appuser.id] = appuser
        return appuser

    @classmethod
    def create(cls, login, password):
        cur = f.get_db().cursor()
        userid = str(uuid.uuid4())
        cur.execute("INSERT into users (uid, login, password) VALUES (%s, %s, %s);", (userid, login, password))
        cur.execute("INSERT into users_permissions (userid, permissionid) VALUES (%s, (SELECT uid FROM permissions WHERE name = 'user'));", (userid,))
        f.get_db().commit()


@login_manager.user_loader
def load_user(user_id):
    if (user_id in users):
        return users[user_id]
    else:
        return CabinetUser.get_by_field("uid", user_id)

@login_manager.unauthorized_handler
def unauth_handler():
    if current_user.is_authenticated:
        raise Forbidden
    else:
        flash(u'Для просмотра страницы необходимо войти!')
        return redirect(url_for('login_page', next=request.url))

def requires_permission(permission):
    def decorator_perm(func):
        @functools.wraps(func)
        def wrapper_perm(*args, **kwargs):
            if (current_user.permissions and permission in current_user.permissions):
                return func(*args, **kwargs)
            else:
                return current_app.login_manager.unauthorized()
        return wrapper_perm
    return decorator_perm