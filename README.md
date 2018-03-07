# Tweeter

This is a project for the SQL-course at [Ludu.co](https://www.ludu.co/course/learn-sql).


## Setup

The application uses python 3 and 4 external libraries:
* **flask** - For setting up the server.
* **wtforms** - For easily creating forms.
* **psycopg2** - For inteacting with our database.
* **passlib** - To hash and salt passwords.


You'll also need four tables in your database:
* Users(**userID**, username, email, age)
* Tweets(**tweetID**, posterID, content, time_posted)
* Followers(**userID**, followerID)
* Passwords(**userID**, password)


You can download the libraries and create the tables manually, or by running `setup.py`. The file will download the libraries and create an `create.sql` file with all tables. It'll also create 4 CSV-files with compatible data for each table.
