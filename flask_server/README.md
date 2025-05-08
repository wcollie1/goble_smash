# PF2E Simulator – Flask Backend

This is the backend API for the PF2E Character Simulator project, built with Flask. It allows the creation, reading, updating, and deletion of characters based on the Pathfinder 2E Remastered ruleset.

## 🚀 Getting Started

### 🔧 Requirements
- Python 3.9+
- pip

### 📦 Installation

1. Clone the repository or unzip the project
2. Navigate into the flask server directory:
   ```bash
   cd flask_server
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python run.py
   ```

---

## 🔗 API Endpoints

Base URL: `http://localhost:5000/api`

### 📋 GET /characters
Returns a list of all characters.

### ➕ POST /characters
Creates a new character.

**Request Body (JSON):**
```json
{
  "name": "Aric",
  "ancestry": "Human",
  "char_class": "Fighter",
  "background": "Warrior",
  "level": 1
}
```

### 🔍 GET /characters/<id>
Returns the character with the given ID.

### 🛠️ PUT /characters/<id>
Updates the character with the given ID.

**Request Body (example):**
```json
{
  "name": "Aric the Brave",
  "level": 2
}
```

### ❌ DELETE /characters/<id>
Deletes the character with the given ID.

---

## 🧪 Testing with Postman

1. Download and install Postman
2. Click **Import** and select `pf2e_postman_collection.json`
3. Use the preconfigured requests to test all endpoints

---

## 📁 Project Structure

```
flask_server/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # SQLAlchemy models
│   ├── routes.py         # API endpoints
├── run.py                # Entry point
├── requirements.txt
├── .gitignore
```

---

## 👥 API Collaboration Notes

The backend is built to communicate via JSON. All front-end applications (including Godot) should use `HTTPRequest` with JSON headers when sending or receiving data.

### Example Godot Request (GDScript)
```gdscript
var url = "http://localhost:5000/api/characters"
var headers = ["Content-Type: application/json"]
var json_body = {
    "name": "Kaelen",
    "ancestry": "Elf",
    "char_class": "Rogue",
    "background": "Street Urchin",
    "level": 1
}
$HTTPRequest.request(url, headers, true, HTTPClient.METHOD_POST, to_json(json_body))
```

---

## 🛡️ Notes

- Do NOT commit the `.db` file into source control.
- Keep API responses consistent and in JSON format.
- Ensure CORS is enabled for Godot to connect properly.

---

© PF2E Simulator Team – 2025
