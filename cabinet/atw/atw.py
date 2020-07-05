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

@atw.route('/author/<string:author>', methods=['GET'])
@atw.route('/tag/<string:tag>', methods=['GET'])
def translations_filtered_mainpage(author=None, tag=None):
    return render_template('translations.html', list=get_translations_list(author, tag), authors=get_authors(), tags=get_tags(), linkname='')

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
            select tr.uid, tr.link, tr.engname, tr.runame, tr.original, tr.translation, tr.footnotes, tr.comment, tr.video, 
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
    engname = request.form['engname'].strip()
    runame = request.form['runame'].strip()
    original = request.form['original']
    translation = request.form['translation']
    link = request.form['link']
    footnotes = request.form['footnotes']
    author = request.form['author'].strip()
    authoruid = None
    tags = request.form['tags']
    comment = request.form['comment']
    video = request.form['video']

    if (uid == ""):
        uid = str(uuid.uuid4())

    if (link == ""):
        link = f.sanitize_url(engname, 64)
        if not link: # in case there's nothing left after sanitizing
            link = str(uuid.uuid4())

    cur = f.get_db().cursor()
    sql = """\
            select uid from translations.translations
            where link = '%s' ;""" % (link)
    try:
        cur.execute(sql)

        # checking if a translation with identical name exists
        result = cur.fetchone()
        if result and result[0] != uid:
            # if we have a different translation with identical name, just slap random uuid on the link to make it unique
            link = link + str(uuid.uuid4())

        if author:
            authorlink = f.sanitize_url(author, 64)
            if not authorlink: # in case there's nothing left after sanitizing
                authorlink = str(uuid.uuid4())
            authoruid = str(uuid.uuid4())
            # checking if author exists
            cur.execute("SELECT uid from translations.authors "
                "where author = %s ;", (author,))
            result = cur.fetchone()
            if result: # if he does we use UID from db
                authoruid = result[0]
            else:
                # if he doesn't we check if link exists
                # (possible when two authors differ by capitalization or spaces)
                cur.execute("SELECT uid from translations.authors "
                "where link = %s ;", (authorlink,))
                if cur.fetchone():
                    # if we have a different author with identical link, just slap random uuid on the link to make it unique
                    authorlink = authorlink + str(uuid.uuid4())
                cur.execute("INSERT INTO translations.authors (uid, author, link) "
                    "VALUES (%s, %s, %s);", (authoruid, author, authorlink))

        cur.execute("INSERT INTO translations.translations (uid, engname, runame, original, translation, link, footnotes, author, comment, video) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (uid) DO UPDATE SET engname=excluded.engname, runame=excluded.runame, "
            "original=excluded.original, translation=excluded.translation, link=excluded.link, footnotes=excluded.footnotes, "
            "author=excluded.author, comment=excluded.comment, video=excluded.video;", 
            (uid, engname, runame, original, translation, link, footnotes, authoruid, comment, video))

        if tags:
            tagarray = tags.split(',')
            tagarray = [i.strip() for i in tagarray]
            tagarray = [i for i in tagarray if i] # removing empty strings
            cur.execute("DELETE FROM translations.translations_tags WHERE translation = %s;", (uid,))
            for tag in tagarray:
                taglink = f.sanitize_url(tag, 64)
                if not taglink: # in case there's nothing left after sanitizing
                    taglink = str(uuid.uuid4())
                taguid = str(uuid.uuid4())
                # checking if tag exists
                cur.execute("SELECT uid from translations.tags "
                    "where tag = %s ;", (tag,))
                result = cur.fetchone()
                if result: # if it does we use UID from db
                    taguid = result[0]
                else:
                    # if it doesn't we check if link exists
                    # (possible when two tags differ by capitalization or spaces)
                    cur.execute("SELECT uid from translations.tags "
                    "where link = %s ;", (taglink,))
                    if cur.fetchone():
                        # if we have a different tag with identical link, just slap random uuid on the link to make it unique
                        taglink = taglink + str(uuid.uuid4())
                    cur.execute("INSERT INTO translations.tags (uid, tag, link) "
                        "VALUES (%s, %s, %s);", (taguid, tag, taglink))
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

@atw.route('/get/song/<string:link>', methods=['GET'])
def get_translation(link):
    # get translation by name
    cur = f.get_db().cursor()
    sql = """\
            select tr.engname, tr.link, tr.runame, tr.original, tr.translation, tr.footnotes, tr.comment, tr.video, 
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

@atw.route('/get/author/<string:author>', methods=['GET'])
@atw.route('/get/tag/<string:tag>', methods=['GET'])
@atw.route('/get/all', methods=['GET'])
def get_translations_list(author=None, tag=None):
    cur = f.get_db().cursor()
    where = ''
    filter = None
    filtername = None
    if author:
        filter = 'author'
        where = "and a.link = '%s'" % author.replace("'", "''")
        cur.execute("SELECT author from translations.authors "
                "where link = %s ;", (author,))
        result = f.dictfetchall(cur)
        if result:
            filtername = result[0]['author']
    elif tag: # it's either author or tag, not both
        filter = 'tag'
        where = "and t.link = '%s'" % tag.replace("'", "''")
        cur.execute("SELECT tag from translations.tags "
                "where link = %s ;", (tag,))
        result = f.dictfetchall(cur)
        if result:
            filtername = result[0]['tag']
    sql = """\
            select distinct tr.uid, tr.engname, tr.runame, tr.link
            from translations.translations tr
            left join translations.authors a
            on tr.author = a.uid
            left join translations.translations_tags tt
            on tr.uid = tt.translation
            left join translations.tags t
            on t.uid = tt.tag
            where tr.deleted = false
            %s
            order by tr.engname;""" % (where,)
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
    # flask 1.1 feature: any dict gets converted into json response on endpoint function call
    return {'filter': filter, 'filtername': filtername, 'response': result}

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