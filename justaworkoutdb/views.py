from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from utility import requires_login, init_db, connect_db, get_db
from justaworkoutdb import app, twitter, db
from .forms import AddExerciseForm, AddWorkoutSessionForm
from .models import Exercise, WorkoutSession, User, LoggedExercise

@app.route('/')
@requires_login
def home():
    return redirect(url_for('workouts'))


@app.route('/workouts')
@requires_login
def workouts():
    workouts = WorkoutSession.query.filter_by(owner_id=g.user.id).order_by(WorkoutSession.datetime.desc())
    return render_template('workouts.html', workouts=workouts)

@app.route('/workouts/<id>/edit', methods=['GET', 'POST'])
@requires_login
def edit_workout( id ):
    workout_session = WorkoutSession.query.filter_by(id=id).first()

    if workout_session is None:
        # If this was a submission throw up an error.
        if request.method == 'POST':
            flash('Unable to modify workout! Maybe it no longer exists?', category='error')
        return redirect(url_for('workouts'))

    # Edit submission.
    if request.method == 'POST':
        # on POST we fill with the form data.
        form = AddWorkoutSessionForm()
        if form.validate_on_submit():

            # Delete the existing workout_session
            db.session.delete(workout_session)
            db.session.commit()

            # Add the new one
            workout = WorkoutSession(g.user.id, form.datetime.data)

            for form_log_item in form.logged_exercises.entries:
                logged_item = LoggedExercise(form_log_item.exercise.data.id
                                             , form_log_item.sets.data
                                             , form_log_item.reps.data)
                workout.logged_exercises.append(logged_item)

            db.session.add(workout)
            db.session.commit()

            flash('Workout modified!', category='success')
            return redirect(url_for('workouts'))
    else:
        # on GET use the queried Model.
        form = AddWorkoutSessionForm(formdata=None, obj=workout_session)

    exercises = Exercise.query.all()
    return render_template('workouts_add.html', form=form, exercises=exercises, isEdit=True, workout=workout_session)

@app.route('/workouts/add', methods=['GET', 'POST'])
@requires_login
def add_workout():
    form = AddWorkoutSessionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            workout = WorkoutSession(g.user.id, form.datetime.data)

            for form_log_item in form.logged_exercises.entries:
                logged_item = LoggedExercise(form_log_item.exercise.data.id
                                             , form_log_item.sets.data
                                             , form_log_item.reps.data)
                workout.logged_exercises.append(logged_item)

            db.session.add(workout)
            db.session.commit()

            flash('Workout session added!', category='success')
            return redirect(url_for('workouts'))

    exercises = Exercise.query.all()
    return render_template('workouts_add.html', form=form, exercises=exercises)

@app.route('/workouts/remove', methods=['POST'])
@requires_login
def remove_workout():
    workout_id = request.form['id']
    response = jsonify(id=workout_id)

    workout_session = WorkoutSession.query.filter_by(id=workout_id, owner_id=g.user.id).first()
    if workout_session:
        db.session.delete(workout_session)
        db.session.commit()
    else:
        response.status_code = 500

    return response

@app.route('/exercises')
@requires_login
def exercises():
    exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=exercises)


@app.route('/exercises/add', methods=['GET', 'POST'])
@requires_login
def add_exercise():
    form = AddExerciseForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            exercise = Exercise(form.name.data, form.description.data)
            db.session.add(exercise)
            db.session.commit()

            flash('Exercise added!', category='success')
            return redirect(url_for('exercises'))

    return render_template('exercise_add.html', form=form)

@app.route('/exercises/remove', methods=['POST'])
@requires_login
def remove_exercise():
    exercise_id = request.form['id']
    response = jsonify(id=exercise_id)

    exercise = Exercise.query.filter_by(id=exercise_id).first()
    if exercise:
        try:
            LoggedExercise.query.filter_by(exercise=exercise).delete(synchronize_session=False)
            WorkoutSession.query.filter(~WorkoutSession.logged_exercises.any()).delete(synchronize_session=False)
            db.session.delete(exercise)
            db.session.commit()
        except:
            db.session.rollback()
            raise
    else:
        response.status_code = 500

    return response


@app.route('/exercises/<id>/edit', methods=['GET', 'POST'])
@requires_login
def edit_exercise( id ):
    exercise = Exercise.query.filter_by(id=id).first()

    if exercise is None:
        # If this was a submission throw up an error.
        if request.method == 'POST':
            flash('Unable to modify exercise! Maybe it no longer exists?', category='error')
        return redirect(url_for('exercises'))

    # Edit submission.
    if request.method == 'POST':
        # on POST we fill with the form data.
        form = AddExerciseForm()
        if form.validate_on_submit():

            # Modify the existing exercise
            exercise.name = form.name.data
            exercise.description = form.description.data
            db.session.commit()

            flash('Exercise modified!', category='success')
            return redirect(url_for('exercises'))
    else:
        # on GET use the queried Model.
        form = AddExerciseForm(formdata=None, obj=exercise)

    return render_template('exercise_add.html', form=form, isEdit=True, exercise=exercise)

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
