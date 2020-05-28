# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
import psycopg2
# from cabinet import app
from cabinet import functions as f
from flask_login import login_required, current_user

translations = Blueprint('translations', __name__, template_folder='templates', static_folder='static', 
	static_url_path='/translations/static', subdomain="translations")

##################
# VIEW FUNCTIONS #
##################

@translations.route('/', methods=['GET'])
@login_required
def translations_mainpage():
    return render_template('translations.html', list=get_translations_list(), linkname='')

@translations.route('/<string:link>', methods=['GET'])
@login_required
def translations_page(link):
    return render_template('translations.html', list=get_translations_list(), linkname=link)

@translations.route('/get/<string:link>', methods=['GET'])
@login_required
def get_translation(link):
    # get translation by name
    cur = f.get_db().cursor()
    sql = """\
            select tr.engname, tr.runame, tr.original, tr.translation 
            from translations.translations tr
            where link = '%s' ;""" % (link)
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{'error': 'Текст не найден!', 'details': ''}]
    except psycopg2.Error as e: 
        f.get_db().rollback()
        result = [{'error': f.QUERY_ERR, 'details': str(e)}]
    finally:
        cur.close()
    return render_template('single_tr.html', content=result[0])

def get_translations_list():
    cur = f.get_db().cursor()
    sql = """\
            select tr.uid, tr.engname, tr.runame, tr.link
            from translations.translations tr
            order by tr.engname;"""
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{'error': 'Переводов не найдено!', 'details': ''}]
    except psycopg2.Error as e: 
        f.get_db().rollback()
        result = [{'error': f.QUERY_ERR, 'details': str(e)}]
    finally:
        cur.close()
    return result