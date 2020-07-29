from flask_wtf import FlaskForm
from wtforms import FieldList,  SubmitField

N = 3


class UltimateTictactoeForm(FlaskForm):
    submit= SubmitField('')
