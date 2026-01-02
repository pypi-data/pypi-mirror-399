"""Input handling for menu and game."""

import pygame


class InputHandler:
    """Handles keyboard and mouse input."""
    
    def __init__(self, controller):
        self.controller = controller
    
    def handle_mouse(self, pos):
        """Handle mouse click."""
        game_state = self.controller.game_state
        
        if game_state.state == "menu":
            self.controller.views["menu"].handle_click(pos)
            
            # Check menu state changes
            menu_view = self.controller.views["menu"]
            if menu_view.start_game:
                game_state.state = "playing"
                menu_view.start_game = False
            elif menu_view.exit_requested:
                import sys
                sys.exit(0)
            
            game_state.sound_on = menu_view.sound_enabled
    
    def handle_key(self, key):
        """Handle keyboard input."""
        game_state = self.controller.game_state
        
        if game_state.state == "playing":
            # Movement keys using pygame constants
            if key in (pygame.K_UP, pygame.K_w):
                self.controller.hero.move(0, -1)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.controller.hero.move(0, 1)
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.controller.hero.move(-1, 0)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.controller.hero.move(1, 0)
            elif key == pygame.K_SPACE:
                self.controller.hero.attack()
            elif key == pygame.K_p:
                game_state.state = "paused"
        
        elif game_state.state == "paused":
            if key == pygame.K_p:
                game_state.state = "playing"