"""
We use simple forms in this tutorial, but a more common practice is to use an ORM, which generates code to the database
based on the model of the forms (like Django's 'Model' class). However, it would be quite a boring SQL-course without
having to write any SQL. Just take in mind that the lack of an ORM makes it harder to synchronize the fields of the
application with the fields of the database.

Currently, we've just hardcoded the fields and restrictions.
"""
from wtforms import Form, StringField, PasswordField, TextAreaField, validators


class RegisterForm(Form):
    username = StringField(
        'Username ',
        validators=[validators.input_required(message='Must provide a username!'), validators.length(min=1, max=144)]
    )
    email = StringField(
        'Email ',
        validators=[validators.input_required(message='Must provide an email!'), validators.length(min=1, max=144)]
    )
    age = StringField(
        'Age',
        validators=[]
    )
    password = PasswordField(
        'Password',
        validators=[validators.input_required(message='Must provide a password!'), validators.length(min=1, max=144)]
    )
    confirm = PasswordField(
        'Confirm',
        validators=[
            validators.input_required(message='Must confirm password!'),
            validators.equal_to('password', message="Password didn't match!")
        ]
    )


class ChangeInfoForm(Form):
    username = StringField(
        'Change username ',
        validators=[validators.length(min=1, max=144)]
    )
    email = StringField(
        'Change email ',
        validators=[validators.length(max=144)]
    )
    age = StringField(
        'Change age',
        validators=[]
    )
    password = PasswordField(
        'Change password',
        validators=[validators.length(max=144)]
    )
    confirm = PasswordField(
        'Confirm with current password',
        validators=[
            validators.input_required(message='Must approve changes with your password!')
        ]
    )


class LoginForm(Form):
    email = StringField(
        'Email ',
        validators=[validators.input_required(message='Must provide username')]
    )
    password = PasswordField(
        'Password',
        validators=[validators.input_required(message='Must provide password')]
    )


class SearchForm(Form):
    username = StringField(
        '',
        validators=[validators.input_required(message='Cannot search for nothing...')]
    )


class TweetForm(Form):
    post = TextAreaField(
        '',
        validators=[
            validators.input_required(message='Cannot post emtpy tweets...'),
            validators.length(min=1, max=144)
        ]
    )
