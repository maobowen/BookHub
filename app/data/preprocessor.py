from collections import defaultdict, OrderedDict
import json
import numpy as np
from numpy import linalg as LA
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import tqdm

DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "v2"))
TOP_K = 50
MAX_FEATURES = 5000
MIN_DF = 5
MAX_DF_RATIO = 0.9


def indexing(books: dict) -> tuple:
    book_id_to_index = {}
    book_index_to_id = {}
    for index, book_id in enumerate([bid for bid in books]):
        book_id_to_index[book_id] = index
        book_index_to_id[index] = book_id
    return book_id_to_index, book_index_to_id


def cos_sim(book1_id: str, book2_id: str, input_doc_mat, book_id_to_index: dict) -> float:
    book1_index = book_id_to_index[book1_id]
    book2_index = book_id_to_index[book2_id]
    denominator = LA.norm(input_doc_mat[book1_index]) * LA.norm(input_doc_mat[book2_index])
    if denominator != 0:
        return np.dot(input_doc_mat[book1_index], input_doc_mat[book2_index]) / denominator
    else:
        return 0.0


def calc_cos_sim_desc():
    FIN_FILENAME = "books.json"
    FOUT_FILENAME = "cos-sim-desc.json"

    print("Building mappings between book IDs and indices.")
    with open(os.path.join(DATA_DIR, FIN_FILENAME), "r") as fin:
        books0 = json.load(fin)
        books = {book_id: books0[book_id]["description"] for book_id in books0}
    n_books = len(books)
    book_id_to_index, book_index_to_id = indexing(books)

    print("Building tf-idf vectors.")
    tfidf_vec = TfidfVectorizer(max_features=MAX_FEATURES, stop_words="english", max_df=MAX_DF_RATIO, min_df=MIN_DF, norm="l2")
    doc_by_vocab = tfidf_vec.fit_transform([books[book_id] for book_id in books]).toarray()

    print("Calculating cosine similarities.")
    cos_sim_matrix = np.zeros((n_books, n_books))
    for book1_index in tqdm.tqdm(range(n_books)):
        for book2_index in range(book1_index, n_books):
            book1_id = book_index_to_id[book1_index]
            book2_id = book_index_to_id[book2_index]
            cos_sim_matrix[book1_index][book2_index] = cos_sim(book1_id, book2_id, doc_by_vocab, book_id_to_index)
            cos_sim_matrix[book2_index][book1_index] = cos_sim_matrix[book1_index][book2_index]

    print("Picking top %d cosine similarities." % TOP_K)
    top_k_cos_sim = {}
    for book_index in tqdm.tqdm(range(n_books)):
        book_id = book_index_to_id[book_index]
        cos_sim_row = cos_sim_matrix[book_index, :]
        top_k_indices = np.argsort(cos_sim_row)[::-1][:TOP_K + 1]
        top_k_cos_sim[book_id] = {}
        for target_index in top_k_indices:
            if cos_sim_row[target_index] == 0.0:
                break
            target_id = book_index_to_id[target_index]
            if target_id == book_id:
                np.testing.assert_almost_equal(1.0, cos_sim_row[target_index])
                continue
            top_k_cos_sim[book_id][target_id] = cos_sim_row[target_index]

    top_k_cos_sim = OrderedDict(sorted(top_k_cos_sim.items(), key=lambda x: x[0]))
    with open(os.path.join(DATA_DIR, FOUT_FILENAME), "w") as fout:
        json.dump(top_k_cos_sim, fout, indent=2)


def topic_modeling_decompose():
    ALL_REVIEWS_FILENAME = "reviews.json"
    ALL_BOOKS_FILENAME = "books.json"
    BOOK_REVIEW_MAP_FILENAME = "book-review-map.json"

    with open(os.path.join(DATA_DIR, ALL_BOOKS_FILENAME), "r") as fin:
        books = json.load(fin)
    with open(os.path.join(DATA_DIR, ALL_REVIEWS_FILENAME), "r") as fin:
        reviews = json.load(fin)
    with open(os.path.join(DATA_DIR, BOOK_REVIEW_MAP_FILENAME), "r") as fin:
        book_review_map = json.load(fin)
    books_dir = os.path.join(DATA_DIR, "books")
    if not os.path.exists(books_dir):
        os.mkdir(books_dir)
    reviews_dir = os.path.join(DATA_DIR, "reviews")
    if not os.path.exists(reviews_dir):
        os.mkdir(reviews_dir)

    book_reviews = defaultdict(list)
    for book_id in tqdm.tqdm(books):
        assert type(book_id) == str
        with open(os.path.join(books_dir, book_id + ".txt"), "w") as fout:
            fout.write(books[book_id]["description"])
        for review_id in book_review_map[book_id]:
            assert type(review_id) == int
            book_reviews[book_id].append(reviews[str(review_id)]["body"])
        with open(os.path.join(reviews_dir, book_id + ".txt"), "w") as fout:
            for review_body in book_reviews[book_id]:
                fout.writelines(review_body)


def calc_cos_sim_vector(filepath: str) -> OrderedDict:
    print("Reading vectors.")
    vectors = {}
    with open(filepath, "r") as fin:
        for line in fin:
            cells = line.split("\t")
            id = cells[1].split("/")[-1].split(".")[0]
            vectors[id] = np.array(cells[2:], dtype=np.float)

    print("Calculating cosine similarities.")
    ids = list(vectors.keys())
    n_items = len(ids)
    cos_sim_matrix = np.zeros((n_items, n_items))
    for index1 in tqdm.tqdm(range(n_items)):
        id1 = ids[index1]
        for index2 in range(index1, n_items):
            id2 = ids[index2]
            cos_sim_matrix[index1][index2] = np.dot(vectors[id1], vectors[id2]) / LA.norm(vectors[id1]) / LA.norm(vectors[id2])
            cos_sim_matrix[index2][index1] = cos_sim_matrix[index1][index2]

    print("Picking top %d cosine similarities." % TOP_K)
    top_k_cos_sim = {}
    for index in tqdm.tqdm(range(n_items)):
        id = ids[index]
        cos_sim_row = cos_sim_matrix[index, :]
        top_k_indices = np.argsort(cos_sim_row)[::-1][:TOP_K + 1]
        top_k_cos_sim[id] = {}
        for target_index in top_k_indices:
            if cos_sim_row[target_index] == 0.0:
                break
            target_id = ids[target_index]
            if target_id == id:
                np.testing.assert_almost_equal(1.0, cos_sim_row[target_index])
                continue
            top_k_cos_sim[id][target_id] = cos_sim_row[target_index]
    return OrderedDict(sorted(top_k_cos_sim.items(), key=lambda x: x[0]))


def calc_cos_sim_tm_reviews():
    FIN_FILENAME = "reviews_composition.txt"
    FOUT_FILENAME = "cos_sim_tm_reviews.json"

    top_k_cos_sim = calc_cos_sim_vector(os.path.join(DATA_DIR, FIN_FILENAME))
    with open(os.path.join(DATA_DIR, FOUT_FILENAME), "w") as fout:
        json.dump(top_k_cos_sim, fout, indent=2)


def calc_cos_sim_tm_books():
    FIN_FILENAME = "books_composition.txt"
    FOUT_FILENAME = "cos_sim_tm_books.json"

    top_k_cos_sim = calc_cos_sim_vector(os.path.join(DATA_DIR, FIN_FILENAME))
    with open(os.path.join(DATA_DIR, FOUT_FILENAME), "w") as fout:
        json.dump(top_k_cos_sim, fout, indent=2)


def calc_jaccard_sim_tags():
    FIN_FILENAME = "books.json"
    FOUT_FILENAME = "jaccard_sim_tags.json"

    with open(os.path.join(DATA_DIR, FIN_FILENAME), "r") as fin:
        books = json.load(fin)
    print("Calculating Jaccard similarities.")
    book_ids = list(books.keys())
    n_books = len(book_ids)
    j_sim_matrix = np.zeros((n_books, n_books))
    for book1_index in tqdm.tqdm(range(n_books)):
        book1_id = book_ids[book1_index]
        book1_tags = books[book1_id]["tags"]
        for book2_index in range(book1_index, n_books):
            book2_id = book_ids[book2_index]
            book2_tags = books[book2_id]["tags"]
            numerator = len(set(book1_tags).intersection(book2_tags))
            denominator = len(set(book1_tags).union(book2_tags))
            j_sim_matrix[book1_index][book2_index] = 0.0 if denominator == 0 else float(numerator) / denominator
            j_sim_matrix[book2_index][book1_index] = j_sim_matrix[book1_index][book2_index]

    print("Picking top %d Jaccard similarities." % TOP_K)
    top_k_j_sim = {}
    for index in tqdm.tqdm(range(n_books)):
        book_id = book_ids[index]
        j_sim_row = j_sim_matrix[index, :]
        top_k_indices = np.argsort(j_sim_row)[::-1][:TOP_K + 1]
        top_k_j_sim[book_id] = {}
        for target_index in top_k_indices:
            if j_sim_row[target_index] == 0.0:
                break
            target_id = book_ids[target_index]
            if target_id == book_id:
                np.testing.assert_almost_equal(1.0, j_sim_row[target_index])
                continue
            top_k_j_sim[book_id][target_id] = j_sim_row[target_index]

    top_k_j_sim = OrderedDict(sorted(top_k_j_sim.items(), key=lambda x: x[0]))
    with open(os.path.join(DATA_DIR, FOUT_FILENAME), "w") as fout:
        json.dump(top_k_j_sim, fout, indent=2)
