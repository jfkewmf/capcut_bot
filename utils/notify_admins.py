import logging

from aiogram import Dispatcher
from database.database import db
from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Bot ishga tushdi")
            
        except Exception as err:
            logging.exception(err)