from utils.constants import SCREEN
from utils.helpers import get_messages

class BaseView:
    def __init__(self, language="en"):
        self.language = language
        self.messages = get_messages(language)

    def draw_text(self, screen, text_key, position, fontsize=30, color="white"):
        text = self.messages.get(text_key, text_key)
        screen.draw.text(text, center=position, fontsize=fontsize, color=color)