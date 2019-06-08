import telethon.sync as telethon
from secrets import telegram_api_id as api_id, \
        telegram_api_hash as api_hash

def get_interesting_messages(chat_id, count, time_limit):
    with telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash) as client:
        message = client.iter_messages(chat_id, limit=count)
    return message    

if __name__ == "__main__":
    print(get_interesting_messages('@Cbpub', 5, 3))

