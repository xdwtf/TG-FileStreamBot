# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

import logging
from pyrogram import filters, errors
from WebStreamer.vars import Var
from urllib.parse import quote_plus
from WebStreamer.bot import StreamBot, logger
from WebStreamer.utils import get_hash, get_name
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant


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
    banned_users = Var.BANNED_USERS.split() if Var.BANNED_USERS else []
    if str(m.from_user.id) in banned_users:
        return await m.reply("You are banned from using this bot.", quote=True)

    try:
        user = await client.get_chat_member(Var.UPDATES_CHANNEL, user_id=m.from_user.id)
    except UserNotParticipant:
        return await m.reply("Please join our channel first! @nexiuo", quote=True)

    if Var.ALLOWED_USERS and not ((str(m.from_user.id) in Var.ALLOWED_USERS) or (m.from_user.username in Var.ALLOWED_USERS)):
        return await m.reply("You are not <b>allowed to use</b> this <a href='https://github.com/EverythingSuckz/TG-FileStreamBot'>bot</a>.", quote=True)
    
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        
        file_hash = get_hash(log_msg, Var.HASH_LENGTH)
        stream_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(m))}?hash={file_hash}"
        short_link = f"{Var.URL}{file_hash}{log_msg.id}"
        logger.info(f"Generated link: {stream_link} for {m.from_user.first_name}")
        await m.reply_text(
            text="<code>{}</code>\n(<a href='{}'>shortened</a>)".format(
                stream_link, short_link
            ),
            quote=True,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open", url=stream_link)]]
            ),
        )
        
        await log_msg.reply_text(text=f"Requested by [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Download Link:** {stream_link}\n**Rapid Link:** {short_link}", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)
    except Exception as e:
        logger.exception(e) # Log the error
        await m.reply("Something went wrong. Please contact the bot admin for support.", quote=True)
