from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    source = StringField('Source', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    date_from = DateTimeField(
        label='Date From',
        format='%Y-%m-%d',
        validators=[DataRequired()])
    date_from = DateTimeField(
        label='Date From',
        format='%Y-%m-%d',
        validators=[DataRequired()])
    date_to = DateTimeField(
        label='Date To',
        format='%Y-%m-%d',
        validators=[DataRequired()])
