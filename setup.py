"""
Run this file to install all libraries needed to run the application, and to create data
files. You'll need access to internet in order to run this file properly.


"""
import pip
import requests
from random import random, choice
from random import randrange
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt


LIBRARIES = [
    'flask',
    'psycopg2',
    'wtforms',
    'passlib'
]

URL_TO_ENGLISH_WORDS = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'

FILE_PATH = 'data/'
USER_DATA = FILE_PATH + 'users_data.txt'
TWEET_DATA = FILE_PATH + 'tweets_data.txt'
FOLLOWER_DATA = FILE_PATH + 'followers_data.txt'
PASSWORD_DATA = FILE_PATH + 'passwords_data.txt'
SQL_CREATE_FILE = FILE_PATH + 'create.sql'


if __name__ == '__main__':
    for library in LIBRARIES:
        pip.main(['install', library])


    def random_date(start, end):
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return start + timedelta(seconds=random_second)


    names = [
        'transportwildcat', 'wrapteal', 'listenseagull', 'peerswallow', 'admireowl', 'shrugbuzzard', 'orderoxbird',
        'requestlion', 'operatewildebeest', 'yodelplover', 'hidechamois', 'minehamster', 'scrapegoldfinch',
        'volunteersheldrake', 'entertainsnail', 'severblackbird', 'causekookaburra', 'commenttuna', 'bleachraven',
        'wishptarmigan', 'fearpheasant', 'avowlemur', 'borroweland', 'tossdoves'
    ]
    domains = ['@hotmail.com', '@kth.se', '@gmail.com', '@msn.com']
    words = requests.get(URL_TO_ENGLISH_WORDS).content.decode('utf-8').split()

    with open(USER_DATA, 'w') as datafile:
        for i, name in enumerate(names):
            username = name

            email = ''
            for _ in range(1, int(random() * 4) + 2):
                email += words[int(random() * (len(words) - 1))]
            email += choice(domains)

            age = int(random() * 100) + 1

            datafile.write('{},{},{}\n'.format(username, email, age))

    with open(TWEET_DATA, 'w') as datafile:

        d1 = datetime.strptime('2008-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        d2 = datetime.now()

        posterID = 1
        for i in range(len(names) * 10):

            content = ' '.join(words[int(random() * (len(words) - 1))] for _ in range(1, int(random() * 30) + 5))
            content += choice(['!', '.', '...', '?', ''])
            if len(content) > 144:
                content = content[0:144]

            time_posted = random_date(d1, d2)

            datafile.write('{},{},{}\n'.format(posterID, content, time_posted))

            if random() < 0.08:
                posterID += 1
                if posterID > len(names):
                    break

    with open(FOLLOWER_DATA, 'w') as datafile:

        followers = set()

        for i in range((len(names) ** 2)):

            a, b = int(random() * (len(names) - 1) + 1), int(random() * (len(names) - 1) + 1)

            if (a, b) in followers or a == b:
                continue
            else:
                followers.add((a, b))
                datafile.write('{},{}\n'.format(a, b))

    with open(PASSWORD_DATA, 'w') as datafile:

        for i, name in enumerate(names, start=1):
            password = sha256_crypt.hash(name[0:4])
            datafile.write('{},{}\n'.format(i, password))


    sql_create_file = """
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



COPY Users(username, email, age) FROM {userdata} USING DELIMITERS ',';
COPY Tweets(posterID, content, time_posted) FROM {tweetdata} USING DELIMITERS ',';
COPY Followers(userID, followerID) FROM {followerdata} USING DELIMITERS ',';
COPY Passwords(userID, password) FROM {passworddata} USING DELIMITERS ',';
""".format(userdata=USER_DATA, tweetdata=TWEET_DATA, followerdata=FOLLOWER_DATA, passworddata=PASSWORD_DATA)

    with open(SQL_CREATE_FILE, 'w') as datafile:
        datafile.write(sql_create_file)