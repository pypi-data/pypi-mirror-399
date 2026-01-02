from models.enemy import Enemy

class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.enemies = self.create_enemies()
        self.layout = self.generate_layout()

    def create_enemies(self):
        if self.level_num == 1:
            return [Enemy(200, 200, "zone1"), Enemy(400, 300, "zone2")]
        elif self.level_num == 2:
            return [Enemy(150, 150, "zone1"), Enemy(350, 250, "zone2"), Enemy(500, 400, "zone3")]
        elif self.level_num == 3:
            return [Enemy(100, 100, "zone1"), Enemy(300, 200, "zone2"), Enemy(500, 300, "zone3"), Enemy(600, 450, "zone4")]
        return []

    def generate_layout(self):
        # Placeholder para layout do mapa
        return {"background": "level_bg.png"}