from config import TG_token
from class_GameBot import GameBot
from create_list import create_list
import vectors as v

if __name__ == '__main__':
    create_list()
    game_bot = GameBot(TG_token)
    game_bot.start()
