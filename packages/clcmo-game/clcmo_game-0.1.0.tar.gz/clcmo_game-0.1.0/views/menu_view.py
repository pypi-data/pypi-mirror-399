from views.base_view import BaseView
from utils.constants import SCREEN
from utils.button import Button


class MenuView(BaseView):
    """Main menu view with interactive buttons."""
    
    def __init__(self, language="en"):
        super().__init__(language)
        
        # Calculate button positions
        center_x = SCREEN["WIDTH"] // 2
        button_width = 300
        button_height = 60
        button_x = center_x - button_width // 2
        
        # Create buttons
        self.buttons = {
            "start": Button(
                button_x, 300, button_width, button_height,
                self.messages.get("start", "Start Game"),
                action=self.on_start_click
            ),
            "sound": Button(
                button_x, 400, button_width, button_height,
                self.messages.get("settings", "Settings"),
                action=self.on_sound_click
            ),
            "exit": Button(
                button_x, 500, button_width, button_height,
                self.messages.get("exit", "Exit"),
                action=self.on_exit_click
            )
        }
        
        self.sound_enabled = True
        self.exit_requested = False
        self.start_game = False
    
    def on_start_click(self):
        """Handle start button click."""
        self.start_game = True
    
    def on_sound_click(self):
        """Handle sound toggle click."""
        self.sound_enabled = not self.sound_enabled
        # Update button text
        status = "ON" if self.sound_enabled else "OFF"
        self.buttons["sound"].text = f"{self.messages.get('settings', 'Settings')} [{status}]"
    
    def on_exit_click(self):
        """Handle exit button click."""
        self.exit_requested = True
    
    def update(self, mouse_pos):
        """Update button hover states."""
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
    
    def handle_click(self, mouse_pos):
        """Handle mouse click on buttons."""
        for button in self.buttons.values():
            if button.is_clicked(mouse_pos):
                button.on_click()
    
    def draw(self, screen):
        """Draw menu on screen."""
        screen.fill((0, 0, 0))
        
        # Draw title
        self.draw_text(
            screen, "title",
            (SCREEN["WIDTH"] // 2, 100),
            fontsize=60
        )
        
        # Draw sound status
        status = "ON" if self.sound_enabled else "OFF"
        self.buttons["sound"].text = f"{self.messages.get('settings', 'Settings')} [{status}]"
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
