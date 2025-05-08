from . import db

# =====================
# Core Character Models
# =====================

class Ancestry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hit_points = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    size = db.Column(db.String)
    traits = db.Column(db.String)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    key_ability = db.Column(db.String)
    hp_per_level = db.Column(db.Integer)

class Background(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    fixed_boosts = db.Column(db.String)  # e.g. "Strength|Dexterity"
    description = db.Column(db.Text)

# =====================
# Feats
# =====================

class Feat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer)
    type = db.Column(db.String)  # General, Skill, Ancestry, Class
    class_name = db.Column(db.String, nullable=True)
    description = db.Column(db.Text)

# =====================
# Items
# =====================

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String)  # Weapon, Armor, Equipment, Consumable
    level = db.Column(db.Integer)
    description = db.Column(db.Text)

# =====================
# Character
# =====================

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    ancestry_id = db.Column(db.Integer, db.ForeignKey('ancestry.id'))
    ancestry = db.relationship('Ancestry')

    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    char_class = db.relationship('Class')

    background_id = db.Column(db.Integer, db.ForeignKey('background.id'))
    background = db.relationship('Background')

    level = db.Column(db.Integer, default=1)
