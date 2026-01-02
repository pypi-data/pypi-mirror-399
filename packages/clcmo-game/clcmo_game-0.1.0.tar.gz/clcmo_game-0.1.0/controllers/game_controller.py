from models.game_state import GameState
from models.hero import Hero
from models.level import Level
from views.menu_view import MenuView
from views.game_view import GameView
from views.pause_view import PauseView
from views.hud_view import HUDView
from controllers.input_handler import InputHandler
from utils.constants import MECHANIC

class GameController:
    def __init__(self):
        self.game_state = GameState()
        self.hero = Hero(100, 100)
        self.level = Level(self.game_state.level)
        self.input_handler = InputHandler(self)
        self.views = {
            "menu": MenuView(self.game_state.language),
            "playing": GameView(self.game_state.language),
            "paused": PauseView(self.game_state.language),
            "hud": HUDView(self.game_state.language)
        }

    def update(self, dt):
        if self.game_state.state == "playing":
            self.hero.update_animation()
            for enemy in self.level.enemies:
                enemy.patrol()
                enemy.update_animation()
            self.check_collisions()
            self.check_victory()

    def draw(self, screen):
        if self.game_state.state == "menu":
            self.views["menu"].draw(screen)
        elif self.game_state.state == "playing":
            self.views["playing"].draw(screen, self.hero, self.level.enemies, self.game_state.power_ups)
            self.views["hud"].draw(screen, self.game_state.score, self.game_state.lives)
        elif self.game_state.state == "paused":
            self.views["paused"].draw(screen)

    def on_mouse_down(self, pos):
        self.input_handler.handle_mouse(pos)

    def on_key_down(self, key):
        self.input_handler.handle_key(key)

    def check_collisions(self):
        for enemy in self.level.enemies:
            if enemy.alive and self.hero.rect.colliderect(enemy.rect):
                if self.hero.attacking:
                    enemy.defeat()
                    self.game_state.score += MECHANIC["score_per_enemy"]
                else:
                    self.game_state.lives -= 1
                    if self.game_state.lives <= 0:
                        self.game_state.state = "game_over"

    def check_victory(self):
        if all(not enemy.alive for enemy in self.level.enemies):
            if self.game_state.level < self.game_state.max_levels:
                self.game_state.level += 1
                self.level = Level(self.game_state.level)
                self.hero = Hero(100, 100)
            else:
                self.game_state.state = "victory"