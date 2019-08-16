"""
Run this file to install all libraries needed to run the application, and to create data
files. You'll need access to internet in order to run this file successfully.
"""
from install import install_libraries_with_pip, LIBRARIES

install_libraries_with_pip(LIBRARIES)   # Install all necessary libraries before continuing.

# Built-in python packages.
from urllib import request
from random import random, choice, randint
from random import randrange
from datetime import datetime, timedelta
import os
import re

# Third-party python packages.
from passlib.hash import sha256_crypt


CURRENT_DIRECTORY = os.getcwd()
DATA_PATH  = os.path.join(CURRENT_DIRECTORY, 'data')
USER_DATA  = os.path.join(DATA_PATH, 'users_data.txt')
TWEET_DATA = os.path.join(DATA_PATH, 'tweets_data.txt')
FOLLOWER_DATA   = os.path.join(DATA_PATH, 'followers_data.txt')
PASSWORD_DATA   = os.path.join(DATA_PATH, 'passwords_data.txt')
SQL_CREATE_FILE = os.path.join(DATA_PATH, 'create.sql')

SQL_CREATE_FILE_TEMPLATE = """
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Tweets CASCADE;
DROP TABLE IF EXISTS Followers CASCADE;
DROP TABLE IF EXISTS Passwords CASCADE;


CREATE TABLE Users (
	userID   SERIAL PRIMARY KEY,
	username VARCHAR(144) NOT NULL,
	email    VARCHAR(144) UNIQUE NOT NULL,
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

	PRIMARY KEY (userID, followerID)
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
NAMES = [
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

    message = ''.join(word_list)

    if len(message) > max_character_count:
        message = message[0:max_character_count]

    return message


def create_users_data_file(filename, names, words):
    with open(filename, 'w') as datafile:
        for i, name in enumerate(names):
            username = name
            email = random_mail(words)
            age = int(random() * 100) + 1

            datafile.write('{},{},{}\n'.format(username, email, age))


def create_tweets_data_file(filename, number_of_posters, words):
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


def create_followers_data_file(filename, number_of_users):
    with open(filename, 'w') as datafile:
        followers = set()
        following_percentage = 0.6

        for userID in range(number_of_users):
            for followerID in range(number_of_users):
                if random() < following_percentage and userID != followerID:
                    followers.add((userID, followerID))
                    datafile.write('{},{}\n'.format(userID, followerID))


def create_passwords_data_file(filename, names):
    with open(filename, 'w') as datafile:
        for i, name in enumerate(names, start=1):
            password = sha256_crypt.hash(name[0:4])
            datafile.write('{},{}\n'.format(i, password))


def create_sql_create_file(filename, template):
    sql_create_file = template.format(
        userdata=USER_DATA, tweetdata=TWEET_DATA, followerdata=FOLLOWER_DATA, passworddata=PASSWORD_DATA
    )
    with open(filename, 'w') as datafile:
        datafile.write(sql_create_file)


def main():
    random_words = request.urlopen(URL_TO_ENGLISH_WORDS).read().decode('utf-8').split()
    os.mkdir(DATA_PATH)

    create_users_data_file(USER_DATA, NAMES, random_words)
    create_tweets_data_file(TWEET_DATA, len(NAMES), random_words)
    create_followers_data_file(FOLLOWER_DATA, len(NAMES))
    create_passwords_data_file(PASSWORD_DATA, NAMES)

    create_sql_create_file(SQL_CREATE_FILE, SQL_CREATE_FILE_TEMPLATE)


if __name__ == '__main__':
    main()
