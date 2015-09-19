from flask.ext.sqlalchemy import SQLAlchemy
from . import db, twitter
from datetime import datetime
from colour import Color

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(512))
    color = db.Column(db.String(20))

    def __init__(self, name, description, color):
        self.name = name
        self.description = description
        self.color = color.hex

    def get_color(self):
        return Color(self.color)

class LoggedExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_session = db.Column(db.Integer, db.ForeignKey('workout_session.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
    exercise = db.relationship("Exercise", uselist=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)

    def __init__(self, exercise_id, sets, reps, weight):
        self.exercise_id = exercise_id
        self.sets = sets
        self.reps = reps
        self.weight = weight


class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship("User", uselist=False)
    logged_exercises = db.relationship("LoggedExercise", backref=db.backref("session", uselist=False), cascade="all, delete-orphan")


    def __init__(self, owner_id, log_time):
        self.owner_id = owner_id
        self.datetime = log_time


    @classmethod
    def new_today(cls, owner_id):
        return cls(owner_id, datetime.today())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    twitter_name = db.Column(db.String(50))
    twitter_id = db.Column(db.Integer, unique=True)
    twitter_profile_img = db.Column(db.String(256))
    twitter_oauth_token = db.Column(db.Text())
    twitter_oauth_token_secret = db.Column(db.Text())


    def __init__(self, resp, oauth_token, oauth_token_secret ):
        self.twitter_name = resp.data['screen_name']
        self.twitter_id = resp.data['id']
        self.twitter_profile_img = resp.data.get('profile_image_url', None)
        self.set_twitter_oauth(oauth_token, oauth_token_secret)


    def set_twitter_oauth(self, oauth_token, oauth_token_secret):
        self.twitter_oauth_token = oauth_token
        self.twitter_oauth_token_secret = oauth_token_secret


    @classmethod
    def fetch_and_create(cls, user_id, oauth_token, oauth_token_secret):
        userResp = twitter.get('users/show.json', data={
            'user_id':   user_id
        })

        if userResp.status == 403:
            return None

        return cls(userResp, oauth_token, oauth_token_secret)