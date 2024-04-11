# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

import logging, os
from pyrogram import Client
from async_pymongo import AsyncClient

from ..vars import Var

logger = logging.getLogger("bot")

sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
if Var.USE_SESSION_FILE:
    logger.info("Using session files")
    logger.info("Session folder path: {}".format(sessions_dir))
    if not os.path.isdir(sessions_dir):
        os.makedirs(sessions_dir)

mongo_conn = AsyncClient(Var.DATABASE_URL)

StreamBot = Client(
    name="WebStreamer",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    plugins={"root": "WebStreamer/bot/plugins"},
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
    in_memory=False,
    mongodb=dict(connection=mongo_conn, remove_peers=False)
)

multi_clients = {}
work_loads = {}