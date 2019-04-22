from app import db # Grab the db from the top-level app
from marshmallow_sqlalchemy import ModelSchema # Needed for serialization in each model
from werkzeug import check_password_hash, generate_password_hash # Hashing
import hashlib # For session_token generation (session-based auth. flow)
import datetime # For handling dates 


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False)
    isbn13 = db.Column(db.String(15))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    average_rating = db.Column(db.Float)
    url = db.Column(db.String(255))
    authors = db.Column(db.Text)
    tags = db.Column(db.Text)
    buy_link = db.Column(db.String(255))
    reviews = db.Column(db.Text)
    cos_sim_desc = db.Column(db.Text)
    cos_sim_tm_reviews = db.Column(db.Text)
    cos_sim_tm_books = db.Column(db.Text)
    jaccard_sim_tags = db.Column(db.Text)

    def __init__(self, id: int, title: str, isbn13="", description="", image_url="",
                 average_rating=0.0, url="", authors=[], tags=[], buy_link="",
                 reviews=[], cos_sim_desc={}, cos_sim_tm_reviews={},
                 cos_sim_tm_books={}, jaccard_sim_tags={}):
        db.Model.__init__(self, id=id, title=title, isbn13=isbn13, description=description, image_url=image_url,
                          average_rating=average_rating, url=url, authors=authors, tags=tags, buy_link=buy_link,
                          reviews=reviews, cos_sim_desc=cos_sim_desc, cos_sim_tm_reviews=cos_sim_tm_reviews,
                          cos_sim_tm_books=cos_sim_tm_books, jaccard_sim_tags=jaccard_sim_tags)

    def __repr__(self):
        return "<Book %s: %r>" % (self.id, self.title)
