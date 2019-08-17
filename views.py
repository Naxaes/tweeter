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
    content = TextAreaField(
        '',
        validators=[
            validators.input_required(message='Cannot post emtpy tweets...'),
            validators.length(min=1, max=144)
        ]
    )
