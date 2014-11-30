from flask import current_app
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, DateField, FormField, IntegerField, FieldList, SelectField
from wtforms.validators import DataRequired, Length, URL, NumberRange
from wtforms.widgets import html_params, HTMLString, ListWidget
from wtforms.compat import text_type
from flask_wtf.form import _is_hidden
from flask import get_template_attribute

class AddExerciseForm(Form):
    name = StringField('Exercise Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Exercise Description', validators=[DataRequired(), Length(max=512)])
    img = StringField('Exercise Image', validators=[DataRequired(), URL(), Length(max=256)])

class LoggedExerciseForm(Form):
    logged_exercise_name = StringField('Exercise Name', validators=[Length(max=50)])
    logged_exercise_id = SelectField('Logged Exercise Id', validators=[DataRequired()], coerce=int)
    sets = IntegerField('Sets', validators=[DataRequired(), NumberRange(min=1)], default=1)
    reps = IntegerField('Reps', validators=[DataRequired(), NumberRange(min=1)], default=1)

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(LoggedExerciseForm, self).__init__(*args, **kwargs)

class LogItemWidget(object):
    def __call__(self, field, **kwargs):
        logged_exercise_widget = get_template_attribute('widgets.html', 'logged_exercise_widget')
        html = logged_exercise_widget(field)
        return HTMLString(html)

class LogListWidget(ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
                html.append('<li>%s</li>' % subfield())
        html.append('</%s>' % self.html_tag)
        return HTMLString(''.join(html))

class AddWorkoutSessionForm(Form):
    date_logged = DateField('Date Logged', validators=[DataRequired()], format='%Y-%m-%d')
    logged_exercises = FieldList(FormField(LoggedExerciseForm, widget=LogItemWidget()), min_entries=1, widget=LogListWidget())
