from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,TextAreaField)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError)
from app.models import User
from flask_wtf.file import FileAllowed, FileField

class RegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[
        DataRequired(), Length(max=16)])
    lastName = StringField('Last Name', validators=[
                           DataRequired(), Length(max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[
                                    DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign up')

    # Function to make a custom error validation message
    def validate_username(self, field):
        user = User.query.filter_by(UserName=field.data).first()

        if user:
            raise ValidationError("Username is already taken.")

    def validate_email(self, field):
        user = User.query.filter_by(Email=field.data).first()

        if user:
            raise ValidationError("Email is already taken.")

class InterestForm(FlaskForm):
    chess = BooleanField('Interested in Chess')
    sudoku = BooleanField('Interested in Sudoku')
    crosswords = BooleanField('Interest in Chess')
    job = BooleanField('Interested in Job')
    volunteer = BooleanField('Interested in Volunteer')
    dating = BooleanField('Interested in Dating')


class SearchForm(FlaskForm):
    inp = StringField('Search Email...', validators=[
        DataRequired()] )
    submit = SubmitField('Search')

class FamilyForm(FlaskForm):
    postImage = FileField('Add Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class JobForm(FlaskForm):
    postImage = FileField('Add Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class VolunteerForm(FlaskForm):
    postImage = FileField('Add Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class LivingForm(FlaskForm):
    postImage = FileField('Add Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class QuestionForm(FlaskForm):
    postImage = FileField('Add Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


