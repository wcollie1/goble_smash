import random

def roll_dice(sides, num=1):
    rolls = [random.randint(1, sides) for _ in range(num)]
    return rolls, sum(rolls)

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
        self.round_damage = 0  # Tracks damage dealt by this character in the round


    def is_alive(self):
        return self.hp > 0

    def get_ac(self):
        return self.base_ac - 2 if self.off_guard else self.base_ac

    def take_damage(self, damage):
        self.hp = max(self.hp - damage, 0)
        print(f"{self.name} takes {damage} damage! (HP: {self.hp}/{self.max_hp})")
        if self.hp == 0:
            self.alive = False
            print(f"{self.name} has fallen!")

    def heal(self):
        if self.potions > 0:
            print(f"{self.name} uses a potion to heal 15 HP.")
            self.hp = min(self.hp + 15, self.max_hp)
            self.potions -= 1
            print(f"HP after healing: {self.hp}/{self.max_hp} | Potions left: {self.potions}")
            return 1
        else:
            print("No potions left!")
            return 0

    def attack(self, target, dice=(1, 8), bonus_damage=0, sneak_attack=False):
        roll = random.randint(1, 20)
        total = roll + self.attack_bonus
        target_ac = target.get_ac()
        print(f"{self.name} rolls to hit: d20({roll}) + ATK({self.attack_bonus}) = {total} vs AC {target_ac}")

        if roll == 1:
            print("Critical Miss!")
            return 1, False
        elif roll == 20 or total >= target_ac + 10:
            print("Critical Hit!")
            dice_num, dice_sides = dice
            rolls, dmg = roll_dice(dice_sides, dice_num * 2)
        elif total >= target_ac:
            print("Hit!")
            dice_num, dice_sides = dice
            rolls, dmg = roll_dice(dice_sides, dice_num)
        else:
            print("Miss!")
            return 1, False

        if sneak_attack:
            sa_roll, sa_dmg = roll_dice(6)
            dmg += sa_dmg
            print(f"Sneak Attack! Extra d6: {sa_roll} = +{sa_dmg}")

        dmg += bonus_damage
        print(f"Damage Total: {dmg}")
        target.take_damage(dmg)
        return 1, dmg  # Always return number of actions used and damage dealt


    def take_turn(self, enemy):
        raise NotImplementedError()

class Fighter(Character):
    def __init__(self, name):
        super().__init__(name, hp=50, ac=18, attack_bonus=9)

    def take_turn(self, enemy):
        actions = 3
        while actions > 0 and enemy.is_alive():
            print(f"\n{self.name}'s HP: {self.hp}/{self.max_hp} | Potions: {self.potions}")
            print(f"{self.name}'s Actions Left: {actions}")
            print("1. Strike (1 action)\n2. Power Attack (2 actions)\n3. Heal (1 action)")
            choice = input("Choose action: ").strip()
            if choice == "1" and actions >= 1:
                used, _ = self.attack(enemy, dice=(1, 10))
                actions -= used
            elif choice == "2" and actions >= 2:
                print(f"{self.name} uses Power Attack!")
                _, _ = self.attack(enemy, dice=(2, 10))
                actions -= 2
            elif choice == "3" and actions >= 1:
                actions -= self.heal()
            else:
                print("Invalid or not enough actions.")

class AIFighter(Fighter):
    def take_turn(self, enemy):
        actions = 3
        print(f"\n{self.name} (AI Fighter) begins their turn.")
        while actions > 0 and enemy.is_alive():
            if actions >= 2:
                print(f"{self.name} uses Power Attack!")
                _, _ = self.attack(enemy, dice=(2, 10))
                actions -= 2
            elif actions == 1:
                _, _ = self.attack(enemy, dice=(1, 10))
                actions -= 1

class Rogue(Character):
    def __init__(self, name):
        super().__init__(name, hp=38, ac=17, attack_bonus=8)
        
    def take_turn(self, enemy):
        actions = 3
        while actions > 0 and enemy.is_alive():
            print(f"\n{self.name}'s HP: {self.hp}/{self.max_hp} | Potions: {self.potions}")
            print(f"{self.name}'s Actions Left: {actions}")
            print("1. Strike (1 action)\n2. Feint (1 action)\n3. Heal (1 action)")
            choice = input("Choose action: ").strip()
            if choice == "1" and actions >= 1:
                sneak = enemy.off_guard
                used, hit = self.attack(enemy, dice=(1, 6), sneak_attack=sneak)
                actions -= used
                if hit and random.random() < 0.5:
                    enemy.off_guard = True
                    print(f"{enemy.name} is now Off-Guard until their next turn!")
            elif choice == "2" and actions >= 1:
                feint_roll = random.randint(1, 20) + self.attack_bonus
                will_dc = 10 + enemy.attack_bonus
                print(f"{self.name} attempts to Feint! d20 + Deception ({self.attack_bonus}) = {feint_roll} vs DC {will_dc}")
                if feint_roll >= will_dc:
                    print(f"{self.name} successfully feints! {enemy.name} is now Off-Guard.")
                    enemy.off_guard = True
                else:
                    print("Feint failed.")
                actions -= 1
            elif choice == "3" and actions >= 1:
                actions -= self.heal()
            else:
                print("Invalid or not enough actions.")

class AIRogue(Rogue):
    def take_turn(self, enemy):
        actions = 3
        print(f"\n{self.name} (AI Rogue) begins their turn.")
        while actions > 0 and enemy.is_alive():
            if not enemy.off_guard and actions >= 1:
                feint_roll = random.randint(1, 20) + self.attack_bonus
                will_dc = 10 + enemy.attack_bonus
                print(f"{self.name} attempts to Feint! d20 + Deception ({self.attack_bonus}) = {feint_roll} vs DC {will_dc}")
                if feint_roll >= will_dc:
                    print(f"{self.name} successfully feints! {enemy.name} is now Off-Guard.")
                    enemy.off_guard = True
                else:
                    print("Feint failed.")
                actions -= 1
            else:
                sneak = enemy.off_guard
                used, hit = self.attack(enemy, dice=(1, 6), sneak_attack=sneak)
                actions -= used

class Wizard(Character):
    def __init__(self, name):
        super().__init__(name, hp=32, ac=16, attack_bonus=6)
        self.shield_up = False

    def take_turn(self, enemy):
        actions = 3
        while actions > 0 and enemy.is_alive():
            print(f"\n{self.name}'s HP: {self.hp}/{self.max_hp} | Potions: {self.potions}")
            print(f"{self.name}'s Actions Left: {actions}")
            print("1. Arcane Blast (1 action)\n2. Magic Missile (1 - 3 actions)\n3. Shield (1 action)\n4. Heal(1 action)")
            choice = input("Choose action: ").strip()
            if choice == "1" and actions >= 1:
                used, _ = self.attack(enemy, dice=(2, 4))
                actions -= used
                if self.shield_up:
                    print("Shield fades.")
                    self.base_ac -= 2
                    self.shield_up = False

            elif choice == "2":
                while True:
                    missile_count = input("How many actions to use for Magic Missile (1–3)? ").strip()
                    if missile_count in {"1", "2", "3"}:
                        missile_count = int(missile_count)
                        if missile_count > actions:
                            print("Not enough actions remaining.")
                            continue
                        break
                    else:
                        print("Invalid number.")
                for i in range(missile_count):
                    roll, dmg = roll_dice(4)
                    force_dmg = dmg + 1
                    print(f"{self.name} fires Magic Missile #{i+1}! Roll: {roll} + 1 = {force_dmg} force damage.")
                    enemy.take_damage(force_dmg)
                actions -= missile_count
                if self.shield_up:
                    print("Shield fades.")
                    self.base_ac -= 2
                    self.shield_up = False

            elif choice == "3" and actions >= 1 and not self.shield_up:
                print(f"{self.name} casts Shield! +2 AC until next turn.")
                self.base_ac += 2
                self.shield_up = True
                actions -= 1

            elif choice == "4" and actions >= 1:
                actions -= self.heal()

            else:
                print("Invalid or not enough actions.")


class AIWizard(Wizard):
    def take_turn(self, enemy):
        actions = 3
        print(f"\n{self.name} (AI Wizard) begins their turn.")
        while actions > 0 and enemy.is_alive():
            if not self.shield_up:
                print(f"{self.name} casts Shield!")
                self.base_ac += 2
                self.shield_up = True
                actions -= 1
            else:
                _, _ = self.attack(enemy, dice=(2, 4))
                actions -= 1
                if self.shield_up:
                    self.base_ac -= 2
                    self.shield_up = False

class Enemy(Character):
    def __init__(self, name, hp, ac, attack_bonus, damage_dice=(1, 8)):
        super().__init__(name, hp, ac, attack_bonus)
        self.damage_dice = damage_dice

    def take_turn(self, player):
        actions = 3
        print(f"\n{self.name} takes its turn!")
        while actions > 0 and player.is_alive():
            used, _ = self.attack(player, dice=self.damage_dice)
            actions -= used
        self.off_guard = False

def battle(party, enemies):
    for enemy in enemies:
        if not any(member.is_alive() for member in party):
            break
        print(f"\n--- A wild {enemy.name} appears! ---")
        while enemy.is_alive() and any(member.is_alive() for member in party):
            for member in party:
                if member.is_alive() and enemy.is_alive():  # ✅ check enemy status again before turn
                    member.take_turn(enemy)

            if enemy.is_alive():
                enemy.take_turn(party[0])  # Attacks the player by default
        if all(member.is_alive() for member in party) and enemy != enemies[-1]:
            print("\n--- Rest Phase ---")
            rest = input("Use a potion before next fight? (y/n): ").strip().lower()
            if rest == 'y':
                party[0].heal()
    if any(member.is_alive() for member in party):
        print("\n🏆 Your party has defeated all foes!")
    else:
        print("\n💀 Your party was defeated...")

def start_game():
    print("Choose your class:\n1. Fighter\n2. Rogue\n3. Wizard")
    choice = input("Enter 1-3: ").strip()
    if choice == "1":
        player = Fighter("Valeros")
        party = [player, AIRogue("Merisiel"), AIWizard("Ezren")]
    elif choice == "2":
        player = Rogue("Merisiel")
        party = [player, AIFighter("Valeros"), AIWizard("Ezren")]
    elif choice == "3":
        player = Wizard("Ezren")
        party = [player, AIFighter("Valeros"), AIRogue("Merisiel")]
    else:
        print("Defaulting to Fighter.")
        player = Fighter("Valeros")
        party = [player, AIRogue("Merisiel"), AIWizard("Ezren")]

    enemies = [
        Enemy("Goblin", hp=20, ac=15, attack_bonus=5),
        Enemy("Ogre", hp=40, ac=17, attack_bonus=7, damage_dice=(2, 6)),
        Enemy("Wyvern", hp=55, ac=19, attack_bonus=9, damage_dice=(2, 8))
    ]

    battle(party, enemies)

if __name__ == "__main__":
    start_game()
