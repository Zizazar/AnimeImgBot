import requests
import telebot
from telebot.types import  ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import timedelta
import json
TOKEN = '5408793129:AAFSTsOIRhxCwZ9PJw7jFiX4dbdK7e2HraQ'
bot = telebot.TeleBot(TOKEN)
animeData = {}
page = 0
VideoMoment = False
@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    req = call.data.split('_')
    #Обработка кнопок - вперед и назад
    if 'pagination' in req[0]:
      	#Расспарсим полученный JSON
        json_string = json.loads(req[0])
        count = json_string['CountPage']
        page = json_string['NumberPage']
				#Пересоздаем markup
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Подробнее', url='https://anilist.co/anime/{}'.format(animeData['result'][page-1]['anilist']['id'])))
        #markup для первой страницы
        if page == 1:
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        #markup для второй страницы
        elif page == count:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
        #markup для остальных страниц
        else:
            markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page-1) + ",\"CountPage\":" + str(count) + "}"),
                           InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                           InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page+1) + ",\"CountPage\":" + str(count) + "}"))

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_video(       #Отправка результата
        call.message.chat.id,
        video= animeData['result'][page-1]['video'],
        caption= f'''<u>Результаты поиска:</u>
🇯🇵Название: {animeData['result'][page-1]['anilist']['title']['native']} 
🇺🇸Название: {animeData['result'][page-1]['anilist']['title']['english'] if animeData['result'][page-1]['anilist']['title']['english']!=None else 'нет'}
📺Серия: {animeData['result'][page-1]['episode']}
🕒Фрагмент: <b>{timedelta(seconds=round(animeData['result'][page-1]['from']))}</b> - <b>{timedelta(seconds=round(animeData['result'][page-1]['to']))}</b> 
📊Сходство: {round(float(animeData['result'][page-1]['similarity'])*100, 2)}%
{'🔞'if animeData['result'][page-1]['anilist']['isAdult'] else ''}
''',
        reply_markup=markup,
        parse_mode='HTML'
        )


@bot.message_handler(content_types=['photo'])
def Sarcher(message):
    try:
        photo_id = message.photo[len(message.photo) - 1].file_id
        file_info = bot.get_file(photo_id)
        print(file_info.file_path)
        print(f'http://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        response = requests.get(f'https://api.trace.moe/search?anilistInfo&url=http://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        global animeData
        animeData = response.json()
        
        count = 10
        page = 1
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Подробнее', url='https://anilist.co/anime/{}'.format(animeData['result'][page-1]['anilist']['id'])))
        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page+1) + ",\"CountPage\":" + str(count) + "}"))

        bot.send_video(       #Отправка результата с видео
        message.chat.id,
        video= animeData['result'][page-1]['video'],
        caption= f'''<u>Результаты поиска:</u>
🇯🇵Название: {animeData['result'][page-1]['anilist']['title']['native']} 
🇺🇸Название: {animeData['result'][page-1]['anilist']['title']['english'] if animeData['result'][page-1]['anilist']['title']['english']!=None else 'нет'}
📺Серия: {animeData['result'][page-1]['episode']}
🕒Фрагмент: <b>{timedelta(seconds=round(animeData['result'][page-1]['from']))}</b> - <b>{timedelta(seconds=round(animeData['result'][page-1]['to']))}</b> 
📊Сходство: {round(float(animeData['result'][page-1]['similarity'])*100, 2)}%
{'🔞'if animeData['result'][page-1]['anilist']['isAdult'] else ''}
''',
        reply_markup=markup,
        parse_mode='HTML'
        )
    except:
        bot.send_message(message.chat.id, 'Ошибка')
@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, 'Ошибка: Отправьте картинку для распознавания')
bot.polling()