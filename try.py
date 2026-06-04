from os import name

from kivy.logger import Logger
import mysql.connector

DB_HOST = "187.77.112.162"
DB_USER = "Pndujikir2026!"  # Changed to the clean username
DB_PASSWORD = "@PndKir2026!"
DB_NAME = "pkbpandeglang"

def exec_reload_database():
    global mydb
    try:
        if 'mydb' in globals() and mydb is not None:
            mydb.ping(reconnect=True, attempts=3, delay=2)
            if mydb.is_connected():
                return

        mydb = mysql.connector.connect(
            host=DB_HOST, 
            user=DB_USER, 
            password=DB_PASSWORD,
            database=DB_NAME, 
            buffered=True, 
            autocommit=True,
            auth_plugin='mysql_native_password',  # Forces standard authentication
            connection_timeout=10
        )
    except Exception as e:
        Logger.error(f"Database Error: {e}")

exec_reload_database()