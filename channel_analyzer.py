import telethon.sync as telethon
import operator
import datetime
import subprocess
import pickle

from secrets import telegram_api_id as api_id, \
        telegram_api_hash as api_hash

class MessageData:
    def  __init__(self, message, file_path):
        self.id = message.id
        self.channel_id = message.chat_id
        self.text = message.message
        self.media_type = message.media
        self.file_path = file_path

class MessagesCollector:
    def __init__(self):
        self.client = telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash)
        self.client.connect()

    def __del__(self):
        self.client.disconnect()

    def get_interesting_messages(self, chat_id, count, time_limit):
        '''
        @param {str} chat_id A string, which contain chat share link
        @param {int} count Amount of the most popular messages, which ids will be return
        @param {int} time_limit Amount of hours, so messages, which have been send after current time - this amount of hours, will be included into comparison  
        @returns {list} List, which contains ids, which belong to most popular messsages in this chat 
        '''
        all_messages = []
        data = {}
        today = datetime.datetime.utcnow()
        if today.hour - time_limit < 0:
            limit_date = datetime.datetime(hour=today.hour-time_limit + 24, minute=today.minute, second=today.second,  \
                day=today.day - 1, month=today.month, year=today.year, tzinfo=datetime.timezone.utc)
        else:
            limit_date = datetime.datetime(hour=today.hour-time_limit, minute=today.minute, second=today.second,  \
                day=today.day, month=today.month, year=today.year, tzinfo=datetime.timezone.utc)
        for message in self.client.iter_messages(chat_id, offset_date=limit_date, reverse=True):
            data[message.id] = message.views
            all_messages.append(message)
        sorted_data = sorted(data.items(), key=operator.itemgetter(1))
        sorted_data.reverse()
        sorted_data = sorted_data[:count]
        messages = [i[0] for i in sorted_data]
        sorted_messages = []
        for iter in all_messages:
            if iter.id in messages:
                sorted_messages.append(iter)
        arr = []
        for x in sorted_messages:
            filename = 'media/{}/{}'.format(chat_id, str(pickle.dumps(x)))
            print(filename)
            # self.client.download_media(x, filename)
            if(subprocess.call(['python3', 'download_media.py', str(chat_id), str(x.id)]) == 0):
                arr.append(MessageData(x, file_path=filename))
            else:
                print("download_media.py had a non-zero exit code")
        return arr

if __name__ == "__main__":
    a =  MessagesCollector()
    data = a.get_interesting_messages('@Cbpub', 5, 24)
    print(data)
