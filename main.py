import telebot
from os import environ
from os import makedirs
from os.path import exists

from requests import get
from json import loads

if __name__ == '__main__':
    bot = telebot.TeleBot(environ['TELEGRAM_TOKEN'])

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "hewwo UwU")
        bot.send_message(message.chat.id, "Я присылаю первые 10 картинок из треда, ссылку на который ты можешь указать в следующем сообщении. Хочешь попробовать?")
        bot.register_next_step_handler(message, get_answer)

    def get_answer(message):
        if str.lower(message.text) == 'нет':
            bot.send_message(message.chat.id, "Ну и ладно :(")
        elif str.lower(message.text) == 'да':
            bot.send_message(message.chat.id, 'Отлично, пришли мне ссылку на тред')
            bot.register_next_step_handler(message, scraper)
        else:
            bot.send_message(message.chat.id, 'Не понимаю тебя :(')

    def exception_handler(message):
        bot.send_message(message.chat.id, 'Это не очень похоже на ссылку :( Хочешь попробовать снова?')
        bot.register_next_step_handler(message, get_answer)

    def scraper(message):
        url = message.text

        header = {"User-Agent": "Mozilla/5.0"}
        if ".html" in url:
            url = url.replace(".html", ".json")
        else:
            exception_handler(message)
            return
        delimiter = "hk"
        parts = url.split(delimiter)
        base_url = parts[0] + delimiter
        j = 0
        try:
            scraper = get(url)
        except:
            exception_handler(message)
            return

        result = scraper.content
        js = loads(result)

        for post in js['threads'][0]['posts']:
            if post['files'] is not None and j < 10:
                for file in post['files']:
                    ref = file['path']
                    if ".html" not in ref and ".mp4" not in ref and ".webm" not in ref:
                        img_url = base_url + ref
                        print(img_url)
                        image = get(img_url, headers=header, stream=True).content
                        if image.__sizeof__() >= 10739054:
                            bot.send_message(message.chat.id, 'Не могу отправить фото больше 10МБ, отправлю следующее за ним')
                        else:
                            bot.send_photo(message.chat.id, image)
                            j += 1
        print("Success")


    @bot.message_handler(content_types=["text"])
    def message(message):
        if message.text == 'Привет':
            bot.send_message(message.chat.id, 'Приветик! :3 Напиши /start!')
        else:
            bot.send_message(message.chat.id, 'Я пока только учусь :( Напиши /start, чтобы начать!')

    bot.infinity_polling()
