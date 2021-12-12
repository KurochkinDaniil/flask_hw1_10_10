import sqlite3
import math
import time


class FlaskDataBase:
    def __init__(self, db) -> None:
        self.__db = db
        self.__curs = db.cursor()

    def is_email_exists(self, email):
        command = f"SELECT user_.email FROM user_ where user_.email = \'{email}\'"
        try:
            self.__curs.execute(command)
            res = self.__curs.fetchall()
            if res:
                return True
        except Exception as e:
            print(e)
        return False

    def add_new_user(self, email, password):
        registered_at = math.floor(time.time())
        try:
            self.__curs.execute(
                "insert into user_ values (NULL, ?, ?, ?)",
                (email, password,registered_at)
            )
            self.__db.commit()
        except Exception as e:
            print(e)

    def get_user(self, email):
        command = f"SELECT * FROM user_ where user_.email = \'{email}\'"
        try:
            self.__curs.execute(command)
            res = self.__curs.fetchall()
            if res:
                return res[0]
        except Exception as e:
            print(e)
        return []

    def get_menu(self):
        query = "SELECT * FROM mainmenu"
        try:
            self.__curs.execute(query)
            res = self.__curs.fetchall()
            return res
        except Exception as e:
            print(e)
        return []

    def add_post(self, title, description):
        updated_at = math.floor(time.time())
        try:
            self.__curs.execute(
                "insert into post values (NULL, ?, ?, ?)",
                (title, description, updated_at)
            )
            self.__db.commit()
        except Exception as e:
            print(e)
            return False
        return True

    def get_posts(self):
        command = "select id, title, description from post order by post.updated_at"
        try:
            self.__curs.execute(command)
            res = self.__curs.fetchall()
            if res:
                return res
        except Exception as e:
            print(e)
        return []

    def get_post_content(self, post_id):
        try:
            self.__curs.execute(
                f"SELECT title, description FROM post WHERE id = {post_id}"
            )
            res = self.__curs.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Exception in getting post by id {post_id}: {e}")
        return False, False
