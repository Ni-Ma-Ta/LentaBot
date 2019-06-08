import telethon.sync as telethon
from secrets import telegram_api_id as api_id, \
        telegram_api_hash as api_hash

class MessagesCollector:
    def __init__(self):
        self.client = telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash)
        self.client.connect()

    def __del__(self):
        self.client.disconnect()

    def get_interesting_messages(self, chat_id, count, time_limit):
        messages = []
        data = {}
        for message in self.client.iter_messages(chat_id, limit=count):
            messages.append(message.id)
            data[message.id] = message.date
        return messages

if __name__ == "__main__":
    a =  MessagesCollector()
    data = a.get_interesting_messages('@Cbpub', 5, 3)
    print(data)
