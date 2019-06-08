import telethon.sync as telethon
from secrets import telegram_api_id as api_id, \
        telegram_api_hash as api_hash

def get_interesting_messages(chat_id, count, time_limit):
    messages = []
    with telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash) as client: 
        for message in client.iter_messages(chat_id, limit=count):
            messages.append('{} : {}'.format(message.date, message.views))         
    return messages

if __name__ == "__main__":
    data = get_interesting_messages('@Cbpub', 5, 3)
    for iter in data:
        print(iter)

