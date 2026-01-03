from typing import Literal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery

from xync_bot.shared import BoolCd
from xync_schema import models

hot = Router(name="hot")


class HotCd(CallbackData, prefix="hot"):
    typ: Literal["sell", "buy"]
    cex: int = 4


@hot.message(Command("hot"))
async def start(msg: Message, xbt: "XyncBot"):  # noqa: F821
    user = await models.User.get(username_id=msg.from_user.id)
    await xbt.go_hot(user, [4])


@hot.callback_query(BoolCd.filter(F.req.__eq__("is_you")))
async def is_you(query: CallbackQuery, callback_data: BoolCd, xbt: "XyncBot"):  # noqa: F821
    if not callback_data.res:
        await query.message.delete()
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

    await query.message.delete()
    return await query.answer("ok")
