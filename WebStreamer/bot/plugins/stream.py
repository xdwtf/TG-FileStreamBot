# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

import logging, asyncio
from pyrogram import filters
from WebStreamer.vars import Var
from urllib.parse import quote_plus
from WebStreamer.bot import StreamBot, logger
from WebStreamer.utils import get_hash, get_name, encod
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from WebStreamer.utils.database import Database

db = Database(Var.DATABASE_URL, Var.DATABASE_NAME)

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def media_receive_handler(client, m: Message):
    user_id = m.from_user.id
    try:
        user = await client.get_chat_member(Var.UPDATES_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return await m.reply("Please join our channel first! @nexiuo", quote=True)

    if await db.is_user_banned(user_id):
        return await m.reply("You are banned from using this bot.")

    # Check if the user is in the allowed users list
    allowed_users = await db.get_allowed_users()
    if allowed_users and not ((str(user_id) in allowed_users) or (m.from_user.username in allowed_users)):
        return await m.reply(
            "You are not in the allowed list of users who can use me. \
            Check <a href='https://github.com/EverythingSuckz/TG-FileStreamBot#optional-vars'>this link</a> for more info.",
            disable_web_page_preview=True, quote=True
        )

    await db.insert_user(user_id)
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        
        file_hash = get_hash(log_msg, Var.HASH_LENGTH)
        stream_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(m))}?hash={file_hash}"
        short_link = f"{Var.URL}{file_hash}{log_msg.id}"
        x_link = "https://xdwtf.vercel.app/play?id=" + encod(short_link)
        logger.info(f"Generated link: {stream_link} for {m.from_user.first_name}")
        await m.reply_text(
            text="<code>{}</code>\n(<a href='{}'>shortened</a>)\n(<a href='{}'>Player</a>)".format(
                stream_link, short_link, x_link
            ),
            quote=True,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open", url=stream_link)]]
            ),
        )
        await db.increment_file_count(user_id)
        await log_msg.reply_text(text=f"Requested by [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Download Link:** {stream_link}\n**Rapid Link:** {short_link}", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        logger.warning(f"Floodwait occurred. Retrying the operation after waiting for {e.x} seconds.")
        await media_receive_handler(client, m)
    except Exception as e:
        logger.exception(e)
        await m.reply("Something went wrong. Please contact the bot admin for support.", quote=True)