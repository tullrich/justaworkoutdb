from flask import Flask, session, g
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from colour import Color

app = Flask(__name__)

# Configuration
app.config.from_pyfile('config.cfg')
app.secret_key  = app.config['SECRET_KEY']
oauth           = OAuth()
db              = SQLAlchemy(app)
twitter         = oauth.remote_app('twitter',
    base_url            = 'https://api.twitter.com/1.1/',
    request_token_url   = 'https://api.twitter.com/oauth/request_token',
    access_token_url    = 'https://api.twitter.com/oauth/access_token',
    authorize_url       = 'https://api.twitter.com/oauth/authenticate',
    consumer_key        = app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret     = app.config['TWITTER_CONSUMER_SECRET']
)

# Global after-request operation.
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Required by flask.ext.oauth.
@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


# Must happen after app is created above.
from . import utility, forms, views, models