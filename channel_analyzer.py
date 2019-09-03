__author__ = "Maksim Bessonov"

import datetime
from operator import itemgetter
from threading import Lock

import telethon.sync as telethon
import pickle

from secrets import telegram_api_id as api_id, \
        telegram_api_hash as api_hash

class MessageData:
    def  __init__(self, message, chat_id, file_path):
        self.id = message.id
        self.channel_id = chat_id
        self.text = message.message
        self.media_type = message.media
        self.file_path = file_path

class MessagesCollector:
    def __init__(self):
        self.client = telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash)
        self.client.connect()
        self._mutex = Lock()

    def __del__(self):
        self.client.disconnect()
        self._mutex.acquire()

    def get_interesting_messages(self, chat_id, count, time_limit):
        """
        @param {str} chat_id The channel id
        @param {int} count Amount of the most popular messages, which ids will be returned
        @param {int} time_limit Amount of hours, so messages, which have been sent after (current_time - count) hours will be included into comparison  
        @returns {list} A list, which contains ids, which belong to most popular messsages in this chat 
        """
        self._mutex.acquire()
        try:
            all_messages = []
            data = {}
            data_delta = 0
            hours_delta = 0
            data_delta += time_limit // 24
            hours_delta += time_limit % 24
            today = datetime.datetime.utcnow()
            if today.hour - hours_delta < 0:
                limit_date = datetime.datetime(hour=today.hour - hours_delta + 24, minute=today.minute, second=today.second,  \
                    day=today.day - data_delta - 1, month=today.month, year=today.year, tzinfo=datetime.timezone.utc)
            else:
                limit_date = datetime.datetime(hour=today.hour - hours_delta, minute=today.minute, second=today.second,  \
                    day=today.day - data_delta, month=today.month, year=today.year, tzinfo=datetime.timezone.utc)
            for message in self.client.iter_messages(chat_id, offset_date=limit_date, reverse=True):
                try:
                    data[message.id] = int(message.views)
                except:
                    data[message.id] = 0
                all_messages.append(message)
            sorted_data = sorted(data.items(), key=itemgetter(1))
            sorted_data.reverse()
            sorted_data = sorted_data[:count]
            messages = [i[0] for i in sorted_data]
            return messages
        except:
            return None
        finally:
            self._mutex.release()

if __name__ == '__main__':
    a = MessagesCollector()
    data = a.get_interesting_messages("@Cbpub", 5, 72)
    print(data)
