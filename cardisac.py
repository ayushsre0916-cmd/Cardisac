import pygame
import random
import math
import time
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 800
CARD_W, CARD_H = 140, 200

# Colors - Added missing PURPLE and other colors
DARK_BG = (15, 15, 25)
WOOD_BG = (40, 30, 20)
CANDLE_LIGHT = (255, 200, 100)
GLOW = (180, 40, 255)
BLOOD_RED = (120, 20, 30)
BONE_WHITE = (220, 210, 190)
GOLD = (255, 215, 0)
SILVER = (200, 200, 210)
DARK_GREEN = (20, 80, 40)
DARK_BLUE = (30, 40, 80)
PURPLE = (160, 60, 220)  # Added missing PURPLE
WHITE = (255, 255, 255)  # Added missing WHITE

# Load card images
def load_card_images():
    card_images = {}
    try:
        # Create placeholder images with the card names
        card_images["angel"] = pygame.Surface((CARD_W-20, CARD_H-60))
        card_images["angel"].fill((100, 150, 255))
        
        card_images["shelster"] = pygame.Surface((CARD_W-20, CARD_H-60))
        card_images["shelster"].fill((150, 100, 200))
        
        card_images["player"] = pygame.Surface((CARD_W-20, CARD_H-60))
        card_images["player"].fill((200, 150, 100))
        
        card_images["witch"] = pygame.Surface((CARD_W-20, CARD_H-60))
        card_images["witch"].fill((100, 200, 150))
        
        card_images["arrow_head"] = pygame.Surface((CARD_W-20, CARD_H-60))
        card_images["arrow_head"].fill((200, 100, 100))
        
        # Add text to placeholder images
        font = pygame.font.SysFont("arial", 14)
        for name, surf in card_images.items():
            text = font.render(name.upper(), True, WHITE)
            surf.blit(text, (surf.get_width()//2 - text.get_width()//2, surf.get_height()//2 - text.get_height()//2))
            
    except Exception as e:
        print(f"Could not load card images: {e}")
        # Create fallback colored squares
        colors = [(100, 150, 255), (150, 100, 200), (200, 150, 100), (100, 200, 150), (200, 100, 100)]
        names = ["angel", "shelster", "player", "witch", "arrow_head"]
        for i, name in enumerate(names):
            card_images[name] = pygame.Surface((CARD_W-20, CARD_H-60))
            card_images[name].fill(colors[i])
    
    return card_images

# Load sounds
def load_sounds():
    sounds = {}
    try:
        # Create silent placeholder sounds
        for sound_name in ["background", "card_place", "sacrifice", "battle", "victory", "defeat"]:
            sounds[sound_name] = pygame.mixer.Sound(pygame.mixer.Sound(buffer=bytes([0])))
    except:
        print("Could not load sounds - using silent placeholders")
        for sound_name in ["background", "card_place", "sacrifice", "battle", "victory", "defeat"]:
            sounds[sound_name] = pygame.mixer.Sound(pygame.mixer.Sound(buffer=bytes([0])))
    
    return sounds

# Card types based on your images - FIXED with proper colors
CARD_TYPES = [
    {"name": "Angel Healer", "atk": 2, "hp": 4, "cost": 2, "icon": "😇", "color": (100, 150, 255), "souls": 2, "sigil": "Healer", "image_key": "angel"},
    {"name": "Your Shelster", "atk": 3, "hp": 2, "cost": 2, "icon": "🦀", "color": (150, 100, 200), "souls": 2, "sigil": "Rib Sacrifice", "image_key": "shelster"},
    {"name": "The Player", "atk": 1, "hp": 3, "cost": 1, "icon": "👤", "color": (200, 150, 100), "souls": 1, "sigil": "Sacrifice", "image_key": "player"},
    {"name": "Mysterious Witch", "atk": 4, "hp": 3, "cost": 3, "icon": "🧙", "color": (100, 200, 150), "souls": 3, "sigil": "Corner", "image_key": "witch"},
    {"name": "Arrow Head", "atk": 3, "hp": 1, "cost": 2, "icon": "🏹", "color": (200, 100, 100), "souls": 2, "sigil": "Piercing", "image_key": "arrow_head"},
    {"name": "Ancient Guardian", "atk": 2, "hp": 5, "cost": 3, "icon": "🛡️", "color": SILVER, "souls": 3, "sigil": "Protector", "image_key": "guardian"},
    {"name": "Soul Eater", "atk": 4, "hp": 2, "cost": 3, "icon": "👻", "color": PURPLE, "souls": 3, "sigil": "Soul Steal", "image_key": "soul_eater"},
    {"name": "Blood Mage", "atk": 5, "hp": 3, "cost": 4, "icon": "🔮", "color": BLOOD_RED, "souls": 4, "sigil": "Blood Ritual", "image_key": "blood_mage"},
]

# Fonts
FONT = pygame.font.SysFont("arial", 16)
FONT_SMALL = pygame.font.SysFont("arial", 12)
FONT_LARGE = pygame.font.SysFont("arial", 20)
CREEPY_FONT = pygame.font.SysFont("candara", 24, bold=True)
TITLE_FONT = pygame.font.SysFont("candara", 64, bold=True)
SIGIL_FONT = pygame.font.SysFont("arial", 10)

class Particle:
    def __init__(self, x, y, color, speed_range=(-2, 2), life_range=(20, 40)):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(speed_range[0], speed_range[1])
        self.speed_y = random.uniform(speed_range[0], speed_range[1])
        self.life = random.randint(life_range[0], life_range[1])
        self.max_life = self.life
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
    
    def draw(self, surface):
        alpha = min(255, (self.life / self.max_life) * 255)
        color_with_alpha = (*self.color, alpha)
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))

class FloatingText:
    def __init__(self, x, y, text, color, size=20, duration=60):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.life = duration
        self.max_life = duration
        self.font = pygame.font.SysFont("arial", size)
    
    def update(self):
        self.y -= 1
        self.life -= 1
        return self.life > 0
    
    def draw(self, surface):
        alpha = min(255, self.life * 4)
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (self.x - text_surf.get_width()//2, self.y))

class Candle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lit = True
        self.flame_particles = []
        self.flicker_timer = 0
    
    def update(self):
        self.flicker_timer += 1
        
        if random.random() < 0.3:
            self.flame_particles.append(Particle(
                self.x + random.randint(-5, 5),
                self.y - 20 + random.randint(-10, 0),
                CANDLE_LIGHT,
                speed_range=(-0.5, 0.5),
                life_range=(10, 25)
            ))
        
        self.flame_particles = [p for p in self.flame_particles if p.update()]
    
    def draw(self, surface):
        pygame.draw.rect(surface, (100, 100, 120), (self.x - 8, self.y, 16, 40))
        
        if self.lit:
            flicker_offset = math.sin(self.flicker_timer * 0.2) * 2
            flame_points = [
                (self.x, self.y - 25 + flicker_offset),
                (self.x - 8, self.y - 15),
                (self.x + 8, self.y - 15)
            ]
            pygame.draw.polygon(surface, CANDLE_LIGHT, flame_points)
            
            for particle in self.flame_particles:
                particle.draw(surface)

class Card:
    def __init__(self, data, owner, card_images):
        self.data = data
        self.owner = owner
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.atk = data["atk"]
        self.cost = data["cost"]
        self.souls = data["souls"]
        self.rect = pygame.Rect(0, 0, CARD_W, CARD_H)
        self.selected = False
        self.particles = []
        self.shake_timer = 0
        self.glow_timer = 0
        self.sacrifice_highlight = False
        self.dragging = False
        self.card_images = card_images
    
    def add_damage_particles(self):
        for _ in range(8):
            self.particles.append(Particle(
                self.rect.centerx + random.randint(-40, 40),
                self.rect.centery + random.randint(-40, 40),
                BLOOD_RED
            ))
    
    def add_soul_particles(self):
        for _ in range(12):
            self.particles.append(Particle(
                self.rect.centerx + random.randint(-30, 30),
                self.rect.centery + random.randint(-30, 30),
                GLOW
            ))
    
    def add_blood_particles(self):
        for _ in range(15):
            self.particles.append(Particle(
                self.rect.centerx + random.randint(-50, 50),
                self.rect.centery + random.randint(-50, 50),
                BLOOD_RED,
                speed_range=(-3, 3),
                life_range=(30, 60)
            ))
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
        if self.glow_timer > 0:
            self.glow_timer -= 1
    
    def draw(self, surface, highlight=False, dragging=False):
        shake_x = random.randint(-2, 2) if self.shake_timer > 0 else 0
        shake_y = random.randint(-2, 2) if self.shake_timer > 0 else 0
        
        for particle in self.particles:
            particle.draw(surface)
        
        rect = self.rect.copy()
        if dragging:
            rect.x += shake_x
            rect.y += shake_y
        
        # Card background
        pygame.draw.rect(surface, (30, 25, 20), rect, border_radius=12)
        
        # Card border with glow effect
        border_color = self.data.get("color", BONE_WHITE)
        if highlight or self.selected or self.glow_timer > 0:
            glow_intensity = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)
            border_color = (
                min(255, int(border_color[0] * glow_intensity)),
                min(255, int(border_color[1] * glow_intensity)),
                min(255, int(border_color[2] * glow_intensity))
            )
        
        if self.sacrifice_highlight:
            border_color = GLOW
        
        border_width = 4 if dragging else 3
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=12)
        
        # Card interior
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(surface, (45, 40, 35), inner_rect, border_radius=8)
        
        # Card name
        name = CREEPY_FONT.render(self.data["name"], True, border_color)
        surface.blit(name, (rect.x + 10, rect.y + 10))
        
        # Card image/art
        image_rect = pygame.Rect(rect.x + 20, rect.y + 45, CARD_W - 40, 60)
        image_key = self.data.get("image_key", self.data["name"].lower().replace(" ", "_"))
        if image_key in self.card_images:
            # Scale image to fit
            scaled_image = pygame.transform.smoothscale(self.card_images[image_key], (CARD_W - 40, 60))
            surface.blit(scaled_image, image_rect)
        else:
            # Fallback: colored rectangle with icon
            pygame.draw.rect(surface, (60, 55, 50), image_rect, border_radius=6)
            icon = FONT_LARGE.render(self.data.get("icon", "?"), True, border_color)
            surface.blit(icon, (rect.centerx - icon.get_width()//2, rect.y + 75))
        
        # Sigil
        sigil_text = SIGIL_FONT.render(self.data["sigil"], True, SILVER)
        surface.blit(sigil_text, (rect.centerx - sigil_text.get_width()//2, rect.y + 130))
        
        # Stats in corners
        atk_bg = pygame.Rect(rect.x + 10, rect.y + CARD_H - 35, 30, 25)
        hp_bg = pygame.Rect(rect.x + CARD_W - 40, rect.y + CARD_H - 35, 30, 25)
        
        pygame.draw.rect(surface, (80, 40, 40), atk_bg, border_radius=4)
        pygame.draw.rect(surface, (40, 80, 40), hp_bg, border_radius=4)
        
        atk = FONT.render(str(self.atk), True, BONE_WHITE)
        hp = FONT.render(str(self.hp), True, BONE_WHITE)
        cost = FONT_SMALL.render(f"💀{self.cost}", True, BONE_WHITE)
        souls = FONT_SMALL.render(f"💜{self.souls}", True, GLOW)
        
        surface.blit(atk, (rect.x + 18, rect.y + CARD_H - 30))
        surface.blit(hp, (rect.x + CARD_W - 28, rect.y + CARD_H - 30))
        surface.blit(cost, (rect.x + 12, rect.y + CARD_H - 55))
        surface.blit(souls, (rect.x + CARD_W - 35, rect.y + CARD_H - 55))
        
        # HP bar
        if self.max_hp > 0:
            hp_ratio = self.hp / self.max_hp
            hp_bar = pygame.Rect(rect.x + 15, rect.y + CARD_H - 75, rect.width - 30, 6)
            pygame.draw.rect(surface, (60, 60, 70), hp_bar, border_radius=3)
            if hp_ratio > 0:
                hp_fill = pygame.Rect(rect.x + 15, rect.y + CARD_H - 75, 
                                     (rect.width - 30) * hp_ratio, 6)
                hp_color = (50, 200, 80) if hp_ratio > 0.5 else (255, 200, 50) if hp_ratio > 0.25 else (220, 60, 60)
                pygame.draw.rect(surface, hp_color, hp_fill, border_radius=3)

def make_deck(card_images):
    deck = []
    # Add cards based on your images
    for _ in range(2):
        deck.append(Card(CARD_TYPES[0], 'player', card_images))  # Angel Healer
    for _ in range(2):
        deck.append(Card(CARD_TYPES[1], 'player', card_images))  # Your Shelster
    for _ in range(2):
        deck.append(Card(CARD_TYPES[2], 'player', card_images))  # The Player
    for _ in range(1):
        deck.append(Card(CARD_TYPES[3], 'player', card_images))  # Mysterious Witch
    for _ in range(2):
        deck.append(Card(CARD_TYPES[4], 'player', card_images))  # Arrow Head
    for _ in range(1):
        deck.append(Card(CARD_TYPES[5], 'player', card_images))  # Ancient Guardian
    random.shuffle(deck)
    return deck

def enemy_deck(card_images):
    deck = []
    for _ in range(2):
        deck.append(Card(CARD_TYPES[1], 'enemy', card_images))  # Your Shelster
    for _ in range(2):
        deck.append(Card(CARD_TYPES[3], 'enemy', card_images))  # Mysterious Witch
    for _ in range(2):
        deck.append(Card(CARD_TYPES[4], 'enemy', card_images))  # Arrow Head
    for _ in range(2):
        deck.append(Card(CARD_TYPES[6], 'enemy', card_images))  # Soul Eater
    for _ in range(1):
        deck.append(Card(CARD_TYPES[7], 'enemy', card_images))  # Blood Mage
    random.shuffle(deck)
    return deck

def deal_hand(deck, n=4):
    hand = []
    for _ in range(min(n, len(deck))):
        if deck:
            hand.append(deck.pop())
    return hand

def draw_hand(surface, hand, y, dragging_card=None):
    for i, card in enumerate(hand):
        if dragging_card == card:
            continue
        card.rect = pygame.Rect(200 + i * (CARD_W + 20), y, CARD_W, CARD_H)
        card.draw(surface)

    if dragging_card:
        dragging_card.draw(surface, dragging=True)

def draw_table(surface, table, y, is_player=True):
    for i, card in enumerate(table):
        # Fixed: Proper spacing to prevent overlap
        x = 300 + i * (CARD_W + 50)  # Increased spacing
        rect = pygame.Rect(x, y, CARD_W, CARD_H)
        if card:
            card.rect = rect
            card.draw(surface)
        else:
            slot_color = (70, 60, 50) if is_player else (60, 50, 70)
            pygame.draw.rect(surface, slot_color, rect, 2, border_radius=8)
            slot_text = FONT_SMALL.render("Empty", True, (100, 100, 100))
            surface.blit(slot_text, (rect.centerx - slot_text.get_width()//2, rect.centery - 6))

def draw_deck_box(surface, x, y, deck_count, is_player=True):
    rect = pygame.Rect(x, y, 80, 120)
    color = (70, 60, 50) if is_player else (60, 50, 70)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, (100, 90, 80), rect, 2, border_radius=10)
    
    count_txt = FONT_LARGE.render(str(deck_count), True, BONE_WHITE)
    surface.blit(count_txt, (x + 30, y + 45))
    
    label = FONT_SMALL.render("DECK", True, (150, 150, 150))
    surface.blit(label, (x + 20, y + 15))
    return rect

def draw_button(surface, rect, text, active=True, hover=False):
    if active:
        color = (40, 180, 60) if not hover else (60, 220, 80)
        border_color = (80, 255, 100)
    else:
        color = (60, 60, 60)
        border_color = (100, 100, 100)
    
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=10)
    
    btxt = CREEPY_FONT.render(text, True, BONE_WHITE)
    surface.blit(btxt, (rect.centerx - btxt.get_width()//2, rect.centery - btxt.get_height()//2))

def draw_soul_meter(surface, x, y, current_souls, max_souls=10, is_player=True):
    meter_bg = pygame.Rect(x, y, 250, 30)
    
    pygame.draw.rect(surface, (40, 35, 45), meter_bg, border_radius=15)
    
    if max_souls > 0:
        fill_width = (current_souls / max_souls) * 250
        fill_rect = pygame.Rect(x, y, fill_width, 30)
        
        if fill_width > 0:
            for i in range(int(fill_width)):
                pos_ratio = i / fill_width
                r = int(120 + 60 * pos_ratio)
                g = int(40 + 100 * pos_ratio)
                b = int(180 + 40 * pos_ratio)
                pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + 30))
    
    pygame.draw.rect(surface, GLOW, meter_bg, 2, border_radius=15)
    
    soul_text = FONT.render(f"SOULS: {current_souls}/{max_souls}", True, BONE_WHITE)
    surface.blit(soul_text, (x + 80, y + 7))

def draw_scales(surface, player_hp, enemy_hp, max_hp=15):
    center_x = WIDTH // 2
    scale_width = 200
    scale_height = 40
    
    scale_rect = pygame.Rect(center_x - scale_width//2, 20, scale_width, scale_height)
    pygame.draw.rect(surface, (50, 45, 55), scale_rect, border_radius=20)
    pygame.draw.rect(surface, (80, 75, 85), scale_rect, 2, border_radius=20)
    
    total_hp = player_hp + enemy_hp
    if total_hp > 0:
        balance_ratio = player_hp / total_hp
        balance_x = center_x - scale_width//2 + scale_width * balance_ratio
        
        pygame.draw.line(surface, GOLD, (balance_x, 25), (balance_x, 55), 3)
        
        player_width = (player_hp / max_hp) * (scale_width // 2)
        if player_width > 0:
            player_rect = pygame.Rect(balance_x - player_width, 30, player_width, 20)
            for i in range(int(player_width)):
                pos_ratio = i / player_width
                r = int(50 + 100 * pos_ratio)
                g = int(180 + 40 * pos_ratio)
                b = int(80 + 20 * pos_ratio)
                pygame.draw.line(surface, (r, g, b), (balance_x - i, 30), (balance_x - i, 50))
        
        enemy_width = (enemy_hp / max_hp) * (scale_width // 2)
        if enemy_width > 0:
            enemy_rect = pygame.Rect(balance_x, 30, enemy_width, 20)
            for i in range(int(enemy_width)):
                pos_ratio = i / enemy_width
                r = int(180 + 40 * pos_ratio)
                g = int(50 + 40 * pos_ratio)
                b = int(80 + 100 * pos_ratio)
                pygame.draw.line(surface, (r, g, b), (balance_x + i, 30), (balance_x + i, 50))
    
    player_label = FONT.render(f"YOU: {player_hp}", True, (100, 200, 100))
    enemy_label = FONT.render(f"FOE: {enemy_hp}", True, (200, 100, 100))
    
    surface.blit(player_label, (center_x - scale_width//2 - player_label.get_width() - 10, 30))
    surface.blit(enemy_label, (center_x + scale_width//2 + 10, 30))

def draw_round_indicator(surface, current_round, total_rounds=3, player_wins=0, enemy_wins=0):
    round_text = FONT_LARGE.render(f"ROUND {current_round}/{total_rounds}", True, SILVER)
    surface.blit(round_text, (WIDTH//2 - round_text.get_width()//2, 100))
    
    wins_text = FONT.render(f"Your Wins: {player_wins}  |  Enemy Wins: {enemy_wins}", True, BONE_WHITE)
    surface.blit(wins_text, (WIDTH//2 - wins_text.get_width()//2, 130))

def draw_main_menu(surface, start_button, hover_start=False, particles=[]):
    for y in range(0, HEIGHT, 4):
        for x in range(0, WIDTH, 4):
            wood_shade = random.randint(20, 30)
            pygame.draw.rect(surface, (wood_shade, wood_shade-5, wood_shade-10), (x, y, 4, 4))
    
    for particle in particles:
        particle.draw(surface)
    
    title_text = "DARK CARD BATTLE"
    title_shadow = TITLE_FONT.render(title_text, True, (30, 0, 40))
    title_main = TITLE_FONT.render(title_text, True, GLOW)
    
    title_x = WIDTH // 2 - title_main.get_width() // 2
    title_y = HEIGHT // 4
    
    for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3), (0, 3)]:
        surface.blit(title_shadow, (title_x + offset[0], title_y + offset[1]))
    
    surface.blit(title_main, (title_x, title_y))
    
    subtitle = CREEPY_FONT.render("A Game of Sacrifice and Strategy", True, SILVER)
    surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, title_y + 80))
    
    button_color = (60, 180, 70) if hover_start else (40, 140, 50)
    pygame.draw.rect(surface, button_color, start_button, border_radius=15)
    pygame.draw.rect(surface, (100, 255, 120), start_button, 3, border_radius=15)
    
    button_text = CREEPY_FONT.render("BEGIN RITUAL", True, BONE_WHITE)
    text_shadow = CREEPY_FONT.render("BEGIN RITUAL", True, (20, 20, 20))
    
    surface.blit(text_shadow, (start_button.centerx - button_text.get_width()//2 + 2, 
                              start_button.centery - button_text.get_height()//2 + 2))
    surface.blit(button_text, (start_button.centerx - button_text.get_width()//2, 
                              start_button.centery - button_text.get_height()//2))
    
    features = [
        "• BEST OF 3 ROUNDS - Win 2 rounds to claim victory",
        "• SACRIFICE cards to gain SOULS for powerful summons", 
        "• STRATEGIC COMBAT with unique card abilities",
        "• DARK ATMOSPHERE with immersive visuals and sound"
    ]
    
    for i, feature in enumerate(features):
        feature_text = FONT.render(feature, True, (180, 180, 200))
        surface.blit(feature_text, (WIDTH // 2 - feature_text.get_width() // 2, 
                                  HEIGHT // 2 + 20 + i * 30))
    
    footer = FONT_SMALL.render("Your fate awaits in the cards...", True, (120, 120, 140))
    surface.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 80))

def get_card_at(pos, hand):
    for card in hand:
        if card.rect.collidepoint(pos):
            return card
    return None

def get_table_slot(pos, table_y, is_player=True):
    x, y = pos
    for i in range(4):
        slot_x = 300 + i * (CARD_W + 50)  # Consistent increased spacing
        slot_rect = pygame.Rect(slot_x, table_y, CARD_W, CARD_H)
        if slot_rect.collidepoint(x, y):
            return i
    return None

def compare_and_battle(player_table, enemy_table, floating_texts, sounds):
    for i in range(4):
        p_card = player_table[i]
        e_card = enemy_table[i]
        if p_card and e_card:
            # Cards battle each other
            p_card.hp -= e_card.atk
            e_card.hp -= p_card.atk
            
            # Visual effects
            p_card.add_damage_particles()
            e_card.add_damage_particles()
            p_card.shake_timer = 15
            e_card.shake_timer = 15
            
            # Play battle sound
            try:
                sounds["battle"].play()
            except:
                pass
            
            # Floating combat text
            floating_texts.append(FloatingText(
                p_card.rect.centerx, p_card.rect.centery - 30, 
                f"-{e_card.atk}", BLOOD_RED, 16, 45
            ))
            floating_texts.append(FloatingText(
                e_card.rect.centerx, e_card.rect.centery - 30,
                f"-{p_card.atk}", BLOOD_RED, 16, 45
            ))
            
            # Check for deaths
            if p_card.hp <= 0:
                player_table[i] = None
                p_card.add_blood_particles()
            if e_card.hp <= 0:
                enemy_table[i] = None
                e_card.add_blood_particles()

def enemy_ai(hand, table, player_table, enemy_souls, floating_texts, sounds):
    empty_slots = [i for i, card in enumerate(table) if card is None]
    
    if empty_slots and hand:
        playable_cards = [card for card in hand if card.cost <= enemy_souls]
        playable_cards.sort(key=lambda x: x.cost)
        
        for card in playable_cards:
            if empty_slots and enemy_souls >= card.cost:
                slot = empty_slots.pop(0)
                table[slot] = card
                hand.remove(card)
                enemy_souls -= card.cost
                
                # Play card place sound
                try:
                    sounds["card_place"].play()
                except:
                    pass
                
                floating_texts.append(FloatingText(
                    table[slot].rect.centerx, table[slot].rect.centery,
                    f"Summoned!", SILVER, 14, 50
                ))
                card.glow_timer = 30
    
    return enemy_souls

def draw_round_result(surface, round_num, player_won, final_round=False):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    if final_round:
        if player_won:
            result_text = "VICTORY ACHIEVED!"
            result_color = GOLD
            sub_text = "You have proven worthy of the ancient ritual"
        else:
            result_text = "DEFEAT"
            result_color = BLOOD_RED
            sub_text = "The darkness has consumed you..."
    else:
        if player_won:
            result_text = f"ROUND {round_num} WON!"
            result_color = (100, 200, 100)
            sub_text = "The balance shifts in your favor"
        else:
            result_text = f"ROUND {round_num} LOST"
            result_color = (200, 100, 100)
            sub_text = "The enemy gains ground"
    
    result_surface = TITLE_FONT.render(result_text, True, result_color)
    sub_surface = CREEPY_FONT.render(sub_text, True, SILVER)
    
    surface.blit(result_surface, (WIDTH//2 - result_surface.get_width()//2, HEIGHT//2 - 60))
    surface.blit(sub_surface, (WIDTH//2 - sub_surface.get_width()//2, HEIGHT//2 + 20))
    
    continue_text = FONT.render("Press SPACE to continue...", True, BONE_WHITE)
    surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 80))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dark Card Battle - A Game of Sacrifice")
    clock = pygame.time.Clock()

    # Load resources
    card_images = load_card_images()
    sounds = load_sounds()
    
    # Play background music
    try:
        pygame.mixer.music.load(sounds["background"])
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except:
        print("Could not play background music")

    # Game state
    menu = True
    start_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 180, 240, 70)

    # Game variables
    player_deck = []
    enemy_deck_ = []
    player_hp = 15
    player_max_hp = 15
    enemy_hp = 15
    enemy_max_hp = 15
    player_souls = 3
    enemy_souls = 3
    max_souls = 10
    hand = []
    enemy_hand = []
    table = [None] * 4
    enemy_table = [None] * 4
    dragging_card = None
    drag_offset = (0, 0)
    turn_stage = 'play'
    message = ""
    message_timer = 0
    fight_btn_rect = pygame.Rect(WIDTH - 220, HEIGHT - 120, 180, 60)
    player_turn = True
    game_over = False
    turn_count = 0
    floating_texts = []
    
    # Round system
    current_round = 1
    total_rounds = 3
    player_wins = 0
    enemy_wins = 0
    showing_round_result = False
    round_result_timer = 0
    player_won_round = False
    
    # Atmospheric elements
    candles = [Candle(100, 150), Candle(WIDTH-100, 150), Candle(100, HEIGHT-150), Candle(WIDTH-100, HEIGHT-150)]
    menu_particles = []
    
    # Create menu particles
    for _ in range(80):
        menu_particles.append(Particle(
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            (random.randint(50, 100), random.randint(20, 60), random.randint(100, 150))
        ))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()
        
        if menu:
            menu_particles = [p for p in menu_particles if p.update()]
            while len(menu_particles) < 80:
                menu_particles.append(Particle(
                    random.randint(0, WIDTH),
                    random.randint(-50, 0),
                    (random.randint(50, 100), random.randint(20, 60), random.randint(100, 150))
                ))
            
            hover_start = start_button.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_button.collidepoint(event.pos):
                        menu = False
                        player_deck = make_deck(card_images)
                        enemy_deck_ = enemy_deck(card_images)
                        hand = deal_hand(player_deck, 4)
                        enemy_hand = deal_hand(enemy_deck_, 4)
                        player_hp, enemy_hp = player_max_hp, enemy_max_hp
                        player_souls, enemy_souls = 3, 3
                        table = [None] * 4
                        enemy_table = [None] * 4
                        turn_stage = 'play'
                        message = f"Round {current_round} begins! Your turn."
                        message_timer = 120
                        player_turn = True
                        game_over = False
                        turn_count = 0
                        floating_texts = []
                        current_round = 1
                        player_wins = 0
                        enemy_wins = 0
                        showing_round_result = False
            
            screen.fill(DARK_BG)
            draw_main_menu(screen, start_button, hover_start, menu_particles)
            pygame.display.flip()
            clock.tick(60)
            continue

        # Handle round result display
        if showing_round_result:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    showing_round_result = False
                    
                    if current_round > total_rounds or player_wins >= 2 or enemy_wins >= 2:
                        # Tournament over, return to menu
                        menu = True
                        try:
                            if player_wins >= 2:
                                sounds["victory"].play()
                            else:
                                sounds["defeat"].play()
                        except:
                            pass
                    else:
                        # Start next round
                        current_round += 1
                        player_deck = make_deck(card_images)
                        enemy_deck_ = enemy_deck(card_images)
                        hand = deal_hand(player_deck, 4)
                        enemy_hand = deal_hand(enemy_deck_, 4)
                        player_hp, enemy_hp = player_max_hp, enemy_max_hp
                        player_souls, enemy_souls = 3, 3
                        table = [None] * 4
                        enemy_table = [None] * 4
                        turn_stage = 'play'
                        message = f"Round {current_round} begins! Your turn."
                        message_timer = 120
                        player_turn = True
                        game_over = False
                        turn_count = 0
                        floating_texts = []
            
            screen.fill(DARK_BG)
            draw_round_result(screen, current_round - 1, player_won_round, 
                            final_round=(current_round > total_rounds or player_wins >= 2 or enemy_wins >= 2))
            pygame.display.flip()
            clock.tick(60)
            continue

        # Update candles
        for candle in candles:
            candle.update()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                deck_box = pygame.Rect(50, HEIGHT - 180, 80, 120)
                
                if player_turn and turn_stage == 'play' and deck_box.collidepoint(pos):
                    if player_souls >= 1 and len(hand) < 6 and player_deck:
                        drawn = deal_hand(player_deck, 1)
                        if drawn:
                            hand.extend(drawn)
                            player_souls -= 1
                            message = "Drew a card (-1 Soul)"
                            message_timer = 90
                            try:
                                sounds["card_place"].play()
                            except:
                                pass
                            floating_texts.append(FloatingText(
                                deck_box.centerx, deck_box.centery, "-1", GLOW, 16
                            ))
                            
                elif turn_stage == 'play' and player_turn:
                    sel = get_card_at(pos, hand)
                    if sel and table.count(None) > 0 and player_souls >= sel.cost:
                        dragging_card = sel
                        drag_offset = (pos[0] - sel.rect.x, pos[1] - sel.rect.y)
                        sel.dragging = True
                        
                    elif fight_btn_rect.collidepoint(pos) and any(c for c in table):
                        turn_stage = 'fight'
                        message = "The battle begins..."
                        message_timer = 60
                        try:
                            sounds["battle"].play()
                        except:
                            pass
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if player_turn and turn_stage == 'play':
                    sel = get_card_at(event.pos, hand)
                    if sel:
                        player_souls += sel.souls
                        if player_souls > max_souls:
                            player_souls = max_souls
                        hand.remove(sel)
                        message = f"Sacrificed {sel.data['name']} for {sel.souls} Souls"
                        message_timer = 90
                        sel.add_soul_particles()
                        try:
                            sounds["sacrifice"].play()
                        except:
                            pass
                        floating_texts.append(FloatingText(
                            sel.rect.centerx, sel.rect.centery, f"+{sel.souls}", GLOW, 18
                        ))
                        
            elif event.type == pygame.MOUSEMOTION:
                if dragging_card:
                    mx, my = event.pos
                    dragging_card.rect.topleft = (mx - drag_offset[0], my - drag_offset[1])
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_card:
                    slot_idx = get_table_slot(pygame.mouse.get_pos(), HEIGHT//2 - CARD_H//2 - 20, True)
                    if (slot_idx is not None and table[slot_idx] is None and 
                        player_souls >= dragging_card.cost):
                        
                        table[slot_idx] = dragging_card
                        if dragging_card in hand:
                            hand.remove(dragging_card)
                        player_souls -= dragging_card.cost
                        dragging_card.glow_timer = 45
                        dragging_card.add_soul_particles()
                        
                        try:
                            sounds["card_place"].play()
                        except:
                            pass
                        
                        floating_texts.append(FloatingText(
                            table[slot_idx].rect.centerx, table[slot_idx].rect.centery,
                            "Placed!", SILVER, 16, 50
                        ))
                    
                    dragging_card.dragging = False
                    dragging_card = None

        # Update game objects
        for card in hand + [c for c in table if c] + [c for c in enemy_table if c]:
            if card:
                card.update()
                
        for candle in candles:
            candle.update()
            
        floating_texts = [text for text in floating_texts if text.update()]

        # Draw everything
        screen.fill(DARK_BG)
        
        # Draw wood texture background
        for y in range(0, HEIGHT, 6):
            for x in range(0, WIDTH, 6):
                shade = random.randint(25, 35)
                pygame.draw.rect(screen, (shade, shade-8, shade-12), (x, y, 6, 6))
        
        # Draw candles
        for candle in candles:
            candle.draw(screen)
        
        # Draw scales (HP display)
        draw_scales(screen, player_hp, enemy_hp)
        
        # Draw round indicator
        draw_round_indicator(screen, current_round, total_rounds, player_wins, enemy_wins)
        
        # Draw soul meters
        draw_soul_meter(screen, 50, 80, player_souls, max_souls, True)
        draw_soul_meter(screen, WIDTH - 300, 80, enemy_souls, max_souls, False)
        
        # Draw turn indicator
        turn_text = "YOUR TURN" if player_turn else "ENEMY'S TURN"
        turn_color = (100, 200, 100) if player_turn else (200, 100, 100)
        turn_surface = CREEPY_FONT.render(turn_text, True, turn_color)
        screen.blit(turn_surface, (WIDTH//2 - turn_surface.get_width()//2, 150))
        
        # Draw decks
        player_deck_rect = draw_deck_box(screen, 50, HEIGHT - 180, len(player_deck), True)
        enemy_deck_rect = draw_deck_box(screen, WIDTH - 130, 180, len(enemy_deck_), False)
        
        # Draw hands and tables with proper separation
        draw_hand(screen, hand, HEIGHT - 250, dragging_card)
        draw_table(screen, table, HEIGHT//2 - CARD_H//2 - 20, True)
        draw_table(screen, enemy_table, 200, False)  # Fixed: Proper vertical separation
        
        # Draw floating text
        for text in floating_texts:
            text.draw(screen)
        
        # Draw message
        if message_timer > 0:
            message_timer -= 1
            msg_surface = FONT.render(message, True, CANDLE_LIGHT)
            screen.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, HEIGHT - 40))
        
        # Draw fight button
        if turn_stage == 'play' and player_turn:
            active = any(c for c in table)
            hover_fight = fight_btn_rect.collidepoint(mouse_pos)
            draw_button(screen, fight_btn_rect, "FIGHT", active, hover_fight)
        
        # Draw turn counter
        turn_count_text = FONT_SMALL.render(f"Turn: {turn_count}", True, SILVER)
        screen.blit(turn_count_text, (WIDTH - 120, HEIGHT - 30))
        
        # Draw instructions
        if player_turn and turn_stage == 'play':
            instructions = [
                "LEFT-CLICK & DRAG: Play card (costs souls)",
                "RIGHT-CLICK: Sacrifice card (gains souls)", 
                "CLICK DECK: Draw card (costs 1 soul)",
                "FIGHT: Begin battle phase"
            ]
            for i, instr in enumerate(instructions):
                instr_surface = FONT_SMALL.render(instr, True, (150, 150, 170))
                screen.blit(instr_surface, (20, HEIGHT - 120 + i * 20))
        
        # Battle phase logic
        if turn_stage == 'fight' and player_turn and not game_over:
            # Direct attacks to opponent
            for i in range(4):
                p_card = table[i]
                e_card = enemy_table[i]
                
                if p_card and not e_card:
                    enemy_hp -= p_card.atk
                    message = f"Direct hit! {p_card.atk} damage to enemy!"
                    message_timer = 60
                    p_card.add_blood_particles()
                    
                    floating_texts.append(FloatingText(
                        p_card.rect.centerx, p_card.rect.centery - 40,
                        f"Direct {p_card.atk}!", BLOOD_RED, 18
                    ))
                    
                if e_card and not p_card:
                    player_hp -= e_card.atk
                    message = f"Enemy attacks! {e_card.atk} damage to you!"
                    message_timer = 60
                    e_card.add_blood_particles()
                    
                    floating_texts.append(FloatingText(
                        e_card.rect.centerx, e_card.rect.centery - 40, 
                        f"Direct {e_card.atk}!", BLOOD_RED, 18
                    ))
            
            # Card vs card battles
            compare_and_battle(table, enemy_table, floating_texts, sounds)
            
            # Enemy draws souls and plays cards
            enemy_souls += 2
            if enemy_souls > max_souls:
                enemy_souls = max_souls
                
            enemy_souls = enemy_ai(enemy_hand, enemy_table, table, enemy_souls, floating_texts, sounds)

            # Clean up dead cards
            for i in range(4):
                if table[i] and table[i].hp <= 0:
                    table[i] = None
                if enemy_table[i] and enemy_table[i].hp <= 0:
                    enemy_table[i] = None

            # Check win/lose conditions for the round
            if enemy_hp <= 0 or player_hp <= 0:
                # Determine round winner
                if enemy_hp <= 0:
                    player_wins += 1
                    player_won_round = True
                    message = f"You won Round {current_round}!"
                    try:
                        sounds["victory"].play()
                    except:
                        pass
                else:
                    enemy_wins += 1
                    player_won_round = False
                    message = f"You lost Round {current_round}."
                    try:
                        sounds["defeat"].play()
                    except:
                        pass
                
                showing_round_result = True
                turn_stage = 'play'
                
            else:
                turn_stage = 'play'
                player_turn = False
                player_souls += 2
                if player_souls > max_souls:
                    player_souls = max_souls
                message = "Enemy's turn approaches..."
                message_timer = 60
                turn_count += 1

        elif not player_turn and turn_stage == 'play' and not game_over:
            # Enemy turn
            enemy_souls += 2
            if enemy_souls > max_souls:
                enemy_souls = max_souls
                
            enemy_souls = enemy_ai(enemy_hand, enemy_table, table, enemy_souls, floating_texts, sounds)
            
            # Enemy direct attacks
            for i in range(4):
                p_card = table[i]
                e_card = enemy_table[i]
                
                if e_card and not p_card:
                    player_hp -= e_card.atk
                    message = f"Enemy strikes! {e_card.atk} damage!"
                    message_timer = 60
                    e_card.add_blood_particles()
                    
                if p_card and not e_card:
                    enemy_hp -= p_card.atk
                    message = f"Your card retaliates! {p_card.atk} damage!"
                    message_timer = 60
                    p_card.add_blood_particles()

            # Clean up
            for i in range(4):
                if table[i] and table[i].hp <= 0:
                    table[i] = None
                if enemy_table[i] and enemy_table[i].hp <= 0:
                    enemy_table[i] = None

            if enemy_hp <= 0 or player_hp <= 0:
                if enemy_hp <= 0:
                    player_wins += 1
                    player_won_round = True
                    message = f"You won Round {current_round}!"
                    try:
                        sounds["victory"].play()
                    except:
                        pass
                else:
                    enemy_wins += 1
                    player_won_round = False
                    message = f"You lost Round {current_round}."
                    try:
                        sounds["defeat"].play()
                    except:
                        pass
                
                showing_round_result = True
                turn_stage = 'play'
                
            else:
                player_turn = True
                player_souls += 2
                if player_souls > max_souls:
                    player_souls = max_souls
                message = "Your turn. The cards await your command..."
                message_timer = 90
                turn_count += 1

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()