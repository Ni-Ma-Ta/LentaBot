import telebot
import pickle
from secrets import telebot_token as token
from sys import stdin

bot = telebot.TeleBot(token)
print("Let's start. To interrupt the process, type ^C")
print("I'm going to send your message to all the users. Type the message. To finish message, type ^D (for linux) or ^Z (for windows). To cancel this, type ^C")
print("\nFormatting style is Markdown\n")
message = stdin.read()
print()
with open("userdata.pickle", "rb") as f:
    for user_id in pickle.load(f).keys():
        try:
            bot.send_message(user_id, message, parse_mode='Markdown')
        except:
            print("Couldn't send message to {}".format(user_id))
