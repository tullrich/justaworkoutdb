from flask import session, redirect, url_for, g
from functools import wraps
from contextlib import closing
from justaworkoutdb import app
from sqlite3 import dbapi2 as sqlite3
from .models import User

def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('logged_on') and session.get('user_id'):
            user = User.query.filter_by(id=session['user_id']).first()
            if user:
                g.user = user
                return f(*args, **kwargs)

        return redirect(url_for('login'))
    return decorated


def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


@app.template_filter(name='datetime')
def format_datetime(value):
    return value.strftime('%Y-%m-%d')