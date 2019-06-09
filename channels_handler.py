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


def _send_message(bot, user_id, message):
    '''if message.media_type == 'video':
        pass
    elif message.media_type == 'photo':
        pass
    el'''
    if message.media_type is None:
        prologue = 'Сообщение из {}:\n\n\n'.format(bot.channel_id)
        bot.send_message(user_id, prologue + message.text)
    else:
        bot.send_message(
                user_id,
                'Не смог переслать вам сообщение. Вы можете посмотреть его в telegram: http://t.me/{}/{}'.format(
                    message.chat_id[1:],
                    message.id
                    )
                )


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
        @param {float} frequency How often (in hours) do I have to check
            new messages in the channel
        @param {int} count How much interesting messages do I have to send
        """
        channel_id = get_channel_id(channel_link)
        self.channels[channel_id] = ChannelData(channel_id, frequency, count)
        local_stop = Event()
        self.stop_events[channel_id] = local_stop
        def f(stop_event, user_id, channel_data, messages_collector):
            while True:
                if stop_event.is_set():
                    return
                msgs = messages_collector.get_interesting_messages(
                        channel_data.channel_id,
                        channel_data.count,
                        channel_data.frequency)
                for msg in msgs:
                    _send_message(bot, user_id, msg)
                sleep(60 * 60 * time_limit)

        Timer(1, f, [local_stop, self.user_id, self.channels[channel_id], self.msg_collector]).start()

    def del_channel(self, channel_link):
        """
        @param {str} channel_link Either a t.me link or @ChannelName
        """
        channel_id = get_channel_id(channel_link)
        self.stop_events[channel_id].set()
        del self.stop_events[channel_id]
        del self.channels[channel_id]

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
        """
        channel_id = get_channel_id(channel_link)
        if new_frequency is None:
            new_frequency = self.channels[channel_id].frequency
        if new_count is None:
            new_count = self.channels[channel_id].count
        self.del_channel(channel_link)
        self.add_channel(channel_link, frequency, count)

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
        for channel_data in data:
            self.add_channel(
                channel_data.channel_id,
                channel_data.frequency,
                channel_data.count
                )
        return self
