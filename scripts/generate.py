import os
import shutil
from urllib   import request
from datetime import datetime, timedelta
from random   import random, randrange, randint, choice, choices

from dateutil.relativedelta import relativedelta

# Third-party python package.
from passlib.hash import sha256_crypt


USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 32
PASSWORD_MIN_LENGTH = 4
PASSWORD_MAX_LENGTH = 32
TWEET_MIN_LENGTH = 4
TWEET_MAX_LENGTH = 144
USER_MIN_AGE = 0
USER_MAX_AGE = 150

EMAIL_MIN_LENGTH = 4
EMAIL_MAX_LENGTH = 144


PSQL_CREATE_FILE_TEMPLATE = f"""\
DROP TABLE IF EXISTS users     CASCADE;
DROP TABLE IF EXISTS tweets    CASCADE;
DROP TABLE IF EXISTS followers CASCADE;
DROP TABLE IF EXISTS passwords CASCADE;


CREATE TABLE users (
	user_id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	username TEXT NOT NULL CONSTRAINT invalid_username_length CHECK(LENGTH(username) BETWEEN {USERNAME_MIN_LENGTH} AND {USERNAME_MAX_LENGTH}),
	email    TEXT UNIQUE NOT NULL CONSTRAINT invalid_email CHECK(email LIKE '%@%.%'),
	age      INTEGER CONSTRAINT invalid_age CHECK(age BETWEEN {USER_MIN_AGE} AND {USER_MAX_AGE})
);


CREATE TABLE tweets (
	tweet_id    INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	poster_id   INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
	content     TEXT NOT NULL CONSTRAINT invalid_tweet_length CHECK(LENGTH(content) BETWEEN {TWEET_MIN_LENGTH} AND {TWEET_MAX_LENGTH}),
	time_posted TIMESTAMP NOT NULL
);


CREATE TABLE followers (
	user_id     INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
	follower_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,

	PRIMARY KEY (user_id, follower_id)
);


CREATE TABLE passwords (
    user_id  INTEGER REFERENCES users(user_id) ON DELETE CASCADE PRIMARY KEY,
    -- The length of the password shouldn't be checked, as we'll not store it in plain text. 
    -- Thus, the stored password length will differ from the actual password length.
    password TEXT NOT NULL
);



\copy users(username, email, age)             FROM '{{userdata}}'     USING DELIMITERS ',';
\copy tweets(poster_id, content, time_posted) FROM '{{tweetdata}}'    USING DELIMITERS ',';
\copy followers(user_id, follower_id)         FROM '{{followerdata}}' USING DELIMITERS ',';
\copy passwords(user_id, password)            FROM '{{passworddata}}' USING DELIMITERS ',';
"""

FORMS_TEMPLATES = f"""\
# ---- AUTO-GENERATED ----
from wtforms import Form, StringField, PasswordField, TextAreaField, IntegerField, validators


USERNAME_LENGTH_VALIDATOR = validators.length(
        min={USERNAME_MIN_LENGTH},
        max={USERNAME_MAX_LENGTH},
        message='Username must be between %(min)s and %(max)s!'
    )
USER_AGE_RANGE_VALIDATOR = validators.NumberRange(
        min={USER_MIN_AGE},
        max={USER_MAX_AGE},
        message='Is that really your age? We only allow people between %(min)s and %(max)s.'
    )
PASSWORD_LENGTH_VALIDATOR = validators.length(
        min={PASSWORD_MIN_LENGTH},
        max={PASSWORD_MAX_LENGTH},
        message='Password must be between %(min)s and %(max)s characters!'
    )
TWEET_LENGTH_VALIDATOR  = validators.length(
        min={TWEET_MIN_LENGTH},
        max={TWEET_MAX_LENGTH},
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

"""


# Site with random words to generate text from.
URL_TO_ENGLISH_WORDS = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'

# Some random words if the url goes down or the connection won't work.
RANDOM_WORDS = [
    'armitas', 'spinto', 'waddler', 'grapnel', 'amphid', 'copalm', 'asquint', 'heils', 'refine', 'pippins', 'tells',
    'esne', 'greeter', 'humming', 'acrobat', 'subeth', 'jatoba', 'thummin', 'frower', 'wee', 'twills', 'roelike',
    'kraal', 'woolmen', 'washes', 'anadem', 'amental', 'effund', 'lanais', 'flub', 'faceoff', 'cupful', 'axin',
    'khis', 'cadelle', 'liposis', 'steid', 'kudos', 'apast', 'conceit', 'flarer', 'rapt', 'yelper', 'horntip',
    'rammer', 'cista', 'compt', 'tipiti', 'minge', 'genappe', 'globby', 'reecho', 'ruboffs', 'kymnel', 'inkbush',
    'applot', 'veldman', 'facings', 'sethead', 'sejero', 'respice', 'probant', 'townee', 'sith', 'preppie', 'leeched',
    'bumwood', 'dister', 'didder', 'bemercy', 'rabbish', 'analav', 'soodled', 'signify', 'hairse', 'strowed',
    'cyclope', 'tigerly', 'commem', 'purvoe', 'kadsura', 'pawns', 'furmity', 'pelting', 'goodbye', 'gipser', 'boa',
    'unmaid', 'belayer', 'strew', 'mamsell', 'kirkify', 'none', 'finew', 'cadrans', 'enfrai', 'deeds',
    'hyperintelligence', 'lawfullness', 'rageless', 'essayers', 'twirliest'
]

NAMES   = [
    'transportwildcat', 'wrapteal', 'listenseagull', 'peerswallow', 'admireowl', 'shrugbuzzard', 'orderoxbird',
    'requestlion', 'operatewildebeest', 'yodelplover', 'hidechamois', 'minehamster', 'scrapegoldfinch',
    'volunteersheldrake', 'entertainsnail', 'severblackbird', 'causekookaburra', 'commenttuna', 'bleachraven',
    'wishptarmigan', 'fearpheasant', 'avowlemur', 'borroweland', 'tossdoves'
]
DOMAINS = ['@hotmail.com', '@kth.se', '@gmail.com', '@msn.com']


def random_bool(percentage=0.5):
    return random() < percentage


def random_date(start, end):
    delta = end - start
    seconds_between_start_and_end = delta.total_seconds()
    random_seconds = randrange(seconds_between_start_and_end)
    return start + timedelta(seconds=random_seconds)


def random_mail(words, domains):
    email = choice(words) + '@' + choice(domains)
    return email


def random_message(words, max_character_count, min_word_count=5, max_word_count=18):
    punctuation = ['!', '.', '...', '?', '']
    word_count = randint(min_word_count, max_word_count)

    word_list = [word for word in choices(words, k=word_count)]
    message = ' '.join(word_list) + choice(punctuation)

    if len(message) > max_character_count:
        message = message[0:max_character_count]

    return message


def users_data_file(filename, names, domains, words, user_min_age, user_max_age):
    with open(filename, 'w') as datafile:
        for name in names:
            username = name
            email    = random_mail(words, domains)
            age      = randint(user_min_age, user_max_age)

            datafile.write('{},{},{}\n'.format(username, email, age))


def tweets_data_file(filename, number_of_posters, max_tweet_length, words):
    with open(filename, 'w') as datafile:

        end_time   = datetime.now()
        start_time = end_time - relativedelta(years=5)

        for poster_id in range(1, number_of_posters+1):
            number_of_tweets = randint(1, 10)
            for _ in range(number_of_tweets):
                content     = random_message(words, max_character_count=max_tweet_length)
                time_posted = random_date(start_time, end_time)

                datafile.write('{},{},{}\n'.format(poster_id, content, time_posted))



def followers_data_file(filename, number_of_users):
    with open(filename, 'w') as datafile:
        for user_id in range(1, number_of_users+1):
            for follower_id in range(1, number_of_users+1):
                if user_id != follower_id and random_bool(percentage=0.6):
                    datafile.write('{},{}\n'.format(user_id, follower_id))


def passwords_data_file(filename, names):
    with open(filename, 'w') as datafile:
        for password_id, name in enumerate(names, start=1):
            password = sha256_crypt.hash(name[0:4])
            datafile.write('{},{}\n'.format(password_id, password))


def ask_for_confirmation(message, yes='y', no='n'):
    answer = input(message)
    while answer not in (yes, no):
        answer = input("Please type '{yes}' for yes or '{no}' for no. ".format(yes=yes, no=no))
    return answer


def sql_create_file_and_data(root, data_directory_name='data'):
    root_directory  = root
    data_directory  = os.path.join(root_directory, data_directory_name)

    user_data_path  = os.path.join(data_directory, 'users_data.txt')
    tweet_data_path = os.path.join(data_directory, 'tweets_data.txt')
    follower_data_path = os.path.join(data_directory, 'followers_data.txt')
    password_data_path = os.path.join(data_directory, 'passwords_data.txt')
    sql_create_path = os.path.join(data_directory, 'create.sql')

    try:
        os.mkdir(data_directory)
    except FileExistsError:
        answer = ask_for_confirmation(f"The directory '{data_directory}' already exist! Do you want to override it? (y/n): ")
        if answer == 'n':
            return
        else:
            shutil.rmtree(data_directory)
            os.mkdir(data_directory)

    try:
        random_words = request.urlopen(URL_TO_ENGLISH_WORDS).read().decode('utf-8').split('\n')
    except:  # I know, I'm catching all exceptions... I'm disgusting.
        random_words = RANDOM_WORDS

    users_data_file(user_data_path, NAMES, DOMAINS, random_words, USER_MIN_AGE, USER_MAX_AGE)
    tweets_data_file(tweet_data_path, len(NAMES), TWEET_MAX_LENGTH, random_words)
    followers_data_file(follower_data_path, len(NAMES))
    passwords_data_file(password_data_path, NAMES)

    sql_create_file_content = PSQL_CREATE_FILE_TEMPLATE.format(
        userdata=user_data_path,
        tweetdata=tweet_data_path,
        followerdata=follower_data_path,
        passworddata=password_data_path
    )

    with open(sql_create_path, 'w') as datafile:
        datafile.write(sql_create_file_content)


def forms_file(root, form_file_name='forms.py'):
    root_directory = root
    file_path = os.path.join(root_directory, form_file_name)

    if not os.path.isdir(root_directory):
        os.mkdir(root_directory)

    if os.path.isfile(file_path):
        answer = ask_for_confirmation(f"The file '{file_path}' already exist. Do you want to override it? (y/n) ")
        if answer == 'n':
            return

    with open(file_path, 'w') as datafile:
        datafile.write(FORMS_TEMPLATES)
