import os

import requests

from telebot.types import InputMediaPhoto
from bs4 import BeautifulSoup


class ChordsParser:

    @staticmethod
    def get_notes():
        """Parse all notes"""
        response = requests.get(os.environ.get('UCHORDS_URL') + 'ru/ukulele/akkordy.html')
        soup = BeautifulSoup(response.text, 'lxml')
        chords = soup.find_all('h2')

        return chords

    @staticmethod
    def get_chords(instrument, chords):
        """Parse chords images for current song"""
        media_group = []
        add = 'guitar/' if instrument['name'] == 'guitar' else ''
        for chord in list(chords['list'])[:10]:
            url = os.environ.get('UCHORDS_URL') + 'images/' + add + chord + '.png'
            media_group.append(InputMediaPhoto(media=url))

        return media_group

    @staticmethod
    def get_chord(chord, caption):
        """Parse particular chord images for guitar and ukulele"""
        return [
            InputMediaPhoto(
                media=os.environ.get('UCHORDS_URL') + 'images/guitar/' + chord + '.png',
                caption='Аккорд {} на гитаре'.format(caption)
            ),
            InputMediaPhoto(
                media=os.environ.get('UCHORDS_URL') + 'images/' + chord + '.png',
                caption='Аккорд {} на укулеле'.format(caption)
            )
        ]
