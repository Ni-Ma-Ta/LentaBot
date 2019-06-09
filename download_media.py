try:
	import pickle
	import telethon.sync as telethon
	from sys import argv
	from secrets import telegram_api_id as api_id, \
        	telegram_api_hash as api_hash
	client = telethon.TelegramClient('NiMaTaLentaBot', api_id, api_hash)
except:
	exit(1)
try:
	client.connect()
	media = pickle.loads(eval(argv[3]))
	filename = 'media/{}/{}'.format(argv[1], argv[2])
	client.download_media(media, filename)
except:
	exit(1)
finally:
	client.disconnect()
