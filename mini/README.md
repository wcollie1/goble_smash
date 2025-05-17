# PF2E Autobattler

A Python + PyQt6 GUI-based auto-battler inspired by the Pathfinder 2E Remastered ruleset. This game simulates tactical, turn-based combat using real PF2E mechanics such as the three-action economy, off-guard condition, and class-based abilities.

## Features

- Choose from three classes: Fighter, Rogue, or Wizard
- Party members controlled by AI using class-specific logic
- Pathfinder-style actions:
  - Fighter's Power Attack (2 actions)
  - Rogue's Twin Feint (2 actions)
  - Wizard's Magic Missile (1–3 actions) and Shield
- Healing via potions, AC modifiers, and damage types
- Automatic targeting by enemies based on most damage dealt or highest HP
- Visual combat log and turn order in a PyQt6 interface

## Requirements

- Python 3.10+
- PyQt6

Install dependencies with:

```bash
pip install PyQt6
