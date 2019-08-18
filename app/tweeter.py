"""
NOTE: The flask server is supplied by Werkzeug, which loads your application twice in debug mode. This is to enable it
      to reload your server when the code changes without having to completely restart the server. However, this means
      that any code you have in the top-level will be run twice. Shouldn't cause any problem however, but is something
      to be aware about.


It's often very useful to look at other people's code to learn new and effective ways to program!

But not here. This file contains things that shouldn't be used in real production code. It works for this small case,
but doesn't scale well, is hard to debug, and generally is not optimal.
"""
# Built-in python packages
from random      import choice
from collections import namedtuple

# Third-party python packages
from flask import Flask, render_template, redirect, url_for, request, flash, session

# Project python packages
# This import can be switched between 'database_exercise' and 'database.py' in order to test your implementation
# against the expected implementation.
from database_exercise import (
    get_newest_tweets, search_for_tweets, get_user, create_user, validate_login, save_tweet,
    validate_and_perform_user_changes, get_user_by_ID, get_user_followers, get_followers_tweets, add_follower,
    remove_follower, remove_tweet
)
from forms import SearchForm, LoginForm, RegisterForm, TweetForm, ChangeInfoForm


# Due to the global session variable changing the type to an regular tuple (for some reason ...), this User class
# converts it back to a named tuple. A bit of hardcoding going on here so a more sophisticated solution should
# be used in production code. However, this is sufficient for this simple program.
User = namedtuple('User', 'userID, username, email, age')


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
non_logged_in_messages = 'Look at the Postgres-elephant/Twitter-bird hybrid. Look at it!'


class NotLoggedInException(Exception):
    """Raised when someone currently not logged in is trying to access a page that requires log in"""


class DatabaseException(Exception):
    """Raised when the database yields invalid results"""


@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm(request.form)

    # The use either did a search or interacted with a tweet.
    if request.method == 'POST':
        url_redirect_request = dispatch_tweet_actions(request.form)
        if url_redirect_request:
            return url_redirect_request
        elif form.validate():
            return redirect(url_for('tweets', search=form.username.data))
        else:
            # Either the tweet action or the form was invalid, or the tweet action was valid but didn't require any
            # redirection. Anyway, continue to render as if no POST request happened.
            # The other functions should notify the user on invalid data, so no feedback is necessary here.
            pass

    if session.get('logged_in'):
        user   = User(*session['user'])
        tweets = get_followers_tweets(user.userID)
        followers = get_user_followers(user.userID)
        return render_template(
            'home.html',
            form=form,
            tweets=chunks(tweets, 3),
            message=choice(logged_in_messages),
            followers=followers
        )
    else:
        tweets = get_newest_tweets(9)
        return render_template(
            'home.html',
            form=form,
            tweets=chunks(tweets, 3),
            message=non_logged_in_messages,
            followers=[]
        )


@app.route('/tweets', methods=['GET', 'POST'])
@app.route('/tweets/search=<string:search>', methods=['GET', 'POST'])
def tweets(search=None):
    form = TweetForm(request.form)

    if request.method == 'POST':
        url_redirect_request = dispatch_tweet_actions(request.form)
        if url_redirect_request:
            return url_redirect_request
        else:
            # Either the tweet action was invalid or the tweet action was valid but didn't require any redirection.
            # Anyway, continue to render as if no POST request happened.
            # The other functions should notify the user on invalid data, so no feedback is necessary here.
            pass

    if search:
        tweets = search_for_tweets(search)

        # Only notify first time we're getting the page.
        if request.method == 'GET':
            if len(tweets) == 0:
                flash('No tweets found!', 'danger')
            else:
                flash('{number} tweets found!'.format(number=len(tweets)), 'success')
    else:
        tweets = get_newest_tweets(9)

    if session.get('logged_in'):
        user = User(*session['user'])
        followers = get_user_followers(user.userID)
        return render_template('tweets.html', form=form, tweets=chunks(tweets, 3), followers=followers)
    else:
        return render_template('tweets.html', form=form, tweets=chunks(tweets, 3), followers=[])


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
            flash("Couldn't create user!", 'danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        result = validate_login(form.email.data, form.password.data)

        if result == 1:
            session['user']      = get_user(form.email.data)
            session['logged_in'] = True
            flash('You were successfully logged in.', 'success')
            return redirect(url_for('home'))
        elif result == 0:
            flash('Invalid password.', 'danger')
        elif result == -1:
            flash('Invalid email.', 'danger')
        else:
            raise DatabaseException('Invalid result from "validate_login"!')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    flash("You've logged out.", 'success')
    session['logged_in'] = False
    session['user']      = None
    session.clear()
    return redirect(url_for('home'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # This page is only available for logged in users.
    if not session.get('logged_in'):
        flash('No! Bad!', 'danger')
        return redirect(url_for('home'))

    form = ChangeInfoForm(request.form)

    if request.method == 'POST' and form.validate():
        user_id = session['user'][0]
        result = validate_and_perform_user_changes(
            user_id, form.confirm.data, form.username.data, form.email.data, form.age.data, form.password.data
        )

        if result:
            session['user'] = get_user_by_ID(user_id)  # Update the session to hold the new values for the user.
            flash('Change made!', 'success')
        else:
            flash('Wrong password or invalid data!', 'danger')

    return render_template('settings.html', form=form)


def post_tweet(content):
    if session.get('logged_in'):
        user = User(*session['user'])
        if save_tweet(user.userID, content):
            flash('Your tweet has been posted!', 'success')
            return redirect(url_for('tweets'))
        else:
            raise DatabaseException("Tweet couldn't be posted!")
    else:
        raise NotLoggedInException('You must be logged in to post a tweet.')


def follow_user(user_to_follow):
    if session.get('logged_in'):
        user = User(*session['user'])
        if not add_follower(user.userID, user_to_follow):
            raise DatabaseException("Couldn't follow user!")
        else:
            other_user = User(*get_user_by_ID(user_to_follow))
            flash('Successfully followed {user}!'.format(user=other_user.username), 'success')
    else:
        raise NotLoggedInException('You must be logged in to follow a user.')


def unfollow_user(user_to_unfollow):
    if session.get('logged_in'):
        user = User(*session['user'])
        if not remove_follower(user.userID, user_to_unfollow):
            raise DatabaseException("Couldn't unfollow user!")
        else:
            other_user = User(*get_user_by_ID(user_to_unfollow))
            flash('Successfully unfollowed {user}!'.format(user=other_user.username), 'success')
    else:
        raise NotLoggedInException('You must be logged in to unfollow a user.')


def delete_tweet(tweet):
    if session.get('logged_in'):
        if not remove_tweet(tweet):
            raise DatabaseException("Couldn't delete tweet!")
        flash('Tweet deleted.', 'success')
    else:
        raise NotLoggedInException("You can only delete your tweets if you're logged in.")


def dispatch_tweet_actions(form):
    """
    Checks the tweet actions 'follow', 'unfollow', 'delete' and 'post', and returns the appropriate redirection, or None if no
    redirection is needed.
    """
    actions = { 'follow': follow_user, 'unfollow': unfollow_user, 'delete': delete_tweet, 'post': post_tweet }

    for name, func in actions.items():
        argument = form.get(name)
        if argument:
            try:
                return func(argument)
            except DatabaseException as error:
                flash(str(error), 'danger')
                return None
            except NotLoggedInException as error:
                flash(str(error), 'danger')
                return redirect(url_for('login'))
    return None


def get_logged_in_user():
    """
    Due to the global session variable changing the type to an regular tuple (for some reason ...), this tuple
    converts it back to a named tuple. A bit of hardcoding going on here so a more sophisticated solution should
    be used in production code. However, this is sufficient for this simple program.
    """
    user_class = namedtuple('User', 'userID, username, email, age')
    return user_class(*session['user'])


def chunks(sequence, n):
    for i in range(0, len(sequence), n):
        yield sequence[i:i + n]


if __name__ == '__main__':
    app.run()
