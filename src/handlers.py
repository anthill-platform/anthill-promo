# coding=utf-8

from tornado.gen import coroutine
from tornado.web import HTTPError

from common.access import scoped, AccessToken
from common.handler import AuthenticatedHandler

import ujson

from model.promo import PromoNotFound, PromoError

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
            self.write(ujson.dumps(promo_usage))
