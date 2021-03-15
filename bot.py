from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

from export import excel,pdf

with sqlite3.connect('Murojaat.sqlite3') as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "murojaatlar" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"user_id"	INTEGER,
	"name"	TEXT,
	"murojaat"	TEXT)
    """)

yangi_murojaat_inline = InlineKeyboardMarkup()
yangi_murojaat_inline.add(InlineKeyboardButton("Yangi Murojaat yaratish",callback_data='new'))

TOKEN = "1663406803:AAHRMKNA65Tn9iqzvQ6hL8EiOgI3lDvj_OA"

bot = TeleBot(token=TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    step_message = bot.send_message(msg.from_user.id,"Assalomu alaykum! \n\nIsm, familyangizni kiriting")
    bot.register_next_step_handler(step_message,anketa_name)


def anketa_name(msg):
    name = msg.text
    with sqlite3.connect('Murojaat.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO murojaatlar (user_id,name) values(?,?)",(msg.from_user.id,name))
        except Exception as e:
            print(e)
            step_message = bot.reply_to(msg,"Xatolik yuz berdi, Iltimos ism, familyangizni qayta kiriting!")
            bot.register_next_step_handler(step_message, anketa_name)
            return
    step_message = bot.send_message(msg.from_user.id,"Murojaatingizni matn ko'rinishida yozib qoldiring\n\nEslatma: Murojaat faqat bitta habardan iborat bo'ladi!")
    bot.register_next_step_handler(step_message, murojaat_text)

def murojaat_text(msg):
    content = msg.text
    with sqlite3.connect('Murojaat.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("Update murojaatlar set murojaat = ? where id=(SELECT max(id) FROM murojaatlar where user_id=?)", (content,msg.from_user.id))
        except Exception as e:
            print(e)
            step_message = bot.reply_to(msg, "Xatolik yuz berdi, Iltimos Murojaatnoma habarini qayta yuboring!")
            bot.register_next_step_handler(step_message, murojaat_text)
    bot.send_message(msg.from_user.id,'Murojaatingiz qabul qilindi',reply_markup=yangi_murojaat_inline)

@bot.callback_query_handler(func=lambda call:call.data=='new')
def set_lang1(call):
    bot.delete_message(call.from_user.id, call.message.message_id)
    step_message = bot.send_message(call.from_user.id, "Ism, familyangizni kiriting!")
    bot.register_next_step_handler(step_message, anketa_name)


@bot.message_handler(commands=['excel'])
def export_excel(msg):
    bot.send_document(msg.from_user.id,excel())

@bot.message_handler(commands=['pdf'])
def export_excel(msg):
    bot.send_document(msg.from_user.id,pdf())

@bot.message_handler(func=lambda x:True)
def yangi_murojaat_uchun(msg):
    bot.send_message(msg.from_user.id, "Yangi murojaatnoma yozish uchun pastdagi tugmani bo'sing", reply_markup=yangi_murojaat_inline)

if __name__ == '__main__':
    bot.polling()