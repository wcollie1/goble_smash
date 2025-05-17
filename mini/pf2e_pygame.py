import pygame
import sys
import random
import os
import math
import logging
from datetime import datetime
from typing import List, Tuple

# Set up logging
log_file = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Pygame
pygame.init()
pygame.font.init()

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        logging.debug(f"Using PyInstaller base path: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        logging.debug(f"Using development base path: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    logging.debug(f"Full resource path: {full_path}")
    return full_path

# Log system information
logging.info(f"Python version: {sys.version}")
logging.info(f"Pygame version: {pygame.version.ver}")
logging.info(f"Working directory: {os.getcwd()}")
logging.info(f"System platform: {sys.platform}")

# Ensure Pygame has image support
if not pygame.image.get_extended():
    raise RuntimeError("Pygame extended image support not available")

# Create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')
    logging.info("Created images directory")

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 15
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (40, 40, 40)

# Character colors and sizes (kept for fallback)
FIGHTER_COLOR = (200, 50, 50)  # Red
ROGUE_COLOR = (50, 200, 50)    # Green
WIZARD_COLOR = (50, 50, 200)   # Blue
ENEMY_COLOR = (200, 50, 200)   # Purple
CHAR_SIZE = 80
SPRITE_SIZE = 100  # Size for character sprites
HEALTH_BAR_HEIGHT = 10
HEALTH_BAR_WIDTH = SPRITE_SIZE
PORTRAIT_SIZE = 100

# Image paths
IMAGE_PATHS = {
    'fighter': resource_path('images/fighter.webp'),
    'rogue': resource_path('images/rogue.webp'),
    'wizard': resource_path('images/wizard.webp'),
    'goblin': resource_path('images/goblin.webp'),
    'ogre': resource_path('images/ogre.webp'),
    'wyvern': resource_path('images/wyvern.webp')
}

# Font setup
FONT_SIZE = 20
FONT = pygame.font.SysFont('Arial', FONT_SIZE)
TITLE_FONT = pygame.font.SysFont('Arial', 32)

# UI Constants
SCROLLBAR_WIDTH = 15
SCROLL_SPEED = 20
MESSAGE_SPACING = 25  # Space between messages

# Special Effects Constants
EFFECT_DURATION = 30  # frames
MAGIC_MISSILE_COLOR = (100, 100, 255)  # Light blue
HEAL_COLOR = (100, 255, 100)  # Light green
SHIELD_COLOR = (200, 200, 255)  # Light blue
STRIKE_COLOR = (255, 100, 100)  # Light red
SNEAK_ATTACK_COLOR = (255, 255, 100)  # Yellow

def roll_dice(sides, num=1):
    rolls = [random.randint(1, sides) for _ in range(num)]
    return rolls, sum(rolls)

class Effect:
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], color: Tuple[int, int, int], 
                 duration: int = EFFECT_DURATION, effect_type: str = "basic"):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.duration = duration
        self.current_frame = 0
        self.effect_type = effect_type
        
        # Calculate trajectory
        self.dx = end_pos[0] - start_pos[0]
        self.dy = end_pos[1] - start_pos[1]
        
    def update(self) -> bool:
        """Update effect animation. Returns True if effect is still active."""
        self.current_frame += 1
        return self.current_frame < self.duration
        
    def draw(self, surface: pygame.Surface):
        progress = self.current_frame / self.duration
        
        if self.effect_type == "magic_missile":
            self._draw_magic_missile(surface, progress)
        elif self.effect_type == "heal":
            self._draw_heal(surface, progress)
        elif self.effect_type == "shield":
            self._draw_shield(surface, progress)
        elif self.effect_type == "strike":
            self._draw_strike(surface, progress)
        elif self.effect_type == "sneak_attack":
            self._draw_sneak_attack(surface, progress)
            
    def _draw_magic_missile(self, surface, progress):
        # Draw multiple magic missile particles
        current_x = self.start_pos[0] + self.dx * progress
        current_y = self.start_pos[1] + self.dy * progress
        
        for i in range(3):  # Draw 3 trailing particles
            trail_progress = max(0, progress - i * 0.1)
            trail_x = self.start_pos[0] + self.dx * trail_progress
            trail_y = self.start_pos[1] + self.dy * trail_progress
            
            size = max(2, 8 - i * 2)
            alpha = max(0, 255 - i * 60)
            
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), (size, size), size)
            surface.blit(particle_surface, (trail_x - size, trail_y - size))
            
    def _draw_heal(self, surface, progress):
        center_x = self.start_pos[0] + SPRITE_SIZE // 2
        center_y = self.start_pos[1] + SPRITE_SIZE // 2
        radius = SPRITE_SIZE // 2 * progress
        
        # Draw expanding healing circle
        circle_surface = pygame.Surface((SPRITE_SIZE * 2, SPRITE_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        pygame.draw.circle(circle_surface, (*self.color, alpha), (SPRITE_SIZE, SPRITE_SIZE), radius, 3)
        
        # Draw healing crosses
        for i in range(4):
            angle = math.pi * 2 * (i / 4) + progress * math.pi
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            cross_size = 10
            pygame.draw.line(surface, self.color, (x - cross_size, y), (x + cross_size, y), 2)
            pygame.draw.line(surface, self.color, (x, y - cross_size), (x, y + cross_size), 2)
            
        surface.blit(circle_surface, (center_x - SPRITE_SIZE, center_y - SPRITE_SIZE))
        
    def _draw_shield(self, surface, progress):
        center_x = self.start_pos[0] + SPRITE_SIZE // 2
        center_y = self.start_pos[1] + SPRITE_SIZE // 2
        
        # Draw rotating shield effect
        angle = progress * math.pi * 4
        radius = SPRITE_SIZE // 2 + 5
        
        shield_surface = pygame.Surface((SPRITE_SIZE * 2, SPRITE_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress * 0.5))
        
        # Draw multiple shield arcs
        for i in range(3):
            start_angle = angle + (i * math.pi * 2 / 3)
            end_angle = start_angle + math.pi / 2
            
            points = []
            for a in range(int(start_angle * 180/math.pi), int(end_angle * 180/math.pi)):
                rad = a * math.pi / 180
                x = SPRITE_SIZE + math.cos(rad) * radius
                y = SPRITE_SIZE + math.sin(rad) * radius
                points.append((x, y))
                
            if len(points) > 1:
                pygame.draw.lines(shield_surface, (*self.color, alpha), False, points, 3)
        
        surface.blit(shield_surface, (center_x - SPRITE_SIZE, center_y - SPRITE_SIZE))
        
    def _draw_strike(self, surface, progress):
        # Draw slashing effect
        start_x = self.start_pos[0] + SPRITE_SIZE // 2
        start_y = self.start_pos[1] + SPRITE_SIZE // 2
        end_x = self.end_pos[0] + SPRITE_SIZE // 2
        end_y = self.end_pos[1] + SPRITE_SIZE // 2
        
        # Create slash trail
        slash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw multiple slash lines
        for i in range(3):
            p = max(0, min(1, progress * 3 - i * 0.5))
            if 0 < p < 1:
                current_x = start_x + (end_x - start_x) * p
                current_y = start_y + (end_y - start_y) * p
                
                # Add some vertical variation to create a slash effect
                offset = math.sin(p * math.pi) * 20
                pygame.draw.line(slash_surface, (*self.color, alpha),
                               (current_x - 20, current_y + offset),
                               (current_x + 20, current_y - offset), 3)
        
        surface.blit(slash_surface, (0, 0))
        
    def _draw_sneak_attack(self, surface, progress):
        # Draw multiple striking effects for sneak attack
        center_x = self.end_pos[0] + SPRITE_SIZE // 2
        center_y = self.end_pos[1] + SPRITE_SIZE // 2
        
        # Create sparkle effect
        sparkle_surface = pygame.Surface((SPRITE_SIZE * 2, SPRITE_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        for i in range(8):
            angle = (i / 8) * math.pi * 2 + progress * math.pi * 4
            distance = SPRITE_SIZE//2 * (0.5 + math.sin(progress * math.pi * 2) * 0.5)
            
            x = SPRITE_SIZE + math.cos(angle) * distance
            y = SPRITE_SIZE + math.sin(angle) * distance
            
            size = max(2, 6 * (1 - progress))
            pygame.draw.circle(sparkle_surface, (*self.color, alpha), (x, y), size)
            
            # Draw lines from center to sparkles
            line_progress = max(0, min(1, progress * 3 - 0.5))
            if line_progress > 0:
                line_x = SPRITE_SIZE + math.cos(angle) * distance * line_progress
                line_y = SPRITE_SIZE + math.sin(angle) * distance * line_progress
                pygame.draw.line(sparkle_surface, (*self.color, alpha),
                               (SPRITE_SIZE, SPRITE_SIZE), (line_x, line_y), 2)
        
        surface.blit(sparkle_surface, (center_x - SPRITE_SIZE, center_y - SPRITE_SIZE))

class Character:
    def __init__(self, name, hp, ac, attack_bonus):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.base_ac = ac
        self.attack_bonus = attack_bonus
        self.potions = 3
        self.alive = True
        self.off_guard = False
        self.round_damage = 0
        self.damage_dealt = {}
        self.color = (200, 200, 200)  # Default color
        self.position = (0, 0)  # Will be set by the game
        self.is_enemy = False
        self.sprite = None
        self.sprite_path = None
        
    def load_sprite(self, sprite_path):
        """Load and scale the character's sprite."""
        logging.info(f"Attempting to load sprite: {sprite_path}")
        try:
            if os.path.exists(sprite_path):
                self.sprite_path = sprite_path
                logging.debug(f"Sprite path exists: {sprite_path}")
                try:
                    original_sprite = pygame.image.load(sprite_path).convert_alpha()
                    self.sprite = pygame.transform.scale(original_sprite, (SPRITE_SIZE, SPRITE_SIZE))
                    logging.info(f"Successfully loaded and scaled sprite: {sprite_path}")
                except pygame.error as e:
                    logging.error(f"Pygame error loading sprite {sprite_path}: {e}")
                    self.sprite = None
            else:
                logging.error(f"Sprite path does not exist: {sprite_path}")
                self.sprite = None
        except Exception as e:
            logging.error(f"Error loading sprite {sprite_path}: {e}")
            self.sprite = None

    def is_alive(self):
        return self.hp > 0

    def get_ac(self):
        return self.base_ac - 2 if self.off_guard else self.base_ac

    def take_damage(self, damage, attacker=None, game=None):
        self.hp = max(self.hp - damage, 0)
        msg = f"{self.name} takes {damage} damage! (HP: {self.hp}/{self.max_hp})"
        if game: game.add_message(msg)
        
        # Track damage from attacker if it's a Character instance
        if attacker and isinstance(attacker, Character):
            if attacker.name not in self.damage_dealt:
                self.damage_dealt[attacker.name] = 0
            self.damage_dealt[attacker.name] += damage
        
        if self.hp == 0:
            self.alive = False
            if game: game.add_message(f"{self.name} has fallen!")

    def heal(self, game=None):
        if self.potions > 0:
            if game: game.add_message(f"{self.name} uses a potion to heal 15 HP.")
            self.hp = min(self.hp + 15, self.max_hp)
            self.potions -= 1
            if game: game.add_message(f"HP after healing: {self.hp}/{self.max_hp} | Potions left: {self.potions}")
            return 1
        else:
            if game: game.add_message("No potions left!")
            return 0

    def attack(self, target, game=None, dice=(1, 8), bonus_damage=0, sneak_attack=False):
        try:
            logging.info(f"{self.name} attacks {target.name} with dice {dice}")
            
            roll = random.randint(1, 20)
            total = roll + self.attack_bonus
            target_ac = target.get_ac()
            
            if game:
                game.add_message(f"{self.name} rolls to hit: d20({roll}) + ATK({self.attack_bonus}) = {total} vs AC {target_ac}")
                # Add attack effect
                start_pos = self.position
                end_pos = target.position
                if sneak_attack:
                    game.add_effect(Effect(start_pos, end_pos, SNEAK_ATTACK_COLOR, effect_type="sneak_attack"))
                else:
                    game.add_effect(Effect(start_pos, end_pos, STRIKE_COLOR, effect_type="strike"))

            if roll == 1:
                if game:
                    game.add_message("Critical Miss!")
                return 1, False
            
            # Calculate damage
            dice_num, dice_sides = dice
            if roll == 20 or total >= target_ac + 10:
                if game:
                    game.add_message("Critical Hit!")
                rolls, dmg = roll_dice(dice_sides, dice_num * 2)
                if game:
                    game.add_message(f"Critical damage rolls: {rolls}")
            elif total >= target_ac:
                if game:
                    game.add_message("Hit!")
                rolls, dmg = roll_dice(dice_sides, dice_num)
                if game:
                    game.add_message(f"Damage rolls: {rolls}")
            else:
                if game:
                    game.add_message("Miss!")
                return 1, False

            if sneak_attack:
                sa_roll, sa_dmg = roll_dice(6)
                dmg += sa_dmg
                if game:
                    game.add_message(f"Sneak Attack! Extra d6: {sa_roll} = +{sa_dmg}")

            dmg += bonus_damage
            if game:
                game.add_message(f"Damage Total: {dmg}")
            
            target.take_damage(dmg, self, game)
            return 1, True
            
        except Exception as e:
            logging.error(f"Error in attack method: {e}")
            if game:
                game.add_message(f"Error processing attack: {str(e)}")
            return 1, False

    def draw(self, surface):
        if not self.alive:
            return

        x, y = self.position
        
        # Draw character sprite or fallback shape
        if self.sprite:
            surface.blit(self.sprite, (x, y))
        else:
            if self.is_enemy:
                # Draw enemy as diamond (fallback)
                points = [
                    (x + SPRITE_SIZE//2, y),  # Top
                    (x + SPRITE_SIZE, y + SPRITE_SIZE//2),  # Right
                    (x + SPRITE_SIZE//2, y + SPRITE_SIZE),  # Bottom
                    (x, y + SPRITE_SIZE//2)  # Left
                ]
                pygame.draw.polygon(surface, self.color, points)
                pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            else:
                # Draw hero as circle (fallback)
                pygame.draw.circle(surface, self.color, (x + SPRITE_SIZE//2, y + SPRITE_SIZE//2), SPRITE_SIZE//2)
                pygame.draw.circle(surface, (255, 255, 255), (x + SPRITE_SIZE//2, y + SPRITE_SIZE//2), SPRITE_SIZE//2, 2)

        # Draw health bar
        health_percent = self.hp / self.max_hp
        bar_width = HEALTH_BAR_WIDTH * health_percent
        
        # Health bar background
        pygame.draw.rect(surface, (100, 0, 0), 
                        (x, y + SPRITE_SIZE + 5, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        # Health bar fill
        if health_percent > 0:
            pygame.draw.rect(surface, (0, 255, 0), 
                           (x, y + SPRITE_SIZE + 5, bar_width, HEALTH_BAR_HEIGHT))

        # Draw name and HP
        name_text = FONT.render(f"{self.name}", True, TEXT_COLOR)
        hp_text = FONT.render(f"{self.hp}/{self.max_hp}", True, TEXT_COLOR)
        surface.blit(name_text, (x, y + SPRITE_SIZE + 20))
        surface.blit(hp_text, (x, y + SPRITE_SIZE + 40))

class Fighter(Character):
    def __init__(self, name):
        super().__init__(name, hp=50, ac=18, attack_bonus=9)
        self.color = FIGHTER_COLOR
        self.load_sprite(IMAGE_PATHS['fighter'])
        
    def get_actions(self, enemy, game):
        actions = []
        # Only show Power Attack if we have 2 or more actions
        if game.actions_left >= 2:
            actions.append(("Power Attack (2 actions)", lambda: self.power_attack(enemy, game)))
        if game.actions_left >= 1:
            actions.append(("Strike (1 action)", lambda: self.attack(enemy, game, dice=(1, 10))))
        if game.actions_left >= 1:
            actions.append(("Heal (1 action)", lambda: self.heal(game)))
        return actions

    def power_attack(self, enemy, game):
        """Execute a Power Attack action."""
        try:
            logging.info(f"{self.name} attempts Power Attack with {game.actions_left} actions remaining")
            
            # Double check we have enough actions
            if game.actions_left < 2:
                game.add_message("Not enough actions for Power Attack!")
                return 0
                
            game.add_message(f"{self.name} uses Power Attack!")
            attack_result = self.attack(enemy, game, dice=(2, 10))
            
            # Power Attack always uses 2 actions, regardless of hit or miss
            logging.info(f"Power Attack completed. Attack result: {attack_result}. Using 2 actions.")
            return 2
            
        except Exception as e:
            logging.error(f"Error in Power Attack: {e}")
            game.add_message("Error executing Power Attack!")
            return 0

class AIFighter(Fighter):
    def take_turn(self, enemy, game):
        actions = game.actions_left
        while actions > 0 and enemy.is_alive():
            if actions >= 2:
                logging.debug(f"AI Fighter attempting Power Attack with {actions} actions")
                used = self.power_attack(enemy, game)
                # Handle tuple return if present
                actions -= used if not isinstance(used, tuple) else used[0]
                logging.debug(f"AI Fighter has {actions} actions remaining after Power Attack")
            elif actions == 1:
                attack_result = self.attack(enemy, game, dice=(1, 10))
                actions -= attack_result[0] if isinstance(attack_result, tuple) else 1
        return 0

class Rogue(Character):
    def __init__(self, name):
        super().__init__(name, hp=38, ac=17, attack_bonus=8)
        self.color = ROGUE_COLOR
        self.load_sprite(IMAGE_PATHS['rogue'])

    def get_actions(self, enemy, game):
        actions = []
        if game.actions_left >= 1:
            actions.append(("Strike (1 action)", lambda: self.strike(enemy, game)))
        if game.actions_left >= 2:
            actions.append(("Twin Feint (2 actions)", lambda: self.twin_feint(enemy, game)))
        if game.actions_left >= 1:
            actions.append(("Heal (1 action)", lambda: self.heal(game)))
        return actions

    def strike(self, enemy, game):
        sneak = enemy.off_guard
        used, hit = self.attack(enemy, game, dice=(1, 6), sneak_attack=sneak)
        if hit and random.random() < 0.5:
            enemy.off_guard = True
            game.add_message(f"{enemy.name} is now Off-Guard until their next turn!")
        return used

    def twin_feint(self, enemy, game):
        game.add_message(f"{self.name} uses Twin Feint!")
        used1, hit1 = self.attack(enemy, game, dice=(1, 6))
        enemy.off_guard = True
        used2, hit2 = self.attack(enemy, game, dice=(1, 6), sneak_attack=True)
        enemy.off_guard = False
        return 2

class AIRogue(Rogue):
    def take_turn(self, enemy, game):
        actions = game.actions_left
        while actions > 0 and enemy.is_alive():
            if not enemy.off_guard and actions >= 1:
                feint_roll = random.randint(1, 20) + self.attack_bonus
                will_dc = 10 + enemy.attack_bonus
                game.add_message(f"{self.name} attempts to Feint! d20 + Deception ({self.attack_bonus}) = {feint_roll} vs DC {will_dc}")
                if feint_roll >= will_dc:
                    game.add_message(f"{self.name} successfully feints! {enemy.name} is now Off-Guard.")
                    enemy.off_guard = True
                else:
                    game.add_message("Feint failed.")
                actions -= 1
            else:
                sneak = enemy.off_guard
                used, hit = self.attack(enemy, game, dice=(1, 6), sneak_attack=sneak)
                actions -= used
        return 0

class Wizard(Character):
    def __init__(self, name):
        super().__init__(name, hp=32, ac=16, attack_bonus=6)
        self.color = WIZARD_COLOR
        self.shield_up = False
        self.load_sprite(IMAGE_PATHS['wizard'])

    def get_actions(self, enemy, game):
        actions = []
        if game.actions_left >= 1:
            actions.append(("Arcane Blast (1 action)", lambda: self.arcane_blast(enemy, game)))
        if game.actions_left >= 1:
            for i in range(1, min(game.actions_left + 1, 4)):
                actions.append((f"Magic Missile ({i} action{'s' if i > 1 else ''})", lambda i=i: self.magic_missile(enemy, game, i)))
        if game.actions_left >= 1 and not self.shield_up:
            actions.append(("Shield (1 action)", lambda: self.cast_shield(game)))
        if game.actions_left >= 1:
            actions.append(("Heal (1 action)", lambda: self.heal(game)))
        return actions

    def arcane_blast(self, enemy, game):
        used, _ = self.attack(enemy, game, dice=(2, 4))
        if self.shield_up:
            game.add_message("Shield fades.")
            self.base_ac -= 2
            self.shield_up = False
        return used

    def magic_missile(self, enemy, game, action_count=1):
        if game:
            start_pos = self.position
            end_pos = enemy.position
            game.add_effect(Effect(start_pos, end_pos, MAGIC_MISSILE_COLOR, effect_type="magic_missile"))
        
        count = action_count
        game.add_message(f"{self.name} uses {count} action{'s' if count > 1 else ''} to cast Magic Missile!")
        for i in range(count):
            roll, dmg = roll_dice(4)
            force_dmg = dmg + 1
            game.add_message(f"Magic Missile #{i+1}! Roll: {roll} + 1 = {force_dmg} force damage.")
            enemy.take_damage(force_dmg, self, game)  # Pass self as the attacker
        if self.shield_up:
            game.add_message("Shield fades.")
            self.base_ac -= 2
            self.shield_up = False
        return count

    def cast_shield(self, game):
        if game:
            game.add_effect(Effect(self.position, self.position, SHIELD_COLOR, effect_type="shield"))
        
        game.add_message(f"{self.name} casts Shield! +2 AC until next turn.")
        self.base_ac += 2
        self.shield_up = True
        return 1

class AIWizard(Wizard):
    def take_turn(self, enemy, game):
        actions = game.actions_left
        while actions > 0 and enemy.is_alive():
            if not self.shield_up:
                game.add_message(f"{self.name} casts Shield!")
                self.base_ac += 2
                self.shield_up = True
                actions -= 1
            else:
                _, _ = self.attack(enemy, game, dice=(2, 4))
                actions -= 1
                if self.shield_up:
                    self.base_ac -= 2
                    self.shield_up = False
        return 0

class Enemy(Character):
    def __init__(self, name, hp, ac, attack_bonus, damage_dice=(1, 8)):
        super().__init__(name, hp, ac, attack_bonus)
        self.damage_dice = damage_dice
        self.color = ENEMY_COLOR
        self.is_enemy = True
        
        # Load appropriate sprite based on enemy type
        if name == "Goblin":
            self.load_sprite(IMAGE_PATHS['goblin'])
        elif name == "Ogre":
            self.load_sprite(IMAGE_PATHS['ogre'])
        elif name == "Wyvern":
            self.load_sprite(IMAGE_PATHS['wyvern'])

    def choose_target(self, party, game):
        # Filter out dead party members
        valid_targets = [member for member in party if member.is_alive()]
        if not valid_targets:
            return None

        # Find who dealt the most damage to this enemy
        max_damage_dealer = None
        max_damage = -1
        for member in valid_targets:
            damage_dealt = self.damage_dealt.get(member.name, 0)
            if damage_dealt > max_damage:
                max_damage = damage_dealt
                max_damage_dealer = member

        # If someone has damaged this enemy, target them
        if max_damage_dealer and max_damage > 0:
            game.add_message(f"{self.name} focuses on {max_damage_dealer.name} who dealt {max_damage} damage!")
            return max_damage_dealer

        # Otherwise, target the party member with the most current HP
        target = max(valid_targets, key=lambda x: x.hp)
        game.add_message(f"{self.name} targets {target.name} who has the most health!")
        return target

    def take_turn(self, party, game):
        actions = 3
        game.add_message(f"\n{self.name} takes its turn!")
        
        while actions > 0:
            target = self.choose_target(party, game)
            if not target or not target.is_alive():
                break
                
            used, _ = self.attack(target, game, dice=self.damage_dice)
            actions -= used
            
        self.off_guard = False
        return 0

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2)
        
        text_surface = FONT.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.action:
                return self.action()
        return None

class ScrollBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.slider_rect = pygame.Rect(x, y, width, 50)  # Initial slider size
        self.dragging = False
        self.drag_start = 0
        self.scroll_pos = 0
        self.total_content_height = 0
        self.visible_height = height

    def update_content_height(self, content_height):
        self.total_content_height = content_height
        # Calculate slider height based on content
        visible_ratio = min(1.0, self.visible_height / max(1, self.total_content_height))
        self.slider_rect.height = max(20, int(self.rect.height * visible_ratio))
        # Adjust scroll position if needed
        self.scroll_pos = min(self.scroll_pos, self.total_content_height - self.visible_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.slider_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_start = event.pos[1] - self.slider_rect.y
            elif event.button == 4:  # Mouse wheel up
                self.scroll_pos = max(0, self.scroll_pos - SCROLL_SPEED)
            elif event.button == 5:  # Mouse wheel down
                self.scroll_pos = min(
                    max(0, self.total_content_height - self.visible_height),
                    self.scroll_pos + SCROLL_SPEED
                )
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.drag_start
            # Constrain slider movement
            new_y = max(self.rect.y, min(self.rect.bottom - self.slider_rect.height, new_y))
            # Calculate scroll position based on slider position
            scroll_ratio = (new_y - self.rect.y) / (self.rect.height - self.slider_rect.height)
            self.scroll_pos = int(scroll_ratio * (self.total_content_height - self.visible_height))
            self.slider_rect.y = new_y

    def draw(self, surface):
        # Draw scrollbar background
        pygame.draw.rect(surface, (60, 60, 60), self.rect)
        # Draw slider
        pygame.draw.rect(surface, (100, 100, 100), self.slider_rect)
        pygame.draw.rect(surface, (120, 120, 120), self.slider_rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PF2E Autobattler")
        
        self.clock = pygame.time.Clock()
        self.messages = []
        self.buttons = []
        self.party = []
        self.enemies = []
        self.current_enemy = None
        self.current_member_idx = 0
        self.actions_left = 3
        self.state = "class_select"
        self.rest_phase = False
        
        # Define UI regions with more space
        self.message_area_height = WINDOW_HEIGHT - 250
        self.status_area_height = 100
        self.button_area_height = 130
        
        # Define combat area
        self.combat_area = pygame.Rect(20, 100, WINDOW_WIDTH - 40, 300)
        
        self.message_surface = pygame.Surface((WINDOW_WIDTH - 40, self.message_area_height))
        self.message_surface.fill(BACKGROUND_COLOR)
        
        # Define message log area
        self.log_area = pygame.Rect(20, 
                                  self.combat_area.bottom + 20,
                                  WINDOW_WIDTH - 60 - SCROLLBAR_WIDTH,
                                  WINDOW_HEIGHT - self.combat_area.bottom - self.button_area_height - self.status_area_height - 40)
        
        # Create scrollbar for message log
        self.scrollbar = ScrollBar(self.log_area.right + 10,
                                 self.log_area.y,
                                 SCROLLBAR_WIDTH,
                                 self.log_area.height)
        
        self.effects: List[Effect] = []  # Add this line to store active effects
        
        self.init_game()

    def add_message(self, message):
        self.messages.append(message)
        # Update scrollbar content height
        total_height = len(self.messages) * MESSAGE_SPACING
        self.scrollbar.update_content_height(total_height)
        # Auto-scroll to bottom when new message arrives
        if total_height > self.log_area.height:
            self.scrollbar.scroll_pos = total_height - self.log_area.height

    def create_buttons(self, actions):
        self.buttons.clear()
        
        # Calculate button dimensions based on number of actions
        num_buttons = len(actions)
        max_buttons_per_row = 4
        num_rows = (num_buttons + max_buttons_per_row - 1) // max_buttons_per_row
        
        # Calculate button width with more space between buttons
        width = (WINDOW_WIDTH - (BUTTON_MARGIN * (max_buttons_per_row + 1))) // max_buttons_per_row
        
        for i, (text, action) in enumerate(actions):
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row
            
            x = BUTTON_MARGIN + col * (width + BUTTON_MARGIN)
            y = WINDOW_HEIGHT - self.button_area_height + row * (BUTTON_HEIGHT + BUTTON_MARGIN) + BUTTON_MARGIN
            
            self.buttons.append(Button(x, y, width, BUTTON_HEIGHT, text, action))

    def init_game(self):
        self.messages = ["Choose your class:"]
        self.create_buttons([
            ("Fighter", lambda: self.choose_class("Fighter")),
            ("Rogue", lambda: self.choose_class("Rogue")),
            ("Wizard", lambda: self.choose_class("Wizard"))
        ])

    def position_characters(self):
        if not self.party or not self.current_enemy:
            return

        # Position party members on the left side
        party_spacing = WINDOW_WIDTH // (len(self.party) + 2)
        for i, member in enumerate(self.party):
            member.position = (party_spacing * (i + 1) - CHAR_SIZE//2, 
                             self.combat_area.centery - CHAR_SIZE//2)

        # Position enemy on the right side
        self.current_enemy.position = (WINDOW_WIDTH - party_spacing, 
                                     self.combat_area.centery - CHAR_SIZE//2)

    def choose_class(self, choice):
        if choice == "Fighter":
            player = Fighter("Valeros")
            self.party = [player, AIRogue("Merisiel"), AIWizard("Ezren")]
        elif choice == "Rogue":
            player = Rogue("Merisiel")
            self.party = [player, AIFighter("Valeros"), AIWizard("Ezren")]
        else:  # Wizard
            player = Wizard("Ezren")
            self.party = [player, AIFighter("Valeros"), AIRogue("Merisiel")]

        self.enemies = [
            Enemy("Goblin", hp=20, ac=15, attack_bonus=5),
            Enemy("Ogre", hp=40, ac=17, attack_bonus=7, damage_dice=(2, 6)),
            Enemy("Wyvern", hp=55, ac=19, attack_bonus=9, damage_dice=(2, 8))
        ]
        
        self.start_battle()

    def start_battle(self):
        if not self.enemies or not any(m.is_alive() for m in self.party):
            self.end_battle()
            return

        self.current_enemy = self.enemies.pop(0)
        self.add_message(f"\n--- A wild {self.current_enemy.name} appears! ---")
        self.current_member_idx = 0
        self.position_characters()
        self.next_turn()

    def next_turn(self):
        if not self.current_enemy.is_alive():
            if all(m.is_alive() for m in self.party) and self.enemies:
                self.rest_phase = True
                self.add_message("\n--- Rest Phase ---")
                self.create_buttons([
                    ("Use Potion", lambda: self.rest_action(True)),
                    ("Continue", lambda: self.rest_action(False))
                ])
            else:
                self.start_battle()
            return

        if self.current_member_idx >= len(self.party):
            # Enemy's turn
            if self.party[0].is_alive():
                self.current_enemy.take_turn(self.party, self)  # Pass entire party instead of just player
                self.current_member_idx = 0
                self.next_turn()
            else:
                self.end_battle()
            return

        member = self.party[self.current_member_idx]
        if not member.is_alive():
            self.current_member_idx += 1
            self.next_turn()
            return

        self.actions_left = 3
        if self.current_member_idx == 0:
            # Player's turn
            self.create_buttons(member.get_actions(self.current_enemy, self))
        else:
            # AI turn
            member.take_turn(self.current_enemy, self)
            self.current_member_idx += 1
            self.next_turn()

    def rest_action(self, use_potion):
        if use_potion:
            self.party[0].heal(self)
        self.rest_phase = False
        self.start_battle()

    def end_battle(self):
        if any(m.is_alive() for m in self.party):
            self.add_message("\n🏆 Your party has defeated all foes!")
        else:
            self.add_message("\n💀 Your party was defeated...")
        
        self.create_buttons([
            ("Restart", self.init_game),
            ("Quit", pygame.quit)
        ])

    def handle_action_result(self, used):
        if used is not None:
            # If used is a tuple, extract the first value (actions used)
            if isinstance(used, tuple):
                actions_used = used[0]
            else:
                actions_used = used
                
            logging.debug(f"Handling action result: {actions_used} actions used, {self.actions_left} actions remaining")
            self.actions_left = max(0, self.actions_left - actions_used)  # Ensure we don't go negative
            logging.debug(f"Actions remaining after update: {self.actions_left}")
            
            if self.actions_left <= 0 or not self.current_enemy.is_alive():
                self.current_member_idx += 1
                self.next_turn()
            else:
                # Only show actions if we're still in the same turn
                if self.current_member_idx == 0:  # Player's turn
                    self.create_buttons(self.party[0].get_actions(self.current_enemy, self))

    def add_effect(self, effect: Effect):
        self.effects.append(effect)
        
    def update_effects(self):
        # Update and remove finished effects
        self.effects = [effect for effect in self.effects if effect.update()]

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw combat area background
        pygame.draw.rect(self.screen, (30, 30, 30), self.combat_area)
        pygame.draw.rect(self.screen, (50, 50, 50), self.combat_area, 2)

        # Draw characters
        if self.party and self.current_enemy:
            for member in self.party:
                member.draw(self.screen)
            self.current_enemy.draw(self.screen)
        
        # Draw message log area background
        pygame.draw.rect(self.screen, (30, 30, 30), self.log_area)
        pygame.draw.rect(self.screen, (50, 50, 50), self.log_area, 2)
        
        # Create a surface for the messages with clipping
        message_surface = pygame.Surface((self.log_area.width, self.log_area.height))
        message_surface.fill((30, 30, 30))
        
        # Draw messages on the surface
        y = -self.scrollbar.scroll_pos
        for message in self.messages:
            if y + MESSAGE_SPACING > 0:  # Only render messages that might be visible
                text_surface = FONT.render(message, True, TEXT_COLOR)
                message_surface.blit(text_surface, (5, y))
            y += MESSAGE_SPACING
            if y > self.log_area.height:  # Stop rendering if we're beyond visible area
                break
        
        # Draw the message surface to the screen
        self.screen.blit(message_surface, self.log_area)
        
        # Draw scrollbar
        self.scrollbar.draw(self.screen)

        # Draw status area
        if self.party and self.current_enemy:
            status_y = WINDOW_HEIGHT - self.button_area_height - self.status_area_height
            
            # Draw status background
            status_bg = pygame.Rect(0, status_y, WINDOW_WIDTH, self.status_area_height)
            pygame.draw.rect(self.screen, (30, 30, 30), status_bg)
            
            # Draw status text
            status_text = f"Actions: {self.actions_left} | "
            status_text += f"Potions: {self.party[0].potions}"
            status_surface = FONT.render(status_text, True, TEXT_COLOR)
            self.screen.blit(status_surface, (20, status_y + 20))

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

        # Draw all active effects
        for effect in self.effects:
            effect.draw(self.screen)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle scrollbar events
                self.scrollbar.handle_event(event)
                
                # Handle button events
                for button in self.buttons:
                    result = button.handle_event(event)
                    if result is not None:
                        self.handle_action_result(result)

            # Update effects
            self.update_effects()
            
            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run() 