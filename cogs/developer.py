import asyncio
from typing import TYPE_CHECKING
import bale
from utils import persianNumbers

if TYPE_CHECKING:
    from ..bot import GroupBan

async def render_chat_info(chat: "bale.Chat"):
    return "👥 *مشخصات اصلی گروه*\n\nℹ نام گروه: *{}*\n🆔 شناسه یکتای گروه: *{}*\n🔗 لینک دعوت گروه: *{}*\n*گروه بان؛ دولوپر مود*".format(chat.title, chat.chat_id, chat.invite_link)


class Developer:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    def setup(self):
        return {
            self.when_send_command: "developer_message"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content or message.forward_from_message_id:
            return

        for (persian_num, english_num) in persianNumbers:
            message.content = message.content.replace(persian_num, english_num)

        if message.content == "/d info":
            return await message.chat.send("✨ هویت شما تائید شد؛ شما یکی از توسعه دهندگان گروه بان هستید")

        elif message.content in ["/developer", "/d"]:
            return await message.chat.send("✨ *توسعه دهندگان*\n\n⛏ دریافت لیست چت های ثبت شده\n/d group list\n\n⛏ ارسال پیام به چت (الزاما ثبت شده)\n/d group fetch <chat id>\n\n⛏ دریافت گروه (ثبت شده یا نشده)\n/d group send <chat id>\n\n⛏ دریافت آیدی کاربر (با یکی از پیام های وی)\n/d user get\n\n⛏ خارج شدن از چت (ثبت شده یا نشده)\n/d group leave <chat id>\n\n⛏ دریافت اطلاعات پیام\n/d message get\n\n⛏ پاک کردن پیام از چت\n/d message delete <chat id> <message id>\n\n⛏ بن کردن فرد در گروه خاص (الزاما گروه ثبت شده)\n/d group ban <chat id> <member id>\n\n🚀 گروه بان با شما توسعه دهندگان گرامی، *گـــروه بـــان* شده است.")

        elif message.content == "/d group list":
            with self.bot.make_db() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT chat_id FROM chat LIMIT 200")
                chats = cursor.fetchall()
                return await message.chat.send("💎 *لیست چت ها*\n\n{}".format("\n".join([f"🔧 {chat_id} | [💬](send:/d group send {chat_id}) - [❔](send:/d group fetch {chat_id}) - [🚀](send:/d group leave {chat_id})" for (chat_id, ) in chats])))

        elif message.content.startswith("/d group fetch "):
            chat_id = "".join(message.content.split(" ")[3::])
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            chat = await self.bot.get_chat(chat_id)
            if not chat:
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")
            groupinfo = await render_chat_info(chat)
            return await message.chat.send(groupinfo)

        elif message.content.startswith("/d group leave "):
            chat_id = "".join(message.content.split(" ")[3::])
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            try:
                await self.bot.leave_chat(chat_id)
            except bale.BaleError as err:
                return await message.chat.send("❌ درخواست انجام نشد\n{}".format(err))
            else:
                await message.chat.send("🟢 *درخواست با موفقیت برای سرور های بله ارسال شد*")
                with self.bot.make_db() as connection:
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM chat WHERE chat_id = '{}'".format(chat_id))
                    connection.commit()
                    cursor.close()

        elif message.content.startswith("/d group send "):
            chat_id = "".join(message.content.split(" ")[3::])
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            await message.chat.send("💎 *لطفا تا 120 ثانیه دیگر پیام مورد نظر خود را ارسال کنید*")
            try:
                msg: "bale.Message" = await self.bot.wait_for("developer_message", check = lambda m: m.author == message.author and m.chat == message.chat, timeout = 120.0)
            except asyncio.TimeoutError:
                return await message.chat.send("💡 متاستفانه ارسال نکردید")
            else:
                sent_message = await self.bot.send_message(chat_id, msg.content)
                return await msg.reply("🚀 *پیام با موفقیت ارسال شد*\n\nپیام با آیدی {0} بر روی سرور های بله و در گروهی با آیدی {1} قرار گرفت.".format(sent_message.message_id, sent_message.chat_id))

        elif message.content == "/d user get":
            await message.chat.send("💎 *لطفا تا 30 ثانیه دیگر یک پیام از کاربر مورد نظر ارسال نمائید*")
            try:
                msg: "bale.Message" = await self.bot.wait_for("developer_message", check=lambda m: m.author == message.author and m.chat == message.chat and m.forward_from)
            except asyncio.TimeoutError:
                return await message.chat.send("💡 متاستفانه ارسال نکردید")
            else:
                return await msg.reply(
                    "🚀 *پیام با موفقیت دریافت شد*\n\nپیام با آیدی {0} بر روی سرور های بله و توسط {1} با آیدی {2} قرار گرفته است.".format(
                        msg.message_id, msg.forward_from.first_name, msg.forward_from.user_id))

        elif message.content == "/d message get":
            await message.chat.send("💎 *لطفا تا 30 ثانیه دیگر پیام مورد نظر ارسال نمائید*")
            try:
                msg: "bale.Message" = await self.bot.wait_for("developer_message", check=lambda m: m.author == message.author and m.chat == message.chat and m.forward_from_chat, timeout=30.0)
            except asyncio.TimeoutError:
                return await message.chat.send("💡 متاستفانه ارسال نکردید")
            else:
                return await msg.reply(
                    "🚀 *پیام با موفقیت دریافت شد*\n\nپیام با آیدی {} و در چتی با آیدی {} بر روی سرور های بله قرار گرفته است.".format(msg.forward_from_message_id, msg.forward_from_chat.chat_id))

        elif message.content.startswith("/d message delete "):
            (chat_id, message_id) = message.content.split(" ")[3::]
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            try:
                await self.bot.delete_message(chat_id, message_id)
            except bale.BaleError as err:
                return await message.chat.send("❌ درخواست انجام نشد\n{}".format(err))
            else:
                return await message.chat.send("🟢 *با موفقیت پاک شد*")

        elif message.content.startswith("/d group ban "):
            (chat_id, user_id) = message.content.split(" ")[3::]
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            try:
                await self.bot.ban_chat_member(chat_id, user_id)
            except bale.BaleError as err:
                return await message.chat.send("❌ درخواست انجام نشد\n{}".format(err))
            else:
                return await message.chat.send("🟢 *با موفقیت بن شد*")

        elif message.content.startswith("/ads set "):
            (user_id, max_visit_cnt) = message.content.split(" ")[2::]
            if not user_id.isdigit() or not max_visit_cnt.isdigit():
                return await message.chat.send("❌ *نادرست وارد شده است*")

            check_message = await message.chat.send("✨ *لطفا عنوان تبلیغ را وارد نمائید*\n💡 غنوان شما میبایست حداقل *2* کاراکتر و حداکثر *30* کاراکتر داشته باشد\n\n⭕ برای لغو عملیات از عبارت *کنسل* و یا */cancel* استفاده کنید")
            try:
                _title: "bale.Message" = await self.bot.wait_for("developer_message", check = lambda m: m.author == message.author and m.chat == message.chat, timeout = 120.0)
            except asyncio.TimeoutError:
                return await check_message.reply("*ثبت تبلیغ لغو شد*")
            else:
                await _title.delete()
                if _title.content in ["/cancel", "کنسل"]:
                    return await check_message.edit("❌ *عملیات توسط شما لغو شد*")

                if not (30 >= len(_title.content) >= 2):
                    return await check_message.edit("❌ *عملیات لغو شد؛ متن شما فاقد موارد خواسته شده بود*")

                await check_message.edit("✨ *لطفا متن تبلیغ را وارد نمائید*\n💡 غنوان شما میبایست حداقل *10* کاراکتر و حداکثر *200* کاراکتر داشته باشد\n\n⭕ برای لغو عملیات از عبارت *کنسل* و یا */cancel* استفاده کنید")
                try:
                    _desc: "bale.Message" = await self.bot.wait_for("developer_message", check=lambda m: m.author == message.author and m.chat == message.chat, timeout=120.0)
                except asyncio.TimeoutError:
                    return await check_message.reply("*ثبت تبلیغ لغو شد*")
                else:
                    await _desc.delete()
                    if _desc.content in ["/cancel", "کنسل"]:
                        return await check_message.edit("❌ *عملیات توسط شما لغو شد*")

                    if not (200 >= len(_desc.content) >= 10):
                        return await check_message.edit("❌ *عملیات لغو شد؛ متن شما فاقد موارد خواسته شده بود*")

                    await check_message.edit(self.bot.base_messages["wait"])
                    with self.bot.make_db() as connection:
                        cursor = connection.cursor()
                        cursor.execute("SELECT * FROM ads WHERE name = '{}' AND user_id = '{}'".format(_title.content, user_id))
                        if cursor.fetchone():
                            return await check_message.edit("❌ *عنوان {} از قبل در دیتابیس وجود داشته است*".format(_title.content))

                        cursor.execute("INSERT INTO ads(user_id, name, description, max_visit_cnt) VALUES (%s, %s, %s, %s)", (user_id, _title.content, _desc.content, int(max_visit_cnt)))
                        connection.commit()
                        cursor.close()

                    await check_message.edit("😉 *تبلیغ مورد نظر با موفقیت برای کاربر اضافه شد*")
