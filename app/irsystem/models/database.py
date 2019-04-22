from app.irsystem.models import db, Book
import json
import os


def init_db():
    DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "v2"))
    ALL_BOOKS_FILENAME = "books.json"
    ALL_REVIEWS_FILENAME = "reviews.json"
    BOOK_REVIEW_MAP_FILENAME = "book-review-map.json"
    COS_SIM_DESC_FILENAME = "cos-sim-desc.json"
    COS_SIM_TM_REVIEWS_FILENAME = "cos_sim_tm_reviews.json"
    COS_SIM_TM_BOOKS_FILENAME = "cos_sim_tm_books.json"
    JACCARD_SIM_TAGS_FILENAME = "jaccard_sim_tags.json"

    # Create tables
    print("Creating all database tables...")
    db.create_all()

    # Create data
    print("Dumping all data...")

    with open(os.path.join(DATA_DIR, ALL_BOOKS_FILENAME), "r") as fin:
        books = json.load(fin)
    with open(os.path.join(DATA_DIR, ALL_REVIEWS_FILENAME), "r") as fin:
        reviews = json.load(fin)
    with open(os.path.join(DATA_DIR, BOOK_REVIEW_MAP_FILENAME), "r") as fin:
        book_review_map = json.load(fin)
    with open(os.path.join(DATA_DIR, COS_SIM_DESC_FILENAME), "r") as fin:
        top_k_cos_sim_desc = json.load(fin)
    with open(os.path.join(DATA_DIR, COS_SIM_TM_REVIEWS_FILENAME), "r") as fin:
        top_k_cos_sim_tm_reviews = json.load(fin)
    with open(os.path.join(DATA_DIR, COS_SIM_TM_BOOKS_FILENAME), "r") as fin:
        top_k_cos_sim_tm_books = json.load(fin)
    with open(os.path.join(DATA_DIR, JACCARD_SIM_TAGS_FILENAME), "r") as fin:
        top_k_j_sim_tags = json.load(fin)

    for book_id in books:
        assert type(book_id) == str
        book_reviews = []
        top_upvote_review_ids = book_review_map[book_id][:10]
        for review_id in top_upvote_review_ids:
            assert type(review_id) == int
            review = reviews[str(review_id)]
            assert review["book"] == int(book_id)
            del review["book"]
            review["id"] = review_id
            book_reviews.append(review)

        db.session.add(Book(
            id=int(book_id),
            title=books[book_id]["title"],
            isbn13=books[book_id]["isbn13"],
            description=books[book_id]["description"],
            image_url=books[book_id]["image_url"],
            average_rating=books[book_id]["average_rating"],
            url=books[book_id]["url"],
            authors=json.dumps(books[book_id]["authors"]),
            tags=json.dumps(books[book_id]["tags"]),
            buy_link=books[book_id]["buy_link"],
            reviews=json.dumps(book_reviews),
            cos_sim_desc=json.dumps(top_k_cos_sim_desc[book_id]),
            cos_sim_tm_reviews=json.dumps(top_k_cos_sim_tm_reviews[book_id]),
            cos_sim_tm_books=json.dumps(top_k_cos_sim_tm_books[book_id]),
            jaccard_sim_tags=json.dumps(top_k_j_sim_tags[book_id]),
        ))
    db.session.commit()

    print("Done!")


def drop_db():
    print("Dropping all database tables...")
    db.session.remove()
    db.drop_all()


if __name__ == '__main__':
    drop_db()
    init_db()
