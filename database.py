import sys

from psycopg2 import connect, Error, ProgrammingError, OperationalError
from psycopg2.extras import NamedTupleCursor


class Database:

    def __init__(self, database, user, password='', host='localhost', port=5432):
        self.arguments = {
            'dbname':   database,
            'user':     user,
            'password': password,
            'host':     host,
            'port':     port
        }

        try:
            self.connection = connect(**self.arguments)
        except Error as error:
            print(error, "\nDid you remember to start your server?\n", file=sys.stderr)

        self.cursor = self.connection.cursor(cursor_factory=NamedTupleCursor)

    def execute(self, query, **arguments):
        """
        This function will try to execute the query and commit. If the query fails, it'll rollback.

        Parameters:
            query:       The SQL query to execute.
            **arguments: The named arguments to inject in the query. (Optional)
        """
        try:
            self.cursor.execute(query, arguments)
        except Error as error:
            print(error.pgerror, file=sys.stderr)
            self.connection.rollback()
        else:
            # This will be executed if the exception isn't raised.
            self.connection.commit()

    def get_result_from_last_query(self, number_of_tuples = -1):
        """
        Returns the tuples produced from last query.

        Parameters:
            number_of_tuples: The amount of tuples to return.
                    If the number is negative, a list of all tuples will be returned.
                    If the number is 1, only one tuple will be returned (it'll not be in a list).
                    If the number is greater than 1, return a list of at most that amount of tuples.
        Returns:
            List of tuples.
        """
        try:
            if number_of_tuples < 0:
                return self.cursor.fetchall()
            elif number_of_tuples == 1:
                return self.cursor.fetchone()
            else:
                return self.cursor.fetchmany(number_of_tuples)
        except Error as error:
            print(error, "\nThere were no results to fetch.", file=sys.stderr)
            return ()