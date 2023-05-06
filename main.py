import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from database.sqlite_db import Database
from service.trello import Trello
import pprint
import os

load_dotenv()
db = Database(db_name='data.db')
trello = Trello()

variables = ['BOT_TOKEN', 'API_HASH', 'API_ID']
API_TOKEN, API_HASH, API_ID = [os.getenv(name) for name in variables]
CHAT_ID = 175431040

bot = Client("echo_bot", api_id=API_ID, api_hash=API_HASH, bot_token=API_TOKEN)
storage = {}

@bot.on_message(filters.command(["start"]))
async def start_command(client, message):
    if not (db.check_user(message.from_user.id, 'users')):
        record = (message.from_user.id, 'token', 'token', 'active', message.from_user.username)
        db.add_record('users', record)
        await message.reply("Пользователь создан в базе. Теперь необходимо добавить ключ и токен вашего Trello.")
    else:
        await message.reply("Вы уже есть в базе. Можете воспользоваться командами.")

@bot.on_message(filters.command(["trello_api"]))
async def get_api_key(client, message):
    if (db.check_user(message.from_user.id, 'users')):
        await message.reply("Введите ваш ключ Trello API.")
        storage[message.from_user.id] = 'waiting_apikey'
    else:
        await message.reply("Выполните команду /start для добавления в базу")

@bot.on_message(filters.command(["trello_token"]))
async def get_api_key(client, message):
    if (db.check_user(message.from_user.id, 'users')):
        await message.reply("Введите ваш токен Trello API.")
        storage.update({message.from_user.id: 'waiting_token'})
    else:
        await message.reply("Выполните команду /start для добавления в базу")

@bot.on_message(filters.command(["menu"]))
async def menu_command(client, message):
    if db.check_user(message.from_user.id, 'users'):
        if db.check_token(message.from_user.id, 'users') and db.check_api(message.from_user.id, 'users'):
            buttons = [
                [InlineKeyboardButton("Протухающие таски.", callback_data="tasks")],
                [InlineKeyboardButton("Отмена.", callback_data="cancel")]
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            await message.reply("Что желаешь хозяин?", reply_markup=keyboard)
        else:
            await message.reply("Выполни команду /trello_api и /trello_token, для добавления ключа и токена")
    else:
        await message.from_user.id

@bot.on_message(filters.command(["boards"]))
async def boards_command(client, message):
    desks =[desk[0] for desk in db.get_table_ids(message.from_user.id)]
    if desks:
        await message.reply(f'Ваши доски: {desks}, что бы изменить отправьте команду /change_boards')
    else:
        await message.reply(f'Вы не добавили ни одной доски. Что бы добавить отправьте команду /change_boards')

@bot.on_message(filters.command(["change_boards"]))
async def change_boards_command(client, message):
    await message.reply(f'Введите ID доски которую хотите добавить\удалить')
    storage[message.from_user.id] = 'waiting_desk'


@bot.on_message()
async def trello_api_handler(client, message):
    state = storage.get(message.from_user.id)
    if state == 'waiting_desk':
        desks =[desk[0] for desk in db.get_table_ids(message.from_user.id)]
        if message.text in desks:
            db.remove_table(message.from_user.id, message.text)
            await message.reply(f"Удалили доску {message.text}")
        else:
            db.add_table(message.from_user.id, message.text)
            await message.reply(f"Добавили доску: {message.text}")
        storage[message.from_user.id] = 'finished'
    if state == 'waiting_apikey':
        db.add_api_trello(message.text, message.from_user.id)
        await message.reply(f"Добавили ваш ключ в базу. {message.text[0:5]}XXXXXXXXXXXXXX")
        storage[message.from_user.id] = 'finished'
    if state == 'waiting_token':
        db.add_token_trello(message.text, message.from_user.id)
        await message.reply(f"Добавили ваш токен в базу. {message.text[0:5]}XXXXXXXXXXXXXX")
        storage[message.from_user.id] = 'finished'


@bot.on_callback_query()
async def button_click(client, callback_query):
    message = callback_query.message
    
    if callback_query.data == "tasks":
        desks =[desk[0] for desk in db.get_table_ids(callback_query.from_user.id)]
        if desks:
            api_key = db.get_api_key(callback_query.from_user.id)
            api_token = db.get_api_token(callback_query.from_user.id)
            for desk in desks:
                try:
                    tasks = await trello.get_board_tasks(api_key, api_token, desk)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")
                    break
                    
                task_list = f'Доска:{desk}\n'
                for task in tasks:
                    name = task.get('name')
                    url = task.get('url')
                    due = task.get('due')
                    if due:
                        due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ')
                        now = datetime.datetime.now()
                        time_left = due_date - now
                        days = time_left.days
                        hours = time_left.seconds / 3600
                        time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов.'
                    # else:
                    #     time_left='Без дедлайна'
                        if days <= 1:
                            task_list += (f'[{name}]({url})\n {time_left}\n')
                await message.edit_text(task_list)
        else:
            await message.edit_text(f'Нет досок для отслеживания')
    elif callback_query.data == "cancel":
        await message.edit_text(f"Пока! {callback_query.from_user.username}")

if __name__ == "__main__":
    bot.run()