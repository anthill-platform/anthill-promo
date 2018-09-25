
from tornado.web import HTTPError

from anthill.common.access import scoped, AccessToken
from anthill.common.handler import AuthenticatedHandler
from anthill.common.validate import validate
from anthill.common.internal import InternalError

from . model.promo import PromoNotFound, PromoError, PromoExists


class UsePromoHandler(AuthenticatedHandler):
    @scoped(scopes=["promo"])
    async def post(self, promo_key):
        promos = self.application.promos
        gamespace_id = self.token.get(AccessToken.GAMESPACE)

        try:
            promo_usage = await promos.use_promo(gamespace_id, self.token.account, promo_key)
        except PromoError as e:
            raise HTTPError(e.code, e.message)
        except PromoNotFound as e:
            raise HTTPError(404, str(e))
        else:
            self.dumps(promo_usage)


class InternalHandler(object):
    def __init__(self, application):
        self.application = application

    @validate(gamespace="int", amount="int", codes_count="int", expires="datetime", contents="json_dict")
    async def generate_code(self, gamespace, amount, expires, contents, codes_count=1):

        promos = self.application.promos

        contents = await promos.wrap_contents(gamespace, contents)

        keys = []

        for i in range(0, codes_count):
            while True:
                promo_key = promos.random()

                try:
                    await promos.new_promo(gamespace, promo_key, amount, expires, contents)
                except PromoExists:
                    continue
                except PromoError as e:
                    raise InternalError(e.code, e.message)
                else:
                    keys.append(promo_key)
                    break

        return {
            "keys": keys
        }

    @validate(gamespace="int", account="int", key="str")
    async def use_code(self, gamespace, account, key):
        promos = self.application.promos

        try:
            promo_usage = await promos.use_promo(gamespace, account, key)
        except PromoError as e:
            raise InternalError(e.code, e.message)
        except PromoNotFound as e:
            raise InternalError(404, str(e))
        else:
            return promo_usage

    @validate(gamespace="int")
    async def list_contents(self, gamespace):
        contents = self.application.contents

        try:
            items = await contents.list_contents(gamespace)
        except PromoError as e:
            raise InternalError(e.code, e.message)
        except PromoNotFound as e:
            raise InternalError(404, str(e))
        else:
            return {
                "items": {
                    item.content_id: item.name
                    for item in items
                }
            }

    @validate(gamespace="int", promo_key="str")
    async def get_code_info(self, gamespace, promo_key):
        promos = self.application.promos

        try:
            promo = await promos.find_promo(gamespace, promo_key)
        except PromoError as e:
            raise InternalError(e.code, e.message)
        except PromoNotFound as e:
            raise InternalError(404, "No such promo code")
        else:
            return {
                "code": {
                    "expires": str(promo.expires),
                    "id": promo.code_id,
                    "contents": promo.contents,
                    "amount": promo.amount,
                }
            }

    @validate(gamespace="int", code_id="int")
    async def list_code_users(self, gamespace, code_id):
        promos = self.application.promos

        try:
            users = await promos.get_promo_usages(gamespace, code_id)
        except PromoError as e:
            raise InternalError(e.code, e.message)
        else:
            return {
                "users": users
            }
