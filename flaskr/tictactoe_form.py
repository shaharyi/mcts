from flask_wtf import FlaskForm
from wtforms import FieldList, SubmitField

N = 3


class TictactoeForm(FlaskForm):
    buttons = FieldList(SubmitField(''), min_entries=N * N)
