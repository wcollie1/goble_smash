import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

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
        self.round_damage = 0

    def is_alive(self):
        return self.hp > 0

    def get_ac(self):
        return self.base_ac - 2 if self.off_guard else self.base_ac

    def take_damage(self, damage, gui=None):
        self.hp = max(self.hp - damage, 0)
        msg = f"{self.name} takes {damage} damage! (HP: {self.hp}/{self.max_hp})"
        if gui: gui.append(msg)
        if self.hp == 0:
            self.alive = False
            if gui: gui.append(f"{self.name} has fallen!")

    def heal(self, gui=None):
        if self.potions > 0:
            if gui: gui.append(f"{self.name} uses a potion to heal 15 HP.")
            self.hp = min(self.hp + 15, self.max_hp)
            self.potions -= 1
            if gui: gui.append(f"HP after healing: {self.hp}/{self.max_hp} | Potions left: {self.potions}")
            return 1
        else:
            if gui: gui.append("No potions left!")
            return 0

    def attack(self, target, gui=None, dice=(1, 8), bonus_damage=0, sneak_attack=False):
        roll = random.randint(1, 20)
        total = roll + self.attack_bonus
        target_ac = target.get_ac()
        if gui: gui.append(f"{self.name} rolls to hit: d20({roll}) + ATK({self.attack_bonus}) = {total} vs AC {target_ac}")

        if roll == 1:
            if gui: gui.append("Critical Miss!")
            return 1, False
        elif roll == 20 or total >= target_ac + 10:
            if gui: gui.append("Critical Hit!")
            dice_num, dice_sides = dice
            rolls, dmg = roll_dice(dice_sides, dice_num * 2)
        elif total >= target_ac:
            if gui: gui.append("Hit!")
            dice_num, dice_sides = dice
            rolls, dmg = roll_dice(dice_sides, dice_num)
        else:
            if gui: gui.append("Miss!")
            return 1, False

        if sneak_attack:
            sa_roll, sa_dmg = roll_dice(6)
            dmg += sa_dmg
            if gui: gui.append(f"Sneak Attack! Extra d6: {sa_roll} = +{sa_dmg}")

        dmg += bonus_damage
        if gui: gui.append(f"Damage Total: {dmg}")
        target.take_damage(dmg, gui)
        return 1, dmg

    def take_turn(self, enemy, gui, callback):
        raise NotImplementedError()

class Fighter(Character):
    def __init__(self, name):
        super().__init__(name, hp=50, ac=18, attack_bonus=9)

    def take_turn(self, enemy, gui, callback):
        gui.show_actions([
            ("Strike (1 action)", lambda: callback(self.attack(enemy, gui, dice=(1, 10))[0])),
            ("Power Attack (2 actions)", lambda: gui.append("Not enough actions.") if gui.actions_left < 2 else callback(2) if self.attack(enemy, gui, dice=(2, 10)) else None),
            ("Heal (1 action)", lambda: callback(self.heal(gui))),
        ])

class AIFighter(Fighter):
    def take_turn(self, enemy, gui, callback):
        actions = gui.actions_left
        while actions > 0 and enemy.is_alive():
            if actions >= 2:
                gui.append(f"{self.name} uses Power Attack!")
                _, _ = self.attack(enemy, gui, dice=(2, 10))
                actions -= 2
            elif actions == 1:
                _, _ = self.attack(enemy, gui, dice=(1, 10))
                actions -= 1
        callback(0)

class Rogue(Character):
    def __init__(self, name):
        super().__init__(name, hp=38, ac=17, attack_bonus=8)

    def take_turn(self, enemy, gui, callback):
        def strike():
            sneak = enemy.off_guard
            used, hit = self.attack(enemy, gui, dice=(1, 6), sneak_attack=sneak)
            if hit and random.random() < 0.5:
                enemy.off_guard = True
                gui.append(f"{enemy.name} is nksow Off-Guard until their next turn!")
            callback(used)
        def twin_feint():
            gui.append(f"{self.name} uses Twin Feint!")

            # First strike: no MAP
            used1, hit1 = self.attack(enemy, gui, dice=(1, 6))
            total_used = used1

            # Second strike: enemy is Off-Guard just for this
            enemy.off_guard = True
            used2, hit2 = self.attack(enemy, gui, dice=(1, 6), sneak_attack=True)
            total_used += used2

            enemy.off_guard = False  # remove Off-Guard immediately after second strike
            callback(2)

        gui.show_actions([
            ("Strike (1 action)", strike),
            ("Twin Feint (2 action)", twin_feint),
            ("Heal (1 action)", lambda: callback(self.heal(gui))),
        ])

class AIRogue(Rogue):
    def take_turn(self, enemy, gui, callback):
        actions = gui.actions_left
        while actions > 0 and enemy.is_alive():
            if not enemy.off_guard and actions >= 1:
                feint_roll = random.randint(1, 20) + self.attack_bonus
                will_dc = 10 + enemy.attack_bonus
                gui.append(f"{self.name} attempts to Feint! d20 + Deception ({self.attack_bonus}) = {feint_roll} vs DC {will_dc}")
                if feint_roll >= will_dc:
                    gui.append(f"{self.name} successfully feints! {enemy.name} is now Off-Guard.")
                    enemy.off_guard = True
                else:
                    gui.append("Feint failed.")
                actions -= 1
            else:
                sneak = enemy.off_guard
                used, hit = self.attack(enemy, gui, dice=(1, 6), sneak_attack=sneak)
                actions -= used
        callback(0)

class Wizard(Character):
    def __init__(self, name):
        super().__init__(name, hp=32, ac=16, attack_bonus=6)
        self.shield_up = False

    def take_turn(self, enemy, gui, callback):
        def arcane_blast():
            used, _ = self.attack(enemy, gui, dice=(2, 4))
            if self.shield_up:
                gui.append("Shield fades.")
                self.base_ac -= 2
                self.shield_up = False
            callback(used)
        def magic_missile():
            count, ok = QInputDialog.getInt(gui, "Magic Missile", "How many actions to use (1-3)?", 1, 1, 3)
            if not ok or count > gui.actions_left:
                gui.append("Not enough actions or cancelled.")
                return
            for i in range(count):
                roll, dmg = roll_dice(4)
                force_dmg = dmg + 1
                gui.append(f"{self.name} fires Magic Missile #{i+1}! Roll: {roll} + 1 = {force_dmg} force damage.")
                enemy.take_damage(force_dmg, gui)
            if self.shield_up:
                gui.append("Shield fades.")
                self.base_ac -= 2
                self.shield_up = False
            callback(count)
        def shield():
            gui.append(f"{self.name} casts Shield! +2 AC until next turn.")
            self.base_ac += 2
            self.shield_up = True
            callback(1)
        gui.show_actions([
            ("Arcane Blast (1 action)", arcane_blast),
            ("Magic Missile (1-3 actions)", magic_missile),
            ("Shield (1 action)", shield if not self.shield_up else None),
            ("Heal (1 action)", lambda: callback(self.heal(gui))),
        ])

class AIWizard(Wizard):
    def take_turn(self, enemy, gui, callback):
        actions = gui.actions_left
        while actions > 0 and enemy.is_alive():
            if not self.shield_up:
                gui.append(f"{self.name} casts Shield!")
                self.base_ac += 2
                self.shield_up = True
                actions -= 1
            else:
                _, _ = self.attack(enemy, gui, dice=(2, 4))
                actions -= 1
                if self.shield_up:
                    self.base_ac -= 2
                    self.shield_up = False
        callback(0)

class Enemy(Character):
    def __init__(self, name, hp, ac, attack_bonus, damage_dice=(1, 8)):
        super().__init__(name, hp, ac, attack_bonus)
        self.damage_dice = damage_dice

    def take_turn(self, player, gui, callback):
        actions = 3
        gui.append(f"\n{self.name} takes its turn!")
        while actions > 0 and player.is_alive():
            used, _ = self.attack(player, gui, dice=self.damage_dice)
            actions -= used
        self.off_guard = False
        callback(0)

class BattleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PF2E Autobattler")
        self.resize(700, 500)
        self.layout = QVBoxLayout(self)
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)
        self.actions_left = 3
        self.party = []
        self.enemies = []
        self.current_enemy = None
        self.current_member_idx = 0
        self.rest_phase = False
        self.init_game()

    def append(self, msg):
        self.text.append(msg)
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())

    def show_actions(self, actions):
        # Remove old buttons
        for i in reversed(range(self.button_layout.count())):
            btn = self.button_layout.itemAt(i).widget()
            if btn: btn.setParent(None)
        # Add new buttons
        for label, func in actions:
            if func is None: continue
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, f=func: self.handle_action(f))
            self.button_layout.addWidget(btn)

    def handle_action(self, func):
        used = func()
        if used is not None:
            self.actions_left -= used
            self.update_status()
            if self.actions_left <= 0 or not self.current_enemy.is_alive():
                QTimer.singleShot(500, self.next_turn)

    def update_status(self):
        if self.party:
            player = self.party[0]
            self.append(f"\n{player.name}'s HP: {player.hp}/{player.max_hp} | Potions: {player.potions} | Actions Left: {self.actions_left}")

    def init_game(self):
        self.append("Choose your class:\n1. Fighter\n2. Rogue\n3. Wizard")
        self.show_actions([
            ("Fighter", lambda: self.choose_class("Fighter")),
            ("Rogue", lambda: self.choose_class("Rogue")),
            ("Wizard", lambda: self.choose_class("Wizard")),
        ])

    def choose_class(self, choice):
        if choice == "Fighter":
            player = Fighter("Valeros")
            self.party = [player, AIRogue("Merisiel"), AIWizard("Ezren")]
        elif choice == "Rogue":
            player = Rogue("Merisiel")
            self.party = [player, AIFighter("Valeros"), AIWizard("Ezren")]
        elif choice == "Wizard":
            player = Wizard("Ezren")
            self.party = [player, AIFighter("Valeros"), AIRogue("Merisiel")]
        self.enemies = [
            Enemy("Goblin", hp=20, ac=15, attack_bonus=5),
            Enemy("Ogre", hp=40, ac=17, attack_bonus=7, damage_dice=(2, 6)),
            Enemy("Wyvern", hp=55, ac=19, attack_bonus=9, damage_dice=(2, 8))
        ]
        self.current_enemy = None
        self.current_member_idx = 0
        self.rest_phase = False
        self.start_battle()

    def start_battle(self):
        if not self.enemies or not any(m.is_alive() for m in self.party):
            self.end_battle()
            return
        self.current_enemy = self.enemies.pop(0)
        self.append(f"\n--- A wild {self.current_enemy.name} appears! ---")
        self.current_member_idx = 0
        self.next_turn()

    def next_turn(self):
        # Remove old buttons
        for i in reversed(range(self.button_layout.count())):
            btn = self.button_layout.itemAt(i).widget()
            if btn: btn.setParent(None)
        if not self.current_enemy.is_alive():
            if all(m.is_alive() for m in self.party) and self.enemies:
                self.rest_phase = True
                self.append("\n--- Rest Phase ---")
                self.show_actions([
                    ("Use Potion", lambda: self.rest_action(True)),
                    ("Continue", lambda: self.rest_action(False)),
                ])
            else:
                self.start_battle()
            return
        if self.current_member_idx >= len(self.party):
            # Enemy's turn
            if self.party[0].is_alive():
                self.current_enemy.take_turn(self.party[0], self, lambda _: self.after_enemy_turn())
            else:
                self.end_battle()
            return
        member = self.party[self.current_member_idx]
        if not member.is_alive():
            self.current_member_idx += 1
            self.next_turn()
            return
        self.actions_left = 3
        self.update_status()
        if self.current_member_idx == 0:
            # Player's turn
            member.take_turn(self.current_enemy, self, self.after_player_action)
        else:
            # AI turn
            member.take_turn(self.current_enemy, self, lambda _: self.after_ai_action())

    def after_player_action(self, used):
        self.actions_left -= used
        self.update_status()
        if self.actions_left > 0 and self.current_enemy.is_alive():
            self.party[0].take_turn(self.current_enemy, self, self.after_player_action)
        else:
            self.current_member_idx += 1
            QTimer.singleShot(500, self.next_turn)

    def after_ai_action(self):
        self.current_member_idx += 1
        QTimer.singleShot(500, self.next_turn)

    def after_enemy_turn(self):
        self.current_member_idx = 0
        QTimer.singleShot(500, self.next_turn)

    def rest_action(self, use_potion):
        if use_potion:
            self.party[0].heal(self)
        self.rest_phase = False
        self.start_battle()

    def end_battle(self):
        if any(m.is_alive() for m in self.party):
            self.append("\n🏆 Your party has defeated all foes!")
        else:
            self.append("\n💀 Your party was defeated...")
        self.show_actions([
            ("Restart", self.init_game),
            ("Quit", self.close),
        ])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = BattleGUI()
    gui.show()
    sys.exit(app.exec())
