from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import render_template, request

## Coded with the help of github copilot

# Initialize Flask App
app = Flask(__name__)

# Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///thereviews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with Declarative Base
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define the Review model using `Mapped` and `mapped_column`
class Review(db.Model):
    __tablename__ = "thereviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    def __init__(self, title: str, text: str, rating: int):
        self.title = title
        self.text = text
        self.rating = rating

# DATABASE UTILITY CLASS
class Database:
    def __init__(self):
        pass

    def get(self, review_id: int = None):
        """Retrieve all reviews or a specific review by ID."""
        if review_id:
            return db.session.get(Review, review_id)
        return db.session.query(Review).all()

    def create(self, title: str, text: str, rating: int):
        """Create a new review."""
        new_review = Review(title=title, text=text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

    def update(self, review_id: int, title: str, text: str, rating: int):
        """Update an existing review."""
        review = self.get(review_id)
        if review:
            review.title = title
            review.text = text
            review.rating = rating
            db.session.commit()

    def delete(self, review_id: int):
        """Delete a review."""
        review = self.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()

db_manager = Database()  # Create a database manager instance

# Initialize database with sample data
@app.before_request
def setup():
    with app.app_context():
        db.create_all()
        if not db_manager.get():  # If database is empty, add a sample entry
            db_manager.create("Mr. Pumpkin Man", "This is a pretty bad movie", 4)
            print("Database initialized with sample data!")

# Reset the database
@app.route('/reset-db', methods=['GET', 'POST'])
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset: success!")
    return "Database has been reset!", 200


# ROUTES
"""You will add all of your routes below, there is a sample one which you can use for testing"""

@app.route('/', endpoint="reviews")
def show_all_reviews():
    """Display all reviews."""
    reviews = db_manager.get()
    return render_template("reviews.html", reviews=reviews)

@app.route("/review/<review_id>", endpoint="review")
def show_review(review_id):
    """Display a specific review."""
    review_id = int(review_id)
    review = db_manager.get(review_id)
    if review:
        return render_template("review.html", review=review)
    return "Review not found", 404

@app.route("/edit/<review_id>", endpoint="edit")
def edit_review(review_id):
    """Edit a specific review. Returns the editing page"""
    review_id = int(review_id)
    review = db_manager.get(review_id)
    if review:
        return render_template("edit_review.html", review=review)
    return "Review not found", 404

@app.route("/edit/<review_id>", endpoint="editSubmit", methods=["POST"])
def edit_review(review_id):
    """Edit a specific review. Updates the review in the database."""
    review_id = int(review_id)
    review = db_manager.get(review_id)
    if review:
        title = request.form.get("title")
        text = request.form.get("content")
        rating = int(request.form.get("rating"))
        db_manager.update(review_id, title, text, rating)
        return render_template("review.html", review=review)

@app.route("/delete/<review_id>", endpoint="delete", methods=["POST", "GET"])
def delete_review(review_id):
    """Delete a specific review. Removes the review from the database."""
    review_id = int(review_id)
    db_manager.delete(review_id)
    reviews = db_manager.get()
    return render_template("reviews.html", reviews=reviews)

@app.route("/add", endpoint="add")
def add_review():
    """Display the form to add a new review."""
    return render_template("add_review.html")

@app.route("/add", endpoint="addSubmit", methods=["POST"])
def add_review():
    """Add a new review. Takes the data from the form and adds it to the database."""
    title = request.form.get("title")
    text = request.form.get("content")
    rating = int(request.form.get("rating"))
    db_manager.create(title, text, rating)
    reviews = db_manager.get()
    return render_template("reviews.html", reviews=reviews)

# RUN THE FLASK APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure DB is created before running the app
    app.run(debug=True)
