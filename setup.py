"""
Run this file to install all libraries needed to run the application.
"""
import pip

needed_libraries = [
    'flask',
    'psycopg2',
    'wtforms',
    'passlib'
]


if __name__ == '__main__':
    for library in needed_libraries:
        pip.main(['install', library])