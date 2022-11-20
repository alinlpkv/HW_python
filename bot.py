import telebot
from telebot import types
import collections
import pymorphy2
import requests
bot = telebot.TeleBot('5504235592:AAG0kpJKnO885NDqCMFHzclLs11H37KIvuQ')

@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'I am here. Text me smth.')

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == '/analyse':
        bot.send_message(message.from_user.id, 'Input the text for analysing')
        bot.register_next_step_handler(message, analyse_user_text)
    elif message.text == '/calc':
        calculation(message)
    elif message.text == '/chek_site':
        bot.send_message(message.from_user.id, 'Input url')
        bot.register_next_step_handler(message, cheking_site)
    else:
        bot.send_message(message.from_user.id, 'Text /chek_site')
        bot.send_message(message.from_user.id, 'Text /analyse')
        bot.send_message(message.from_user.id, 'Text /calc')

# Ex 1
def cheking_site(message):
    try:
        r = requests.get(message.text)
        if r.status_code == 200:
            bot.send_message(message.from_user.id, '👍👍👍')
        else:
            bot.send_message(message.from_user.id, '👎👎👎')
    except:
            bot.send_message(message.from_user.id, 'Input correct url')
            bot.register_next_step_handler(message, cheking_site)

# Ex 2
def analyse_user_text(message):
    text = message.text
    # Разбиваем на слова
    word_list = text.split()
    for index in range(len(word_list)):
        word_list[index] = word_list[index].translate({ord(i): None for i in '—,.!|%?-^$:;\'"*/'}).lower()

    # Удаление служебных частей речи
    gramem = {'PREP', 'CONJ', 'PRCL'}
    morph = pymorphy2.MorphAnalyzer()
    for word in word_list:
        p = morph.parse(word)[0]
        if p.tag.POS in gramem:
            word_list.remove(word)

    # Преобразуем в counter
    word_counter = collections.Counter(word_list)

    # Подсчитываем кол-во предложений
    count_sentences = 0
    sentences = list(filter(None, text.split('.')))
    for s in sentences:
        sen_1 = list(filter(None, s.split('!?')))
        for i in sen_1:
            sen_2 = list(filter(None, i.split('!')))
            for j in sen_2:
                sen_3 = list(filter(None, j.split('?')))
                count_sentences += len(sen_3)

    # Статистика
    bot.send_message(message.from_user.id, f'There are {count_sentences} sentences in the text.')
    bot.send_message(message.from_user.id, f'There are {len(list(word_counter))} unique words in the text.')
    for t in word_counter.most_common(5):
        if t[1] > 1:
            bot.send_message(message.from_user.id, f'The word "{t[0]}" occurs {t[1]} times in the text.')

# Ex 3
keyboard = types.InlineKeyboardMarkup()
key_9 = types.InlineKeyboardButton(text='9', callback_data='9')
key_8 = types.InlineKeyboardButton(text='8', callback_data='8')
key_7 = types.InlineKeyboardButton(text='7', callback_data='7')
key_6 = types.InlineKeyboardButton(text='6', callback_data='6')
key_5 = types.InlineKeyboardButton(text='5', callback_data='5')
key_4 = types.InlineKeyboardButton(text='4', callback_data='4')
key_3 = types.InlineKeyboardButton(text='3', callback_data='3')
key_2 = types.InlineKeyboardButton(text='2', callback_data='2')
key_1 = types.InlineKeyboardButton(text='1', callback_data='1')
key_0 = types.InlineKeyboardButton(text='0', callback_data='0')
key_symbol = types.InlineKeyboardButton(text=',', callback_data='.')
key_mult = types.InlineKeyboardButton(text='*', callback_data=' * ')
key_minus = types.InlineKeyboardButton(text='-', callback_data=' - ')
key_plus = types.InlineKeyboardButton(text='+', callback_data=' + ')
key_calc = types.InlineKeyboardButton(text='=', callback_data='=')
key_del = types.InlineKeyboardButton(text='C', callback_data='C')
key_div = types.InlineKeyboardButton(text='/', callback_data=' / ')
key_sqrt = types.InlineKeyboardButton(text='sqrt', callback_data='sqrt')
key_pow = types.InlineKeyboardButton(text='x^2', callback_data='pow')
key_pi = types.InlineKeyboardButton(text='pi', callback_data='3.14159265')

keyboard.row(key_pi, key_sqrt, key_pow, key_div)
keyboard.row(key_7, key_8, key_9, key_mult)
keyboard.row(key_4, key_5, key_6, key_minus)
keyboard.row(key_1, key_2, key_3, key_plus)
keyboard.row(key_del, key_0, key_symbol, key_calc)


mes = ''
value = '0'

def calculation(message):
    global mes, value
    value ='0'
    mes = bot.send_message(message.from_user.id, text= f'expression: {value}')
    bot.send_message(message.from_user.id, text='I am waiting ^_^', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(query):
    global value
    data = query.data

    if data == '=':
        try:
            result = eval(value)
            bot.send_message(query.message.chat.id, f'result = {result}')
            value = value + '=' + str(result)
        except:
            bot.send_message(query.message.chat.id, f'Error! Something went wrong!')
    elif data == 'pow' or data == 'sqrt':
        index_last_number = value.rfind(' ')
        try:
            number = float(value[index_last_number::])
            if data == 'pow':
                data = number ** 2
            else:
                data = number ** 0.5
            value = value[:index_last_number+1] + str(data)
        except:
            bot.send_message(query.message.chat.id, f'Error! Something went wrong!')
    elif data == 'C':
        if len(value) == 1:
            value = '0'
        else:
            value = value[:-1]
    else:
        if value == '0':
            value = ''
        value += data
    try:
        bot.edit_message_text(chat_id=query.message.chat.id, message_id=mes.id,
                                text=f'expression: {value}')
    except:
        pass


bot.polling(none_stop=False, interval=0)

