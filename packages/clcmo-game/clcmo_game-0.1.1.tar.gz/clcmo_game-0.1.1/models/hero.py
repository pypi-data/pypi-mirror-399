from pygame import Rect
from utils.constants import HERO_SPEED
from utils.animations import SpriteAnimation


class Hero:
    """Hero character with animation support."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = HERO_SPEED
        self.alive = True
        self.attacking = False
        self.attack_timer = 0
        self.rect = Rect(self.x, self.y, 32, 32)
        
        # Animation setup
        self.idle_animation = SpriteAnimation(["blue"], duration_per_frame=0.2)
        self.moving_animation = SpriteAnimation(
            ["blue", "cyan"],
            duration_per_frame=0.1
        )
        self.current_animation = self.idle_animation
        self.is_moving = False
    
    def move(self, dx, dy):
        """Move the hero."""
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.topleft = (self.x, self.y)
        
        # Switch to moving animation
        if dx != 0 or dy != 0:
            self.is_moving = True
            self.current_animation = self.moving_animation
        else:
            self.is_moving = False
            self.current_animation = self.idle_animation
    
    def attack(self):
        """Start attack animation."""
        self.attacking = True
        self.attack_timer = 0.2
    
    def update_animation(self, dt=0.016):
        """Update animation frame."""
        self.current_animation.update(dt)
        
        # Update attack timer
        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False
    
    def get_color(self):
        """Get current sprite color based on animation."""
        return self.current_animation.get_current_frame()
