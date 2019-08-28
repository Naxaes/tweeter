# ---- AUTO-GENERATED ----
from wtforms import Form, StringField, PasswordField, TextAreaField, IntegerField, validators


USERNAME_LENGTH_VALIDATOR = validators.length(
        min=4,
        max=32,
        message='Username must be between %(min)s and %(max)s!'
    )
USER_AGE_RANGE_VALIDATOR = validators.NumberRange(
        min=0,
        max=150,
        message='Is that really your age? We only allow people between %(min)s and %(max)s.'
    )
PASSWORD_LENGTH_VALIDATOR = validators.length(
        min=4,
        max=32,
        message='Password must be between %(min)s and %(max)s characters!'
    )
TWEET_LENGTH_VALIDATOR  = validators.length(
        min=4,
        max=144,
        message='Tweet must be between %(min)s and %(max)s characters!'
    )


class RegisterForm(Form):
    username = StringField(
        label='Username',
        validators=[
            USERNAME_LENGTH_VALIDATOR,
            validators.input_required(message='Username must be provided!')
        ]
    )
    email = StringField(
        label='Email',
        validators=[
            validators.Email(message='Email is invalid!'),
            validators.input_required(message='Email must be provided!'),
        ]
    )
    age = IntegerField(
        label='Age',
        validators=[
            validators.Optional(),
            USER_AGE_RANGE_VALIDATOR
        ]
    )
    password = PasswordField(
        label='Password',
        validators=[
            validators.input_required(message='Password must be provided!'),
            PASSWORD_LENGTH_VALIDATOR
        ]
    )
    confirm = PasswordField(
        label='Confirm',
        validators=[
            validators.input_required(message='Must confirm password!'),
            validators.equal_to(fieldname='password', message="Passwords didn't match!")
        ]
    )


class ChangeInfoForm(Form):
    username = StringField(
        label='New username ',
        validators=[validators.Optional(), USERNAME_LENGTH_VALIDATOR]
    )
    email = StringField(
        label='New email ',
        validators=[validators.Optional(), validators.Email(message='Email is invalid!')]
    )
    age = IntegerField(
        label='New age',
        validators=[validators.Optional(), USER_AGE_RANGE_VALIDATOR]
    )
    password = PasswordField(
        label='New password',
        validators=[validators.Optional(), PASSWORD_LENGTH_VALIDATOR]
    )
    confirm = PasswordField(
        label='Confirm with current password',
        validators=[
            validators.input_required(message='Password is required to approve changes!')
        ]
    )


class LoginForm(Form):
    email = StringField(
        label='Email ',
        validators=[
            validators.Email(message='Email is invalid!'),
            validators.input_required(message='Must provide username')
        ]
    )
    password = PasswordField(
        label='Password',
        validators=[
            PASSWORD_LENGTH_VALIDATOR,
            validators.input_required(message='Must provide password')
        ]
    )


class SearchForm(Form):
    search = StringField(label='Search')


class TweetForm(Form):
    post = TextAreaField(validators=[TWEET_LENGTH_VALIDATOR])

