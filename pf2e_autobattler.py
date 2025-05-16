import random
from typing import List

# === BASE CHARACTER ===
class Character:
    def __init__(self, name: str, hp: int, defense: int):
        self.name = name
        self._hp = hp
        self.max_hp = hp
        self.defense = defense
        self.alive = True
        self.potions = 3

    def get_hp(self) -> int:
        return self._hp

    def set_hp(self, new_hp: int):
        self._hp = min(max(0, new_hp), self.max_hp)
        if self._hp == 0:
            self.alive = False
            print(f"{self.name} has fallen!")

    def heal(self):
        if self.potions > 0:
            print(f"{self.name} uses a Healing Potion!")
            self.set_hp(self._hp + 15)
            self.potions -= 1
            print(f"{self.name} now has {self._hp} HP and {self.potions} potions left.")
        else:
            print("No potions left!")

    def take_damage(self, amount: int):
        damage = max(0, amount - self.defense)
        print(f"{self.name} takes {damage} damage.")
        self.set_hp(self._hp - damage)

    def take_turn(self, enemy: 'Character'):
        raise NotImplementedError()

# === PLAYER CLASSES ===

class Fighter(Character):
    def __init__(self, name: str):
        super().__init__(name, hp=40, defense=6)
        self.attack = 12

    def strike(self, enemy):
        print(f"{self.name} uses Strike!")
        enemy.take_damage(self.attack)

    def power_attack(self, enemy):
        damage = self.attack + random.randint(2, 6)
        print(f"{self.name} uses Power Attack!")
        enemy.take_damage(damage)

    def take_turn(self, enemy: Character):
        print("\nChoose your action:")
        print("1. Strike")
        print("2. Power Attack")
        print("3. Use Healing Potion")
        action = input("Enter 1, 2, or 3: ").strip()
        if action == "1":
            self.strike(enemy)
        elif action == "2":
            self.power_attack(enemy)
        elif action == "3":
            self.heal()
        else:
            print("Invalid input. Defaulting to Strike.")
            self.strike(enemy)

class Rogue(Character):
    def __init__(self, name: str):
        super().__init__(name, hp=28, defense=4)
        self.attack = 8

    def strike(self, enemy):
        print(f"{self.name} uses Strike!")
        enemy.take_damage(self.attack)

    def sneak_attack(self, enemy):
        crit = random.random() < 0.3
        damage = self.attack * 2 if crit else self.attack
        print(f"{self.name} uses Sneak Attack{' (CRIT!)' if crit else ''}!")
        enemy.take_damage(damage)

    def take_turn(self, enemy: Character):
        print("\nChoose your action:")
        print("1. Strike")
        print("2. Sneak Attack")
        print("3. Use Healing Potion")
        action = input("Enter 1, 2, or 3: ").strip()
        if action == "1":
            self.strike(enemy)
        elif action == "2":
            self.sneak_attack(enemy)
        elif action == "3":
            self.heal()
        else:
            print("Invalid input. Defaulting to Sneak Attack.")
            self.sneak_attack(enemy)

class Wizard(Character):
    def __init__(self, name: str):
        super().__init__(name, hp=22, defense=2)
        self.attack = 6
        self.shield_up = False

    def arcane_blast(self, enemy):
        damage = self.attack + random.randint(4, 10)
        print(f"{self.name} casts Arcane Blast!")
        enemy.take_damage(damage)

    def shield(self):
        if not self.shield_up:
            self.shield_up = True
            self.defense += 3
            print(f"{self.name} casts Shield! Defense increased to {self.defense}.")

    def take_turn(self, enemy: Character):
        print("\nChoose your action:")
        print("1. Arcane Blast")
        print("2. Shield")
        print("3. Use Healing Potion")
        action = input("Enter 1, 2, or 3: ").strip()
        if action == "1":
            self.arcane_blast(enemy)
        elif action == "2":
            self.shield()
        elif action == "3":
            self.heal()
        else:
            print("Invalid input. Defaulting to Arcane Blast.")
            self.arcane_blast(enemy)

        # Reset shield after blast
        if self.shield_up and action == "1":
            self.defense -= 3
            self.shield_up = False
            print(f"{self.name}'s Shield wears off. Defense returns to {self.defense}.")

# === ENEMIES ===

class Enemy(Character):
    def __init__(self, name: str, hp: int, attack: int, defense: int):
        super().__init__(name, hp, defense)
        self.attack = attack

    def attack_player(self, player: Character):
        damage = self.attack + random.randint(0, 4)
        print(f"{self.name} attacks {player.name}!")
        player.take_damage(damage)

    def take_turn(self, player: Character):
        self.attack_player(player)

# === GAME LOGIC ===

def battle(player: Character, enemy: Enemy):
    print(f"\n=== {player.name} vs {enemy.name} ===")
    round_num = 1
    while player.alive and enemy.alive:
        print(f"\n--- Round {round_num} ---")
        print(f"{player.name} HP: {player.get_hp()} | {enemy.name} HP: {enemy.get_hp()}")
        player.take_turn(enemy)
        if enemy.alive:
            enemy.take_turn(player)
        round_num += 1
    return player.alive

def rest_phase(player: Character):
    print("\nRest Phase: Do you want to heal?")
    if player.potions > 0:
        choice = input(f"Use a Healing Potion? ({player.potions} left) [y/n]: ").strip().lower()
        if choice == 'y':
            player.heal()
    else:
        print("No healing potions left.")

def start_game():
    print("Choose your class:\n1. Fighter\n2. Rogue\n3. Wizard")
    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        player = Fighter("Valeros")
    elif choice == "2":
        player = Rogue("Merisiel")
    elif choice == "3":
        player = Wizard("Ezren")
    else:
        print("Invalid choice. Defaulting to Fighter.")
        player = Fighter("Valeros")

    waves = [
        Enemy("Goblin", hp=20, attack=6, defense=2),
        Enemy("Ogre", hp=35, attack=10, defense=4),
        Enemy("Wyvern", hp=50, attack=12, defense=5)
    ]

    for enemy in waves:
        if not battle(player, enemy):
            print("\nGame Over!")
            return
        if enemy != waves[-1]:  # No rest after final wave
            rest_phase(player)

    print(f"\n{player.name} has triumphed over all enemies! Victory!")

if __name__ == "__main__":
    start_game()
