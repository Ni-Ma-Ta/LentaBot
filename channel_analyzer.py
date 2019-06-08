import telethon.sync as telethon
from secrets import telegram_api_id as api_id, \
        telegram_api_hash as api_hash

def get_channels_messages(chat_id, count, time_limit):
    with telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash) as client:
        for message in client.iter_messages(chat_id, limit=count):
            print(message.date, ":", message.views)

if __name__ == "__main__":
    get_channels_messages('@Cbpub', 5, 3)
