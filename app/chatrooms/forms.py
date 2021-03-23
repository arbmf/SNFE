from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField


class NewChatroom(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])


class NewChat(FlaskForm):
    title = StringField('Message', validators=[DataRequired()])
