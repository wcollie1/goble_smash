from flask import Blueprint, request, jsonify
from .models import Character, Ancestry, Class, Background, Feat, Item
from . import db

main = Blueprint('main', __name__)

# =========================
# Character CRUD Endpoints
# =========================

@main.route('/api/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "ancestry": c.ancestry.name if c.ancestry else None,
        "char_class": c.char_class.name if c.char_class else None,
        "background": c.background.name if c.background else None,
        "level": c.level
    } for c in characters])

@main.route('/api/characters', methods=['POST'])
def create_character():
    data = request.json
    new_char = Character(
        name=data['name'],
        ancestry_id=data['ancestry_id'],
        class_id=data['class_id'],
        background_id=data['background_id'],
        level=data.get('level', 1)
    )
    db.session.add(new_char)
    db.session.commit()
    return jsonify({"message": "Character created", "id": new_char.id})

@main.route('/api/characters/<int:id>', methods=['GET'])
def get_character(id):
    char = Character.query.get_or_404(id)
    return jsonify({
        "id": char.id,
        "name": char.name,
        "ancestry": char.ancestry.name if char.ancestry else None,
        "char_class": char.char_class.name if char.char_class else None,
        "background": char.background.name if char.background else None,
        "level": char.level
    })

@main.route('/api/characters/<int:id>', methods=['PUT'])
def update_character(id):
    char = Character.query.get_or_404(id)
    data = request.json
    char.name = data.get('name', char.name)
    char.ancestry_id = data.get('ancestry_id', char.ancestry_id)
    char.class_id = data.get('class_id', char.class_id)
    char.background_id = data.get('background_id', char.background_id)
    char.level = data.get('level', char.level)
    db.session.commit()
    return jsonify({"message": "Character updated"})

@main.route('/api/characters/<int:id>', methods=['DELETE'])
def delete_character(id):
    char = Character.query.get_or_404(id)
    db.session.delete(char)
    db.session.commit()
    return jsonify({"message": "Character deleted"})

# =========================
# Static Rule Data Endpoints
# =========================

@main.route('/api/ancestries', methods=['GET'])
def get_ancestries():
    data = Ancestry.query.all()
    return jsonify([{
        "id": a.id,
        "name": a.name,
        "hit_points": a.hit_points,
        "speed": a.speed,
        "size": a.size,
        "traits": a.traits
    } for a in data])

@main.route('/api/classes', methods=['GET'])
def get_classes():
    data = Class.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "key_ability": c.key_ability,
        "hp_per_level": c.hp_per_level
    } for c in data])

@main.route('/api/backgrounds', methods=['GET'])
def get_backgrounds():
    data = Background.query.all()
    return jsonify([{
        "id": b.id,
        "name": b.name,
        "fixed_boosts": b.fixed_boosts,
        "description": b.description
    } for b in data])

@main.route('/api/feats', methods=['GET'])
def get_feats():
    feat_type = request.args.get('type')
    query = Feat.query
    if feat_type:
        query = query.filter_by(type=feat_type)
    feats = query.all()
    return jsonify([{
        "id": f.id,
        "name": f.name,
        "level": f.level,
        "type": f.type,
        "class_name": f.class_name,
        "description": f.description
    } for f in feats])

@main.route('/api/items', methods=['GET'])
def get_items():
    data = Item.query.all()
    return jsonify([{
        "id": i.id,
        "name": i.name,
        "type": i.type,
        "level": i.level,
        "description": i.description
    } for i in data])
