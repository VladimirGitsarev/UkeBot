from telebot import types
from database.services import DBServices

class SongsKeyboards:

    @staticmethod
    def query_list_keyboard(tags, links, query):
        """Generate keyboard for listing query results"""
        keyboard = types.InlineKeyboardMarkup()
        iterator = 0
        links.clear()
        for e in tags[query['count'] % 30:query['count'] % 30 + 10]:
            singer_tag, song_tag = e.findAll('a')
            links.append(song_tag['href'])
            btn = types.InlineKeyboardButton(
                text="{} - {}".format(singer_tag.text, song_tag.text),
                callback_data='link:' + str(iterator)
            )
            keyboard.add(btn)
            iterator += 1

        more_btn = types.InlineKeyboardButton(
            text='Далее ' + u'\U0001F449',
            callback_data='link:more'
        )
        less_btn = types.InlineKeyboardButton(
            text=u"\U0001F448" + ' Назад',
            callback_data='link:less'
        )
        if query['count'] == 0 and query['result'] > 10:
            keyboard.add(more_btn)
        elif query['count'] + 10 > query['result'] > 10:
            keyboard.add(less_btn)
        else:
            if query['result'] > 10:
                keyboard.row(less_btn, more_btn)
        return keyboard

    @staticmethod
    def favorite_list_keyboard(songs, query, links):
        """Generate keyboard for listing favorites"""
        keyboard = types.InlineKeyboardMarkup()
        iterator = 0
        links.clear()
        for song in songs[query['count'] % 30:query['count'] % 30 + 10]:
            links.append(song.url)
            btn = types.InlineKeyboardButton(
                text="{}".format(song.title.replace(', аккорды', '')),
                callback_data='link:' + str(iterator)
            )
            keyboard.add(btn)
            iterator += 1

        more_btn = types.InlineKeyboardButton(
            text='Далее ' + u'\U0001F449',
            callback_data='link:more'
        )
        less_btn = types.InlineKeyboardButton(
            text=u"\U0001F448" + ' Назад',
            callback_data='link:less'
        )
        if query['count'] == 0 and query['result'] > 10:
            keyboard.add(more_btn)
        elif query['count'] + 10 > query['result'] > 10:
            keyboard.add(less_btn)
        else:
            if query['result'] > 10:
                keyboard.row(less_btn, more_btn)
        return keyboard

    @staticmethod
    def song_keyboard(cur_song, user_id, db_session):
        """Generate keyboard for a specific song"""

        liked = DBServices.check_liked(user_id, cur_song, db_session)
        like_text = '\nУдалить' if liked else '\nВ избранное'

        keyboard = types.InlineKeyboardMarkup()
        btn_minus = types.InlineKeyboardButton(text=u'\U00002796', callback_data='tone:minus')
        btn_info = types.InlineKeyboardButton(text=u'\U0001F3B6' + ' Тон: {}'.format(cur_song['tonality']),
                                              callback_data='tone:info')
        btn_plus = types.InlineKeyboardButton(text=u'\U00002795', callback_data='tone:plus')
        btn_left = types.InlineKeyboardButton(
            text=u'\U0001F3BC' + "\nГитара",
            callback_data='chords:guitar'
        )
        btn_right = types.InlineKeyboardButton(
            text=u'\U0001F3BC' + "\nУкулеле",
            callback_data='chords:uke'
        )
        btn_list = types.InlineKeyboardButton(
            text=u'\U0001F5D2' + '\nК списку',
            callback_data='link:list'
        )
        btn_like = types.InlineKeyboardButton(
            text=u'\U00002B50' + like_text,
            callback_data='link:like'
        )
        keyboard.row(btn_minus, btn_info, btn_plus)
        keyboard.row(btn_left, btn_right)
        keyboard.row(btn_list, btn_like)

        return keyboard
