from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    """
    Describes the user credentials form in the frontend for signup and login
    """
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign me up')


class PostForm(FlaskForm):
    """
    Describes the post text form in the frontend
    """
    post_text = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Post')


class RateForm(FlaskForm):
    """
    Describes the 'like and dislike forms' in the frontend for post rating
    """
    post_id = HiddenField()  # a hidden field for render post_id value
    like = HiddenField()  # a hidden field for render like 0 or 1 value
