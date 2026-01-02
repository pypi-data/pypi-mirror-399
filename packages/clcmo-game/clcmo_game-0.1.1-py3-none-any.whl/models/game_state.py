from utils.constants import MECHANIC

class GameState:
    def __init__(self):
        self.level = 1
        self.max_levels = MECHANIC["max_levels"]
        self.score = 0
        self.lives = MECHANIC["initial_lives"]
        self.state = "menu"  # Estados: menu, playing, paused, game_over, victory
        self.sound_on = True
        self.language = "en"  # Idioma padrão
        self.power_ups = []  # Lista de power-ups ativos