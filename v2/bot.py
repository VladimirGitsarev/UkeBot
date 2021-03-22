import os

import traceback
import telebot


from dotenv import load_dotenv

from keyboards.chords import ChordsKeyboards
from callbacks.chords import ChordsCallback
from keyboards.songs import SongsKeyboards
from callbacks.tones import TonesCallback
from database.services import DBServices
from callbacks.link import LinkCallback
from messages.messages import Messages
from database.db import Database

load_dotenv()

"""
favorite - Избранные композиции
chords - Поиск аккорда 
help - Помощь
"""

bot = telebot.TeleBot(os.environ.get('TOKEN', '1038924278:AAHoYHOuNnzlEEh3EH8wjc0Alw9GDXJ2pWI'))
db_session = Database().create_session()
query = {'query': '', 'count': 0, 'result': None}
cur_song = {'url': None, 'tonality': 0}
chords_list = {'list': []}
links = []


@bot.message_handler(commands=['start'])
def start_handler(message):
    """Handle "/start" command call"""
    chat_id = message.chat.id
    text = Messages.start_message()
    bot.send_message(chat_id, text, parse_mode="Markdown")


@bot.message_handler(commands=['help'])
def help_handler(message):
    """Handle "/help" command call"""
    text = Messages.help_message()
    bot.send_message(message.chat.id, parse_mode="Markdown", text=text)


@bot.message_handler(commands=['chords'])
def chords_handler(message):
    keyboard = ChordsKeyboards.notes_keyboard()
    bot.send_message(message.chat.id, u'\U0001F3B5' + ' Выберите ноту:', reply_markup=keyboard)


@bot.message_handler(commands=['favorite'])
def chords_handler(message):
    user_id = message.from_user.id
    query['query'], query['count'] = '', 0
    keyboard, text = LinkCallback.link_callback('list', query, links, cur_song, chords_list, user_id, db_session)
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def get_text_message(message):
    """Handle user input message to use it as search query"""
    try:
        user_id = message.from_user.id
        query['query'], query['count'] = message.text, 0
        links.clear()
        keyboard, text = LinkCallback.link_callback('list', query, links, cur_song, chords_list, user_id, db_session)
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)
    except AttributeError:
        bot.send_message(
            message.chat.id,
            u'\U0001F6AB' + ' Поисковый запрос не дал результатов\nНичего не найдено. Попробуйте еще раз!'
        )
    except:
        traceback.print_exc()
        bot.send_message(message.chat.id, u'\U0000274C' + ' Что-то пошло не так...\nПопробуйте еще раз!')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    print(call.from_user.id)
    """Handle keyboard buttons clicks"""
    try:
        user_id = call.from_user.id
        data_key, data_value = call.data.split(':')
        if data_key == 'link':
            keyboard, text = LinkCallback.link_callback(data_value, query, links, cur_song, chords_list, user_id, db_session)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data_key == 'chords':
            data = ChordsCallback.chords_callback(data_value, chords_list)
            bot.send_media_group(call.message.chat.id, data) if type(data) == list else bot.send_message(
                call.message.chat.id,
                u'\U0001F3B6' + ' Выберите аккорд:',
                reply_markup=data
            )
        elif data_key == 'tone':
            keyboard, text = TonesCallback.tone_callback(data_value, cur_song, chords_list, user_id, db_session)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

        bot.answer_callback_query(call.id)
    except:
        traceback.print_exc()
        bot.send_message(call.message.chat.id, u'\U0001F914' + ' Cообщение не может быть отправлено.\n' +
                         '\nК сожалению, Telegram не позволяет отправить данное сообщение. ' +
                         'Вы можете просмотреть аккорды к данной композиции на сайте по ссылке:\n{}' \
                         .format('https:' + cur_song['url']))
        # bot.send_message(call.message.chat.id, u'\U0000274C' + ' Что-то пошло не так...\nПопробуйте еще раз!')


bot.polling()

# TODO add database for favorite songs: connection, models, logic
