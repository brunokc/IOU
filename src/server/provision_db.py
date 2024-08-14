import os
import re
import psycopg2

from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

def sqlId(key):
    return sql.Identifier(os.getenv(key))

def sqlStr(key):
    return sql.Literal(os.getenv(key))

CREATE_STATEMENTS = (
    ("CREATE ROLE {}", (sqlId("DB_ADMIN_GROUP"),)),
    ("CREATE ROLE {} LOGIN ENCRYPTED PASSWORD {}", (sqlId("DB_ADMIN_USER"), sqlStr("DB_ADMIN_PASSWORD"))),
    ("GRANT {} TO {}", (sqlId("DB_ADMIN_GROUP"), sqlId("DB_ADMIN_USER"),)),

    ("CREATE ROLE {} LOGIN ENCRYPTED PASSWORD {}", (sqlId("DB_USER"), sqlStr("DB_USER_PASSWORD"))),

    ("CREATE DATABASE {} WITH OWNER {}", (sqlId("DB_NAME"), sqlId("DB_ADMIN_GROUP"))),
)

CONFIG_STATEMENTS = (
    ("GRANT pg_read_all_data, pg_write_all_data TO {}", (sqlId("DB_ADMIN_USER"),)),
    ("GRANT ALL ON SCHEMA public TO {}, {}", (sqlId("DB_ADMIN_USER"), sqlId("DB_USER"))),

    ("GRANT pg_read_all_data, pg_write_all_data TO {}", (sqlId("DB_USER"),)),
)

DROP_STATEMENTS = (
    ("DROP DATABASE IF EXISTS {}", (sqlId("DB_NAME"),)),
    ("DROP ROLE IF EXISTS {0}", (sql.SQL(", ").join([sqlId("DB_ADMIN_USER"), sqlId("DB_USER"), sqlId("DB_ADMIN_GROUP")]),)),
)

def connect(**kwargs):
    conn = psycopg2.connect(**kwargs)

    # Allow creation of databases using psycopg2
    # Without this, we get error:
    # "psycopg2.errors.ActiveSqlTransaction: CREATE DATABASE cannot run inside a transaction block"
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    return conn

def run_statements(connection, statements):
    with connection.cursor() as cursor:
        for stm in statements:
            query = sql.SQL(stm[0]).format(*stm[1])
            querystr = re.sub("PASSWORD '[^']*'", "PASSWORD '****'", query.as_string(connection))
            print(f"Executing: {querystr}")
            cursor.execute(query)

def setup_database():
    conn = connect(
        database="postgres",
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_SUPERUSER_USERNAME"),
        password=os.getenv("DB_SUPERUSER_PASSWORD")
    )

    try:
        run_statements(conn, DROP_STATEMENTS)
        run_statements(conn, CREATE_STATEMENTS)
    finally:
        conn.close()

def configure_database():
    conn = connect(
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_SUPERUSER_USERNAME"),
        password=os.getenv("DB_SUPERUSER_PASSWORD")
    )

    try:
        run_statements(conn, CONFIG_STATEMENTS)
    finally:
        conn.close()

def main():
    setup_database()
    configure_database()

if __name__ == "__main__":
    main()
