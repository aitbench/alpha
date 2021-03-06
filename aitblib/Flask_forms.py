from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.


class RegisterForm(FlaskForm):
    name = TextField(
        'Username', validators=[DataRequired(), Length(min=2, max=25)]
    )
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
         EqualTo('password', message='Passwords must match')]
    )


class LoginForm(FlaskForm):
    name = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])


class ForgotForm(FlaskForm):
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )


class SetupForm(FlaskForm):
    dbtype = SelectField(
        'DB Type', choices=[('mysql', 'MySQL'), ('postgresql', 'PostgreSQL'), ('oracle', 'Oracle')]
    )
    hostname = TextField(
        'Hostname', validators=[DataRequired(), Length(min=2, max=25)]
    )
    database = TextField(
        'Database', validators=[DataRequired(), Length(min=2, max=25)]
    )
    uname = TextField(
        'Username', validators=[DataRequired(), Length(min=2, max=25)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
