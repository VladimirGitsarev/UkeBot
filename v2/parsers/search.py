import requests
import os

from bs4 import BeautifulSoup


class SearchParser:

    @staticmethod
    def query_result(query):
        """Parse all found songs and links according to the query"""
        url = os.getenv('AMDM_URL') + 'search/?q='
        if query['count'] >= 30:
            url = url.replace('search/', 'search/page' + str(query['count'] // 30 + 1) + '/')
        rq = requests.get(url + query['query'].replace(' ', '+'))
        soup = BeautifulSoup(rq.text, 'lxml')
        string = soup.find('div', class_='h1__info').text
        query['result'] = [int(s) for s in string.split() if s.isdigit()][0]
        tags = soup.find('body').find('table').findAll('td', class_='artist_name')

        return tags
