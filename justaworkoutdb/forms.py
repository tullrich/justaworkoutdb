from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, DateField, FormField, IntegerField, FieldList
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import html_params, HTMLString, ListWidget, HiddenInput
from flask import get_template_attribute
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import Exercise
from datetime import datetime


class HiddenQuerySelectField(QuerySelectField):
    """
    HiddenField is a convenience for a QuerySelectField with a HiddenInput widget.

    It will render as an ``<input type="hidden">`` but otherwise coerce to the provided Model.
    """
    widget = HiddenInput()

    def _value(self):
        if self._formdata is not None:
            return self._formdata
        elif self.data is not None:
            return self.data.id
        else:
            return ''


class AddExerciseForm(Form):
    name = StringField('Exercise Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Exercise Description', validators=[Optional(), Length(max=512)])

class LoggedExerciseForm(Form):

    exercise = HiddenQuerySelectField('Exercise'
                            , validators=[DataRequired()]
                            , query_factory=Exercise.query.all
                            , get_pk=lambda a: a.id
                            , get_label=lambda a: a.name)
    sets = IntegerField('Sets', validators=[DataRequired(), NumberRange(min=1, max=1024)], default=1)
    reps = IntegerField('Reps', validators=[DataRequired(), NumberRange(min=1, max=1024)], default=1)
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=0, max=2000)], default=1)

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
    datetime = DateField('Log Date', validators=[DataRequired()], format='%Y-%m-%d')
    logged_exercises = FieldList(FormField(LoggedExerciseForm, widget=LogItemWidget()), validators=[DataRequired(), Length(min=1)], widget=LogListWidget())

    def __init__(self, *args, **kwargs):
        super(AddWorkoutSessionForm, self).__init__(*args, **kwargs)

        if self.datetime.data is None:
            self.datetime.data = datetime.today()