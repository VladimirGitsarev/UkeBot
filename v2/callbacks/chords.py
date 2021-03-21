from typing import List

from telebot.types import InlineKeyboardMarkup, InputMediaPhoto
from keyboards.chords import ChordsKeyboards
from parsers.chords import ChordsParser


class ChordsCallback:

    @staticmethod
    def chords_callback(data_value, chords_list):
        """Handle chords buttons"""
        if data_value in ['guitar', 'uke']:
            return ChordsCallback._chords_song_callback(data_value, chords_list)
        elif data_value.startswith('note'):
            return ChordsCallback._notes_callback(data_value)
        elif data_value.startswith('chord'):
            return ChordsCallback._chord_callback(data_value)

    @staticmethod
    def _chords_song_callback(data_value, chords_list) -> List[InputMediaPhoto]:
        """Get chords images for current song"""
        instrument = {'name': data_value}
        return ChordsParser.get_chords(instrument, chords_list)

    @staticmethod
    def _chord_callback(data_value) -> List[InputMediaPhoto]:
        """Get chord image for chosen chord for guitar and ukulele"""
        caption = data_value.split('-')[1]
        chord = caption.replace('#', 'x').lower()
        print('Chord:', caption)
        return ChordsParser.get_chord(chord, caption)

    @staticmethod
    def _notes_callback(data_value) -> InlineKeyboardMarkup:
        """Generate chords keyboard for chosen note"""
        note = data_value.split('-')[1][:2].replace(' ', '')
        print('Note:', note)
        return ChordsKeyboards.chords_keyboard(note)
