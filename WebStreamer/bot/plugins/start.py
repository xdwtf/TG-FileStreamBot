# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

import asyncio
import random
import string
import time
import datetime
import aiofiles
import os

from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.database import Database
from WebStreamer.utils.bd import send_msg

broadcast_ids = {}

db = Database(Var.DATABASE_URL, Var.DATABASE_NAME)

@StreamBot.on_message(filters.command(["start", "help"]) & filters.private)
async def start(_, m: Message):
    user_id = m.from_user.id
    if await db.is_user_banned(user_id):
        return await m.reply("You are banned from using this bot.")

    allowed_users = await db.get_allowed_users()
    if allowed_users and not ((str(user_id) in allowed_users)):
        return await m.reply(
            "You are not in the allowed list of users who can use me.",
            disable_web_page_preview=True, quote=True
        )

    await db.insert_user(user_id)
    await m.reply(
        f'Hi {m.from_user.mention(style="md")}, Send me a file to get an instant stream link.'
    )

@StreamBot.on_message(filters.command("myfiles") & filters.private)
async def my_files(_, m: Message):
    user_id = m.from_user.id
    if await db.is_user_banned(user_id):
        return await m.reply("You are banned from using this bot.")

    allowed_users = await db.get_allowed_users()
    if allowed_users and not ((str(user_id) in allowed_users)):
        return await m.reply(
            "You are not in the allowed list of users who can use me.",
            disable_web_page_preview=True, quote=True
        )

    await db.insert_user(user_id)
    user_data = db.users.find_one({"_id": user_id})
    if user_data:
        file_count = user_data.get("file_count", 0)
        await m.reply(f"You have sent {file_count} files so far.")
    else:
        await m.reply("You haven't sent any files yet.")

@StreamBot.on_message(filters.command("stats") & filters.private & filters.user(Var.OWNER_ID))
async def stats(_, m: Message):
    total_users = await db.total_users_count()
    total_allowed_users = await db.total_allowed_user_count()
    total_banned_users = await db.total_banned_users_count()
    total_files = await db.total_files_count()

    stats_message = (
        f"Total users: {total_users}\n"
        f"Total allowed users: {total_allowed_users}\n"
        f"Total banned users: {total_banned_users}\n"
        f"Total files till now: {total_files}"
    )

    await m.reply(stats_message)

@StreamBot.on_message(filters.command("ban") & filters.private & filters.user(Var.OWNER_ID))
async def ban_user(_, m: Message):
    if len(m.command) == 2:
        user_id = int(m.command[1])
        if await db.is_user_banned(user_id):
            await m.reply(f"User with ID {user_id} is already banned.")
        else:
            await db.ban_user(user_id)
            await m.reply(f"User with ID {user_id} has been banned.")
    else:
        await m.reply("Invalid command usage. Use /ban <user_id>.")

@StreamBot.on_message(filters.command("unban") & filters.private & filters.user(Var.OWNER_ID))
async def unban_user(_, m: Message):
    if len(m.command) == 2:
        user_id = int(m.command[1])
        if await db.is_user_banned(user_id):
            await db.unban_user(user_id)
            await m.reply(f"User with ID {user_id} has been unbanned.")
        else:
            await m.reply(f"User with ID {user_id} is not currently banned.")
    else:
        await m.reply("Invalid command usage. Use /unban <user_id>.")

@StreamBot.on_message(filters.command("auth") & filters.private & filters.user(Var.OWNER_ID))
async def add_allowed_user(_, m: Message):
    if len(m.command) == 2:
        user_id = int(m.command[1])
        if not await db.is_user_allowed(user_id):
            await db.add_allowed_user(user_id)
            await m.reply(f"User with ID {user_id} has been added to the allowed users list.")
        else:
            await m.reply(f"User with ID {user_id} is already in the allowed users list.")
    else:
        await m.reply("Invalid command usage. Use /auth <user_id>.")

@StreamBot.on_message(filters.command("unauth") & filters.private & filters.user(Var.OWNER_ID))
async def remove_allowed_user(_, m: Message):
    if len(m.command) == 2:
        user_id = int(m.command[1])
        if await db.is_user_allowed(user_id):
            await db.remove_allowed_user(user_id)
            await m.reply(f"User with ID {user_id} has been removed from the allowed users list.")
        else:
            await m.reply(f"User with ID {user_id} is not in the allowed users list.")
    else:
        await m.reply("Invalid command usage. Use /unauth <user_id>.")

@StreamBot.on_message(filters.command("log") & filters.private & filters.user(Var.OWNER_ID))
async def send_log(_, m: Message):
    log_file_path = "streambot.log"
    if os.path.exists(log_file_path):
        with open(log_file_path, "rb") as file:
            await m.reply_document(document=file, caption="Here's the log file.")
    else:
        await m.reply("Log file not found.")


@StreamBot.on_message(filters.command("broadcast") & filters.private & filters.user(Var.OWNER_ID) & filters.reply)
async def broadcast_(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
    out = await m.reply_text(
        text=f"Broadcast initiated! You will be notified with a log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success
    )
    try:
        async with aiofiles.open(f'broadcast_{broadcast_id}.txt', 'w') as broadcast_log_file:
            for user in all_users:
                sts, msg = await send_msg(
                    user_id=int(user['_id']),
                    message=broadcast_msg
                )
                if msg is not None:
                    await broadcast_log_file.write(msg)
                if sts == 200:
                    success += 1
                else:
                    failed += 1
                if sts == 400:
                    await db.delete_user(user['_id'])
                done += 1
                # Update the broadcast status periodically
                if done % 10 == 0:  # Update every 10 users (adjust as needed)
                    await out.edit_text(f"Broadcast Status\n\ncurrent: {done}\nfailed:{failed}\nsuccess: {success}")
    except Exception as e:
        print(f"An error occurred during broadcast: {e}")
    finally:
        if broadcast_ids.get(broadcast_id):
            broadcast_ids.pop(broadcast_id)
        completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
        await asyncio.sleep(3)
        await out.delete()
        if failed == 0:
            await m.reply_text(
                text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
                quote=True
            )
        else:
            await m.reply_document(
                document=f'broadcast_{broadcast_id}.txt',
                caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
                quote=True
            )
        os.remove(f'broadcast_{broadcast_id}.txt')
