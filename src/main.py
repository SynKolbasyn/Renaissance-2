import logging
import aiogram
import os

import functions

logging.basicConfig(level=logging.INFO, filename="../logs.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

bot = aiogram.Bot(token=os.getenv("BOT_TOKEN"))
dp = aiogram.Dispatcher(bot)


async def setup_bot_commands(dispatcher):
    bot_commands = [
        aiogram.types.BotCommand(command="/start", description="Show start menu"),
        aiogram.types.BotCommand(command="/help", description="Show start menu"),
        aiogram.types.BotCommand(command="/info", description="Show player info"),
        aiogram.types.BotCommand(command="/inventory", description="Show player inventory")
        ]
    await bot.set_my_commands(bot_commands)


@dp.message_handler(commands=["start", "help"])
async def start(message: aiogram.types.Message):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    functions.except_new_player(message.from_user.id, message.from_user.username, message.from_user.first_name)
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*functions.get_action_buttons(message.from_user.id))
    await message.answer(f"Hello {message.from_user.first_name}. "
                         f"Welcome to Renaissance 2, here you can do whatever you want, "
                         f"and your path is determined only by you. What are you waiting for, let's go!",
                         reply_markup=keyboard)


@dp.message_handler(commands="info")
async def info(message: aiogram.types.Message):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    answer = functions.get_player_info(message.from_user.id, message.from_user.username, message.from_user.first_name)
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*functions.get_action_buttons(message.from_user.id))
    await message.answer(answer, reply_markup=keyboard)


@dp.message_handler(commands="inventory")
async def info(message: aiogram.types.Message):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    answer = functions.get_player_inventory_info(message.from_user.id, message.from_user.username,
                                                 message.from_user.first_name)
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*functions.get_action_buttons(message.from_user.id))
    await message.answer(answer, reply_markup=keyboard)


@dp.message_handler()
async def main(message: aiogram.types.Message):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    answer = functions.execute_action(message.text, message.from_user.id, message.from_user.username,
                                      message.from_user.first_name)
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*functions.get_action_buttons(message.from_user.id))
    await message.answer(answer, reply_markup=keyboard)


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)
