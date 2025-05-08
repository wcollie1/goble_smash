from flask import Blueprint, request, jsonify
from .models import Character
from . import db

main = Blueprint('main', __name__)

@main.route('/api/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "ancestry": c.ancestry,
        "char_class": c.char_class,
        "background": c.background,
        "level": c.level
    } for c in characters])

@main.route('/api/characters', methods=['POST'])
def create_character():
    data = request.json
    new_char = Character(
        name=data['name'],
        ancestry=data['ancestry'],
        char_class=data['char_class'],
        background=data['background'],
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
        "ancestry": char.ancestry,
        "char_class": char.char_class,
        "background": char.background,
        "level": char.level
    })

@main.route('/api/characters/<int:id>', methods=['PUT'])
def update_character(id):
    char = Character.query.get_or_404(id)
    data = request.json
    char.name = data.get('name', char.name)
    char.ancestry = data.get('ancestry', char.ancestry)
    char.char_class = data.get('char_class', char.char_class)
    char.background = data.get('background', char.background)
    char.level = data.get('level', char.level)
    db.session.commit()
    return jsonify({"message": "Character updated"})

@main.route('/api/characters/<int:id>', methods=['DELETE'])
def delete_character(id):
    char = Character.query.get_or_404(id)
    db.session.delete(char)
    db.session.commit()
    return jsonify({"message": "Character deleted"})
