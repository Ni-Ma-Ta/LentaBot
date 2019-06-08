from threading import Timer, Event
from time import sleep

from channel_analyzer import get_interesting_messages


def get_channel_id(chat_link):
    """
    @param {str} chat_link Either a t.me link or @ChannelName
    @returns {str} The chat id in @ChannelName format
    """
    ans = chat_link.replace('http://', '') \
            .replace('https://', '') \
            .replace('t.me/', '@')
    return ans


class ChannelData:
    def __init__(self, channel_id, frequency, count):
        self.channel_id = channel_id
        self.frequency = frequency
        self.count = count

class ChannelsHandler:
    def __init__(self, bot, user_id):
        """
        @param {telebot.Bot} bot A Bot object
        @param {int} user_id The telegram user identeficator
        """
        self.bot = bot
        self.user_id = user_id
        self.channels = {} # channel_id to ChannelData object
        self.stop_events = {} # channel_id to Event that stops a thread

    def add_channel(self, channel_link, frequency, count):
        """
        @param {str} channel_link Either a t.me link or @ChannelName
        @param {float} frequency How often (in hours) do I have to check
            new messages in the channel
        @param {int} count How much interesting messages do I have to send
        @returns {NoneType} None
        """
        channel_id = get_channel_id(channel_link)
        self.channels[channel_id] = ChannelData(channel_id, frequency, count)
        local_stop = Event()
        self.stop_events[channel_id] = local_stop
        def f(stop_event, user_id, channel_data):
            while True:
                if stop_event.is_set():
                    return
                msgs = get_interesting_messages(
                        channel_data.channel_id,
                        channel_data.count,
                        channel_data.frequency)
                for msg in msgs:
                    bot.forward_message(
                            user_id,
                            channel_id,
                            msg)
                sleep(60 * 60 * time_limit)

        Timer(1, f, [local_stop, self.user_id, self.channels[channel_id]]).start()

    def del_channel(self, channel_link):
        """
        @param {str} channel_link Either a t.me link or @ChannelName
        @returns {NoneType} None
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
        @returns {NoneType} None
        """
        channel_id = get_channel_id(channel_link)
        if new_frequency is None:
            new_frequency = self.channels[channel_id].frequency
        if new_count is None:
            new_count = self.channels[channel_id].count
        self.del_channel(channel_link)
        self.add_channel(channel_link, frequency, count)
