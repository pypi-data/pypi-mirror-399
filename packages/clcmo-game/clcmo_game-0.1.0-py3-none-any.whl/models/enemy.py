from pygame import Rect
from utils.constants import ENEMY_SPEED
from utils.animations import SpriteAnimation


class Enemy:
    """Enemy character with patrol and animation."""
    
    def __init__(self, x, y, zone):
        self.x = x
        self.y = y
        self.speed = ENEMY_SPEED
        self.zone = zone
        self.alive = True
        self.rect = Rect(self.x, self.y, 32, 32)
        
        # Animation
        self.idle_animation = SpriteAnimation(["red"], duration_per_frame=0.2)
        self.moving_animation = SpriteAnimation(
            ["red", "darkred"],
            duration_per_frame=0.15
        )
        self.current_animation = self.idle_animation
    
    def patrol(self):
        """Patrol within zone."""
        self.x += self.speed
        
        # Zone boundaries
        zone_bounds = {
            "zone1": (200, 400),
            "zone2": (350, 550),
            "zone3": (100, 600),
            "zone4": (200, 700)
        }
        
        if self.zone in zone_bounds:
            min_x, max_x = zone_bounds[self.zone]
            if self.x >= max_x:
                self.speed = -abs(self.speed)
            elif self.x <= min_x:
                self.speed = abs(self.speed)
        
        self.rect.topleft = (self.x, self.y)
        self.current_animation = self.moving_animation
    
    def defeat(self):
        """Mark enemy as defeated."""
        self.alive = False
    
    def update_animation(self, dt=0.016):
        """Update animation."""
        self.current_animation.update(dt)
    
    def get_color(self):
        """Get current sprite color."""
        return self.current_animation.get_current_frame()