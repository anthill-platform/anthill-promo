# coding=utf-8

import common.admin as a
import tornado.gen
import json
import datetime

from common import to_int

from model.content import ContentError, ContentNotFound
from model.promo import PromoError, PromoNotFound


class RootAdminController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.links("Promo service", [
                a.link("contents", "Edit contents", icon="paper-plane"),
                a.link("promos", "Edit promo codes", icon="gift")
            ])
        ]


class ContentsController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.breadcrumbs([], "Contents"),
            a.links("Items", [
                a.link("content", item.name, icon="paper-plane", content_id=item.content_id)
                for item in data["items"]
            ]),
            a.links("Navigate", [
                a.link("index", "Go back", icon="chevron-left"),
                a.link("new_content", "Create content", icon="plus")
            ])
        ]

    @tornado.gen.coroutine
    def get(self):
        contents = self.application.contents
        items = yield contents.list_contents(self.gamespace)

        result = {
            "items": items
        }

        raise a.Return(result)


class ContentController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("contents", "Contents")
            ], "Content"),
            a.form("Update content", fields={
                "content_name": a.field("Content unique ID", "text", "primary", "non-empty"),
                "content_json": a.field("Content payload (any useful data)", "json", "primary", "non-empty")
            }, methods={
                "update": a.method("Update", "primary", order=1),
                "delete": a.method("Delete this content", "danger", order=2)
            }, data=data),
            a.links("Navigate", [
                a.link("contents", "Go back", icon="chevron-left")
            ])
        ]

    @tornado.gen.coroutine
    def get(self, content_id):

        contents = self.application.contents

        try:
            content = yield contents.get_content(self.gamespace, content_id)
        except ContentNotFound:
            raise a.ActionError("No such content")

        result = {
            "content_name": content.name,
            "content_json": content.payload
        }

        raise a.Return(result)

    @tornado.gen.coroutine
    def update(self, content_name, content_json):

        content_id = self.context.get("content_id")

        try:
            content_json = json.loads(content_json)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        contents = self.application.contents

        try:
            yield contents.update_content(self.gamespace, content_id, content_name, content_json)
        except ContentError as e:
            raise a.ActionError("Failed to update content: " + e.args[0])

        raise a.Redirect(
            "content",
            message="Content has been updated",
            content_id=content_id)

    # noinspection PyUnusedLocal
    @tornado.gen.coroutine
    def delete(self, **ignored):

        content_id = self.context.get("content_id")
        contents = self.application.contents

        try:
            yield contents.delete_content(self.gamespace, content_id)
        except ContentError as e:
            raise a.ActionError("Failed to delete content: " + e.args[0])

        raise a.Redirect("contents",
            message="Content has been deleted")


class NewContentController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("contents", "Contents")
            ], "New contents"),
            a.form("New content", fields={
                "content_name": a.field("Content unique ID", "text", "primary", "non-empty"),
                "content_json": a.field("Content payload (any useful data)", "json", "primary", "non-empty")
            }, methods={
                "create": a.method("Create", "primary")
            }, data={"content_json": {}}),
            a.links("Navigate", [
                a.link("contents", "Go back", icon="chevron-left")
            ])
        ]

    @tornado.gen.coroutine
    def create(self, content_name, content_json):

        try:
            content_json = json.loads(content_json)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        contents = self.application.contents

        try:
            content_id = yield contents.new_content(self.gamespace, content_name, content_json)
        except ContentError as e:
            raise a.ActionError("Failed to create new content: " + e.args[0])

        raise a.Redirect(
            "content",
            message="New content has been created",
            content_id=content_id)


class PromosController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.breadcrumbs([], "Promo codes"),
            a.form(title="Edit promo code", fields={
                "code": a.field("Edit promo code", "text", "primary", "non-empty")
            }, methods={
                "edit": a.method("Edit", "primary")
            }, data=data),
            a.links("Navigate", [
                a.link("index", "Go back", icon="chevron-left"),
                a.link("new_promo", "Create a new promo code", icon="plus"),
                a.link("new_promos", "Create multiple promo codes", icon="plus-square")
            ])
        ]

    @tornado.gen.coroutine
    def edit(self, code):
        promos = self.application.promos

        try:
            promos.validate(code)
        except PromoError as e:
            raise a.ActionError(e.message)

        try:
            promo = yield promos.find_promo(self.gamespace, code)
        except PromoNotFound:
            raise a.ActionError("No such promo code")

        raise a.Redirect("promo", promo_id=promo.code_id)


class NewPromoController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("promos", "Promo codes")
            ], "New promo code"),
            a.form("New promo code", fields={
                "promo_key": a.field("Promo code key", "text", "primary", "non-empty"),
                "promo_amount": a.field("Promo uses amount", "text", "primary", "number"),
                "promo_expires": a.field("Expire date", "date", "primary", "non-empty"),
                "promo_contents": a.field("Promo items", "kv", "primary", "non-empty",
                                          values=data["content_items"])
            }, methods={
                "create": a.method("Create", "primary")
            }, data=data),
            a.links("Navigate", [
                a.link("contents", "Go back", icon="chevron-left")
            ])
        ]

    @tornado.gen.coroutine
    def get(self):

        contents = self.application.contents
        content_items = {
            item.content_id: item.name
            for item in (yield contents.list_contents(self.gamespace))
        }

        raise a.Return({
            "promo_key": "<random>",
            "promo_amount": "1",
            "content_items": content_items,
            "promo_expires": str(datetime.datetime.now() + datetime.timedelta(days=30))
        })

    @tornado.gen.coroutine
    def create(self, promo_key, promo_amount, promo_expires, promo_contents):
        promos = self.application.promos

        try:
            promo_contents = json.loads(promo_contents)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        if promo_key == "<random>":
            promo_key = promos.random()

        try:
            promos.validate(promo_key)
        except PromoError as e:
            raise a.ActionError(e.message)

        try:
            promo_id = yield promos.new_promo(self.gamespace, promo_key, promo_amount, promo_expires, promo_contents)
        except ContentError as e:
            raise a.ActionError("Failed to create new promo: " + e.args[0])

        raise a.Redirect(
            "promo",
            message="Promo code has been created",
            promo_id=promo_id)


class NewPromosController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        res = [
            a.breadcrumbs([
                a.link("promos", "Promo codes")
            ], "New promo codes")
        ]

        result = data.get("result", None)

        if result:
            res.append(a.form("Generated keys", fields={
                "result": a.field("Keys", "text", "primary", "non-empty", multiline=20)
            }, methods={}, data=data))
        else:
            res.append(a.form("New promo code", fields={
                "promo_keys": a.field("Number of keys to generate", "text", "primary", "number"),
                "promo_amount": a.field("Promo uses amount", "text", "primary", "number"),
                "promo_expires": a.field("Expire date", "date", "primary", "non-empty"),
                "promo_contents": a.field("Promo items", "kv", "primary", "non-empty",
                                          values=data["content_items"])
            }, methods={
                "create": a.method("Create", "primary")
            }, data=data))

        res.append(a.links("Navigate", [
                a.link("contents", "Go back", icon="chevron-left")
            ]))

        return res

    @tornado.gen.coroutine
    def get(self):

        contents = self.application.contents
        content_items = {
            item.content_id: item.name
            for item in (yield contents.list_contents(self.gamespace))
        }

        raise a.Return({
            "promo_keys": "2",
            "promo_amount": "1",
            "content_items": content_items,
            "promo_expires": str(datetime.datetime.now() + datetime.timedelta(days=30))
        })

    @tornado.gen.coroutine
    def create(self, promo_keys, promo_amount, promo_expires, promo_contents):
        promos = self.application.promos

        promo_keys = to_int(promo_keys)

        try:
            promo_contents = json.loads(promo_contents)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        result = []

        for i in xrange(0, promo_keys):
            promo_key = promos.random()

            try:
                promos.validate(promo_key)
            except PromoError as e:
                raise a.ActionError(e.message)

            try:
                yield promos.new_promo(self.gamespace, promo_key, promo_amount, promo_expires, promo_contents)
            except ContentError as e:
                continue
            else:
                result.append(promo_key)

        raise a.Return({
            "result": "\n".join(result)
        })


class PromoController(a.AdminController):
    def access_scopes(self):
        return ["promo_admin"]

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("promos", "Promo codes")
            ], "Promo code '{0}'".format(data["promo_code"])),
            a.form("Update promo code", fields={
                "promo_code": a.field("Promo code key", "text", "primary", "non-empty"),
                "promo_amount": a.field("Usage amount left", "text", "primary", "number"),
                "promo_expires": a.field("Expire date", "date", "primary", "non-empty"),
                "promo_contents": a.field("Promo items", "kv", "primary", "non-empty",
                                          values=data["content_items"])
            }, methods={
                "update": a.method("Update", "primary"),
                "delete": a.method("Delete this promo code", "danger")
            }, data=data),
            a.links("Accounts used this promo code", [a.link(
                "/profile/profile", "@" + account, account=account) for account in data["usages"]]),
            a.links("Navigate", [
                a.link("contents", "Go back", icon="chevron-left")
            ])
        ]

    @tornado.gen.coroutine
    def get(self, promo_id):

        promos = self.application.promos
        contents = self.application.contents
        content_items = {
            item.content_id: item.name
            for item in (yield contents.list_contents(self.gamespace))
        }

        try:
            promo = yield promos.get_promo(self.gamespace, promo_id)
        except PromoNotFound:
            raise a.ActionError("No such promo code")

        try:
            usages = yield promos.get_promo_usages(self.gamespace, promo_id)
        except PromoError as e:
            raise a.ActionError(e.message)

        result = {
            "promo_code": promo.key,
            "promo_amount": promo.amount,
            "promo_contents": promo.contents,
            "content_items": content_items,
            "promo_expires": str(promo.expires),
            "usages": usages
        }

        raise a.Return(result)

    @tornado.gen.coroutine
    def update(self, promo_code, promo_amount, promo_expires, promo_contents):

        promo_id = self.context.get("promo_id")

        promos = self.application.promos

        try:
            promo_contents = json.loads(promo_contents)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        try:
            yield promos.update_promo(self.gamespace, promo_id, promo_code, promo_amount, promo_expires,
                                      promo_contents)
        except ContentError as e:
            raise a.ActionError("Failed to update promo code: " + e.args[0])

        raise a.Redirect(
            "promo",
            message="Promo code has been updated",
            promo_id=promo_id)

    # noinspection PyUnusedLocal
    @tornado.gen.coroutine
    def delete(self, **ignored):

        promo_id = self.context.get("promo_id")
        promos = self.application.promos

        try:
            yield promos.delete_promo(self.gamespace, promo_id)
        except ContentError as e:
            raise a.ActionError("Failed to delete promo: " + e.args[0])

        raise a.Redirect(
            "promos",
            message="Promo code has been deleted")
