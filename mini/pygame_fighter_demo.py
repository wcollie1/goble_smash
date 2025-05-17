import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1000, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PF2E Autobattler - Fighter with AI Party")

FONT = pygame.font.SysFont("arial", 20)
BIG_FONT = pygame.font.SysFont("arial", 32)

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
RED = (200, 50, 50)

clock = pygame.time.Clock()

def roll_dice(sides, num=1):
    return [random.randint(1, sides) for _ in range(num)]

class Character:
    def __init__(self, name, hp, ac, attack_bonus):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.attack_bonus = attack_bonus
        self.potions = 3
        self.actions = 3
        self.log = []

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        self.log.append(f"{self.name} takes {dmg} damage!")

class Fighter(Character):
    def __init__(self, name):
        super().__init__(name, 50, 18, 9)

    def strike(self, enemy):
        if self.actions < 1:
            self.log.append("Not enough actions.")
            return
        roll = random.randint(1, 20)
        total = roll + self.attack_bonus
        self.log.append(f"{self.name} rolls: d20({roll}) + {self.attack_bonus} = {total} vs AC {enemy.ac}")
        if total >= enemy.ac:
            dmg = sum(roll_dice(10))
            enemy.take_damage(dmg)
            self.log.append(f"Hit! {enemy.name} takes {dmg} damage.")
        else:
            self.log.append("Miss!")
        self.actions -= 1

    def power_attack(self, enemy):
        if self.actions < 2:
            self.log.append("Not enough actions.")
            return
        roll = random.randint(1, 20)
        total = roll + self.attack_bonus
        self.log.append(f"{self.name} Power Attack: d20({roll}) + {self.attack_bonus} = {total} vs AC {enemy.ac}")
        if total >= enemy.ac:
            dmg = sum(roll_dice(10, 2))
            enemy.take_damage(dmg)
            self.log.append(f"{enemy.name} takes {dmg} damage!")
        else:
            self.log.append("Miss!")
        self.actions -= 2

    def heal(self):
        if self.actions < 1 or self.potions <= 0:
            self.log.append("Cannot heal.")
            return
        self.hp = min(self.max_hp, self.hp + 15)
        self.potions -= 1
        self.actions -= 1
        self.log.append(f"{self.name} drinks a potion. Healed to {self.hp}/{self.max_hp} HP.")

class Rogue(Character):
    def __init__(self, name):
        super().__init__(name, 38, 17, 8)

    def twin_feint(self, enemy):
        if self.actions < 2:
            self.log.append("Not enough actions for Twin Feint.")
            return
        self.log.append(f"{self.name} uses Twin Feint!")
        roll1 = random.randint(1, 20)
        total1 = roll1 + self.attack_bonus
        if total1 >= enemy.ac:
            dmg = sum(roll_dice(6))
            enemy.take_damage(dmg)
            self.log.append(f"First attack hits: {dmg} damage.")
        else:
            self.log.append("First attack misses.")

        roll2 = random.randint(1, 20)
        total2 = roll2 + self.attack_bonus - 5
        if total2 >= enemy.ac - 2:  # Off-Guard
            dmg2 = sum(roll_dice(6)) + sum(roll_dice(6))  # Sneak Attack
            enemy.take_damage(dmg2)
            self.log.append(f"Second (Sneak) hits: {dmg2} damage.")
        else:
            self.log.append("Second attack misses.")
        self.actions -= 2

class Wizard(Character):
    def __init__(self, name):
        super().__init__(name, 32, 16, 6)
        self.shield_up = False

    def magic_missile(self, enemy, count):
        if self.actions < count:
            self.log.append("Not enough actions.")
            return
        for i in range(count):
            dmg = random.randint(1, 4) + 1
            enemy.take_damage(dmg)
            self.log.append(f"Magic Missile #{i+1}: {dmg} force damage.")
        self.actions -= count

class Enemy:
    def __init__(self, name, hp, ac):
        self.name = name
        self.hp = hp
        self.ac = ac

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

fighter = Fighter("Valeros")
rogue = Rogue("Merisiel")
wizard = Wizard("Ezren")
enemy = Enemy("Ogre", 45, 17)

buttons = {
    "strike": pygame.Rect(50, 560, 150, 40),
    "power": pygame.Rect(250, 560, 150, 40),
    "heal": pygame.Rect(450, 560, 150, 40),
    "reset": pygame.Rect(650, 560, 150, 40)
}

def draw_window():
    WIN.fill(GRAY)
    title = BIG_FONT.render("Fighter Turn - Choose Action", True, BLACK)
    WIN.blit(title, (WIDTH//2 - title.get_width()//2, 20))

    y_stat = 70
    for pc in [fighter, rogue, wizard]:
        color = BLACK if pc.is_alive() else RED
        stats = FONT.render(f"{pc.name} HP: {pc.hp}/{pc.max_hp} | Potions: {pc.potions} | Actions: {pc.actions}", True, color)
        WIN.blit(stats, (50, y_stat))
        y_stat += 30

    enemy_stats = FONT.render(f"{enemy.name} HP: {enemy.hp}", True, RED)
    WIN.blit(enemy_stats, (50, 170))

    for key, rect in buttons.items():
        pygame.draw.rect(WIN, BLACK, rect, 2)
        label = key.capitalize() if key != "power" else "Power Attack"
        btn_text = FONT.render(label, True, BLACK)
        WIN.blit(btn_text, (rect.x + 10, rect.y + 10))

    y = 220
    for log in fighter.log[-12:]:
        WIN.blit(FONT.render(log, True, BLACK), (50, y))
        y += 20

    pygame.display.update()

running = True
while running:
    clock.tick(30)
    draw_window()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if buttons["strike"].collidepoint(pos):
                fighter.strike(enemy)
            elif buttons["power"].collidepoint(pos):
                fighter.power_attack(enemy)
            elif buttons["heal"].collidepoint(pos):
                fighter.heal()
            elif buttons["reset"].collidepoint(pos):
                fighter.actions = 3
                rogue.actions = 3
                wizard.actions = 3
                fighter.log.append("Actions reset.")
                if rogue.is_alive():
                    rogue.twin_feint(enemy)
                if wizard.is_alive():
                    wizard.magic_missile(enemy, 3)

pygame.quit()
