import telebot
import pickle
from os.path import isfile

from secrets import telebot_token
from channel_analyzer import MessagesCollector
from channels_handler import ChannelsHandler


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
                bot.reply_to(message, "Извините, произошла ошибка. Пожалуйста, обратитесь к разработчикам. Бот продолжит работать в своем обычном режиме")
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
        bot.reply_to(message, 'Вы уже зарегистрированы. Если вы хотите сбросить все настройки, то попрощайтесь со мной (команда /stop), а затем познакомьтесь снова (/start)')
    else:
        bot.reply_to(message, 'Привет! Я симулирую ленту наиболее популярных новостей по выбранным вами каналам. \nДля того, чтобы начать, пришлите мне "Добавить <@Упоминание_канала> [M] [N]". Я начну присылать вам N новостей по этому каналу каждые M часов. \n\nЧтобы посмотреть полный список команд, пришлите /help')

@bot.message_handler(commands=['help'])
@unfalling
@safe_user_access
def comands(message):
    bot.reply_to(message, 'Полный список команд:\n\n\
"Добавить <@Упоминание_канала> <M> <N>" - Я начну присылать вам N самых популярных новостей выбранного канала каждые M часов. Отсчет времени начнется с момента добавления канала\n\n\
"Удалить <@Упоминание_канала> - Я больше не буду присылать вам новости этого канала\n\n\
"Изменить количество <@Упоминание_канала> <N>" - Теперь я буду присылать вам N новостей по этому каналу\n\n\
"Изменить частоту <@Упоминание_канала> <M>" - Я буду присылать вам новости этого канала каждые M часов\n\n\n\
/list - посмотреть мои каналы\n\
/stop - Прекратить общение со мной')

@bot.message_handler(commands=['list'])
@unfalling
def list_channels(message):
    if message.chat.id not in all_users.keys():
        bot.reply_to(message, "Кажется, мы еще не знакомы...")
    elif all_users[message.chat.id] == {}:
        bot.reply_to(message, "У вас нет отслеживаемых каналов")
    else:
        ans = ''
        for channel in all_users[message.chat.id].values():
            ans += 'Для канала {} присылаю {} сообщений каждые {} часов\n'.format(
                channel.channel_id,
                channel.count,
                channel.frequency
                )
        bot.reply_to(message, ans)

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

def answer_success(bot, chat_id, success, ok_message, bad_message, *args, **kwargs):
    """
    @param {telebot.TeleBot} bot A telegram bot to send message from
    @param {int} chat_id The chat id to send message to
    @param {dict} success Information about command execution result
    @param {str} ok_message What to reply if the execution succeeded
        and there're nothing to reply from command
    @param {str} bad_message What to reply if the execution didn't succeed
        and there're nothing to reply from command
    @params {ANY} *args These arguments will be given to send_message
    @params {ANY} **kwargs These arguments will be given to send_message
    """
    if 'user_message' in success:
        bot.send_message(chat_id, success['user_message'], *args, **kwargs)
    elif success['ok']:
        bot.send_message(chat_id, ok_message, *args, **kwargs)
    else:
        bot.send_message(chat_id, bad_message, *args, **kwargs)

@bot.message_handler()
@unfalling
@safe_user_access
@autodump
def msg_handler(message):
    text = message.text.lower()
    if(len(text.split()) == 4 and text.split()[0] == "добавить" and is_int(text.split()[2]) \
            and is_int(text.split()[3])):
        #добавляем новый канал
        answer_success(
            bot,
            message.chat.id,
            all_users[message.chat.id].add_channel(text.split()[1], int(text.split()[2]), int(text.split()[3])),
            "Канал был успешно добавлен",
            "Не удалось добавить канал. Возможно, следует обратиться к разработчикам",
            reply_to_message_id=message.message_id
            )
    elif(len(text.split()) == 2 and text.split()[0] == "удалить"):
        #удаляем канал
        answer_success(
            bot,
            message.chat.id,
            all_users[message.chat.id].del_channel(text.split()[1]),
            "Я навсегда забыл про этот канал",
            "Не удалось забыть канал. Возможно, следует обратиться к разработчикам",
            reply_to_message_id=message.message_id
            )
    elif(len(text.split()) == 4 and " ".join(text.split()[0:2]) == "изменить количество" \
            and is_int(text.split()[-1])):
        #изменяем количество новостей
        answer_success(
            bot,
            message.chat.id,
            all_users[message.chat.id].edit_channel(text.split()[2], new_count=int(text.split()[-1])),
            "Теперь я буду присылать вам другое количество новостей по этому каналу",
            "Не удалось выполнить операцию. Возможно, следует обратиться к разработчикам",
            reply_to_message_id=message.message_id
            )
    elif(len(text.split()) == 4 and " ".join(text.split()[0:2]) == "изменить частоту" \
	    and is_int(text.split()[-1])):
        #изменяем частоту
        answer_success(
            bot,
            message.chat.id,
            all_users[message.chat.id].edit_channel(text.split()[2], new_frequency=int(text.split()[3])),
            "Частота успешно обновлена!",
            "Не удалось выполнить операцию. Возможно, следует обратиться к разработчикам",
            reply_to_message_id=message.message_id
            )
    else:
        bot.reply_to(message, 'Неверный формат. Попробуйте /help')


if __name__ == "__main__":
    if isfile("userdata.pickle"):
        with open("userdata.pickle", "rb") as f:
            all_users = {k: ChannelsHandler(bot, k, msg_collector).loads(v) for k, v in pickle.load(f).items()}
        for user in all_users.keys():
            bot.send_message(user, "Извините, бот был перезагружен. Но не волнуйтесь! Мы сохранили ваши настройки. Время отправки новостей будет отсчитываться с текущего момента")
    bot.polling(none_stop=False)
