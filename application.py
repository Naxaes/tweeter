"""
It's often very useful to look at other people's code to learn new and effective ways to program!

But not here. This file contains things that shouldn't be used in real production code. It works for this small case,
but doesn't scale well, is hard to debug, and generally is not optimal.
"""
# Built-in python packages
from random import choice

# Third-party python packages
from flask import Flask, render_template, redirect, url_for, request, flash, session

# Project python packages
# This import can be switched between 'exercise_queries' and 'solution_queries.py' in order to test your implementation
# against the expected implementation.
from solution_queries import (
    get_newest_tweets, search_for_tweets, get_user, create_user, validate_login, post_tweet,
    validate_and_perform_user_changes, get_user_by_ID, get_user_followers, get_followers_tweets, add_follower,
    remove_follower, remove_tweet
)
from views import SearchForm, LoginForm, RegisterForm, TweetForm, ChangeInfoForm


# Initialize Flask.
# The secret key is used to sign cookies cryptographically. It should be a something hard to figure out.
app = Flask(__name__)
app.secret_key = b'\x8c\xdb#g\x9c\x0ecf-^A\xda\xc6\x10pY'
app.debug = True

# Some fun messages to show to the users.
logged_in_messages = [
    'A place where you can send tweets by yourself, to yourself!',
    "Make sure to get the latest from you!",
    "There are exactly the same tweets here as last time. Predictability and consistency is gold!",
    "There are only quality tweets when no one else can post.",
]
non_logged_in_messages = 'Please take some time to appreciate the Postgres elephant and Twitter bird hybrid abomination.'


class NotLoggedInException(Exception):
    """Raised when someone currently not logged in is trying to access a page that requires log in"""


class DatabaseException(Exception):
    """Raised when the database yields invalid results"""


@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm(request.form)

    # The use either did a search or interacted with a tweet.
    if request.method == 'POST':
        try:
            dispatched = dispatch_request(request.form, follow=follow_user, unfollow=unfollow_user, delete=delete_tweet)
        except (NotLoggedInException, DatabaseException):
            return redirect(url_for('login'))
        else:
            if not dispatched and form.validate():
                return redirect(url_for('tweets_search', search=form.username.data))

    if session.get('logged_in'):
        user_id = session['user'][0]
        tweets  = get_followers_tweets(user_id)
        followers = get_user_followers(user_id)
        return render_template('home.html', form=form, tweets=chunks(tweets, 3), message=choice(logged_in_messages), followers=followers)
    else:
        tweets = get_newest_tweets(18)
        return render_template('home.html', form=form, tweets=chunks(tweets, 3), message=non_logged_in_messages, followers=[])


@app.route('/tweets/search=<string:search>', methods=['GET', 'POST'])
def tweets_search(search):
    return render_tweet_page(search)


@app.route('/tweets', methods=['GET', 'POST'])
def default_tweet_page():
    return render_tweet_page()


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        if create_user(form.username.data, form.password.data, form.email.data, form.age.data):
            flash('Welcome! Try to log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Something went wrong!', 'danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        result = validate_login(form.email.data, form.password.data)

        if result == 1:
            session['user'] = get_user(form.email.data)
            session['logged_in'] = True
            flash('You were successfully logged in.', 'success')
            return redirect(url_for('home'))
        elif result == 0:
            flash('Invalid password.', 'danger')
        elif result == -1:
            flash('Invalid email.', 'danger')
        else:
            raise DatabaseException('Invalid result from "validate_login".')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    flash("You've logged out.", 'success')
    session['logged_in'] = False
    session['user'] = None
    session.clear()
    return redirect(url_for('home'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get('logged_in'):
        flash('No!', 'danger')
        return redirect(url_for('home'))

    form = ChangeInfoForm(request.form)

    if request.method == 'POST' and form.validate():
        user_id = session['user'][0]
        result = validate_and_perform_user_changes(
            user_id, form.confirm.data, form.username.data, form.email.data, form.age.data, form.password.data
        )

        if result:
            session['user'] = get_user_by_ID(user_id)
            flash('Change made!', 'success')
        else:
            flash('Wrong password!', 'danger')

    return render_template('settings.html', form=form)


def render_tweet_page(search=None):
    form = TweetForm(request.form)

    if request.method == 'POST':
        try:
            completed = dispatch_request(request.form, follow=follow_user, unfollow=unfollow_user, delete=delete_tweet)
            if not completed:
                validate_tweet_form(form)
        except (NotLoggedInException, DatabaseException):
            return redirect(url_for('login'))

    if search:
        tweets = search_for_tweets(search)
        if len(tweets) == 0:
            flash('No tweets found!', 'danger')
        else:
            flash('{number} tweets found!'.format(number=len(tweets)), 'success')
    else:
        tweets = get_newest_tweets(18)

    if session.get('logged_in'):
        user_id = session['user'][0]
        followers = get_user_followers(user_id)
        return render_template('tweets.html', form=form, tweets=chunks(tweets, 3), followers=followers)
    else:
        return render_template('tweets.html', form=form, tweets=chunks(tweets, 3), followers=[])


def follow_user(user_to_follow):
    if session.get('logged_in'):
        user_id = session['user'][0]
        if not add_follower(user_id, user_to_follow):
            flash('Something went wrong!', 'danger')
        else:
            flash('Successfully followed {user}!'.format(user=get_user_by_ID(user_to_follow)[1]), 'success')
    else:
        flash('You must be logged in to follow a user.', 'danger')
        raise NotLoggedInException()


def unfollow_user(user_to_unfollow):
    if session.get('logged_in'):
        user_id = session['user'][0]
        if not remove_follower(user_id, user_to_unfollow):
            flash('Something went wrong!', 'danger')
        else:
            flash('Successfully unfollowed {user}!'.format(user=get_user_by_ID(user_to_unfollow)[1]), 'success')
    else:
        flash('You must be logged in to unfollow a user.', 'danger')
        raise NotLoggedInException()


def delete_tweet(tweet):
    if not remove_tweet(tweet):
        flash('Something went wrong!', 'danger')
        raise DatabaseException()
    flash('Tweet deleted.', 'success')


def validate_tweet_form(form):
    if form.validate():
        if session.get('logged_in'):
            user_id = session['user'][0]
            if post_tweet(user_id, form.content.data):
                flash('Your tweet has been posted!', 'success')
            else:
                flash('Something went wrong!', 'danger')
        else:
            flash('You must be logged in to post a tweet.', 'danger')
            raise NotLoggedInException()


def dispatch_request(form, **kwargs):
    """Checks if the given form contains any of the names provided, and if so calls the provided function."""
    completed = False
    for name, function in kwargs.items():
        argument = form.get(name)
        if argument:
            function(argument)
            completed = True
    return completed


def chunks(sequence, n):
    for i in range(0, len(sequence), n):
        yield sequence[i:i + n]


if __name__ == '__main__':
    app.run()
