import telebot
import time
import threading

bot = telebot.TeleBot(token='')

chats = {}
beginner = None


def get_username(user):
    name = ''
    if user.first_name is not None:
        name += user.first_name
    if user.last_name is not None:
        name += ' ' + user.last_name
    if len(name) == 0:
        name = user.username
    return name


def collecting(chat_id, timeout=180):
    t = 0
    while t < timeout:
        time.sleep(1)
        t += 1
    users = [user[1] for user in chats[chat_id]]
    initiator = users[0]
    print('collected in chat {}: {} by {}'.format(chat_id, users, initiator))
    bot.send_message(chat_id, 'Го жрать! Состав: {} 🍕🍗🌯🍔\nСобирал {}'.format(' ,'.join(users), initiator))
    chats[chat_id] = []


@bot.message_handler(commands=['go'])
def go(message):
    chat_id = message.chat.id
    user = message.from_user
    username = get_username(user)

    if chat_id in chats:
        users = chats[chat_id]
    else:
        users = []
        chats[chat_id] = []

    if len(users) == 0:
        collecting_thread = threading.Thread(target=collecting, args=(chat_id,))
        collecting_thread.daemon = True
        collecting_thread.start()
        bot.send_message(chat_id, '{} предлагает пожрать 🍕🍗🌯🍔\nЖми /go если тоже хочешь!'.format(username))
        print('start collecting in chat {}...'.format(chat_id))

    if (user.id, username) not in users:
        chats[chat_id].append((user.id, get_username(user)))
        print('added user {}:{} to chat {} queue'.format(get_username(user), user.id, chat_id))


print('Listening...')
bot.polling()
