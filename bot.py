import telebot
import pickle
from os.path import isfile

from secrets import telebot_token
from channel_analyzer import MessagesCollector
from channels_handler import ChannelsHandler


bot = telebot.TeleBot(telebot_token)
msg_collector = MessagesCollector()
all_users = dict()

def unfalling(func):
    def ans(message, *args, **kwargs):
        try:
            result = func(message, *args, **kwargs)
            return result
        except KeyboardInterrupt:
            exit(0)
        except:
            try:
                bot.reply_to(message, "Извините, произошла ошибка. Обратитесь, пожалуйста, к организаторам. Бот продолжит работать в своем обычном режиме.")
            except:
                pass
    return ans


def safe_user_access(func):
    def ans(message, *args, **kwargs):
        if(message.chat.id not in all_users.keys()):
            all_users[message.chat.id] = ChannelsHandler(
                    bot,
                    message.chat.id,
                    msg_collector
                    )
        return func(message, *args, **kwargs)
    return ans

def autodump(func):
    def ans(*args, **kwargs):
        result = func(*args, **kwargs)
        with open("userdata.pickle", "wb") as f:
            pickle.dump(
                    {k: v.dumps() for k, v in all_users.items()},
                    f
                    )
        return result
    return ans

@bot.message_handler(commands=['start'])
@unfalling
@autodump
def init(message):
    if message.chat.id in all_users:
        bot.reply_to(message, 'Вы уже зарегистрированы. Если вы хотите сбросить все настройки, то пришлите /stop')
    else:
        bot.reply_to(message, 'Привет! Я симулирую ленту наиболее популярных новостей по выбранным вами каналам. \nДля того, чтобы начать, пришлите мне "Добавить <@Упоминание_канала> [M] [N]". Я начну присылать вам N новостей по этому каналу каждые M часов. \n\nЧтобы посмотреть полный список команд, пришлите /help')

@bot.message_handler(commands=['help'])
@unfalling
@safe_user_access
def comands(message):
    bot.reply_to(message, 'Полный список команд: \n\n"Добавить <@Упоминание_канала> <M> <N>" - Я начну присылать вам N самых популярных новостей выбранного канала каждые M часов. Отсчет времени начнется с момента добавления канала. \n\n"Удалить <@Упоминание_канала> - Я больше не буду присылать вам новости этого канала. \n\n"Изменить количество <@Упоминание_канала> <N>" - Теперь я буду присылать вам N новостей по этому каналу. \n\n"Изменить частоту <@Упоминание_канала> <M>" - Я буду присылать вам новости этого канала каждые M часов.\n\n\n /stop - Прекратить со мной общение.')

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
@unfalling
def stop(message):
    if message.chat.id in all_users:
        bot.reply_to(message, 'Вы уверены, что хотите прекратить общаться? Все ваши настройки сбросятся! Если вы согласны, то пришлите мне /yesstop.')
        return
    bot.reply_to(message, "Вы просите меня забыть вас, но мы даже не были знакомы... Чтобы познакомиться, пришлите /start")

@bot.message_handler(commands=['yesstop'])
@unfalling
@safe_user_access
@autodump
def del_user(message):
    bot.reply_to(message, 'Можете считать, что меня никогда не существовало.. Пока-пока')
    del all_users[message.chat.id]

@bot.message_handler()
@unfalling
@safe_user_access
@autodump
def msg_handler(message):
    text = message.text.lower()
    all_users[message.chat.id] = all_users.get(message.chat.id, {})
    if(len(text.split()) == 4 and text.split()[0] == "добавить" and is_int(text.split()[2]) \
            and is_int(text.split()[3])):
        #добавляем новый канал
        all_users[message.chat.id].add_channel(text.split()[1], int(text.split()[2]), int(text.split()[3]))
        bot.reply_to(message, "Канал был успешно добавлен. Ловите новости!")
    elif(len(text.split()) == 2 and text.split()[0] == "удалить"):
        #удаляем канал
        all_users[message.chat.id].del_channel(text.split()[1])
        bot.reply_to(message, "Я навсегда забыл про этот канал.")
    elif(len(text.split()) == 4 and " ".join(text.split()[0:2]) == "изменить количество" \
            and is_int(text.split()[-1])):
        #изменяем количество новостей
        all_users[message.chat.id].edit_channel(text.split()[2], new_count=int(text.split()[-1]))
        bot.reply_to(message, "Теперь я буду присылать вам другое количество новостей по этому каналу.")
    elif(len(text.split()) == 4 and " ".join(text.split()[0:2]) == "изменить частоту" \
	    and is_int(text.split()[-1])):
        #изменяем частоту
        all_users[message.chat.id].edit_channel(text.split()[2], new_frequency=int(text.split()[3]))
        bot.reply_to(message, "Частота успешно обновлена!")
    else:
        bot.reply_to(message, 'Неверный формат. Попробуйте /help')


if __name__ == "__main__":
    if isfile("userdata.pickle"):
        with open("userdata.pickle", "rb") as f:
            all_users = {k: ChannelsHandler(bot, k, msg_collector).loads(v) for k, v in pickle.load(f).items()}
        for user in all_users:
            bot.send_message(user, "Извините, бот был перезагружен. Но не волнуйтесь! Мы сохранили ваши настройки. Время отправки новостей будет отсчитываться с текущего момента. Ловите новости!")
    bot.polling(none_stop=False)
