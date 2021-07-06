import telebot
from telebot import types
import json
from citymobilAPI import requestCORDS, findadress
from db import BotDB
from threading import Thread
import time
import datetime
f = open('api.txt', 'r', encoding='UTF-8')
api_key = f.read()
bot = telebot.TeleBot(api_key)


# @bot.message_handler(content_types=['location'])
# def start_message(message):
#     cords = str({'longitude': 37.53554, 'latitude': 55.884434}).replace("'", '"').replace("'", '"')
##     cords = str(message.location).replace("'", '"')
#     cords_j = json.loads(cords)
#     longitude = cords_j['longitude']
#     latitude = cords_j['latitude']
#     bot.send_message(message.chat.id, f'Привет, твои координаты:\nПо долготе - {longitude}\nПо широте - {latitude}')

def dialog(message):
    markup_geo = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    btn_geo = types.KeyboardButton('Отправить своё местоположение', request_location=True)
    btn_txt = types.KeyboardButton('Написать адрес вручную')
    markup_geo.add(btn_geo, btn_txt)
    bot.send_message(message.chat.id, f'Для начала нам нужно получить адрес отправки', reply_markup=markup_geo)
    bot.register_next_step_handler(message, chooseMethod, 'from')


def chooseMethod(message, type: str):
    if message.location != None:
        changeLOCATION(message, type)
    else:
        if type == 'from':
            bot.send_message(message.chat.id, f'Пишите адрес')
            bot.register_next_step_handler(message, changeTEXT, type)
        if type == 'to':
            changeTEXT(message, type)


def changeLOCATION(message, type: str):
    cur_cords = cordsReceiver(message)
    BotDB().insertRoute(message.from_user.id, cur_cords[0], cur_cords[1], type)

    if type == 'from':
        bot.send_message(message.chat.id, f'Теперь напиши адрес назначения, или пришли в виде геолокации')
        bot.register_next_step_handler(message, chooseMethod, 'to')
    if type == 'to':
        changeTo(message)


def changeTEXT(message, type: str):
    cur_cords = findadress(message.text)
    bot.send_message(message.chat.id, f"<strong>Адрес отправления</strong>\n{cur_cords['country']}, {cur_cords['region']}, {cur_cords['sub_region']}, {cur_cords['postal_code']}, {cur_cords['title']}", parse_mode='HTML')
    BotDB().insertRoute(message.from_user.id, cur_cords['latitude'], cur_cords['longitude'], type)

    if type == 'from':
        bot.send_message(message.chat.id, f'Теперь напиши адрес назначения, или пришли в виде геолокации')
        bot.register_next_step_handler(message, chooseMethod, 'to')
    if type == 'to':
        changeTo(message)


def changeTo(message):
    btn_yes = types.KeyboardButton('Да')
    btn_no = types.KeyboardButton('Нет')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(btn_yes, btn_no)

    data = BotDB().getRouteData(message.from_user.id)
    from_latitude = data[2]
    from_longitude = data[3]
    to_latitude = data[4]
    to_longitude = data[5]

    bot.send_message(message.chat.id, f'<strong>Твои координаты</strong>\n{from_latitude}:{from_longitude}\n\n<strong>Координаты места назначения</strong>\n{to_latitude}:{to_longitude}', parse_mode='HTML')
    answ = requestCORDS(from_latitude, from_longitude, to_latitude, to_longitude)


    for i in range(len(answ)):
        source_link = types.InlineKeyboardMarkup()
        btn_citymobil_details = types.InlineKeyboardButton(text='Подробнее о тарифе', url=f'{answ[i]["link"]}')
        source_link.add(btn_citymobil_details)

        out = (f'<strong>Тариф:</strong> {answ[i]["tariff_type"]}\n<strong>Цена:</strong> {answ[i]["price"]}\n<strong>Модели машин:</strong> {answ[i]["car_models"]}\n<strong>Вместимость:</strong> {answ[i]["space"]}')
        bot.send_message(message.chat.id, out, reply_markup=source_link, parse_mode='HTML')
    bot.send_message(message.chat.id, 'Хотите поставить уведомление на желаемую Вами цену?', reply_markup=markup)
    bot.register_next_step_handler(message, subscriptionPriceInformer)


def subscriptionPriceInformer(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    btn = types.KeyboardButton('Выбрать другой адрес')
    markup.add(btn)

    if message.text == 'Да':
        bot.send_message(message.chat.id, 'Пишите цену')
        bot.register_next_step_handler(message, enterPrice)
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'ок', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Выбирайте ответ на кнопках')
        bot.register_next_step_handler(message, subscriptionPriceInformer)



def enterPrice(message):
        if message.text.isdigit():
            BotDB().insertRequestPrice(message.from_user.id, message.text)
            bot.send_message(message.chat.id, f'Вы подписались на уведомление.\nПри достижении {message.text}руб. вам придёт сообщение!')
        else:
            bot.send_message(message.chat.id, 'Введите число')
            bot.register_next_step_handler(message, enterPrice)


def cordsReceiver(message):
    cords = str(message.location).replace("'", '"')
    cords_j = json.loads(cords)
    longitude = cords_j['longitude']
    latitude = cords_j['latitude']
    # bot.send_message(message.chat.id, f'Привет, твои координаты:\nПо долготе - {longitude}\nПо широте - {latitude}')
    return [latitude, longitude]


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Начать расчёт стоимости поездки':
        dialog(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton('Начать расчёт стоимости поездки')
        markup.add(btn1)
        bot.send_message(message.chat.id, f'Привет! Чтобы начать пользоваться, используй активные кнопки внизу!',  reply_markup=markup)

        tm_login = message.from_user.username
        tm_firstName = message.from_user.first_name
        tm_lastName = message.from_user.last_name
        tm_userId = message.from_user.id
        BotDB().checkUser([tm_login, tm_firstName, tm_lastName, tm_userId], register=True)

class Starter():
    def startBot(self):
        try:
            print("Бот запущен")
            bot.polling()
        except Exception as E:
            print("Какая-то ошибка...")
            print(E)
            self.startBot()

    def priceUpdater(self):
        while True:
            parse = BotDB().showTable()
            for i in range(len(parse)):
                print("Price updater:", datetime.datetime.today())
                answ = requestCORDS(parse[i][2], parse[i][3], parse[i][4], parse[i][5])
                current_price = answ[0]['price']
                BotDB().updateCurrentPrice(int(parse[i][1]), int(current_price))
            self.priceChecker()
            time.sleep(5)


    def priceChecker(self):
        parse = BotDB().showTable()
        for i in range(len(parse)):
            print("Price checker:", datetime.datetime.today(), "\n")
            current_price = parse[i][7]
            chatId = BotDB().findUserByFK(parse[i][1])[4]
            if parse[i][6] is not None: # отсеивание ошибки nonetype
                if (parse[i][6] >= parse[i][7] or (parse[i][6]+((parse[i][6]/100)*5)) >= parse[i][7]):
                    bot.send_message(chatId, f'Цена достигла {current_price} рублей!')
                    BotDB().stopSubInformer(parse[i][1])
                    self.priceUpdater()

if __name__ == '__main__':
    Thread(target=Starter().startBot).start()
    Thread(target=Starter().priceUpdater).start()