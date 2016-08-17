
import handlers as h

from common.options import options
import options as _opts

import common.server
import common.database
import common.access
import common.sign
import common.keyvalue

import admin

from model.content import ContentModel
from model.promo import PromoModel

__author__ = 'desertkun'


class PromoServer(common.server.Server):
    def __init__(self):
        super(PromoServer, self).__init__()

        self.db = common.database.Database(
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

    def get_admin(self):
        return {
            "index": admin.RootAdminController,
            "contents": admin.ContentsController,
            "content": admin.ContentController,
            "new_content": admin.NewContentController,
            "promos": admin.PromosController,
            "new_promo": admin.NewPromoController,
            "promo": admin.PromoController
        }

    def get_metadata(self):
        return {
            "title": "Promo",
            "description": "Reward users with promo-codes",
            "icon": "heart"
        }

if __name__ == "__main__":
    stt = common.server.init()
    common.access.AccessToken.init([common.access.public()])
    common.server.start(PromoServer)
