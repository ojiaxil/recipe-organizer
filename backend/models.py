from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    recipes = db.relationship('Recipe', backref='category', lazy=True)

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text)
    cook_time = db.Column(db.Integer)
    difficulty = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    ingredients = db.relationship(
        'RecipeIngredient', back_populates='recipe', cascade='all, delete-orphan'
    )

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    recipes = db.relationship(
        'RecipeIngredient', back_populates='ingredient', cascade="all, delete-orphan"
    )

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.String(50))

    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipe')