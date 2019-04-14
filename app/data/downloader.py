from collections import defaultdict
import enchant
import json
import os
import re
import requests
import tqdm
import xmltodict

GOODREADS_API_ENDPOINT = "https://www.goodreads.com"
GOODREADS_KEYS = os.environ["GOODREADS_KEY"].split(",")
RAW_DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "raw"))
CLEAN_DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "clean"))
MERGED_DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "merged"))
CACHE_SIZE = 10


def download_reviews(start_id=1, end_id=1000000, start_counter=0):
    GOODREADS_API_REVIEW_SHOW = "/review/show.xml?key=%s&id=%d"
    FOUT_FILENAME = "review-%02d.json"
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
                    print("Review ID: %7d, cache length: %4d" % (id, len(cache)))
                    if len(cache) == CACHE_SIZE:
                        with open(os.path.join(RAW_DATA_DIR, FOUT_FILENAME % counter), "w") as fout:
                            print("Dumping cache into %s" % fout.name)
                            json.dump(cache, fout, indent=2)
                        counter += 1
                        cache = {}
        except Exception as e:
            print(e)
    if len(cache) > 0:
        with open(os.path.join(RAW_DATA_DIR, FOUT_FILENAME % counter), "w") as fout:
            print("Dumping cache into %s" % fout.name)
            json.dump(cache, fout, indent=2)


def download_books(start_counter=0):
    GOODREADS_API_BOOK_SHOW = "/book/show.xml?key=%s&id=%d"
    FIN_FILENAME = "review-%02d.json"
    FOUT_FILENAME = "book-%02d.json"
    finished_file_index = []
    unfinished_file_index = []
    for filename in sorted(os.listdir(CLEAN_DATA_DIR)):
        m = re.match(r"review-(\d+).json", filename)
        if m and m.group(1).isdigit():
            if int(m.group(1)) >= start_counter:
                unfinished_file_index.append(int(m.group(1)))
            else:
                finished_file_index.append(int(m.group(1)))
    books_id = set()
    for idx in finished_file_index:
        with open(os.path.join(RAW_DATA_DIR, FOUT_FILENAME % idx), "r") as fin:
            books = json.load(fin)
            for book_id in books:
                books_id.add(int(book_id))
    print("Books already fetched:", books_id)
    counter = 0
    for idx in unfinished_file_index:
        with open(os.path.join(CLEAN_DATA_DIR, FIN_FILENAME % idx), "r") as fin:
            reviews = json.load(fin)
            cache = {}
            for review_id in reviews:
                book_id = reviews[review_id]["book"]
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
                            print("Book ID: %7d, cache length: %4d" % (book_id, len(cache)))
                        counter += 1
                    except Exception:
                        pass
            if len(cache) > 0:
                with open(os.path.join(RAW_DATA_DIR, FOUT_FILENAME % idx), "w") as fout:
                    print("Dumping cache into %s" % fout.name)
                    json.dump(cache, fout, indent=2)


def tokenize(text: str) -> list:
    return re.findall(r'[0-9a-z]+', text.lower())


def clean_data(data: dict, fields: list) -> dict:
    english_data = {}
    pbar = tqdm.tqdm(total=len(data))
    for id in data:
        i = 0
        while i < len(fields) and not data[id][fields[i]]:
            i += 1
        field = fields[i]
        tokenized_data = tokenize(data[id][field])
        data_len = len(tokenized_data)
        if data_len > 0:
            english_count = 0
            for i in range(data_len):
                if enchant.Dict("en_US").check(tokenized_data[i]):
                    english_count += 1
            if float(english_count) / data_len >= 0.5:
                english_data[id] = data[id]
            else:
                print("ID %s is not English:\n%s" % (id, data[id][field]))
        pbar.update()
    pbar.close()
    return english_data


def clean_wrapper(start_counter: int, filename_regex: str, fields: list):
    for filename in sorted(os.listdir(RAW_DATA_DIR)):
        m = re.match(filename_regex, filename)
        if m and m.group(1).isdigit() and int(m.group(1)) >= start_counter:
            with open(os.path.join(RAW_DATA_DIR, filename), "r") as fin:
                print("Cleaning %s..." % filename)
                reviews = json.load(fin)
                english_review = clean_data(reviews, fields)
                with open(os.path.join(CLEAN_DATA_DIR, filename), "w") as fout:
                    json.dump(english_review, fout, indent=2)


def clean_reviews(start_counter=0):
    clean_wrapper(start_counter, r"review-(\d+).json", ["body"])


def clean_books(start_counter=0):
    clean_wrapper(start_counter, r"book-(\d+).json", ["description", "title"])


def merge():
    ALL_REVIEWS_FILENAME = "reviews.json"
    ALL_BOOKS_FILENAME = "books.json"
    BOOK_REVIEW_MAP_FILENAME = "book-review-map.json"
    BOOK_TITLE_ID_MAP_FILENAME = "book-id-title-map.json"

    book_review_map = defaultdict(list)
    all_reviews = {}
    counter_reviews = 0
    for filename in sorted(os.listdir(CLEAN_DATA_DIR)):
        if re.match(r"review-(\d+).json", filename):
            with open(os.path.join(CLEAN_DATA_DIR, filename), "r") as fin:
                print("Merging %s..." % filename)
                reviews = json.load(fin)
                for review_id in reviews:
                    assert all_reviews.get(review_id) is None
                    counter_reviews += 1
                    all_reviews[review_id] = reviews[review_id]
                    book_id = str(reviews[review_id]["book"])
                    book_review_map[book_id].append(int(review_id))
    with open(os.path.join(MERGED_DATA_DIR, ALL_REVIEWS_FILENAME), "w") as fout:
        json.dump(all_reviews, fout, indent=2)
    with open(os.path.join(MERGED_DATA_DIR, BOOK_REVIEW_MAP_FILENAME), "w") as fout:
        json.dump(book_review_map, fout, indent=2)

    book_title_id_map = defaultdict(list)
    all_books = {}
    counter_books = 0
    for filename in sorted(os.listdir(CLEAN_DATA_DIR)):
        if re.match(r"book-(\d+).json", filename):
            with open(os.path.join(CLEAN_DATA_DIR, filename), "r") as fin:
                print("Merging %s..." % filename)
                books = json.load(fin)
                for book_id in books:
                    assert all_books.get(book_id) is None
                    counter_books += 1
                    if book_review_map.get(book_id):
                        all_books[book_id] = books[book_id]
                        book_title = books[book_id]["title"]
                        book_title_id_map[book_title].append(int(book_id))
    with open(os.path.join(MERGED_DATA_DIR, ALL_BOOKS_FILENAME), "w") as fout:
        json.dump(all_books, fout, indent=2)
    with open(os.path.join(MERGED_DATA_DIR, BOOK_TITLE_ID_MAP_FILENAME), "w") as fout:
        json.dump(book_title_id_map, fout, indent=2)

    print("%d reviews, %d books" % (counter_reviews, counter_books))
