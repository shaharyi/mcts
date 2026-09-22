from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField


class TicTacToe3DForm(FlaskForm):
    pressed_z = HiddenField('pressed_z')
    pressed_r = HiddenField('pressed_r')
    pressed_c = HiddenField('pressed_c')
    submit = SubmitField('')