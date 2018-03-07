
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



COPY Users(username, email, age) FROM '/Users/Kleinman/PycharmProjects/database/data/users_data.txt' USING DELIMITERS ',';
COPY Tweets(posterID, content, time_posted) FROM '/Users/Kleinman/PycharmProjects/database/data/tweets_data.txt' USING DELIMITERS ',';
COPY Followers(userID, followerID) FROM '/Users/Kleinman/PycharmProjects/database/data/followers_data.txt' USING DELIMITERS ',';
COPY Passwords(userID, password) FROM '/Users/Kleinman/PycharmProjects/database/data/passwords_data.txt' USING DELIMITERS ',';
