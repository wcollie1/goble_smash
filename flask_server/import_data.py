import json
import os
from app import create_app, db
from app.models import Ancestry, Class, Background, Feat, Item

app = create_app()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)

def import_data():
    with app.app_context():
        db.create_all()

        # Import Ancestries
        ancestries = load_json("ancestries.json")
        for entry in ancestries:
            db.session.add(Ancestry(**entry))

        # Import Classes
        classes = load_json("classes.json")
        for entry in classes:
            db.session.add(Class(**entry))

        # Import Backgrounds
        backgrounds = load_json("backgrounds.json")
        for entry in backgrounds:
            db.session.add(Background(**entry))

        # Import Feats
        feats = load_json("feats.json")
        for entry in feats:
            db.session.add(Feat(**entry))

        # Import Items
        items = load_json("items.json")
        for entry in items:
            db.session.add(Item(**entry))

        db.session.commit()
        print("✅ Data imported successfully.")

if __name__ == "__main__":
    import_data()
