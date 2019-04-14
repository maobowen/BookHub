import json
import numpy as np
from numpy import linalg as LA
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import tqdm

DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "merged"))
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
        books = {book_id: books0[book_id]["description"] for book_id in books0 if books0[book_id]["description"]}
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

    with open(os.path.join(DATA_DIR, FOUT_FILENAME), "w") as fout:
        json.dump(top_k_cos_sim, fout, indent=2)
