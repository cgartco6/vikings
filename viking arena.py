import pygame
import sys
import random
import math
import os
import time
import datetime
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
GROUND_HEIGHT = 100
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
BLUE = (30, 144, 255)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
GRAY = (105, 105, 105)
LIGHT_BROWN = (210, 180, 140)
DARK_RED = (139, 0, 0)

# Game states
MAIN_MENU = 0
CHARACTER_SELECT = 1
TOURNAMENT = 2
FIGHT = 3
AD_SCREEN = 4
RESULTS = 5
WITHDRAW = 6

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Viking Arena: Tournament of Valor")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("arial", 64, bold=True)
large_font = pygame.font.SysFont("arial", 42, bold=True)
medium_font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 24)
tiny_font = pygame.font.SysFont("arial", 18)

# Load images (in-memory for portability)
def create_weapon_surface(color, size, weapon_type):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    if weapon_type == "sword":
        pygame.draw.rect(surf, color, (0, 0, size[0]//3, size[1]//3))
        pygame.draw.rect(surf, LIGHT_BROWN, (size[0]//3, size[1]//3, size[0]//3, size[1]//3))
        pygame.draw.rect(surf, color, (size[0]//3*2, 0, size[0]//3, size[1]))
    elif weapon_type == "axe":
        pygame.draw.rect(surf, LIGHT_BROWN, (size[0]//3, size[1]//3, size[0]//3, size[1]//3))
        pygame.draw.rect(surf, color, (0, size[1]//3*2, size[0], size[1]//3))
    elif weapon_type == "spear":
        pygame.draw.rect(surf, color, (size[0]//2-5, 0, 10, size[1]))
        pygame.draw.polygon(surf, color, [(size[0]//2-10, size[1]//3), 
                                         (size[0]//2+10, size[1]//3), 
                                         (size[0]//2, 0)])
    return surf

def create_character_surface(color, size, helmet=True):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    # Body
    pygame.draw.rect(surf, color, (size[0]//3, size[1]//3, size[0]//3, size[1]//2))
    # Head
    pygame.draw.circle(surf, (240, 200, 160), (size[0]//2, size[1]//4), size[1]//6)
    # Helmet
    if helmet:
        pygame.draw.arc(surf, GOLD, (size[0]//2-size[1]//4, size[1]//4-size[1]//6, 
                         size[1]//2, size[1]//3), 0, math.pi, 3)
        pygame.draw.circle(surf, RED, (size[0]//2, size[1]//4-size[1]//12), size[1]//20)
    return surf

# Create in-memory images
character_img = create_character_surface(BLUE, (80, 120))
player_img = create_character_surface(RED, (80, 120))
sword_img = create_weapon_surface(GRAY, (40, 80), "sword")
axe_img = create_weapon_surface(GRAY, (60, 60), "axe")
spear_img = create_weapon_surface(GRAY, (30, 100), "spear")
ad_img = pygame.Surface((SCREEN_WIDTH-100, SCREEN_HEIGHT-200))
ad_img.fill((30, 30, 50))
pygame.draw.rect(ad_img, (70, 70, 120), (20, 20, ad_img.get_width()-40, ad_img.get_height()-40))
ad_text = large_font.render("HIGH VALUE AD SPACE", True, GOLD)
ad_img.blit(ad_text, (ad_img.get_width()//2 - ad_text.get_width()//2, 
                     ad_img.get_height()//2 - ad_text.get_height()//2))

# Weapon types
WEAPONS = [
    {"name": "Sword", "damage": 25, "speed": 8, "range": 60, "img": sword_img},
    {"name": "Axe", "damage": 35, "speed": 5, "range": 50, "img": axe_img},
    {"name": "Spear", "damage": 20, "speed": 10, "range": 80, "img": spear_img}
]

class Fighter:
    def __init__(self, name, is_player=False):
        self.name = name
        self.is_player = is_player
        self.health = 100
        self.max_health = 100
        self.weapon = random.choice(WEAPONS)
        self.x = 0
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 120
        self.width = 80
        self.height = 120
        self.velocity = 5
        self.direction = 1  # 1 for right, -1 for left
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_frame = 0
        self.wins = 0
        self.alive = True
    
    def draw(self, screen):
        color = RED if self.is_player else BLUE
        char_img = player_img if self.is_player else character_img
        
        # Draw character
        screen.blit(pygame.transform.flip(char_img, self.direction == -1, False), 
                   (self.x, self.y))
        
        # Draw weapon
        weapon_x = self.x + (self.width//2 if self.direction == 1 else -self.weapon["img"].get_width()//2)
        weapon_y = self.y + 30
        
        if self.attacking:
            # Animate attack
            swing_offset = math.sin(self.attack_frame * 0.5) * 30 * self.direction
            screen.blit(pygame.transform.flip(self.weapon["img"], self.direction == -1, False), 
                       (weapon_x + swing_offset, weapon_y - 20))
        else:
            screen.blit(pygame.transform.flip(self.weapon["img"], self.direction == -1, False), 
                       (weapon_x, weapon_y))
        
        # Draw health bar
        bar_width = 100
        pygame.draw.rect(screen, DARK_RED, (self.x + self.width//2 - bar_width//2, self.y - 30, bar_width, 20))
        pygame.draw.rect(screen, GREEN, (self.x + self.width//2 - bar_width//2, self.y - 30, 
                                         bar_width * (self.health / self.max_health), 20))
        pygame.draw.rect(screen, WHITE, (self.x + self.width//2 - bar_width//2, self.y - 30, bar_width, 20), 2)
        
        # Draw name
        name_text = small_font.render(self.name, True, WHITE)
        screen.blit(name_text, (self.x + self.width//2 - name_text.get_width()//2, self.y - 55))
        
        # Draw weapon info
        weapon_text = tiny_font.render(f"{self.weapon['name']} (Dmg: {self.weapon['damage']})", True, GOLD)
        screen.blit(weapon_text, (self.x + self.width//2 - weapon_text.get_width()//2, self.y - 80))
    
    def move(self, target):
        if self.attacking or not self.alive:
            return
        
        distance = abs(self.x - target.x)
        in_range = distance < self.weapon["range"]
        
        if not in_range:
            # Move toward target
            if self.x < target.x:
                self.x += self.velocity
                self.direction = 1
            else:
                self.x -= self.velocity
                self.direction = -1
        elif self.attack_cooldown <= 0:
            # Attack if in range and cooldown is done
            self.attacking = True
            self.attack_frame = 0
            self.attack_cooldown = 60 // self.weapon["speed"]  # Frames until next attack
            self.direction = 1 if target.x > self.x else -1
            
            # Calculate hit chance (90% base, modified by weapon speed)
            hit_chance = 0.9 + (self.weapon["speed"] - 5) * 0.02
            if random.random() < hit_chance:
                target.health -= self.weapon["damage"]
                if target.health <= 0:
                    target.health = 0
                    target.alive = False
                    self.wins += 1
    
    def update(self):
        if self.attacking:
            self.attack_frame += 1
            if self.attack_frame > 20:  # Attack animation lasts 20 frames
                self.attacking = False
                self.attack_frame = 0
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

class Tournament:
    def __init__(self):
        self.entries = []
        self.rounds = []
        self.current_round = 0
        self.active_fight = None
        self.winner = None
        self.entry_fee = 10  # USD
        self.prize_pool = 0
        self.start_date = datetime.date.today()
        
        # Generate AI fighters
        self.ai_names = ["Ragnar", "Bjorn", "Ivar", "Lagertha", "Floki", "Harald", "Erik", "Sigurd",
                         "Gunnar", "Sven", "Olaf", "Torsten", "Ubbe", "Hvitserk", "Halfdan"]
        
        # Create player
        self.player = Fighter("Player", is_player=True)
        
        # Create AI fighters
        self.ai_fighters = [Fighter(name) for name in random.sample(self.ai_names, 7)]
        self.all_fighters = [self.player] + self.ai_fighters
        
        # Setup tournament bracket
        self.setup_bracket()
    
    def setup_bracket(self):
        # Randomize the bracket
        random.shuffle(self.all_fighters)
        
        # Create rounds (quarter-finals, semi-finals, final)
        self.rounds = []
        current_round = self.all_fighters.copy()
        
        while len(current_round) > 1:
            next_round = []
            matches = []
            
            # Pair up fighters
            for i in range(0, len(current_round), 2):
                if i+1 < len(current_round):
                    matches.append((current_round[i], current_round[i+1]))
            
            self.rounds.append(matches)
            current_round = next_round  # Will be populated with winners
    
    def start_next_fight(self):
        if self.current_round >= len(self.rounds):
            return False  # Tournament finished
        
        current_matches = self.rounds[self.current_round]
        
        # Find next match that hasn't been fought
        for match in current_matches:
            if match[0].alive and match[1].alive:
                self.active_fight = match
                return True
        
        # If all matches in this round are done, move to next round
        self.current_round += 1
        
        if self.current_round >= len(self.rounds):
            # Tournament finished, determine winner
            self.winner = self.get_tournament_winner()
            return False
        
        return self.start_next_fight()
    
    def get_tournament_winner(self):
        # Find the last fighter standing
        for fighter in self.all_fighters:
            if fighter.alive:
                return fighter
        return None

class Game:
    def __init__(self):
        self.state = MAIN_MENU
        self.player_name = "Player"
        self.player_cash = 0.0
        self.free_games = 3
        self.last_free_game_date = datetime.date.today()
        self.ad_count = 0
        self.tournament = None
        self.owner_revenue = 0.0
        self.withdraw_amount = 0.0
        self.game_result = ""
        self.tournament_result = ""
        self.ad_timer = 0
        self.ad_set_count = 0
        self.total_ads_watched = 0
        self.ads_enabled = True
    
    def start_tournament(self):
        if self.free_games > 0:
            self.free_games -= 1
            self.tournament = Tournament()
            self.tournament.prize_pool = len(self.tournament.all_fighters) * self.tournament.entry_fee
            self.state = TOURNAMENT
            return True
        elif self.player_cash >= self.tournament.entry_fee:
            self.player_cash -= self.tournament.entry_fee
            self.tournament = Tournament()
            self.tournament.prize_pool = len(self.tournament.all_fighters) * self.tournament.entry_fee
            self.state = TOURNAMENT
            return True
        return False
    
    def watch_ad(self):
        if not self.ads_enabled:
            return
        
        self.state = AD_SCREEN
        self.ad_timer = 180  # 3 seconds at 60 FPS
        self.ad_count += 1
        self.total_ads_watched += 1
        
        # Owner gets ad revenue ($100 to $2200 CPM)
        cpm = random.uniform(100, 2200)
        self.owner_revenue += cpm / 1000  # Revenue per ad view
        
        # After 3 ads, give 3 free games
        if self.ad_count % 3 == 0:
            self.free_games += 3
            self.ad_set_count += 1
    
    def update_free_games(self):
        today = datetime.date.today()
        if today > self.last_free_game_date:
            days_passed = (today - self.last_free_game_date).days
            if days_passed > 0:
                self.free_games = 3  # Reset to 3 free games
                self.last_free_game_date = today
    
    def withdraw_cash(self, amount):
        if amount <= self.player_cash:
            self.player_cash -= amount
            self.withdraw_amount = amount
            return True
        return False
    
    def run(self):
        running = True
        
        while running:
            self.update_free_games()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.state in [FIGHT, AD_SCREEN]:
                            self.state = TOURNAMENT
                        elif self.state in [TOURNAMENT, CHARACTER_SELECT, RESULTS, WITHDRAW]:
                            self.state = MAIN_MENU
                        else:
                            running = False
                    
                    # Main menu controls
                    if self.state == MAIN_MENU:
                        if event.key == K_1:
                            self.state = CHARACTER_SELECT
                        elif event.key == K_2:
                            self.watch_ad()
                        elif event.key == K_3:
                            self.state = WITHDRAW
                        elif event.key == K_4:
                            running = False
                    
                    # Character select controls
                    elif self.state == CHARACTER_SELECT:
                        if event.key == K_RETURN:
                            if self.start_tournament():
                                self.state = TOURNAMENT
                    
                    # Tournament controls
                    elif self.state == TOURNAMENT:
                        if event.key == K_SPACE:
                            if self.tournament.start_next_fight():
                                self.state = FIGHT
                    
                    # Fight controls (player only)
                    elif self.state == FIGHT and self.tournament.active_fight[0].is_player:
                        if event.key == K_LEFT:
                            self.tournament.active_fight[0].x -= 10
                        elif event.key == K_RIGHT:
                            self.tournament.active_fight[0].x += 10
                        elif event.key == K_a:  # Attack
                            if not self.tournament.active_fight[0].attacking:
                                self.tournament.active_fight[0].attacking = True
                                self.tournament.active_fight[0].attack_frame = 0
                    
                    # Results screen
                    elif self.state == RESULTS:
                        if event.key == K_RETURN:
                            self.state = MAIN_MENU
                    
                    # Withdraw screen
                    elif self.state == WITHDRAW:
                        if event.key == K_RETURN:
                            if self.withdraw_cash(min(2000, self.player_cash)):
                                self.state = RESULTS
                                self.game_result = f"Withdrew ${min(2000, self.player_cash):.2f} to PayPal"
            
            # Game logic
            if self.state == FIGHT and self.tournament.active_fight:
                fighter1, fighter2 = self.tournament.active_fight
                
                # Update fighters
                fighter1.update()
                fighter2.update()
                
                # AI movement
                if not fighter1.is_player:
                    fighter1.move(fighter2)
                if not fighter2.is_player:
                    fighter2.move(fighter1)
                
                # Check if fight is over
                if not fighter1.alive or not fighter2.alive:
                    self.state = TOURNAMENT
                    
                    # Check if tournament is over
                    if self.tournament.winner:
                        if self.tournament.winner.is_player:
                            self.player_cash += self.tournament.prize_pool
                            self.tournament_result = f"You won the tournament! Prize: ${self.tournament.prize_pool}"
                        else:
                            self.tournament_result = f"{self.tournament.winner.name} won the tournament"
                        self.state = RESULTS
            
            # Ad screen timer
            if self.state == AD_SCREEN:
                self.ad_timer -= 1
                if self.ad_timer <= 0:
                    self.state = MAIN_MENU
            
            # Drawing
            screen.fill((30, 30, 50))  # Dark blue background
            
            if self.state == MAIN_MENU:
                self.draw_main_menu()
            elif self.state == CHARACTER_SELECT:
                self.draw_character_select()
            elif self.state == TOURNAMENT:
                self.draw_tournament()
            elif self.state == FIGHT:
                self.draw_fight()
            elif self.state == AD_SCREEN:
                self.draw_ad_screen()
            elif self.state == RESULTS:
                self.draw_results()
            elif self.state == WITHDRAW:
                self.draw_withdraw()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def draw_main_menu(self):
        # Title
        title = title_font.render("VIKING ARENA", True, GOLD)
        subtitle = large_font.render("Tournament of Valor", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 130))
        
        # Stats
        cash_text = medium_font.render(f"Cash: ${self.player_cash:.2f}", True, GREEN)
        free_text = medium_font.render(f"Free Games: {self.free_games}", True, BLUE)
        ads_text = small_font.render(f"Ads Watched: {self.total_ads_watched} (Sets: {self.ad_set_count})", True, WHITE)
        revenue_text = small_font.render(f"Owner Revenue: ${self.owner_revenue:.2f}", True, GOLD)
        
        screen.blit(cash_text, (50, 200))
        screen.blit(free_text, (50, 250))
        screen.blit(ads_text, (50, 300))
        screen.blit(revenue_text, (50, 330))
        
        # Tournament info
        tourney_text = medium_font.render("Monthly Tournament", True, WHITE)
        fee_text = medium_font.render(f"Entry Fee: ${self.tournament.entry_fee if self.tournament else 10}", True, WHITE)
        prize_text = medium_font.render(f"Prize Pool: ${self.tournament.prize_pool if self.tournament else 80}", True, GOLD)
        
        screen.blit(tourney_text, (SCREEN_WIDTH//2 - tourney_text.get_width()//2, 400))
        screen.blit(fee_text, (SCREEN_WIDTH//2 - fee_text.get_width()//2, 450))
        screen.blit(prize_text, (SCREEN_WIDTH//2 - prize_text.get_width()//2, 500))
        
        # Menu options
        pygame.draw.rect(screen, DARK_RED, (SCREEN_WIDTH//2 - 150, 550, 300, 50), border_radius=10)
        option1 = medium_font.render("1. Join Tournament", True, WHITE)
        screen.blit(option1, (SCREEN_WIDTH//2 - option1.get_width()//2, 560))
        
        pygame.draw.rect(screen, DARK_RED, (SCREEN_WIDTH//2 - 150, 610, 300, 50), border_radius=10)
        option2 = medium_font.render("2. Watch Ads (Get 3 Free Games)", True, WHITE)
        screen.blit(option2, (SCREEN_WIDTH//2 - option2.get_width()//2, 620))
        
        # Additional options
        pygame.draw.rect(screen, DARK_RED, (SCREEN_WIDTH - 250, 20, 230, 40), border_radius=5)
        withdraw_opt = small_font.render("3. Withdraw Cash", True, WHITE)
        screen.blit(withdraw_opt, (SCREEN_WIDTH - 240, 28))
        
        pygame.draw.rect(screen, DARK_RED, (SCREEN_WIDTH - 250, 70, 230, 40), border_radius=5)
        quit_opt = small_font.render("4. Quit Game", True, WHITE)
        screen.blit(quit_opt, (SCREEN_WIDTH - 240, 78))
        
        # Help text
        help_text = small_font.render("Press ESC to exit current screen", True, GRAY)
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 40))
    
    def draw_character_select(self):
        # Title
        title = large_font.render("SELECT YOUR FIGHTER", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Player info
        player_text = medium_font.render(f"Player: {self.player_name}", True, RED)
        screen.blit(player_text, (SCREEN_WIDTH//2 - player_text.get_width()//2, 120))
        
        # Weapon selection
        weapon_text = medium_font.render("Choose Your Weapon:", True, WHITE)
        screen.blit(weapon_text, (SCREEN_WIDTH//2 - weapon_text.get_width()//2, 180))
        
        # Draw weapons
        y_pos = 250
        for i, weapon in enumerate(WEAPONS):
            pygame.draw.rect(screen, (50, 50, 70), (SCREEN_WIDTH//2 - 150, y_pos, 300, 80), border_radius=10)
            name_text = medium_font.render(weapon["name"], True, GOLD)
            stats_text = small_font.render(f"Damage: {weapon['damage']} | Speed: {weapon['speed']} | Range: {weapon['range']}", True, WHITE)
            
            screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, y_pos + 10))
            screen.blit(stats_text, (SCREEN_WIDTH//2 - stats_text.get_width()//2, y_pos + 50))
            screen.blit(weapon["img"], (SCREEN_WIDTH//2 - 170, y_pos + 10))
            
            y_pos += 100
        
        # Start button
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 100, y_pos, 200, 50), border_radius=10)
        start_text = medium_font.render("START TOURNAMENT", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, y_pos + 10))
        
        # Help text
        help_text = medium_font.render("Press ENTER to start tournament", True, GRAY)
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 100))
        
        help_text2 = small_font.render("ESC to return to main menu", True, GRAY)
        screen.blit(help_text2, (SCREEN_WIDTH//2 - help_text2.get_width()//2, SCREEN_HEIGHT - 50))
    
    def draw_tournament(self):
        # Title
        title = large_font.render("TOURNAMENT BRACKET", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Round labels
        round_labels = ["Quarter-Finals", "Semi-Finals", "Finals"]
        
        # Draw bracket
        bracket_width = SCREEN_WIDTH - 100
        bracket_height = SCREEN_HEIGHT - 150
        start_x = 50
        start_y = 80
        
        # Draw rounds
        round_width = bracket_width // 3
        for round_idx in range(3):
            # Round label
            round_text = medium_font.render(round_labels[round_idx], True, WHITE)
            screen.blit(round_text, (start_x + round_idx * round_width + round_width//2 - round_text.get_width()//2, start_y - 40))
            
            # Matches in this round
            match_height = bracket_height / 4
            for match_idx in range(4 // (2 ** round_idx)):
                y_pos = start_y + match_idx * match_height * (2 ** round_idx) + match_height * (2 ** round_idx - 1) / 2
                
                # Draw match slot
                pygame.draw.rect(screen, (40, 40, 60), 
                                (start_x + round_idx * round_width, y_pos - 20, round_width - 20, 40), 
                                border_radius=5)
                
                # Draw fighter names if available
                if round_idx < len(self.tournament.rounds) and match_idx < len(self.tournament.rounds[round_idx]):
                    fighter1, fighter2 = self.tournament.rounds[round_idx][match_idx]
                    
                    # Fighter 1
                    f1_color = RED if fighter1.is_player else WHITE
                    f1_text = small_font.render(fighter1.name, True, f1_color)
                    screen.blit(f1_text, (start_x + round_idx * round_width + 10, y_pos - 15))
                    
                    # Fighter 2
                    f2_color = RED if fighter2.is_player else WHITE
                    f2_text = small_font.render(fighter2.name, True, f2_color)
                    screen.blit(f2_text, (start_x + round_idx * round_width + 10, y_pos + 5))
                    
                    # Winner indicator
                    if not fighter1.alive or not fighter2.alive:
                        winner = fighter1 if fighter1.alive else fighter2
                        win_text = small_font.render("WINNER" if winner.alive else "DEAD", True, GREEN if winner.alive else RED)
                        screen.blit(win_text, (start_x + round_idx * round_width + round_width - 90, y_pos - 5))
        
        # Current fight indicator
        if self.tournament.active_fight:
            fight_text = medium_font.render("FIGHT IN PROGRESS", True, RED)
            screen.blit(fight_text, (SCREEN_WIDTH//2 - fight_text.get_width()//2, SCREEN_HEIGHT - 100))
        
        # Start fight button
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 60, 200, 40), border_radius=10)
        fight_text = medium_font.render("START FIGHT", True, WHITE)
        screen.blit(fight_text, (SCREEN_WIDTH//2 - fight_text.get_width()//2, SCREEN_HEIGHT - 55))
        
        # Help text
        help_text = small_font.render("Press SPACE to start next fight", True, GRAY)
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 120))
    
    def draw_fight(self):
        # Background
        pygame.draw.rect(screen, (20, 60, 30), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))  # Sky
        pygame.draw.rect(screen, (100, 70, 40), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))  # Ground
        
        # Draw arena details
        pygame.draw.circle(screen, (150, 150, 150), (SCREEN_WIDTH//2, SCREEN_HEIGHT - GROUND_HEIGHT//2), 200, 5)
        
        # Draw fighters
        if self.tournament.active_fight:
            fighter1, fighter2 = self.tournament.active_fight
            fighter1.draw(screen)
            fighter2.draw(screen)
            
            # Position fighters
            fighter1.x = SCREEN_WIDTH//4 - 40
            fighter2.x = SCREEN_WIDTH*3//4 - 40
            
            # Ensure fighters don't go off screen
            fighter1.x = max(50, min(fighter1.x, SCREEN_WIDTH//2 - 100))
            fighter2.x = max(SCREEN_WIDTH//2 + 50, min(fighter2.x, SCREEN_WIDTH - 150))
        
        # Controls info for player
        if self.tournament.active_fight[0].is_player or self.tournament.active_fight[1].is_player:
            controls_text = small_font.render("Player Controls: Arrow Keys to move, A to attack", True, WHITE)
            screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, 20))
        
        # Fight status
        if not self.tournament.active_fight[0].alive:
            status_text = large_font.render(f"{self.tournament.active_fight[1].name} WINS!", True, GREEN)
            screen.blit(status_text, (SCREEN_WIDTH//2 - status_text.get_width()//2, 60))
        elif not self.tournament.active_fight[1].alive:
            status_text = large_font.render(f"{self.tournament.active_fight[0].name} WINS!", True, GREEN)
            screen.blit(status_text, (SCREEN_WIDTH//2 - status_text.get_width()//2, 60))
    
    def draw_ad_screen(self):
        # Title
        title = large_font.render("HIGH VALUE ADVERTISEMENT", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # Ad display
        pygame.draw.rect(screen, (20, 20, 40), (50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200))
        screen.blit(ad_img, (50, 100))
        
        # Ad info
        cpm = random.randint(100, 2200)
        info_text = medium_font.render(f"CPM: ${cpm} | eCPM: ${cpm}", True, GREEN)
        screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, SCREEN_HEIGHT - 180))
        
        # Timer
        time_left = self.ad_timer // 60 + 1
        timer_text = large_font.render(f"Ad ends in: {time_left}", True, RED)
        screen.blit(timer_text, (SCREEN_WIDTH//2 - timer_text.get_width()//2, SCREEN_HEIGHT - 120))
        
        # Reward info
        reward_text = medium_font.render("After 3 ads, you'll receive 3 free tournament entries", True, BLUE)
        screen.blit(reward_text, (SCREEN_WIDTH//2 - reward_text.get_width()//2, SCREEN_HEIGHT - 70))
    
    def draw_results(self):
        # Background
        pygame.draw.rect(screen, (30, 20, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Title
        title = large_font.render("TOURNAMENT RESULTS", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Result text
        result_text = large_font.render(self.tournament_result, True, GREEN if "You won" in self.tournament_result else RED)
        screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 150))
        
        # Game result (for withdrawals)
        if self.game_result:
            game_text = medium_font.render(self.game_result, True, BLUE)
            screen.blit(game_text, (SCREEN_WIDTH//2 - game_text.get_width()//2, 220))
        
        # Prize info
        prize_text = medium_font.render(f"Prize Pool: ${self.tournament.prize_pool}", True, GOLD)
        screen.blit(prize_text, (SCREEN_WIDTH//2 - prize_text.get_width()//2, 300))
        
        # Player cash
        cash_text = medium_font.render(f"Your Cash: ${self.player_cash:.2f}", True, GREEN)
        screen.blit(cash_text, (SCREEN_WIDTH//2 - cash_text.get_width()//2, 350))
        
        # Continue button
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 100, 450, 200, 50), border_radius=10)
        continue_text = medium_font.render("CONTINUE", True, WHITE)
        screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 460))
        
        # Help text
        help_text = small_font.render("Press ENTER to return to main menu", True, GRAY)
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 50))
    
    def draw_withdraw(self):
        # Title
        title = large_font.render("WITHDRAW EARNINGS", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Player cash
        cash_text = large_font.render(f"Available: ${self.player_cash:.2f}", True, GREEN)
        screen.blit(cash_text, (SCREEN_WIDTH//2 - cash_text.get_width()//2, 150))
        
        # Max withdrawal
        max_withdraw = min(2000, self.player_cash)
        max_text = medium_font.render(f"Max Withdrawal: ${max_withdraw:.2f}", True, WHITE)
        screen.blit(max_text, (SCREEN_WIDTH//2 - max_text.get_width()//2, 220))
        
        # Withdraw button
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 150, 300, 300, 80), border_radius=10)
        withdraw_text = large_font.render("WITHDRAW MAX", True, WHITE)
        screen.blit(withdraw_text, (SCREEN_WIDTH//2 - withdraw_text.get_width()//2, 320))
        
        # PayPal info
        paypal_text = medium_font.render("Funds will be sent to your PayPal account", True, BLUE)
        screen.blit(paypal_text, (SCREEN_WIDTH//2 - paypal_text.get_width()//2, 420))
        
        # Owner revenue
        revenue_text = medium_font.render(f"Owner Revenue: ${self.owner_revenue:.2f}", True, GOLD)
        screen.blit(revenue_text, (SCREEN_WIDTH//2 - revenue_text.get_width()//2, 480))
        
        # Help text
        help_text = small_font.render("Press ENTER to withdraw max amount ($2000 limit)", True, GRAY)
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 100))
        
        help_text2 = small_font.render("ESC to return to main menu", True, GRAY)
        screen.blit(help_text2, (SCREEN_WIDTH//2 - help_text2.get_width()//2, SCREEN_HEIGHT - 50))

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
