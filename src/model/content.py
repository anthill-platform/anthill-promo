
from tornado.gen import coroutine, Return

from common.database import DatabaseError
from common.model import Model
import ujson


class ContentError(Exception):
    pass


class ContentNotFound(Exception):
    pass


class ContentModel(Model):
    def __init__(self, db):
        self.db = db

    def get_setup_tables(self):
        return ["promo_contents"]

    def get_setup_db(self):
        return self.db

    @coroutine
    def new_content(self, gamespace_id, content_name, content_data):

        try:
            yield self.find_content(gamespace_id, content_name)
        except ContentNotFound:
            pass
        else:
            raise ContentError("Content '{0}' already exists.".format(content_name))

        try:
            result = yield self.db.insert("""
                INSERT INTO `promo_contents`
                (`gamespace_id`, `content_name`, `content_json`)
                VALUES (%s, %s, %s);
            """, gamespace_id, content_name, ujson.dumps(content_data))
        except DatabaseError as e:
            raise ContentError("Failed to add new content: " + e.args[1])

        raise Return(result)

    @coroutine
    def find_content(self, gamespace_id, content_name):
        try:
            result = yield self.db.get("""
                SELECT *
                FROM `promo_contents`
                WHERE `content_name`=%s AND `gamespace_id`=%s;
            """, content_name, gamespace_id)
        except DatabaseError as e:
            raise ContentError("Failed to find content: " + e.args[1])

        if result is None:
            raise ContentNotFound()

        raise Return(result)

    @coroutine
    def get_content(self, gamespace_id, content_id):
        try:
            result = yield self.db.get("""
                SELECT *
                FROM `promo_contents`
                WHERE `content_id`=%s AND `gamespace_id`=%s;
            """, content_id, gamespace_id)
        except DatabaseError as e:
            raise ContentError("Failed to get content: " + e.args[1])

        if result is None:
            raise ContentNotFound()

        raise Return(result)

    @coroutine
    def delete_content(self, gamespace_id, content_id):
        try:
            yield self.db.execute("""
                DELETE
                FROM `promo_contents`
                WHERE `content_id`=%s AND `gamespace_id`=%s;
            """, content_id, gamespace_id)
        except DatabaseError as e:
            raise ContentError("Failed to delete content: " + e.args[1])

    @coroutine
    def update_content(self, gamespace_id, content_id, content_name, content_data):
        try:
            yield self.db.execute("""
                UPDATE `promo_contents`
                SET `content_name`=%s, `content_json`=%s
                WHERE `content_id`=%s AND `gamespace_id`=%s;
            """, content_name, ujson.dumps(content_data), content_id, gamespace_id)
        except DatabaseError as e:
            raise ContentError("Failed to update content: " + e.args[1])

    @coroutine
    def list_contents(self, gamespace_id):
        try:
            result = yield self.db.query("""
                SELECT *
                FROM `promo_contents`
                WHERE `gamespace_id`=%s;
            """, gamespace_id)
        except DatabaseError as e:
            raise ContentError("Failed to list content: " + e.args[1])

        raise Return(result)
