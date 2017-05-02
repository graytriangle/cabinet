from flask import Flask
from flask import g
from flask import render_template
from flask import request
import sqlite3

DATABASE = 'D:\example.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

app = Flask(__name__)

@app.route('/')
def test():
    cur = get_db().cursor()
    result = []
    for row in cur.execute('''SELECT ROWID, record FROM testrecords'''):
        result.append(row)
    return render_template('input.html', data=result)

@app.route('/', methods=['POST'])
def my_form_post():
    text = (request.form['add'],)
    cur = get_db().cursor()
    cur.execute('''INSERT INTO testrecords VALUES (?)''', text)
    get_db().commit()
    return test()

@app.route('/delete', methods=['GET'])
def delete():
    rowid = (request.args.get('rowid', ''),)
    cur = get_db().cursor()
    cur.execute('''DELETE FROM testrecords WHERE ROWID = ?''', rowid)
    get_db().commit()
    return test()

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()