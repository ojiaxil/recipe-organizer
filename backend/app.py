import os
from flask import Flask, request, jsonify
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS

app = Flask(__name__)
#CORS(app)
CORS(app, origins=[
    "https://recipe-organizer-481019.web.app",
    "https://recipe-organizer-481019.firebaseapp.com"
])


basedir = os.path.abspath(os.path.dirname(__file__))
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "dev.db")
DB_PATH = "/tmp/dev.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    recipes = db.relationship("Recipe", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    cook_time = db.Column(db.Integer, index=True)
    difficulty = db.Column(db.String(50), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cook_time": self.cook_time,
            "difficulty": self.difficulty,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
        }


'''@app.route("/")
def hello():
    return jsonify({"message": "This is the Recipe Organizer backend."})'''


with app.app_context():
    if not os.path.exists(DB_PATH):
        open(DB_PATH, "a").close()
    db.create_all()

    if not Category.query.first():
        initial = [
            Category(name="Breakfast"),
            Category(name="Lunch"),
            Category(name="Dinner"),
            Category(name="Dessert"),
        ]
        db.session.bulk_save_objects(initial)
        db.session.commit()

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Return all categories"""
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])


@app.route("/api/categories", methods=["POST"])
def create_category():
    """Add a new category"""
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Category name is required"}), 400

    new_cat = Category(name=data["name"])
    db.session.add(new_cat)
    db.session.commit()
    return jsonify(new_cat.to_dict()), 201


@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    """Return all recipes"""
    recipes = Recipe.query.all()
    return jsonify([r.to_dict() for r in recipes])


@app.route("/api/recipes", methods=["POST"])
def create_recipe():
    """Create a new recipe"""
    data = request.get_json()

    if "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    new_recipe = Recipe(
        title=data["title"],
        description=data.get("description"),
        cook_time=data.get("cook_time"),
        difficulty=data.get("difficulty"),
        category_id=data.get("category_id"),
    )

    db.session.add(new_recipe)
    db.session.commit()
    return jsonify(new_recipe.to_dict()), 201


@app.route("/api/recipes/<int:id>", methods=["PUT"])
def update_recipe(id):
    """Update an existing recipe"""
    recipe = db.session.get(Recipe, id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    data = request.get_json()
    recipe.title = data.get("title", recipe.title)
    recipe.description = data.get("description", recipe.description)
    recipe.cook_time = data.get("cook_time", recipe.cook_time)
    recipe.difficulty = data.get("difficulty", recipe.difficulty)
    recipe.category_id = data.get("category_id", recipe.category_id)

    db.session.commit()
    return jsonify(recipe.to_dict())


@app.route("/api/recipes/<int:id>", methods=["DELETE"])
def delete_recipe(id):
    """Delete a recipe"""
    recipe = db.session.get(Recipe, id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": "Recipe deleted"})


@app.route("/api/report", methods=["GET"])
def get_recipe_report():
    """
    Filters recipes by category, difficulty, and max cook time.
    """
    query = Recipe.query

    category_id = request.args.get("category", type=int)
    difficulty = request.args.get("difficulty", type=str)
    max_time = request.args.get("max_time", type=int)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if max_time:
        query = query.filter(Recipe.cook_time <= max_time)

    results = query.all()
    return jsonify([r.to_dict() for r in results])

@app.route("/api/search")
def search_recipes():
    """
    Demonstrates safe SQL
    """
    q = request.args.get("q", "")

    # unsafe
    # sql = f"SELECT * FROM recipe WHERE title LIKE '%{q}%'"

    safe_sql = text("SELECT * FROM recipe WHERE title LIKE :search")
    results = db.session.execute(safe_sql, {"search": f"%{q}%"}).mappings().all()

    return jsonify([dict(r) for r in results])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join("static", path)):
        return send_from_directory("static", path)
    return send_from_directory("static", "index.html")


'''if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not Category.query.first():
            print("Adding initial categories...")
            initial = [
                Category(name="Breakfast"),
                Category(name="Lunch"),
                Category(name="Dinner"),
                Category(name="Dessert"),
            ]
            db.session.bulk_save_objects(initial)
            db.session.commit()

    app.run(debug=True)'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
