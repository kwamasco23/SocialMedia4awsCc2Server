from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(min=3)]
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=4)]
    )

    submit = SubmitField('Register')


class LoginForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[InputRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired()]
    )

    submit = SubmitField('Login')


class PostForm(FlaskForm):

    content = TextAreaField(
        'Post',
        validators=[InputRequired()]
    )

    image = FileField('Image')

    submit = SubmitField('Post')


class EditProfileForm(FlaskForm):

    bio = TextAreaField('Bio')

    profile_pic = FileField('Profile Picture')

    submit = SubmitField('Save')