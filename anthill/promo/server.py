
from anthill.common.options import options
from anthill.common import server, database, access

from . import handlers as h
# noinspection PyUnresolvedReferences
from . import options as _opts
from . import admin

from . model.content import ContentModel
from . model.promo import PromoModel


class PromoServer(server.Server):
    def __init__(self):
        super(PromoServer, self).__init__()

        self.db = database.Database(
            host=options.db_host,
            database=options.db_name,
            user=options.db_username,
            password=options.db_password)

        self.contents = ContentModel(self.db)
        self.promos = PromoModel(self.db)

    def get_models(self):
        return [self.contents, self.promos]

    def get_handlers(self):
        return [
            (r"/use/(.*)", h.UsePromoHandler),
        ]

    def get_internal_handler(self):
        return h.InternalHandler(self)

    def get_admin(self):
        return {
            "index": admin.RootAdminController,
            "contents": admin.ContentsController,
            "content": admin.ContentController,
            "new_content": admin.NewContentController,
            "promos": admin.PromosController,
            "new_promo": admin.NewPromoController,
            "new_promos": admin.NewPromosController,
            "promo": admin.PromoController
        }

    def get_metadata(self):
        return {
            "title": "Promo",
            "description": "Reward users with promo-codes",
            "icon": "gift"
        }


if __name__ == "__main__":
    stt = server.init()
    access.AccessToken.init([access.public()])
    server.start(PromoServer)
