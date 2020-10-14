import telebot
import parser
from telebot import types
from bs4 import BeautifulSoup
import requests
import string
import traceback
from telebot.types import InputMediaPhoto
from PIL import Image

"""
guitar - Поиск по исполнителю для гитары
ukulele -  Поиск по исполнителю для укулеле
chords - Поиск аккорда 
"""

#main variables
TOKEN = "1038924278:AAHoYHOuNnzlEEh3EH8wjc0Alw9GDXJ2pWI"
ROOT_URL = 'https://uchords.net/'
UKULELE_SINGER_URL = 'https://uchords.net/ru/ukulele/ispolniteli/'
GUITAR_SINGER_URL = 'https://uchords.net/ru/gitara/ispolniteli/'
RUS_BTNS = {
            'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'je',
            'ж':'zh', 'з':'z', 'и':'i', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 
            'о':'o', 'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 
            'х':'kh', 'ц':'ts', 'ч':'ch', 'ш':'sh', 'щ':'shch', 'э':'e', 
            'ю':'yu', 'я':'ya', '09':'09'
        } 
TONALITIES = {
    0:'', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', -1:'11', -2:'10', -3:'9', -4:'8', -5:'7'
}
NOTES_ADD = ['', '5', '6', '7', '9', 'maj7', 'sus4', 'dim', 'm', 'm6', 'm7', 'm9']
bot = telebot.TeleBot(TOKEN)
singers = []
songs = []
cur_song = {'url':None, 'tonality':0}
media_group = []
instrument = {'name':None}
singer_url = None

def get_song(url):
    cur_song['url'] = url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    pre = soup.find('pre')
    spans = pre.find_all('span')
    chords = ''
    for span in spans:
        chords += span.text.lower().replace('#', 'x') + ' '
    chords = chords.replace('|', '')
    chords = set(" ".join(chords.split()).split(' '))
    get_chords_images(chords)
    title = soup.h1.text.split(',')[0]
    pattern_div = soup.find('div', id='vibrboy')
    pattern = soup.find('div', id='vibrboy').img['alt'] if pattern_div is not None else 'Нет'
    print('Song:', title)
    text = str(pre).replace('*', '#').replace('_', '#')
    text = text.replace('<span>', '*').replace('</span>', '*')\
                    .replace('<em>', '').replace('</em>', '')\
                    .replace('<pre>', '').replace('</pre>', '')
    return title, pattern, cur_song['tonality'], text

def parse_list(url, obj):
    callback = 'singer:' if obj == 'singers' else 'song:'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('a', class_='aspisn')
    keyboard = types.InlineKeyboardMarkup()
    iterator = 0
    singers.clear() if obj == 'singers' else songs.clear()
    for link in links:
        singers.append(link['href']) if obj == 'singers' else songs.append(link['href'])
        btn = types.InlineKeyboardButton(text=link.text, callback_data=callback+str(iterator))
        keyboard.add(btn)
        iterator += 1
    return keyboard

def get_keyboard(lang='russian', chords=None, note=None):
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if note:
        for n in NOTES_ADD:
            btn = types.InlineKeyboardButton(text=note + n, callback_data='chords:chord-' + note + n.replace('#', 'x').lower())
            btns.append(btn)
        prev_index = 0
        for num in range(4, 12+1, 4):
            keyboard.row(*btns[prev_index:num])
            prev_index += 4
    elif chords:
        if chords == 'notes':
            response = requests.get(ROOT_URL + 'ru/ukulele/akkordy.html')
            soup = BeautifulSoup(response.text, 'lxml')
            chords = soup.find_all('h2')
            for chord in chords:
                btn = types.InlineKeyboardButton(text=chord.text, callback_data='chords:note-'+chord.text)
                btns.append(btn)
            prev_index = 0
            for num in range(3, 12+1, 3):
                keyboard.row(*btns[prev_index:num])
                prev_index += 3
    else:
        letters = RUS_BTNS.keys() if lang == 'russian' else string.ascii_lowercase + '  '
        callback = 'letter-rus:' if lang == 'russian' else 'letter-eng:'
        for letter in letters:
            btn = types.InlineKeyboardButton(text=letter.upper(), callback_data=callback+letter)
            btns.append(btn)
        prev_index = 0
        for num in range(7, 28+1, 7):
            keyboard.row(*btns[prev_index:num])
            prev_index += 7
        if lang == 'russian':
            btn09 = types.InlineKeyboardButton(text='0-9', callback_data='letter-rus:09')
            btn_lang = types.InlineKeyboardButton(text='English', callback_data='lang:english')
        else:
            btn09 = types.InlineKeyboardButton(text='0-9', callback_data='letter-eng:09')
            btn_lang = types.InlineKeyboardButton(text='Русский', callback_data='lang:russian')
        keyboard.row(btn09, btn_lang)
    return keyboard

def get_chords_images(chords):
    media_group.clear()
    add = 'guitar/' if instrument['name'] == 'guitar' else ''
    for chord in list(chords)[:10]:
        url = ROOT_URL + 'images/' + add + chord + '.png'
        media_group.append(InputMediaPhoto(media=url))
    
@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    message = '''
*Привет!*\n
Здесь ты можешь найти большое количество аккордов российских и иностранных исполнителей для гитары и укулеле. 
Все аккорды размещены на сайте _{}_.
Бот создан с целью упростить поиск аккордов без необходимсоти посещения сайта.\n
Используя различные команды ты можешь управлять ботом:\n
*/ukulele* - поиск по исполнителю и выбор композиции для укулеле\n
*/guitar* - поиск по исполнителю и выбор композиции для гитары\n
*/chords* - поиск аккорда для гитары и укулеле
'''.format(ROOT_URL)
    msg = bot.send_message(chat_id, message, parse_mode="Markdown")

@bot.message_handler(commands=['chords'])
def chords_handler(message):
    keyboard = get_keyboard(chords='notes')
    bot.send_message(message.chat.id, u'\U0001F3B5' + ' Выберите ноту:', reply_markup=keyboard)

@bot.message_handler(commands=['ukulele', 'guitar'])
def search_handler(message):
    instrument['name'] = 'ukulele' if message.text == '/ukulele' else 'guitar'
    print('Instrument:', instrument['name'])
    chat_id = message.chat.id
    keyboard = get_keyboard()
    msg = bot.send_message(chat_id, u'\U0001F50E' + ' Поиск исполнителя\n' + u'\U0001F520' + ' Выберите букву:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        data_key = call.data.split(':')[0]
        data_value = call.data.split(':')[1]
        if data_key == 'singer':
            url = ROOT_URL + singers[int(data_value)]
            name = BeautifulSoup(requests.get(url).text, 'lxml').find('h1').text.split('-')[0]
            print('Singer:', name)
            keyboard = parse_list(url, 'songs')
            msg = bot.send_message(call.message.chat.id, u'\U0001F3A4' + ' Композиции исполнителя {}:'.format(name), reply_markup=keyboard)
        elif data_key == 'tonality' and data_value != 'info':
            if cur_song['tonality'] == 0:
                add = '-1.html' if data_value == 'plus' else '-11.html'
                cur_song['url'] = cur_song['url'].replace('.html', add)
                cur_song['tonality'] = 1 if data_value == 'plus' else -1
            else:
                if (cur_song['tonality'] == -1 and data_value == 'plus') or\
                (cur_song['tonality'] == 1 and data_value == 'minus') or\
                    cur_song['tonality'] in [-5, 5]:
                    cur_song['url'] = cur_song['url'].replace('-{}.html'.format(TONALITIES[cur_song['tonality']]), 
                                                        '.html')
                    cur_song['tonality'] = 0
                else:
                    add = 1 if data_value == 'plus' else -1
                    cur_song['url'] = cur_song['url'].replace('-{}.html'.format(TONALITIES[cur_song['tonality']]), 
                                                            '-{}.html'.format(int(TONALITIES[cur_song['tonality']]) + add))
                    cur_song['tonality'] += add
            title, pattern, tonality, text = get_song(cur_song['url'])
            keyboard = types.InlineKeyboardMarkup()
            btn_minus = types.InlineKeyboardButton(text=' - ', callback_data='tonality:minus')
            btn_info = types.InlineKeyboardButton(text=u'\U0001F3B6' + ' Тон: {}'.format(cur_song['tonality']), callback_data='tonality:info')
            btn_plus = types.InlineKeyboardButton(text=' + ', callback_data='tonality:plus')
            btn_chords = types.InlineKeyboardButton(text=u'\U0001F3B5' + 'Показать аккорды', callback_data='chords:show')
            keyboard.add(btn_minus, btn_info, btn_plus)
            keyboard.row(btn_chords)
            msg = bot.send_message(call.message.chat.id, 
                '_{}\nБой: {}\nТональность: {}_\n{}'.format(title, pattern, tonality, text), 
                parse_mode="Markdown", reply_markup=keyboard)
        elif data_key == 'song':
            url = ROOT_URL + songs[int(data_value)]
            cur_song['tonality'] = 0
            keyboard = types.InlineKeyboardMarkup()
            btn_minus = types.InlineKeyboardButton(text=' - ', callback_data='tonality:minus')
            btn_info = types.InlineKeyboardButton(text=u'\U0001F3B6' + ' Тон: 0', callback_data='tonality:info')
            btn_plus = types.InlineKeyboardButton(text=' + ', callback_data='tonality:plus')
            btn_chords = types.InlineKeyboardButton(text=u'\U0001F3B5' + ' Показать аккорды', callback_data='chords:show')
            keyboard.add(btn_minus, btn_info, btn_plus)
            keyboard.row(btn_chords)
            title, pattern, tonality, text = get_song(url)
            msg = bot.send_message(call.message.chat.id, 
                u'\U0001F3A4' + '_ {}\n'.format(title) +  u'\U0001F3BC' + ' Бой: {}\n'.format(pattern) + u'\U0001F3B6' + ' Тональность: {}_\n{}'.format(tonality, text), 
                parse_mode="Markdown", reply_markup=keyboard)
        elif data_key.startswith('letter'):
            print('Letter:', data_value)
            lang = 'ru_' if data_key == 'letter-rus' else 'en_'
            singer_url = UKULELE_SINGER_URL if instrument == 'ukulele' else GUITAR_SINGER_URL
            if lang == 'ru_':
                url = singer_url + lang + RUS_BTNS[data_value] +\
                    '/' + str(list(RUS_BTNS).index(data_value) + 2) + '.html'
            else:
                index = '30' if data_value == '09' else str(string.ascii_lowercase.index(data_value) + 31)
                url = singer_url + lang + data_value +\
                    '/' +  index + '.html'
            keyboard = parse_list(url, 'singers')
            msg = bot.send_message(call.message.chat.id, u'\U0001F3A4' + ' Исполнители на букву {}:'.format(data_value.upper()), reply_markup=keyboard)
        elif data_key == 'lang':
            print('Language:', data_value)
            keyboard = get_keyboard(data_value)
            msg = bot.send_message(call.message.chat.id, u'\U0001F50E' + ' Поиск исполнителя\n' + u'\U0001F520' + ' Выберите букву:', reply_markup=keyboard)
        elif data_key == 'chords':
            if data_value == 'show':
                bot.send_media_group(call.message.chat.id, media_group)
            elif data_value.startswith('note'):
                note = data_value.split('-')[1][:2].replace(' ', '')
                print('Note:', note)
                keyboard = get_keyboard(note=note)
                bot.send_message(call.message.chat.id, u'\U0001F3B6' + ' Выберите аккорд:', reply_markup=keyboard)
            elif data_value.startswith('chord'):
                caption = data_value.split('-')[1]
                print('Chord:', caption)
                chord = caption.replace('#', 'x').lower()
                media = [
                    InputMediaPhoto(media=ROOT_URL + 'images/guitar/' + chord + '.png', 
                                    caption='Аккорд {} на гитаре'.format(caption)),
                    InputMediaPhoto(media=ROOT_URL + 'images/' + chord + '.png', 
                                    caption='Аккорд {} на укулеле'.format(caption))              
                ]
                bot.send_media_group(call.message.chat.id, media)
    except:
        traceback.print_exc()
        bot.send_message(call.message.chat.id, u'\U0000274C' + ' Что-то пошло не так...\nПопробуй еще раз!')

bot.polling()
