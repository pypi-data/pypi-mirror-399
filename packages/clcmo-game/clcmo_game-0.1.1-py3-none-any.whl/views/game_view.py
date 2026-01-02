from views.base_view import BaseView
from utils.constants import SCREEN


class GameView(BaseView):
    """Game view for rendering gameplay."""
    
    def draw(self, screen, hero, enemies, power_ups):
        """Draw game scene."""
        screen.fill((0, 0, 0))
        
        # Draw hero with animation color
        hero_color = hero.get_color()
        screen.draw.filled_rect(hero.rect, hero_color)
        screen.draw.rect(hero.rect, "white")
        
        # Draw enemies with animation
        for enemy in enemies:
            if enemy.alive:
                enemy_color = enemy.get_color()
                screen.draw.filled_rect(enemy.rect, enemy_color)
                screen.draw.rect(enemy.rect, "white")
        
        # Draw power-ups
        for power_up in power_ups:
            screen.draw.filled_circle(power_up["pos"], 10, "yellow")
            screen.draw.circle(power_up["pos"], 10, "white")