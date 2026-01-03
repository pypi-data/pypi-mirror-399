from datetime import timedelta
from typing import Literal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from tortoise.timezone import now

from xync_bot.shared import BoolCd
from xync_schema import models
from xync_schema.enums import HotStatus

hot = Router(name="hot")


class HotCd(CallbackData, prefix="hot"):
    typ: Literal["sell", "buy"]
    cex: int = 4


async def get_hot_db(uid: int) -> models.Hot:
    if not (
        hot_db := await models.Hot.filter(
            user__username_id=uid, updated_at__gt=now() - timedelta(hours=2), status=HotStatus.opened
        )
        .order_by("-created_at")
        .first()
        .prefetch_related("actors")
    ):
        hot_db = await models.Hot.create(user=await models.User.get(username_id=uid))
    return hot_db


async def find_hot_by_actor(aid: int) -> models.Hot | None:
    return (
        await models.Hot.filter(actors__id=aid, updated_at__gt=now() - timedelta(hours=2), status=HotStatus.opened)
        .order_by("-created_at")
        .first()
    )


@hot.message(Command("hot"))
async def start(msg: Message, xbt: "XyncBot"):  # noqa: F821
    user = await models.User.get(username_id=msg.from_user.id)
    await xbt.go_hot(user, [4])


@hot.callback_query(BoolCd.filter(F.req.__eq__("is_you")))
async def is_you(query: CallbackQuery, callback_data: BoolCd, xbt: "XyncBot"):  # noqa: F821
    if not callback_data.res:
        return await query.answer("ok, sorry")
    person = await models.Person.get(user__username_id=query.from_user.id).prefetch_related("user")
    order = await models.Order.get(id=callback_data.xtr).prefetch_related("ad__pair_side__pair", "ad__my_ad")
    old_person: models.Person = await models.Person.get(actors=order.taker_id).prefetch_related(
        "actors", "user", "creds"
    )
    await order.taker.update(person=person)
    await old_person.refresh_from_db()
    if old_person.user:
        raise ValueError(old_person)
    for actor in old_person.actors:
        actor.person = person
        await actor.save(update_fields=["person_id"])
    for cred in old_person.creds:
        cred.person = person
        await cred.save(update_fields=["person_id"])
    await old_person.delete()

    await xbt.hot_result(person.user, order)

    return await query.answer("ok")
