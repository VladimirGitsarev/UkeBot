from telebot import types

from parsers.chords import ChordsParser


class ChordsKeyboards:

    @staticmethod
    def chords_keyboard(note):
        """Generate chords keyboard for chosen note"""
        notes_add = ['', '5', '6', '7', '9', 'maj7', 'sus4', 'dim', 'm', 'm6', 'm7', 'm9']
        keyboard = types.InlineKeyboardMarkup()
        btns = []
        for n in notes_add:
            btn = types.InlineKeyboardButton(
                text=note + n,
                callback_data='chords:chord-' + note + n.replace('#', 'x').lower(),
            )
            btns.append(btn)
        prev_index = 0
        for num in range(4, 12 + 1, 4):
            keyboard.row(*btns[prev_index:num])
            prev_index += 4

        return keyboard

    @staticmethod
    def notes_keyboard():
        """Generate notes keyboard"""
        btns = []
        chords = ChordsParser.get_notes()
        keyboard = types.InlineKeyboardMarkup()
        for chord in chords:
            btn = types.InlineKeyboardButton(text=chord.text, callback_data='chords:note-' + chord.text)
            btns.append(btn)
        prev_index = 0
        for num in range(3, 12 + 1, 3):
            keyboard.row(*btns[prev_index:num])
            prev_index += 3

        return keyboard
