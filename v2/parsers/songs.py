import os

import requests
from bs4 import BeautifulSoup


class SongParser:

    @staticmethod
    def song_text(url, cur_song, chords_list):
        """Parse song text"""
        cur_song['url'] = url
        rq = requests.get('https:' + url)
        soup = BeautifulSoup(rq.text, 'lxml')
        title = soup.h1.text
        cur_song['title'] = title
        spans = soup.find('pre').find_all('b')
        chords = ''
        for span in spans:
            chords += span.text.lower().replace('#', 'x') + ' '
        chords = chords.replace('|', '')
        chords_list['list'] = set(" ".join(chords.split()).split(' '))
        text = str(soup.find('pre')) \
            .replace('<b>', '*').replace('</b>', '*') \
            .replace('<pre itemprop="chordsBlock">', '') \
            .replace('</pre>', '')

        return title, text

    @staticmethod
    def tone_song_text(data, cur_song, chords_list):
        """Parse song text with given tonality"""
        rq = requests.post(os.environ.get('AMDM_URL') + 'json/song/transpon/', data=data)
        soup = BeautifulSoup(str(rq.json()['song_text']), 'lxml')
        spans = soup.find_all('b')
        chords = ''
        for span in spans:
            chords += span.text.lower().replace('#', 'x') + ' '
        chords = chords.replace('|', '')
        chords_list['list'] = set(" ".join(chords.split()).split(' '))
        text = rq.json()['song_text'].replace('<b>', '*').replace('</b>', '*')

        return '_{}_\n \n{}'.format(cur_song['title'], text)

