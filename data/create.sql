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



COPY Users(username, email, age) FROM 'path to users_data.txt' USING DELIMITERS ',';
COPY Tweets(posterID, content, time_posted) FROM 'path to tweets_data.txt' USING DELIMITERS ',';
COPY Followers(userID, followerID) FROM 'path to followers_data.txt' USING DELIMITERS ',';
COPY Passwords(userID, password) FROM 'path to passwords_data.txt' USING DELIMITERS ',';
