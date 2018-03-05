"""
It's often very useful to look at other people's code to learn new and effective ways to program!

But not here. This file contains some pretty wacky stuff, which shouldn't be used in
real production code. It works for this small case, but doesn't scale well, is hard to debug, and generally
is not optimal.
"""

from random import choice

from flask import Flask, render_template, redirect, url_for, request, flash, session
from wtforms import Form, StringField, PasswordField, TextAreaField, validators

from exercise_queries import (
    get_newest_tweets, search_for_tweets, get_user, create_user, validate_login, post_tweet, get_user_tweets,
    validate_and_perform_user_changes, get_user_name, get_user_followers
)

app = Flask(__name__)
messages = [
    "Make sure to get the latest from you!",
    "There are exactly the same tweets here as last time. Predictability and consistency is gold!",
    "There are only quality tweets when no one else can post.",
]


class RegisterForm(Form):
    username = StringField(
        'Username ',
        validators=[validators.input_required(message='Must provide a username!'), validators.length(min=4, max=100)]
    )
    email = StringField(
        'Email ', validators=[validators.input_required(message='Must provide an email!')]
    )
    age = StringField(
        'Age', validators=[]
    )
    password = PasswordField(
        'Password',
        validators=[validators.input_required(message='Must provide a password!')]
    )
    confirm = PasswordField(
        'Confirm', validators=[
            validators.input_required(message='Must confirm password!'),
            validators.equal_to('password', message="Password didn't match!")
        ]
    )


class ChangeInfoForm(Form):
    username = StringField(
        'Change username ',
        validators=[validators.length(min=4, max=100)]
    )
    email = StringField(
        'Change email ', validators=[]
    )
    age = StringField(
        'Change age', validators=[]
    )
    password = PasswordField(
        'Change password',
        validators=[]
    )
    confirm = PasswordField(
        'Confirm with current password', validators=[
            validators.input_required(message='Must approve changes with your password!'),
        ]
    )


class LoginForm(Form):
    email = StringField(
        'Email ', validators=[validators.input_required(message='Must provide username')]
    )
    password = PasswordField(
        'Password', validators=[validators.input_required(message='Must provide password')]
    )


class SearchForm(Form):
    username = StringField('', validators=[validators.input_required(message='Cannot search for nothing...')])


class TweetForm(Form):
    content = TextAreaField(
        '', validators=[
            validators.input_required(message='Cannot post emtpy tweets...'),
            validators.length(min=1, max=144)
        ]
    )



@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm(request.form)

    if request.method == 'POST' and form.validate():
        return redirect(url_for('tweets_search', search=form.username.data))
    else:
        if session['logged_in']:
            tweets = get_user_tweets(session['userID'])
            followers = get_user_followers(session['userID'])
            return render_template('home.html', form=form, tweets=chunks(tweets, 3), message=choice(messages), followers=followers)
        else:
            tweets = get_newest_tweets(9)
            return render_template('home.html', form=form, tweets=chunks(tweets, 3), message='A place where you can send tweets by yourself, to yourself!', followers=[])



@app.route('/tweets/search=<string:search>', methods=['GET', 'POST'])
def tweets_search(search):
    form = TweetForm(request.form)

    if request.method == 'POST' and form.validate():
        if session['logged_in']:
            post_tweet(session['userID'], form.content.data)
            flash('Your tweet has been posted!', 'success')
            return redirect(url_for('tweets_'))
        else:
            flash('You must be logged in to post a tweet.', 'danger')
            return redirect(url_for('login'))

    tweets = search_for_tweets(search)
    followers = get_user_followers(session['userID'])
    return render_template('tweets.html', form=form, tweets=chunks(tweets, 3), followers=followers)


@app.route('/tweets', methods=['GET', 'POST'])
def tweets_():
    form = TweetForm(request.form)

    if request.method == 'POST' and form.validate():
        if session['logged_in']:
            post_tweet(session['userID'], form.content.data)
            flash('Your tweet has been posted!', 'success')
            return redirect(url_for('tweets_'))
        else:
            flash('You must be logged in to post a tweet.', 'danger')
            return redirect(url_for('login'))

    tweets = get_newest_tweets(9)
    followers = get_user_followers(session['userID'])
    return render_template('tweets.html', form=form, tweets=chunks(tweets, 3), followers=followers)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        create_user(form.username.data, form.password.data, form.email.data, form.age.data)
        flash('Welcome! Try to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():

        result = validate_login(form.email.data, form.password.data)

        if result == 1:
            session['logged_in'] = True
            session['userID'] = get_user(form.email.data)
            session['username'] = get_user_name(session['userID'])
            flash('You were successfully logged in.', 'success')
            return redirect(url_for('home'))
        elif result == 0:
            flash('Invalid password.', 'danger')
        elif result == -1:
            flash('Invalid email.', 'danger')
        else:
            pass

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    flash("You've logged out.", 'success')
    session['logged_in'] = False
    session['userID'] = None
    session['username'] = None
    return redirect(url_for('home'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():

    if not session['logged_in']:
        flash('No!', 'danger')
        return redirect(url_for('home'))

    form = ChangeInfoForm(request.form)

    if request.method == 'POST' and form.validate():

        result = validate_and_perform_user_changes(
            session['userID'], form.confirm.data, form.username.data, form.email.data, form.age.data, form.password.data
        )

        if result:
            flash('Changed made!', 'success')
        else:
            flash('Wrong password!', 'danger')

    return render_template('settings.html', form=form)


def chunks(sequence, n):
    for i in range(0, len(sequence), n):
        yield sequence[i:i + n]


def run(file=None):

    if file:
        import file

    app.secret_key = 'some_secret'
    app.run(debug=True)


if __name__ == '__main__':
    run()