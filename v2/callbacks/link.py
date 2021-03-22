from typing import Tuple

from telebot.types import InlineKeyboardMarkup

from database.services import DBServices
from keyboards.songs import SongsKeyboards
from parsers.search import SearchParser
from parsers.songs import SongParser



class LinkCallback:

    @staticmethod
    def link_callback(data_value, query, links, cur_song, chords_list, user_id, db_session):
        """Generate message for songs list or a particular song"""
        if data_value in ['more', 'less', 'list']:
            return LinkCallback._link_list_callback(data_value, query, links, user_id, db_session)
        elif data_value == 'like':
            return LinkCallback._link_like_callback(user_id, db_session, cur_song, chords_list)
        return LinkCallback._link_song_callback(data_value, cur_song, links, chords_list, user_id, db_session)

    @staticmethod
    def _link_list_callback(data_value, query, links, user_id, db_session) -> Tuple[InlineKeyboardMarkup, str]:
        """Generate message for current page of songs list"""
        if data_value == 'more':
            query['count'] += 10
        elif data_value == 'less':
            if query['count'] != 0:
                query['count'] -= 10

        if query['query']:
            tags = SearchParser.query_result(query)
            keyboard = SongsKeyboards.query_list_keyboard(tags, links, query)
            text = u'\U0001F50E' + ' Поиск по запросу \"{}\" \nНайдено {} совпадений\nСтраница {} из {}:' \
                .format(query['query'], query['result'], query['count'] // 10 + 1, query['result'] // 10 + 1)
        else:
            songs = DBServices.get_favorites(user_id, db_session)
            query['result'] = len(songs)
            keyboard = SongsKeyboards.favorite_list_keyboard(songs, query, links)
            text = u'\U00002B50' + ' Избранные композиции\nСтраница {} из {}:'\
                .format(query['count'] // 10 + 1, query['result'] // 10 + 1)
        return keyboard, text

    @staticmethod
    def _link_song_callback(data_value, cur_song, links, chords_list, user_id, db_session) -> Tuple[InlineKeyboardMarkup, str]:
        """Generate message for current song"""
        cur_song['tonality'] = 0
        cur_song['title'] = None
        title, text = SongParser.song_text(links[int(data_value)], cur_song, chords_list)
        print("Song:", title)
        text = '_{}_\n \n{}'.format(title, text)
        keyboard = SongsKeyboards.song_keyboard(cur_song, user_id, db_session)
        return keyboard, text

    @staticmethod
    def _link_like_callback(user_id, db_session, cur_song, chords_list) -> Tuple[InlineKeyboardMarkup, str]:
        if DBServices.check_liked(user_id, cur_song, db_session):
            DBServices.remove_song_from_favorites(user_id, cur_song, db_session)
        else:
            DBServices.add_song_to_favorites(user_id, cur_song, db_session)
        cur_song['tonality'] = 0
        title, text = SongParser.song_text(cur_song['url'], cur_song, chords_list)
        text = '_{}_\n \n{}'.format(title, text)
        keyboard = SongsKeyboards.song_keyboard(cur_song, user_id, db_session)
        return keyboard, text
