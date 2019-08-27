# Tweeter

This is a project for the SQL-course at [Ludu.co](https://www.ludu.co/course/lar-dig-sql).


## Setup

The application uses python 3, and 4 external libraries:
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


## Running the application

To run the application, simply run _application.py_. By default, all functionality will be limited, as it is expected you provide the functionality yourself by filling in the functions in the file _exercise_queries.py_.

If you want to run the full-featured application, change the import in _applications.py_ from "from exercise_queries ..." to "from solution_queries ...". 

## Common errors
* **The application throws the error _"Couldn't connect to server. Potential problems might be: ..."_**

If you want to run the full-featured version, you'll have to start the server. This is done by launching psql and connecting to the correct database.

Another problem might be the arguments you pass (or don't pass). Make sure the arguments match the values from psql:

![Terminal](https://i.imgur.com/tKTUkpG.png)

The only difference should be that the `Database` is _"tweeter"_, rather than _"postgres"_.

* **Another error pops up**

The application is written and tested with Python 3 in mind. If you're using Python 2 it won't work. Check your version by running `python --version`, or `py --version` if you're on Windows, in the command line.

## Notice

This application is written as a simple project for learning to use a database. It is **not** written according to the best practices for a full-blown web application. Please don't take anything in the code as an example of proper use.

## Known errors/bugs

* The paragraph tag doesn't wrap text by default. This means that posting a tweet with just a single long word or reducing your browser width will overflow the edge. Solution to this is to implement some check for long words and manually break them, or to include a CSS property `word-break`.
* An email doesn't have to be valid. This could be fixed by adding a trigger to the User table and make sure the application handles those exceptions.
* The settings page is not displaying good error messages when the data is invalid or the password is wrong. This could be fixed by raising an error from `validate_and_perform_user_changes` which could get caught in the application and displayed with a flash message.
* Searching for a tweet containing an URL (for example 'http://127.0.0.1:5000'), will yield 'Not Found'.

## Author

The project is written by Ted Klein Bergman, a KTH student in Media Technology / Computer Science. He's a T.A. in Database and Software Development and passionated about programming. He's also not afraid of constructive criticism, so don't be afraid to point out errors in the Ludu course.
