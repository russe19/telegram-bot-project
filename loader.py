from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

logger.add("debug/debug.log", format="{time} | {level} | {message}", level="INFO",
           rotation="100 MB", compression="zip")
