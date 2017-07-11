# coding=utf-8

from tornado.gen import coroutine, Return
from tornado.web import HTTPError

from common.access import scoped, AccessToken
from common.handler import AuthenticatedHandler
from common.validate import validate
from common.internal import InternalError

import ujson

from model.promo import PromoNotFound, PromoError, PromoExists

__author__ = 'desertkun'


class UsePromoHandler(AuthenticatedHandler):
    @scoped(scopes=["promo"])
    @coroutine
    def post(self, promo_key):

        promos = self.application.promos

        try:
            promo_usage = yield promos.use_promo(
                self.token.get(AccessToken.GAMESPACE),
                self.token.account,
                promo_key)

        except PromoError as e:
            raise HTTPError(400, e.message)
        except PromoNotFound as e:
            raise HTTPError(404, e.message)
        else:
            self.dumps(promo_usage)


class InternalHandler(object):
    def __init__(self, application):
        self.application = application

    @coroutine
    @validate(gamespace="int", amount="int", codes_count="int", expires="datetime", contents="json_dict")
    def generate_code(self, gamespace, amount, expires, contents, codes_count=1):

        promos = self.application.promos

        contents = yield promos.wrap_contents(gamespace, contents)

        keys = []

        for i in xrange(0, codes_count):
            while True:
                promo_key = promos.random()

                try:
                    yield promos.new_promo(
                        gamespace, promo_key, amount, expires, contents)
                except PromoExists:
                    continue
                except PromoError as e:
                    raise InternalError(500, "Failed to create new promo: " + e.args[0])
                else:
                    keys.append(promo_key)
                    break

        raise Return({
            "keys": keys
        })
