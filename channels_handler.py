from threading import Timer, Event
from time import sleep


def get_channel_id(chat_link):
    """
    @param {str} chat_link Either a t.me link or @ChannelName
    @returns {str} The chat id in @ChannelName format
    """
    ans = chat_link.replace('http://', '') \
            .replace('https://', '') \
            .replace('t.me/', '@')
    return ans


def _notify(bot, user_id, channel_id, message_id):
    bot.send_message(user_id, "Сообщение из {}:\n\nt.me/{}/{}".format(
        channel_id,
        channel_id[1:],
        message_id
        ))


class ChannelData:
    def __init__(self, channel_id, frequency, count):
        self.channel_id = channel_id
        self.frequency = frequency
        self.count = count

class ChannelsHandler:
    def __init__(self, bot, user_id, msg_collector):
        """
        @param {telebot.Bot} bot A Bot object
        @param {int} user_id The telegram user identeficator
        """
        self.bot = bot
        self.user_id = user_id
        self.msg_collector = msg_collector
        self.channels = {} # channel_id to ChannelData object
        self.stop_events = {} # channel_id to Event that stops a thread

    def __del__(self):
        for event in self.stop_events.values():
            event.set()

    def add_channel(self, channel_link, frequency, count):
        """
        @param {str} channel_link Either a t.me link or @ChannelName
        @param {int} frequency How often (in hours) do I have to check
            new messages in the channel
        @param {int} count How much interesting messages do I have to send
        @returns {dict} A dictionary with the following keys:
            {bool} ok Whether the execution succeeded or not
            {str} user_message (optional) A message to be shown for user
        """
        if(channel_link in self.channels.keys()):
            self.del_channel(channel_link)

        channel_id = get_channel_id(channel_link)
        if not(len(channel_id) and (channel_id[0] == '@')):
            return {'ok': False, 'user_message': 'Некорректный channel_id'}

        channel_data = ChannelData(channel_id, frequency, count)
        self.channels[channel_id] = channel_data
        local_stop = Event()
        self.stop_events[channel_id] = local_stop
        def f(stop_event, user_id, channel_data, bot, messages_collector):
            while True:
                if stop_event.is_set():
                    return
                msgs = messages_collector.get_interesting_messages(
                        channel_data.channel_id,
                        channel_data.count,
                        channel_data.frequency
                        )
                for msg in msgs:
                    _notify(bot, user_id, channel_id, msg)
                sleep(60 * 60 * channel_data.frequency)

        try:
            Timer(1, f, [local_stop, self.user_id, self.channels[channel_id], self.bot, self.msg_collector]).start()
            return {'ok': True}
        except:
            return {'ok': False, 'user_message': 'Произошла ошибка при попытке инициализации потока. \
ПОЖАЛУЙСТА, обратитесь к @kolayne'}

    def del_channel(self, channel_link):
        """
        @param {str} channel_link Either a t.me link or @ChannelName
        @returns {dict} A dictionary with the following keys:
            {bool} ok Whether the execution succeeded or not
            {str} user_message (optional) A message to be shown for user
        """
        channel_id = get_channel_id(channel_link)
        try:
            self.stop_events[channel_id].set()
            del self.stop_events[channel_id]
            del self.channels[channel_id]
            return {'ok': True}
        except:
            return {'ok': False, 'user_message': 'Похоже, этот канал не собирается для вас. \
Если это не так, пожалуйста, обратитесь к разработчикам'}

    def edit_channel(
            self,
            channel_link,
            new_frequency=None,
            new_count=None
            ):
        """
        @param {str} channel_link Either a t.me link or @ChannelName
        @param (optional) {float} new_frequency How often (in hours) do I have to check
            new messages in the channel
        @param (optional) {int} new_count How much interesting messages do I have to send
        @returns {dict} A dictionary with the following keys:
            {bool} ok Whether the execution succeeded or not
            {str} user_message (optional) A message to be shown for user
        """
        channel_id = get_channel_id(channel_link)
        if channel_id not in self.channels.keys():
            return {'ok': False, 'user_message': 'Не могу отредактировать \
данные о канале: он не добавлен для вас. Используйте "добавить"'}

        if new_frequency is None:
            new_frequency = self.channels[channel_id].frequency
        if new_count is None:
            new_count = self.channels[channel_id].count
        self.del_channel(channel_link)
        self.add_channel(channel_link, new_frequency, new_count)
        return {'ok': True}

    def dumps(self):
        """
        This function returns a data that can be used in future to
        create a ChannelsHandler with same settigns as this one

        @returns {list[ChannelData]} A data for the self.load funcion
        """
        return self.channels

    def loads(self, data):
        """
        Takes data from the self.dump function and makes this object
        be set up in the same way as the dumped object was

        @param {list[ChannelData]} data An array of ChannelData to be saved now
        @returns {ChannelsHandler} Returns the created object (self)
        """
        for channel_data in data.values():
            self.add_channel(
                channel_data.channel_id,
                channel_data.frequency,
                channel_data.count
                )
            sleep(1)
        return self
