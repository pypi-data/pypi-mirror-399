from views.base_view import BaseView
from utils.constants import SCREEN

class PauseView(BaseView):
    def draw(self, screen):
        screen.fill((0, 0, 0))
        self.draw_text(screen, "pause", (SCREEN["WIDTH"] // 2, SCREEN["HEIGHT"] // 2), fontsize=60, color="yellow")
        self.draw_text(screen, "resume", (SCREEN["WIDTH"] // 2, SCREEN["HEIGHT"] // 2 + 100), fontsize=40)