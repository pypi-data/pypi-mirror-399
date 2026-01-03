from uuid import UUID

from PGram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import UpdateType
from aiogram.types import InlineKeyboardButton, WebAppInfo

from xync_bot.shared import BoolCd
from xync_schema.models import Order, User, Transaction

from xync_bot.store import Store
from xync_bot.routers import last
from xync_bot.routers.main.handler import mr
from xync_bot.routers.pay.handler import pr
from xync_bot.routers.cond import cr
from xync_bot.routers.send import sd
from xync_bot.routers.hot import hot

au = [
    UpdateType.MESSAGE,
    UpdateType.CALLBACK_QUERY,
    UpdateType.CHAT_MEMBER,
    UpdateType.MY_CHAT_MEMBER,
]  # , UpdateType.CHAT_JOIN_REQUEST


class XyncBot(Bot):
    def __init__(self, token, cn):
        super().__init__(token, cn, [hot, sd, cr, pr, mr, last], Store(), DefaultBotProperties(parse_mode="HTML"))

    async def start(self, wh_host: str = None):
        self.dp.workflow_data["xbt"] = self  # todo: refact?
        # self.dp.workflow_data["store"].glob = await Store.Global()  # todo: refact store loading
        await super().start(au, wh_host)
        return self

    # итерация: предоставляем юзеру кнопки для перехода на hot объявления
    async def go_hot(self, user: User, ex_ids: list[int]):
        bads, sads, balances = await user.get_hot_ads(ex_ids)
        btns = [
            [
                InlineKeyboardButton(text=t + "🌐", url=bad.get_url()[0]),
                InlineKeyboardButton(text=t + "📱", url=bad.get_url()[1]),
            ]
            for bad in bads
            if (t := f"{bad.ad.price * 10**-2:.2f}{bad.ad.pair_side.pair.cur.ticker} {bad.ad.maker.name}")
        ]
        await self.send(user.username_id, "🟥Sell USDT", btns)
        # и если есть достаточные балансы валют для покупки:
        if btns := [
            [
                InlineKeyboardButton(text=t + "🌐", url=sad.get_url()[0]),
                InlineKeyboardButton(text=t + "📱", url=sad.get_url()[1]),
            ]
            for sad in sads
            if (
                t := f"{sad.ad.price * 10**-2:.2f} [≤ {balances[sad.ad.pair_side.pair.cur_id]}]"
                f"{sad.ad.pair_side.pair.cur.ticker} {sad.ad.maker.name}"
            )
        ]:
            await self.send(user.username_id, "🟩Buy USDT", btns)

    async def def_actor(self, uid: int, order: Order):
        """
        Если актор прилетевшего ордера по прогреву еще не связан ни с одним юзером, спрашиваем hot-юзера он ли это
        """
        txt = f"{order.taker.name}:{order.taker.exid} is you?"
        btns = [
            [
                InlineKeyboardButton(text="Yes", callback_data=BoolCd(req="is_you", res=True, xtr=order.id).pack()),
                InlineKeyboardButton(text="No", callback_data=BoolCd(req="is_you", res=False, xtr=order.id).pack()),
            ]
        ]
        await self.send(uid, txt, btns)

    async def hot_result(self, user: User, order: Order, app_url: str):
        err, res = await order.hot_process(user)
        btns = None
        if err in (1, 2):
            tx = await Transaction.get(id=UUID(hex=(await order.transfers)[0].pmid))
            await self.tx_send_tg(tx, app_url)
        if err == 0:
            txt = f"bro, you can't buy more than {res * 0.01:.2f} now! Deposit to XyncPay or Sell more at first"
        elif err == 1:
            txt = "Accept the order now, bro!"
            btns = [[InlineKeyboardButton(text=str(res.exid), url=f"https://www.bybit.com/p2p/orderList/{res.exid}")]]
        elif err == 2:
            txt = f"Your USDT buy done! XyncPay balance: {res * 0.01:.2f} now"
        elif err == 3:
            raise ValueError("WTF 3!")
        elif err == 4:
            txt = "At first accept previous orders, bro!"
            btns = [
                [
                    InlineKeyboardButton(text=str(order.exid), url=f"https://www.bybit.com/p2p/orderList/{order.exid}")
                    for order in res
                ]
            ]
        else:
            raise ValueError("WTF?")
        await self.send(user.username_id, txt, btns)

    async def tx_send_tg(self, tx: Transaction, app_url: str):
        await tx.fetch_related("cur", "sender__username", "receiver__username")
        amt = f"{tx.amount * 10**-tx.cur.scale:.2f} {tx.cur.ticker}"
        btns = [[InlineKeyboardButton(text="Transactions", web_app=WebAppInfo(url=app_url + "/history"))]]
        bot_nick = (await self.bot.me()).username
        qr = tx.qr_gen(bot_nick)
        sender = "@" + tx.sender.username.username if tx.sender.username.username else tx.sender.username_id
        await self.send(tx.receiver.username_id, f"{sender} sent you {amt}. <code>#{tx.id.hex}</code>", btns, qr)
        receiver = "@" + tx.receiver.username.username if tx.receiver.username.username else tx.receiver.username_id
        await self.send(tx.sender.username_id, f"You sent {amt} to {receiver}. <code>#{tx.id.hex}</code>", btns)
