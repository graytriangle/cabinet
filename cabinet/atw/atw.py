# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, redirect, make_response, jsonify
from flask import render_template
import psycopg2
import uuid
from cabinet import functions as f
from flask_login import login_required, current_user
from cabinet import auth

atw = Blueprint('atw', __name__, template_folder='templates', static_folder='static', 
	static_url_path='/atw/static', subdomain="almostthewords")

##################
# VIEW FUNCTIONS #
##################

@atw.route('/', methods=['GET'])
def translations_mainpage():
    return render_template('translations.html', list=get_translations_list(), authors=get_authors(), tags=get_tags(), linkname='')

@atw.route('/add', methods=['GET'])
@login_required
@auth.requires_permission('translator')
def translations_addpage():
    return render_template('create_tr.html', content=None)

@atw.route('/edit/<string:link>', methods=['GET'])
@login_required
@auth.requires_permission('translator')
def translations_editpage(link):
    # get translation by name
    cur = f.get_db().cursor()
    sql = """\
            select tr.uid, tr.engname, tr.runame, tr.original, tr.translation, tr.footnotes, tr.comment,
            a.author, a.link as authorlink, json_agg(t) filter (where t.uid is not null) as tags  
            from translations.translations tr
            left join translations.authors a
            on tr.author = a.uid
            left join translations.translations_tags tt
            on tr.uid = tt.translation
            left join translations.tags t
            on t.uid = tt.tag
            where tr.deleted = false
            and tr.link = '%s' 
            GROUP BY tr.uid, a.uid;""" % (link)
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

@atw.route('/save', methods=['POST'])
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
    author = request.form['author']
    authoruid = None
    tags = request.form['tags']
    comment = request.form['comment']

    if (uid == ""):
        uid = str(uuid.uuid4())

    cur = f.get_db().cursor()
    sql = """\
            select uid, link from translations.translations
            where link = '%s' ;""" % (link)
    try:
        cur.execute(sql)

        # checking if a translation with identical name exists
        result = f.dictfetchall(cur)
        if result and result[0]['uid'] != uid:
            # if we have a different translation with identical name, just slap random uuid on the link to make it unique
            link = link + str(uuid.uuid4())

        if author:
            authorlink = author.lower().replace(' ', '-')
            authoruid = str(uuid.uuid4())
            # checking if author exists
            cur.execute("SELECT uid from translations.authors "
                "where author = %s ;", (author,))
            result = f.dictfetchall(cur)
            if result:
                authoruid = result[0]['uid']
            else:
                cur.execute("INSERT INTO translations.authors (uid, author, link) "
                    "VALUES (%s, %s, %s);", (authoruid, author, authorlink))

        cur.execute("INSERT INTO translations.translations (uid, engname, runame, original, translation, link, footnotes, author, comment) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (uid) DO UPDATE SET engname=excluded.engname, runame=excluded.runame, "
            "original=excluded.original, translation=excluded.translation, link=excluded.link, footnotes=excluded.footnotes, "
            "author=excluded.author, comment=excluded.comment;", 
            (uid, engname, runame, original, translation, link, footnotes, authoruid, comment))

        if tags:
            tagarray = tags.split(',')
            tagarray = [i.strip() for i in tagarray]
            tagarray = [i for i in tagarray if i] # removing empty strings
            cur.execute("DELETE FROM translations.translations_tags WHERE translation = %s;", (uid,))
            for tag in tagarray:
                taglink = tag.lower().replace(' ', '-')
                # taguid = str(uuid.uuid4())
                cur.execute("INSERT INTO translations.tags (tag, link) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (tag, taglink))
                cur.execute("SELECT uid FROM translations.tags WHERE tag = %s;", (tag,))
                taguid = cur.fetchone()[0]
                cur.execute("INSERT INTO translations.translations_tags (translation, tag) "
                        "VALUES (%s, %s);", (uid, taguid))
        
        f.get_db().commit()
    finally:
        cur.close()
    return redirect('/' + link)

@atw.route('/delete/<string:link>', methods=['GET'])
@login_required
@auth.requires_permission('translator')
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

@atw.route('/<string:link>', methods=['GET'])
def translations_page(link):
    return render_template('translations.html', list=get_translations_list(), authors=get_authors(), tags=get_tags(), linkname=link)

@atw.route('/get/<string:link>', methods=['GET'])
def get_translation(link):
    # get translation by name
    cur = f.get_db().cursor()
    sql = """\
            select tr.engname, tr.runame, tr.original, tr.translation, tr.footnotes, tr.comment,
            a.author, a.link as authorlink, json_agg(t) filter (where t.uid is not null) as tags
            from translations.translations tr
            left join translations.authors a
            on tr.author = a.uid
            left join translations.translations_tags tt
            on tr.uid = tt.translation
            left join translations.tags t
            on t.uid = tt.tag
            where tr.link = '%s' 
            GROUP BY tr.uid, a.uid;""" % (link)
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

def get_authors():
    cur = f.get_db().cursor()
    sql = """\
            select distinct a.uid, a.author, a.link
            from translations.authors a
            inner join translations.translations tr
            on a.uid = tr.author
            where tr.deleted = false
            order by a.author;"""
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{'error': 'Авторов не найдено!', 'details': ''}]
    except psycopg2.Error as e: 
        f.get_db().rollback()
        result = [{'error': f.QUERY_ERR, 'details': str(e)}]
    finally:
        cur.close()
    return result

def get_tags():
    cur = f.get_db().cursor()
    sql = """\
            select distinct t.uid, t.tag, t.link
            from translations.tags t
            inner join translations.translations_tags tt
            on t.uid = tt.tag
            inner join translations.translations tr
            on tt.translation = tr.uid
            where tr.deleted = false
            order by t.tag;"""
    try:
        cur.execute(sql)
        result = f.dictfetchall(cur)
        if not result:
            result = [{'error': 'Тэгов не найдено!', 'details': ''}]
    except psycopg2.Error as e: 
        f.get_db().rollback()
        result = [{'error': f.QUERY_ERR, 'details': str(e)}]
    finally:
        cur.close()
    return result