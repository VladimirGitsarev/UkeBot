from typing import Tuple

from telebot.types import InlineKeyboardMarkup

from keyboards.songs import SongsKeyboards
from parsers.songs import SongParser


class TonesCallback:

    @staticmethod
    def tone_callback(data_value, cur_song, chords_list, user_id, db_session):
        """Update current song tonality"""
        if data_value == 'plus':
            if cur_song['tonality'] == 11:
                cur_song['tonality'] = 0
            else:
                cur_song['tonality'] += 1
        elif data_value == 'minus':
            if cur_song['tonality'] == -11:
                cur_song['tonality'] = 0
            else:
                cur_song['tonality'] -= 1

        return TonesCallback._get_song_text(cur_song, chords_list, user_id, db_session)

    @staticmethod
    def _get_song_text(cur_song, chords_list, user_id, db_session) -> Tuple[InlineKeyboardMarkup, str]:
        """Get song text with chords for updated tonality"""
        cur_song['id'] = cur_song['url'].split('/')[5]
        data = {'song_id': cur_song['id'], 'tone': cur_song['tonality']}
        text = SongParser.tone_song_text(data, cur_song, chords_list)
        keyboard = SongsKeyboards.song_keyboard(cur_song, user_id, db_session)

        return keyboard, text
