import telebot

from secrets import telebot_token
from channels_handler import ChannelsHandler

bot = telebot.Telebot(telebot_token)
all_users = dict()

@bot.message_handler(commands=['start'])
def init(message):
    if message.chat.id in all_users:
        bot.reply_to(message, 'Вы уже зарегистрированы. Если вы хотите сбросить все настройки, то пришлите /stop')
    else:
        all_users[message.chat.id] = ChannelsHandler(bot, message.chat.id)
        bot.reply_to(message, 'Привет! Я симулирую ленту наиболее популярных новостей по выбранным вами каналам. \nДля того, чтобы начать, пришлите мне "Добавить новый канал [Название канала] [Частота в часах] [Количество новостей]". Я начну присылать вам новости по этому каналу так часто, как вы мне скажете. \n\nЧтобы посмотреть полный список команд, пришлите /help')

@bot.message_handler(commands=['help'])
def comands(message):
    bot.reply_to(message, 'Полный список команд: \n"Добавить новый канал [Название канала] [Частота в часах] [Количество новостей]" - Я начну присылать вам выбранное количество самых популярных новостей выбранного канала через каждое выбранное количество часов. Отсчет времени начнется с момента добавления нового канала. \n"Удалить канал [Название канала] - Я больше не буду присылать вам новости этого канала. \n"Изменить количество новостей канала [Название канала] [Количество новостей]" - Теперь я буду присылать вам другое количество новостей по этому каналу. \n"Изменить частоту получения новостей канала [Название канала] [Частота в часах]" - Я буду присылать вам новости этого канала с измененной частотой.')

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
    if(len(text.split()) == 6 and " ".join(text.split()[0:3]) == "добавить новый канал" and is_int(text.split()[4]) \
            and is_int(text.split()[5])):
        #добавляем новый канал
        all_users[message.chat.id].add_channel(text.split()[3], int(text.split()[4]), int(text.split()[5]))
    elif(len(text.split()) == 3 and " ".join(text.split()[0:2]) == "удалить канал"):
        #удаляем канал
        all_users[message.chat.id].del_channel(text.split()[2])
    elif(len(text.split()) == 6 and " ".join(text.split()[0:4]) == "изменить количество новостей канала" \
            and is_int(text.split()[5])):
        #изменяем количество новостей
        all_users[message.chat.id].edit_channel(text.split()[4], new_count=int(text.split()[-1]))
    elif(len(text.split()) == 7 and " ".join(text.split()[0:5]) == "изменить частоту получения новостей канала" \
	    and is_int(text.split()[-1])):
        #изменяем частоту
        all_users[message.chat.id].edit_channel(text.split()[5], new_frequency=int(text.split()[6]))
    else:
        bot.reply_to(message, 'Неверный формат. Попробуйте /help')


if __name__ == "__main__":
    bot.polling(none_stop=False)
