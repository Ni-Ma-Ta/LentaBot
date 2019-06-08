import telebot

from secrets import telebot_token
from channel_analyzer import MessagesCollector
from channels_handler import ChannelsHandler


bot = telebot.TeleBot(telebot_token)
all_users = dict()

def safe_user_access(func):
    def ans(message, *args, **kwargs):
        if(message.chat.id not in all_users.keys()):
            all_users[message.chat.id] = ChannelsHandler(
                    bot,
                    message.chat.id,
                    MessagesCollector()
                    )
        return func(message, *args, **kwargs)
    return ans

@bot.message_handler(commands=['start'])
@safe_user_access
def init(message):
    if message.chat.id in all_users:
        bot.reply_to(message, 'Вы уже зарегистрированы. Если вы хотите сбросить все настройки, то пришлите /stop')
    else:
        bot.reply_to(message, 'Привет! Я симулирую ленту наиболее популярных новостей по выбранным вами каналам. \nДля того, чтобы начать, пришлите мне "Добавить [Название канала] [M] [N]". Я начну присылать вам N новостей по этому каналу каждые M часов. \n\nЧтобы посмотреть полный список команд, пришлите /help')

@bot.message_handler(commands=['help'])
@safe_user_access
def comands(message):
    bot.reply_to(message, 'Полный список команд: \n\n"Добавить <Название канала> <M> <N>" - Я начну присылать вам N самых популярных новостей выбранного канала каждые M часов. Отсчет времени начнется с момента добавления канала. \n\n"Удалить <Название канала> - Я больше не буду присылать вам новости этого канала. \n\n"Изменить колво новостей <Название канала> <N>" - Теперь я буду присылать вам N новостей по этому каналу. \n\n"Изменить частоту <Название канала> <M>" - Я буду присылать вам новости этого канала каждые M часов.\n\n\n /stop - Прекратить со мной общение.')

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

@bot.message_handler(commands=['stop'])
@safe_user_access
def stop(message):
    bot.reply_to(message, 'Вы уверены, что хотите прекратить общаться? Если да, то пришлите мне /yesstop.')

@bot.message_handler(commands=['yesstop'])
@safe_user_access
def del_user(message):
    bot.reply_to(message, 'Пока-пока')
    del all_users[message.chat.id]

@bot.message_handler()
@safe_user_access
def msg_handler(message):
    text = message.text.lower()
    all_users[message.chat.id] = all_users.get(message.chat.id, {})
    if(len(text.split()) == 4 and text.split()[0] == "добавить" and is_int(text.split()[2]) \
            and is_int(text.split()[3])):
        #добавляем новый канал
        all_users[message.chat.id].add_channel(text.split()[1], int(text.split()[2]), int(text.split()[3]))
    elif(len(text.split()) == 2 and text.split()[0] == "удалить"):
        #удаляем канал
        all_users[message.chat.id].del_channel(text.split()[1])
    elif(len(text.split()) == 5 and " ".join(text.split()[0:3]) == "изменить количество новостей" \
            and is_int(text.split()[-1])):
        #изменяем количество новостей
        all_users[message.chat.id].edit_channel(text.split()[3], new_count=int(text.split()[-1]))
    elif(len(text.split()) == 4 and " ".join(text.split()[0:2]) == "изменить частоту" \
	    and is_int(text.split()[-1])):
        #изменяем частоту
        all_users[message.chat.id].edit_channel(text.split()[2], new_frequency=int(text.split()[3]))
    else:
        bot.reply_to(message, 'Неверный формат. Попробуйте /help')


if __name__ == "__main__":
    bot.polling(none_stop=False)
