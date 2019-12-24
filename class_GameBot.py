from config import TG_API_URL
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from achievemets import ach
import vectors as v
from last_first import last, first
import random
from create_list import create_list


class GameBot():
    player_turn = None
    base_url = TG_API_URL

    CALLBACK_BUTTON_BOT = "callback_button_bot"
    CALLBACK_BUTTON_PLAYER = "callback_button_player"

    TITLES = {
        CALLBACK_BUTTON_BOT: "Ходит бот",
        CALLBACK_BUTTON_PLAYER: "Ходит игрок",
    }

    def __init__(self, token):
        self.message_before_game_handler = MessageHandler(Filters.all, self.do_message_before_game)
        self.read_handler = MessageHandler(Filters.text, self.read_city_from_user)
        self.start_handler = CommandHandler('start', self.do_start)
        self.keyboard_handler = CallbackQueryHandler(callback=self.keyboard_callback_handler, pass_chat_data=True)
        self.bot = Bot(token=token, base_url=self.base_url)
        self.updater = Updater(bot=self.bot)
        self.updater.dispatcher.add_handler(self.start_handler, group=0)
        self.updater.dispatcher.add_handler(self.message_before_game_handler, group=1)

    """Начало работы бота"""
    def start(self):
        print("Start_bot")
        self.updater.start_polling()  # По сути Event poll
        self.updater.idle()

    """Отправление сообщений до начала игры"""
    def do_message_before_game(self, bot: Bot, update: Update):
        text = "Если хочешь начать играть, жми /start"
        bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
        )

    def get_inline_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton(self.TITLES[self.CALLBACK_BUTTON_BOT], callback_data=self.CALLBACK_BUTTON_BOT),
                InlineKeyboardButton(self.TITLES[self.CALLBACK_BUTTON_PLAYER], callback_data=self.CALLBACK_BUTTON_PLAYER),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def keyboard_callback_handler(self, bot: Bot, update: Update, chat_data=None, **kwargs):
        query = update.callback_query
        data = query.data
        self.updater.dispatcher.add_handler(self.read_handler, group=1)
        self.updater.dispatcher.remove_handler(self.keyboard_handler, group=0)
        print(self.updater.dispatcher.handlers)
        if data == self.CALLBACK_BUTTON_BOT:
            self.turn_bot(bot=bot, update=update)
        elif data == self.CALLBACK_BUTTON_PLAYER:
            text = "Твой ход, раунд 0"
            bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=text,
            )

    """Обработчик команды старт"""
    def do_start(self, bot: Bot, update: Update):
        print("Игра началась")
        self.updater.dispatcher.add_handler(self.keyboard_handler, group=0)
        self.updater.dispatcher.remove_handler(self.start_handler, 0)
        self.updater.dispatcher.remove_handler(self.message_before_game_handler, 1)
        text = f"Игра в города. Мой рекорд {ach}! Кто делает первый ход?"
        bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
            reply_markup=self.get_inline_keyboard()
        )
        print(f"Обработка старта {self.updater.dispatcher.handlers}")

    def read_city_from_user(self, bot: Bot, update: Update):
        text = update.message.text
        self.prepare_word(player_word=text, bot=bot, update=update)

    def end_game(self, bot: Bot, update: Update, text):
        bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
        )
        if self.count > ach:
            text = f"Я поставил новый рекорд: {self.count}!"
            bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=text,
            )
            open("achievement.txt", 'w').write(str(self.count - 1))  # Перезапись рекорда при необходимости
        self.updater.dispatcher.remove_handler(self.read_handler, group=1)
        self.updater.dispatcher.add_handler(self.start_handler, group=0)
        self.updater.dispatcher.add_handler(self.message_before_game_handler, group=1)
        self.T = ''
        self.attempts = 7
        create_list()
        self.count = 0
        print("Игра завершилась")

    attempts = 7  # Попытки ввода слова, которое уже было и попытки ввода слова не на ту букву

    T = ''  # Переменная содержит букву, на которое должно начинаться следующее слово

    count = 0  # Раунды

    """Обработка ввёденного игроком слова"""
    def prepare_word(self, bot: Bot, update: Update, player_word):
        if self.attempts == 0:
            self.end_game(bot=bot, update=update, text=f"Ты проиграл. Раундов сыграно {self.count}")

        if self.T == '':  # Если переменная 'T' последней бувы пустая, то есть игрок делает первый ход
            for i in v.all_alph:
                if player_word in i:  # Если слово есть в списке городов из файла
                    v.deleted.append(player_word)
                    i.remove(player_word)
                    self.T = last(player_word)
                    self.turn_bot(bot=bot, update=update)
                    break
                else:
                    continue
            else:  # Если слова нет в списке городов из файла
                if self.attempts != 0:
                    self.attempts -= 1
                    text = f"Такого города нет, осталось попыток {self.attempts}"
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=text
                    )
                else:
                    self.end_game(bot=bot, update=update, text=f"Ты проиграл. Раундов сыграно {self.count}")

        else:  # Если переменная 'T' последней буквы не пустая
            if self.T.title() == first(player_word):   # Если 'T' совпадает с первой буквой названного слова
                if player_word not in v.deleted:  # Если слова не было в списке названных
                    for i in v.all_alph:
                        if player_word in i:  # Если слово есть в списке городов из файла
                            v.deleted.append(player_word)
                            i.remove(player_word)
                            self.T = last(player_word)
                            self.turn_bot(bot=bot, update=update)
                            break
                        else:
                            continue
                    else:  # Если города нет в списке
                        self.attempts -= 1
                        if self.attempts != 0:  # Если попытки ещё есть
                            text = f"Такого города нет, осталось попыток {self.attempts}"
                            bot.send_message(
                                chat_id=update.effective_message.chat_id,
                                text=text,
                            )
                        else:  # Если попыток нет
                            self.end_game(bot=bot, update=update, text=f"Ты проиграл. Раундов сыграно {self.count}")
                else:  # Если город есть в списке названных городов
                    if self.attempts != 0:
                        self.attempts -= 1
                        text = f"Этот город уже называли, попыток осталось {self.attempts}"
                        bot.send_message(
                            chat_id=update.effective_message.chat_id,
                            text=text
                        )
                    else:
                        self.end_game(bot=bot, update=update, text=f"Ты проиграл. Раундов сыграно {self.count}")
            else:  # Если переменная 'T' не совпадает с первой буквой названного слова
                self.attempts -= 1
                if self.attempts != 0:
                    text = f"Тебе нужно назвать город на букву {self.T.title()}, осталось попыток {self.attempts}"
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=text,
                    )
                else:
                    self.end_game(bot=bot, update=update, text=f"Ты проиграл. Раундов сыграно {self.count}")

    """Ход бота"""
    def turn_bot(self, bot: Bot, update: Update):
        self.count += 1
        if self.attempts == 0:
            self.end_game(bot=bot, update=update, text=f"Ты проиграл. Раундов сыграно {self.count}")
        else:
            try:
                if self.T == '':
                    i = random.choice(random.choice(v.all_alph))
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.A.remove(i)
                elif self.T == 'а':  # Если переменная, содержащая последнюю букву равно "а",
                    i = random.choice(v.A)  # то вытаскивай случайное слово из вектора "А"
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)  # Присваивай переменной последней буквы последнюю букву вытащенного слова
                    v.deleted.append(i)  # Добавляй его в вектор названных слов
                    v.A.remove(i)  # Удаляй его из вектора "А"
                elif self.T == 'б':
                    i = random.choice(v.B)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.B.remove(i)
                elif self.T == 'в':
                    i = random.choice(v.V)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.V.remove(i)
                elif self.T == 'г':
                    i = random.choice(v.G)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.G.remove(i)
                elif self.T == 'д':
                    i = random.choice(v.D)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.D.remove(i)
                elif self.T == 'е':
                    i = random.choice(v.E)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.E.remove(i)
                elif self.T == 'ж':
                    i = random.choice(v.J)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.J.remove(i)
                elif self.T == 'з':
                    i = random.choice(v.Z)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.Z.remove(i)
                elif self.T == 'и':
                    i = random.choice(v.I)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.I.remove(i)
                elif self.T == 'й':
                    i = random.choice(v.I1)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.I1.remove(i)
                elif self.T == 'к':
                    i = random.choice(v.K)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.K.remove(i)
                elif self.T == 'л':
                    i = random.choice(v.L)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.L.remove(i)
                elif self.T == 'м':
                    i = random.choice(v.M)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.M.remove(i)
                elif self.T == 'н':
                    i = random.choice(v.N)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.N.remove(i)
                elif self.T == 'о':
                    i = random.choice(v.O)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.O.remove(i)
                elif self.T == 'п':
                    i = random.choice(v.P)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.P.remove(i)
                elif self.T == 'р':
                    i = random.choice(v.R)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.R.remove(i)
                elif self.T == 'с':
                    i = random.choice(v.S)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.S.remove(i)
                elif self.T == 'т':
                    i = random.choice(v.T)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.T.remove(i)
                elif self.T == 'у':
                    i = random.choice(v.Y)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.Y.remove(i)
                elif self.T == 'ф':
                    i = random.choice(v.F)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.F.remove(i)
                elif self.T == 'х':
                    i = random.choice(v.H)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.H.remove(i)
                elif self.T == 'ц':
                    i = random.choice(v.C)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.C.remove(i)
                elif self.T == 'ч':
                    i = random.choice(v.CH)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.CH.remove(i)
                elif self.T == 'ш':
                    i = random.choice(v.SH)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.SH.remove(i)
                elif self.T == 'щ':
                    i = random.choice(v.HI)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.HI.remove(i)
                elif self.T == 'э':
                    i = random.choice(v.EI)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.EI.remove(i)
                elif self.T == 'ю':
                    i = random.choice(v.U)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.U.remove(i)
                elif self.T == 'я':
                    i = random.choice(v.YA)
                    bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=i,
                    )
                    self.T = last(i)
                    v.deleted.append(i)
                    v.YA.remove(i)
            except IndexError:
                self.end_game(bot=bot, update=update, text=f" Вы выиграли! Раундов сыграно:  {self.count}")