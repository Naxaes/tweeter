import os
import re
from urllib   import request
from datetime import datetime, timedelta
from random   import random, randrange, randint, choice

# Third-party python packages.
from passlib.hash import sha256_crypt

SQL_CREATE_FILE_TEMPLATE = """
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Tweets CASCADE;
DROP TABLE IF EXISTS Followers CASCADE;
DROP TABLE IF EXISTS Passwords CASCADE;


CREATE TABLE Users (
	userID   SERIAL PRIMARY KEY,
	username VARCHAR(50) NOT NULL,
	email    VARCHAR(255) UNIQUE NOT NULL,
	age      INTEGER CONSTRAINT over_zero_years_old CHECK(age > 0)
);


CREATE TABLE Tweets (
	tweetID     SERIAL PRIMARY KEY,
	posterID    INTEGER REFERENCES Users(userID) ON DELETE CASCADE,
	content     VARCHAR(144),
	time_posted TIMESTAMP NOT NULL
);


CREATE TABLE Followers (
	userID     INTEGER REFERENCES Users(userID) ON DELETE CASCADE,
	followerID INTEGER REFERENCES Users(userID) ON DELETE CASCADE,

    PRIMARY KEY (userID, followerID),
    CONSTRAINT cant_follow_oneself CHECK (userID != followerID)
);


CREATE TABLE Passwords (
    userID   INTEGER REFERENCES Users(userID) ON DELETE CASCADE PRIMARY KEY,
    password VARCHAR(144) NOT NULL
);



\copy Users(username, email, age) FROM '{userdata}' USING DELIMITERS ',';
\copy Tweets(posterID, content, time_posted) FROM '{tweetdata}' USING DELIMITERS ',';
\copy Followers(userID, followerID) FROM '{followerdata}' USING DELIMITERS ',';
\copy Passwords(userID, password) FROM '{passworddata}' USING DELIMITERS ',';
"""

URL_TO_ENGLISH_WORDS = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'
NAMES   = [
    'transportwildcat', 'wrapteal', 'listenseagull', 'peerswallow', 'admireowl', 'shrugbuzzard', 'orderoxbird',
    'requestlion', 'operatewildebeest', 'yodelplover', 'hidechamois', 'minehamster', 'scrapegoldfinch',
    'volunteersheldrake', 'entertainsnail', 'severblackbird', 'causekookaburra', 'commenttuna', 'bleachraven',
    'wishptarmigan', 'fearpheasant', 'avowlemur', 'borroweland', 'tossdoves'
]
DOMAINS = ['@hotmail.com', '@kth.se', '@gmail.com', '@msn.com']


def random_bool(percentage):
    return random() < percentage


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def random_mail(words):
    email = ''
    for _ in range(1, int(random() * 4) + 2):
        email += words[int(random() * (len(words) - 1))]
    re.sub(r'\W+', '', email)
    email += choice(DOMAINS)
    return email


def random_message(words, max_character_count, min_word_count=5, max_word_count=30):
    punctuation = ['!', '.', '...', '?', '']
    word_list = []
    word_count = randint(min_word_count, max_word_count)

    for _ in range(word_count):
        word_index = randint(0, len(words) - 1)
        word_list.append(words[word_index])
    word_list.append(choice(punctuation))

    message = ' '.join(word_list)

    if len(message) > max_character_count:
        message = message[0:max_character_count]

    return message


def users_data_file(filename, names, words):
    with open(filename, 'w') as datafile:
        for i, name in enumerate(names):
            username = name
            email = random_mail(words)
            age = int(random() * 100) + 1

            datafile.write('{},{},{}\n'.format(username, email, age))


def tweets_data_file(filename, number_of_posters, words):
    with open(filename, 'w') as datafile:

        d1 = datetime.strptime('2008-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        d2 = datetime.now()

        poster_id = 1
        for _ in range(number_of_posters):
            number_of_tweets = randint(1, 10)
            for _ in range(number_of_tweets):
                content = random_message(words, 144)
                time_posted = random_date(d1, d2)

                datafile.write('{},{},{}\n'.format(poster_id, content, time_posted))

            poster_id += 1
            if poster_id > number_of_posters:
                return


def followers_data_file(filename, number_of_users):
    with open(filename, 'w') as datafile:
        following_percentage = 0.6

        for userID in range(1, number_of_users+1):
            for followerID in range(1, number_of_users+1):
                if random() < following_percentage and userID != followerID:
                    datafile.write('{},{}\n'.format(userID, followerID))


def passwords_data_file(filename, names):
    with open(filename, 'w') as datafile:
        for i, name in enumerate(names, start=1):
            password = sha256_crypt.hash(name[0:4])
            datafile.write('{},{}\n'.format(i, password))


def sql_create_file_and_data(root):
    root_directory  = root
    data_directory  = os.path.join(root_directory, 'data')

    user_data_path  = os.path.join(data_directory, 'users_data.txt')
    tweet_data_path = os.path.join(data_directory, 'tweets_data.txt')
    follower_data_path = os.path.join(data_directory, 'followers_data.txt')
    password_data_path = os.path.join(data_directory, 'passwords_data.txt')
    sql_create_path = os.path.join(data_directory, 'create.sql')

    if os.path.isdir(data_directory):
        print("The data directory already exist! Delete it in order to create a new one.")
        return
    else:
        os.mkdir(data_directory)

    random_words = request.urlopen(URL_TO_ENGLISH_WORDS).read().decode('utf-8').split('\n')

    users_data_file(user_data_path, NAMES, random_words)
    tweets_data_file(tweet_data_path, len(NAMES), random_words)
    followers_data_file(follower_data_path, len(NAMES))
    passwords_data_file(password_data_path, NAMES)

    sql_create_file_content = SQL_CREATE_FILE_TEMPLATE.format(
        userdata=user_data_path,
        tweetdata=tweet_data_path,
        followerdata=follower_data_path,
        passworddata=password_data_path
    )

    with open(sql_create_path, 'w') as datafile:
        datafile.write(sql_create_file_content)
