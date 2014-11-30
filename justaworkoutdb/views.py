from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from utility import requires_login, init_db, connect_db, get_db
from justaworkoutdb import app, twitter, db
from .forms import AddExerciseForm, AddWorkoutSessionForm
from .models import Exercise, WorkoutSession, User, LoggedExercise

@app.route('/')
@requires_login
def home():
    db = get_db()
    cur = db.execute('select name, description from exercises order by id asc')
    entries = cur.fetchall()
    return render_template('home.html', entries=entries)


@app.route('/workouts')
@requires_login
def workouts():
    workouts = WorkoutSession.query.filter_by(owner_id=g.user.id).all()
    return render_template('workouts.html', workouts=workouts)


@app.route('/workouts/add', methods=['GET', 'POST'])
@requires_login
def add_workout():
    form = AddWorkoutSessionForm()
    form.logged_exercises[0].logged_exercise_id.choices = [(e.id, e.name) for e in Exercise.query.order_by('name')]

    if request.method == 'POST':
        if form.validate_on_submit():
            workout = WorkoutSession(g.user.id, form.date_logged.data)

            for form_log_item in form.logged_exercises.entries:
                logged_item = LoggedExercise(form_log_item.logged_exercise_id.data)
                workout.logged_exercises.append(logged_item)

            db.session.add(workout)
            db.session.commit()

            flash('Workout session added!', category='success')
            return redirect(url_for('workouts'))

    exercises = Exercise.query.all()
    return render_template('workouts_add.html', form=form, exercises=exercises)


@app.route('/exercises')
@requires_login
def exercises():
    exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=exercises)


@app.route('/exercise/add', methods=['GET', 'POST'])
@requires_login
def add_exercise():
    form = AddExerciseForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            exercise = Exercise(form.name.data, form.description.data, form.img.data)
            db.session.add(exercise)
            db.session.commit()

            flash('Exercise added!', category='success')
            return redirect(url_for('exercises'))

    return render_template('exercise_add.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' or request.args.get('useTwitter', False):
        session.pop('twitter_token', None)
        session.pop('user_id', None)
        session.pop('logged_on', None)
        return twitter.authorize(callback=url_for('oauth_authorized'))

    if session.get('logged_on'):
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('twitter_token', None)
    session.pop('user_id', None)
    session.pop('logged_on', None)
    return redirect(url_for('login'))


@app.route('/authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('home')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    usr = User.query.filter_by(twitter_id=resp['user_id']).first()

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )

    if usr == None:
        usr = User.fetch_and_create(resp['user_id'], resp['oauth_token'], resp['oauth_token_secret'])

        if usr == None:
            flash(u'Could not fetch twitter user.')
            return redirect(next_url)

        db.session.add(usr)

    usr.set_twitter_oauth(resp['oauth_token'], resp['oauth_token_secret'])
    db.session.commit()

    session['user_id'] = usr.id
    session['logged_on'] = True
    return redirect(url_for('exercises'))
