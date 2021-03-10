import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_user(conn, username):
    """
    Create a new project into the projects table
    :param conn:
    :param username:
    :return: project id
    """
    sql = ''' INSERT INTO projects(name,begin_date,end_date)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

if __name__ == '__main__':
    conn = create_connection("hancock_users.db")
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                           id integer PRIMARY KEY,
                                           username text NOT NULL,
                                           password_hash text  ); """
    create_table(conn, sql_create_users_table)
    conn.close()