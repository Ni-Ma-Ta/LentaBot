import telebot

from secrets import telebot_token

bot = telebot.Telebot(telebot_token)

@bot.message_handler(commands=['start'])
def init(message):
    bot.reply_to(message, 'Привет! Я симулирую ленту наиболее популярных новостей по выбранным вами каналам. \nДля того, чтобы начать, пришлите мне "Добавить новый канал [Название канала] [Частота в часах] [Количество новостей]". Я начну присылать вам новости по этому каналу так часто, как вы мне скажете. \n\nЧтобы посмотреть полный список команд, пришлите /help')

@bot.message_handler(commands=['help'])
def init(message):
    bot.reply_to(message, 'Полный список команд: \n"Добавить новый канал [Название канала] [Частота в часах] [Количество новостей]" - Я начну присылать вам выбранное количество самый популярных новостей выбранного канала каждое выбранное количество часов. Отсчет времени начнется с момента добавления нового канала. \n"Удалить канал [Название канала] - Я больше не буду присылать вам новости этого канала. \n"Изменить количество новостей канала [Название канала] [Количество новостей]" - Теперь я буду присылать вам другое количество новостей по этому каналу. \n"Изменить частоту получения новостей канала [Название канала] [Частота в часах]" - Я буду присылать вам новости этого канала с измененной частотой.')

def is_int(s):
    """
    @param {str} s A string to check if it is an int
    @returns {bool} True, if int(s) can be used, else False
    """
    try:
        int(s)
        return True
    except:
        return False


@bot.message_handler()
def msg_handler(message):
    text = message.text.lower()
    if(" ".join(text.split()[0:3]) = "добавить новый канал" and is_int(text.split()[-1])\
            and is_int(text.split()[-2]) and text.split()[0:-2] != "добавить новый канал"):
        #добавляем новый канал

    elif(" ".join(text.split()[0:2]) = "удалить канал" and text != "удалить канал"):
        #удаляем канал

    elif(" ".join(text.split()[0:4]) = "изменить количество новостей канала" \
	        and " ".join(text.split()[0:-1]) != "изменить количество новостей канала" and is_int(text.split()[-1])):
        #изменяем количество новостей

    elif(" ".join(text.split()[0:5]) = "изменить частоту получения новостей канала" \
	        and " ".join(text.split()[0:-1]) != "изменить частоту получения новостей канала" and is_int(text.split()[-1])):
        #изменяем частоту

    else:
        bot.reply_to(message, 'Неверный формат. Попробуйте /help')


if __name__ == "__main__":
    bot.polling(none_stop=False)
