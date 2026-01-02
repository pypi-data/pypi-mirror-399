from views.base_view import BaseView
from utils.constants import SCREEN


class HUDView(BaseView):

    def draw(self, screen, score, lives):
        self.draw_text(screen, "score", (50, 20), fontsize=30)
        screen.draw.text(str(score),
                         topleft=(100, 10),
                         fontsize=30,
                         color="white")
        self.draw_text(screen, "lives", (50, 60), fontsize=30)
        screen.draw.text(str(lives),
                         topleft=(100, 50),
                         fontsize=30,
                         color="white")
