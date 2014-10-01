from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, ValidationError
from wtforms.validators import Required, Email, Regexp
from project.apps.auth.models import User_auth as User


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class AddUser(Form):
    username = TextField('Username', validators=[Required()])
    name = TextField('Name', validators=[Required()])
    family = TextField('Family', validators=[Required()])
    email = StringField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    #, Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')
    #role_id = SelectField('role_id', validators=[Required()])
    submit = SubmitField('Sign Up')


def validate_email(self, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Email already registered.')


class AddRole(Form):
    role_name = TextField('name', validators=[Required()])
    submit = SubmitField('Add Role')