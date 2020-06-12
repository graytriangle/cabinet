# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, redirect, make_response, jsonify
from flask import render_template
import psycopg2
import uuid
# from cabinet import app
from cabinet import functions as f
from flask_login import login_required, current_user
from cabinet import auth

translations = Blueprint('translations', __name__, template_folder='templates', static_folder='static', 
	static_url_path='/translations/static', subdomain="translations")

##################
# VIEW FUNCTIONS #
##################

@translations.route('/', methods=['GET'])
@login_required
@auth.requires_permission('translator')
def translations_mainpage():
    return render_template('translations.html', list=get_translations_list(), linkname='')

@translations.route('/add', methods=['GET'])
@login_required
@auth.requires_permission('translator')
def translations_addpage():
    return render_template('create_tr.html', content=None)

@translations.route('/edit/<string:link>', methods=['GET'])
@login_required
def translations_editpage(link):
    # get translation by name
    cur = f.get_db().cursor()
    sql = """\
            select tr.uid, tr.engname, tr.runame, tr.original, tr.translation, tr.footnotes 
            from translations.translations tr
            where tr.deleted = false
            and link = '%s' ;""" % (link)
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
    return render_template('create_tr.html', content=result[0])

@translations.route('/save', methods=['POST'])
@login_required
@auth.requires_permission('translator')
def save_translation():
    uid = request.form['uid']
    engname = request.form['engname']
    runame = request.form['runame']
    original = request.form['original']
    translation = request.form['translation']
    link = engname.lower().replace(' ', '-')
    footnotes = request.form['footnotes']

    if (uid == ""):
        uid = str(uuid.uuid4())

    cur = f.get_db().cursor()
    sql = """\
            select link from translations.translations
            where link = '%s' ;""" % (link)
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if result:
            # if we have a translation with identical name, just slap random uuid on the link to make it unique
            link = link + str(uuid.uuid4())
        cur.execute("INSERT INTO translations.translations (uid, engname, runame, original, translation, link, footnotes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (uid) DO UPDATE SET engname=excluded.engname, runame=excluded.runame, "
            "original=excluded.original, translation=excluded.translation, link=excluded.link, footnotes=excluded.footnotes;", 
            (uid, engname, runame, original, translation, link, footnotes))
        f.get_db().commit()
    finally:
        cur.close()
    return redirect('/' + link)

@translations.route('/delete/<string:link>', methods=['GET'])
@login_required
def delete_translation(link):
    cur = f.get_db().cursor()
    try:
        cur.execute("UPDATE translations.translations SET deleted = true, datedel = now() WHERE link = %s; ", (link,))
        f.get_db().commit()
    except psycopg2.Error as e: 
        f.get_db().rollback()
        return make_response(jsonify({'error': f.QUERY_ERR, 'details': str(e)}), 500)
    finally:
        cur.close()
    return '', 204 # the "it's done" response

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
            select tr.engname, tr.runame, tr.original, tr.translation, tr.footnotes 
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
            where tr.deleted = false
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