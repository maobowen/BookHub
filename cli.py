import json
import os
import re
import requests
import xmltodict

GOODREADS_API_ENDPOINT = "https://www.goodreads.com"
GOODREADS_KEYS =["vTwpoTvFhucXqhYxX6EQjQ"]
DATA_DIR = os.path.abspath(os.path.join(__file__, ".."))
CACHE_SIZE = 1000


def download_reviews(start_id=1, end_id=10000, start_counter=0):
    GOODREADS_API_REVIEW_SHOW = "/review/show.xml?key=%s&id=%d"
    FOUT_FILENAME = "review-%d.json"
    cache = {}
    counter = start_counter
    for id in range(start_id, end_id + 1):
        goodreads_key = GOODREADS_KEYS[id % len(GOODREADS_KEYS)]
        url = GOODREADS_API_ENDPOINT + GOODREADS_API_REVIEW_SHOW % (goodreads_key, id)
        try:
            content_xml = requests.get(url).content.decode("utf-8")
            content_json = xmltodict.parse(content_xml)
            if not content_json["GoodreadsResponse"].get("error"):
                review = content_json["GoodreadsResponse"]["review"]
                if review["body"]:
                    review["user"] = review["user"]["id"]
                    review["book"] = review["book"]["id"]["#text"]
                    int_keys = {"user", "book", "rating", "votes", "read_count", "owned"}
                    for int_key in int_keys:
                        review[int_key] = int(review[int_key])
                    del_keys = {"id", "read_statuses", "shelves", "comments_count", "comments"}
                    for del_key in del_keys:
                        review.pop(del_key, None)
                    cache[id] = review
                    print(id, len(cache))
                    if len(cache) == CACHE_SIZE:
                        with open(os.path.join(DATA_DIR, FOUT_FILENAME % counter), 'w') as f:
                            json.dump(cache, f, indent=2)
                        counter += 1
                        cache = {}
        except Exception:
            pass
    if len(cache) > 0:
        with open(os.path.join(DATA_DIR, FOUT_FILENAME % counter), 'w') as fout:
            json.dump(cache, fout, indent=2)


def download_books():
    GOODREADS_API_BOOK_SHOW = "/book/show.xml?key=%s&id=%d"
    FOUT_FILENAME = "book-%d.json"
    books_id = set()
    cache = {}
    counter = 0
    for filename in os.listdir(DATA_DIR):
        if re.match("review-\d+.json", filename):
            with open(os.path.join(DATA_DIR, filename), 'r') as fin:
                review = json.load(fin)
                for review_id in review:
                    book_id = review[review_id]["book"]
                    if not book_id in books_id:
                        books_id.add(book_id)
                        goodreads_key = GOODREADS_KEYS[counter % len(GOODREADS_KEYS)]
                        url = GOODREADS_API_ENDPOINT + GOODREADS_API_BOOK_SHOW % (goodreads_key, book_id)
                        try:
                            content_xml = requests.get(url).content.decode("utf-8")
                            content_json = xmltodict.parse(content_xml)
                            if not content_json["GoodreadsResponse"].get("error"):
                                book = content_json["GoodreadsResponse"]["book"]
                                book["popular_shelves"]["shelf"] = [shelf["@name"] for shelf in book["popular_shelves"]["shelf"]]
                                book["similar_books"]["book"] = [int(similar_book["id"]) for similar_book in book["similar_books"]["book"]]
                                int_keys = {"publication_year", "publication_month", "publication_day", "ratings_count", "text_reviews_count"}
                                for int_key in int_keys:
                                    book[int_key] = int(book[int_key])
                                del_keys = {"id", "work", "reviews_widget"}
                                for del_key in del_keys:
                                    book.pop(del_key, None)
                                cache[book_id] = book
                                print(book_id, len(cache))
                                if len(cache) == CACHE_SIZE:
                                    with open(os.path.join(DATA_DIR, FOUT_FILENAME % counter), 'w') as fout:
                                        json.dump(cache, fout, indent=2)
                                    counter += 1
                                    cache = {}
                        except Exception:
                            pass
                if len(cache) > 0:
                    with open(os.path.join(DATA_DIR, FOUT_FILENAME % counter), 'w') as fout:
                        json.dump(cache, fout, indent=2)

if __name__ == "__main__":
    download_books()

