import telebot
import time
import threading
import os

TOKEN = os.environ['TOKEN']

bot = telebot.TeleBot(token=TOKEN)

chats = {}
beginner = None
DEFAULT_TIMEOUT = 180
DEFAULT_ACTION = 'пожрать 🍕🍗🌯🍔'
MAX_TIMEOUT = 600

def get_username(user):
    name = ''
    if user.first_name is not None:
        name += user.first_name
    if user.last_name is not None:
        name += ' ' + user.last_name
    if len(name) == 0:
        name = user.username
    return name


def collecting(chat_id, timeout, action):
    t = 0
    print('start collecting in chat {}...'.format(chat_id))
    while t < timeout:
        time.sleep(1)
        t += 1
    users = [user[1] for user in chats[chat_id]]
    initiator = users[0]
    print('collected in chat {}: {} by {}'.format(chat_id, users, initiator))
    bot.send_message(
        chat_id,
        'Го <b>{}</b>!\nСостав:\n{}\nСобирал {}'.format(action, ' ,'.join(users), initiator),
        parse_mode='html'
    )
    chats[chat_id] = []


def parse_args(text):
    args = text.split(' ')
    timeout = DEFAULT_TIMEOUT
    action = DEFAULT_ACTION

    if len(args) == 2:
        try:
            timeout = int(args[1]) * 60
        except ValueError:
            action = args[1]

    if len(args) > 2:
        try:
            action = ' '.join(args[1:-1])
            timeout = int(args[-1]) * 60
        except ValueError:
            action = ' '.join(args[1:])

    if timeout < 0:
        timeout = DEFAULT_TIMEOUT
    elif timeout > MAX_TIMEOUT:
        timeout = MAX_TIMEOUT

    return action, timeout


@bot.message_handler(commands=['go'], content_types=['text'])
def go(message):
    action, timeout = parse_args(message.text)
    chat_id = message.chat.id
    user = message.from_user
    username = get_username(user)

    if chat_id not in chats:
        chats[chat_id] = []

    if len(chats[chat_id]) == 0:
        bot.send_message(
            chat_id,
            '{} предлагает <b>{}</b> через {:.0f} мин.\nЖми /go если тоже хочешь!'.format(username, action, timeout / 60),
            parse_mode='html'
        )
        chats[chat_id].append((user.id, get_username(user)))
        collecting_thread = threading.Thread(target=collecting, args=(chat_id, timeout, action))
        collecting_thread.daemon = True
        collecting_thread.start()

    if (user.id, username) not in chats[chat_id]:
        chats[chat_id].append((user.id, get_username(user)))
        print('added user {}:{} to chat {} queue'.format(get_username(user), user.id, chat_id))


print('Listening...')
bot.polling()
