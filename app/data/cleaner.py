from bs4 import BeautifulSoup
from collections import defaultdict, OrderedDict
import json
import os
import tqdm
import urllib.parse

MERGED_DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "merged"))
V2_DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "v2"))
ALL_REVIEWS_FILENAME = "reviews.json"
ALL_BOOKS_FILENAME = "books.json"
BOOK_REVIEW_MAP_FILENAME = "book-review-map.json"
BOOK_TITLE_ID_MAP_FILENAME = "book-id-title-map.json"
BOOK_TITLE_ID_MAP_DEDUPED_FILENAME = "book-title-id-map-deduped.json"
BOOK_TITLE_PRIMARY_ID_MAP_FILENAME = "book-title-primary-id-map.json"
BOOK_ID_PRIMARY_ID_MAP_FILENAME = "book-id-primary-id-map.json"
BOOK_PRIMARY_ID_ID_MAP_FILENAME = "book-primary-id-id-map.json"


def levenshtein(s1: str, s2: str) -> bool:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1) <= 2

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            if c1 != c2:
                substitutions = previous_row[j] + 2
            else:
                substitutions = previous_row[j]
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        if min(previous_row) > 2:
            return False

    return previous_row[-1] <= 2


def deduplicate_books_titles_by_edit_distance():
    MIN_LEN = 5

    unique_titles = set()
    book_title_id_map = {}
    with open(os.path.join(MERGED_DATA_DIR, BOOK_TITLE_ID_MAP_FILENAME), "r") as fin:
        books = json.load(fin)

    for book_title in tqdm.tqdm(books):
        new_title = True
        for title in unique_titles:
            if len(book_title) > MIN_LEN and len(title) > MIN_LEN and levenshtein(book_title, title):
                book_title_id_map[title] += books[book_title]
                new_title = False
                break
        if new_title:
            unique_titles.add(book_title)
            book_title_id_map[book_title] = books[book_title]

    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_ID_MAP_DEDUPED_FILENAME), "w") as fout:
        json.dump(book_title_id_map, fout, indent=2)


def find_low_rating_book_ids(threshold) -> list:
    low_rating_book_ids = []
    with open(os.path.join(MERGED_DATA_DIR, ALL_BOOKS_FILENAME), "r") as fin:
        books = json.load(fin)
    for book_id in books:
        if float(books[book_id]["average_rating"]) < threshold:
            low_rating_book_ids.append(int(book_id))
    return low_rating_book_ids


def filter_book_ids_by_ratings(threshold=3.7):
    low_rating_book_id_list = find_low_rating_book_ids(threshold)

    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_ID_MAP_DEDUPED_FILENAME), "r") as fin:
        book_title_id_map = json.load(fin)
    for book_title in book_title_id_map:
        low_rating_book_ids = []
        for book_id in book_title_id_map[book_title]:
            if book_id in low_rating_book_id_list:
                low_rating_book_ids.append(book_id)
        for book_id in low_rating_book_ids:
            book_title_id_map[book_title].remove(book_id)
    low_rating_book_titles = []
    for book_title in book_title_id_map:
        if len(book_title_id_map[book_title]) <= 0:
            low_rating_book_titles.append(book_title)
    for title in low_rating_book_titles:
        del book_title_id_map[title]

    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_ID_MAP_DEDUPED_FILENAME), "w") as fout:
        json.dump(book_title_id_map, fout, indent=2)


def filter_book_ids_by_most_reviews():
    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_ID_MAP_DEDUPED_FILENAME), "r") as fin:
        book_title_id_map = json.load(fin)
    with open(os.path.join(MERGED_DATA_DIR, BOOK_REVIEW_MAP_FILENAME), "r") as fin:
        book_review_map = json.load(fin)
    for book_title in book_title_id_map:
        max_reviews = -1
        max_reviews_book_id = -1
        for book_id in book_title_id_map[book_title]:
            n_reivews = len(book_review_map[str(book_id)])
            if n_reivews > max_reviews:
                max_reviews = n_reivews
                max_reviews_book_id = book_id
        book_title_id_map[book_title] = max_reviews_book_id
    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_PRIMARY_ID_MAP_FILENAME), "w") as fout:
        json.dump(book_title_id_map, fout, indent=2)


def count_book_tags():
    FOUT_FILENAME = "tags-raw.json"

    tag_count = defaultdict(int)
    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_PRIMARY_ID_MAP_FILENAME), "r") as fin:
        book_title_id_map = json.load(fin)
    with open(os.path.join(MERGED_DATA_DIR, ALL_BOOKS_FILENAME), "r") as fin:
        books = json.load(fin)
    for book_title in book_title_id_map:
        book_id = book_title_id_map[book_title]
        for tag in books[str(book_id)]["popular_shelves"]["shelf"]:
            tag_count[tag] += 1
    tag_count = OrderedDict(sorted(tag_count.items(), key=lambda x: -x[1]))
    with open(os.path.join(V2_DATA_DIR, FOUT_FILENAME), "w") as fout:
        json.dump(tag_count, fout, indent=2)


def merge_book_ids():
    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_ID_MAP_DEDUPED_FILENAME), "r") as fin:
        book_title_id_map = json.load(fin)
    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_PRIMARY_ID_MAP_FILENAME), "r") as fin:
        book_title_primary_id_map = json.load(fin)
    book_id_primary_id_map = {}
    book_primary_id_id_map = defaultdict(list)
    for book_title in book_title_id_map:
        primary_id = book_title_primary_id_map[book_title]
        assert type(book_title_id_map[book_title]) == list
        assert type(primary_id) == int
        for book_id in book_title_id_map[book_title]:
            book_id_primary_id_map[book_id] = primary_id
            book_primary_id_id_map[primary_id].append(int(book_id))
    book_id_primary_id_map = OrderedDict(sorted(book_id_primary_id_map.items()))
    book_primary_id_id_map = OrderedDict(sorted(book_primary_id_id_map.items()))
    with open(os.path.join(V2_DATA_DIR, BOOK_ID_PRIMARY_ID_MAP_FILENAME), "w") as fout:
        json.dump(book_id_primary_id_map, fout, indent=2)
    with open(os.path.join(V2_DATA_DIR, BOOK_PRIMARY_ID_ID_MAP_FILENAME), "w") as fout:
        json.dump(book_primary_id_id_map, fout, indent=2)


def clean_reviews():
    with open(os.path.join(MERGED_DATA_DIR, ALL_REVIEWS_FILENAME), "r") as fin:
        reviews = json.load(fin)
    with open(os.path.join(V2_DATA_DIR, BOOK_ID_PRIMARY_ID_MAP_FILENAME), "r") as fin:
        book_id_primary_id_map = json.load(fin)
    cleaned_reviews = {}
    book_review_map = defaultdict(list)
    for review_id in reviews:
        original_book_id = str(reviews[review_id]["book"])
        if original_book_id in book_id_primary_id_map:
            new_book_id = book_id_primary_id_map[original_book_id]
            cleaned_reviews[review_id] = {
                "book": new_book_id,
                "rating": reviews[review_id]["rating"],
                "votes": reviews[review_id]["votes"],
                "body": BeautifulSoup(reviews[review_id]["body"], "lxml").text,
            }
            book_review_map[new_book_id].append((int(review_id), reviews[review_id]["votes"]))
    with open(os.path.join(V2_DATA_DIR, ALL_REVIEWS_FILENAME), "w") as fout:
        json.dump(cleaned_reviews, fout, indent=2)
    for book_id in book_review_map:
        book_review_map[book_id].sort(key=lambda x: -x[1])
        book_review_map[book_id] = [x[0] for x in book_review_map[book_id]]
    with open(os.path.join(V2_DATA_DIR, BOOK_REVIEW_MAP_FILENAME), "w") as fout:
        json.dump(book_review_map, fout, indent=2)


def has_no_image(image_url: str) -> bool:
    return not image_url or "nophoto" in image_url


def load_book_tags() -> dict:
    FIN_FILENAME = "tags-clean.txt"
    tags = {}
    with open(os.path.join(V2_DATA_DIR, FIN_FILENAME), "r") as fin:
        for line in fin:
            tag_group = line.split(",")
            for tag in tag_group:
                tags[tag] = tag_group[0]
    return tags


def clean_books():
    tags = load_book_tags()
    with open(os.path.join(MERGED_DATA_DIR, ALL_BOOKS_FILENAME), "r") as fin:
        books = json.load(fin)
    with open(os.path.join(V2_DATA_DIR, BOOK_ID_PRIMARY_ID_MAP_FILENAME), "r") as fin:
        book_id_primary_id_map = json.load(fin)
    with open(os.path.join(V2_DATA_DIR, BOOK_PRIMARY_ID_ID_MAP_FILENAME), "r") as fin:
        book_primary_id_id_map = json.load(fin)

    cleaned_books = {}
    book_title_id_map = {}
    for original_book_id in books:
        if original_book_id in book_id_primary_id_map:
            new_book_id = book_id_primary_id_map[original_book_id]
            if new_book_id == int(original_book_id):
                cleaned_books[original_book_id] = {
                    "title": books[original_book_id]["title"],
                    "isbn13": "",
                    "description": "" if not books[original_book_id]["description"] else BeautifulSoup(books[original_book_id]["description"], "lxml").text,
                    "image_url": books[original_book_id]["image_url"],
                    "average_rating": float(books[original_book_id]["average_rating"]),
                    "url": books[original_book_id]["url"],
                    "authors": [],
                    "tags": [],
                    "buy_link": "",
                }
                if books[original_book_id]["isbn13"]:
                    cleaned_books[original_book_id]["isbn13"] = books[original_book_id]["isbn13"]
                elif books[original_book_id]["isbn"]:
                    cleaned_books[original_book_id]["isbn13"] = books[original_book_id]["isbn"]

                if has_no_image(cleaned_books[original_book_id]["image_url"]):
                    for dup_book_id in book_primary_id_id_map[original_book_id]:
                        if not has_no_image(books[str(dup_book_id)]["image_url"]):
                            cleaned_books[original_book_id]["image_url"] = books[str(dup_book_id)]["image_url"]
                            break

                if type(books[original_book_id]["authors"]["author"]) == dict:
                    cleaned_books[original_book_id]["authors"].append(books[original_book_id]["authors"]["author"]["name"])
                elif type(books[original_book_id]["authors"]["author"]) == list:
                    for author in books[original_book_id]["authors"]["author"]:
                        cleaned_books[original_book_id]["authors"].append(author["name"])

                for tag in books[original_book_id]["popular_shelves"]["shelf"]:
                    if tag in tags and not tag in cleaned_books[original_book_id]["tags"]:
                        cleaned_books[original_book_id]["tags"].append(tag)
                    else:
                        subtags = tag.split("-")
                        for subtag in subtags:
                            if subtag in tags and not subtag in cleaned_books[original_book_id]["tags"]:
                                cleaned_books[original_book_id]["tags"].append(subtag)

                if cleaned_books[original_book_id]["isbn13"]:
                    cleaned_books[original_book_id]["buy_link"] = "https://www.amazon.com/s?k=%s" % cleaned_books[original_book_id]["isbn13"]
                else:
                    cleaned_books[original_book_id]["buy_link"] = "https://www.amazon.com/s?k=%s" % urllib.parse.quote_plus(cleaned_books[original_book_id]["title"])

                title = cleaned_books[original_book_id]["title"]
                book_title_id_map[title] = int(original_book_id)

    with open(os.path.join(V2_DATA_DIR, ALL_BOOKS_FILENAME), "w") as fout:
        json.dump(cleaned_books, fout, indent=2)
    with open(os.path.join(V2_DATA_DIR, BOOK_TITLE_ID_MAP_FILENAME), "w") as fout:
        json.dump(book_title_id_map, fout, indent=2)
