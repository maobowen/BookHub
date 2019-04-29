from . import *
from app.irsystem.models import Book
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "BookHub"
net_id = "Minghao Li: ml922; Bowen Mao: bm644; Lauren Wong: lqw5; Lu Yang: ly298"

DATA_DIR = [
	os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "merged")),
	os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "v2")),
	os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "v2")),
]
MAX_COMPARED = 20
MAX_RECOMMEND = 8
MAX_REVIEWS = 5
VERSIONS = [1, 2, 3]
N_FACTORS = 4


def _set_version(request) -> int:
	if not session.get("version") in VERSIONS:
		session["version"] = VERSIONS[-1]
	version_query_string = request.args.get("v", type=str)
	if version_query_string == "1":
		session["version"] = VERSIONS[0]
	elif version_query_string == "2":
		session["version"] = VERSIONS[1]
	elif version_query_string:
		session["version"] = VERSIONS[-1]
	return VERSIONS.index(session["version"])


@irsystem.route("/ajax/books/id-title", methods=["GET"])
def get_books_id_title():
	version_idx = _set_version(request)
	try:
		return send_file(os.path.join(DATA_DIR[version_idx], "book-id-title-map.json"))
	except Exception as e:
		return str(e)


@irsystem.route("/ajax/tags", methods=["GET"])
def get_tags():
	version_idx = _set_version(request)
	try:
		with open(os.path.join(DATA_DIR[version_idx], "tags-clean.txt"), "r") as fin:
			tags = [line.split(",")[0].strip() for line in fin if line]
		return Response(json.dumps(tags),  mimetype="application/json")
	except Exception as e:
		return str(e)


def _get_recommendation(version_idx: int, book_ids: list):
	if version_idx == 0:
		with open(os.path.join(DATA_DIR[version_idx], "cos-sim-desc.json"), "r") as fin:
			top_k_cos_sim = json.load(fin)
		cos_sim_sums = defaultdict(float)
		for book_id in book_ids:
			if book_id in top_k_cos_sim:
				for similar_book_id in top_k_cos_sim[book_id]:
					cos_sim_sums[similar_book_id] += top_k_cos_sim[book_id][similar_book_id]
		result = sorted(cos_sim_sums, key=cos_sim_sums.get, reverse=True)[:MAX_COMPARED]
		return result

	else:
		request_books = Book.query.filter(Book.id.in_(book_ids)).all()
		n_request_books = len(request_books)
		sim_scores_sums = [defaultdict(float) for _ in range(N_FACTORS)]
		for book in request_books:
			top_k_sim_scores = [
				json.loads(book.cos_sim_desc),
				json.loads(book.cos_sim_tm_reviews),
				json.loads(book.cos_sim_tm_books),
				json.loads(book.jaccard_sim_tags),
			]
			assert len(top_k_sim_scores) == N_FACTORS
			for i in range(N_FACTORS):
				for similar_book_id in top_k_sim_scores[i]:
					sim_scores_sums[i][similar_book_id] += top_k_sim_scores[i][similar_book_id] / float(n_request_books)

		sim_scores_avg = defaultdict(float)
		ratio = [0.85, 0.05, 0.0, 0.1]
		assert len(ratio) == N_FACTORS
		for i in range(N_FACTORS):
			for similar_book_id in sim_scores_sums[i]:
				sim_scores_avg[similar_book_id] += ratio[i] * sim_scores_sums[i][similar_book_id]

		for book in request_books:
			if str(book.id) in sim_scores_avg:
				sim_scores_avg.pop(str(book.id))

		result = sorted(sim_scores_avg, key=sim_scores_avg.get, reverse=True)[:MAX_COMPARED]
		result_scores = defaultdict(list)
		for similar_book_id in result:
			for i in range(N_FACTORS):
				result_scores[similar_book_id].append(sim_scores_sums[i][similar_book_id])
		return result, result_scores


def _get_book_reviews(version_idx: int, book_id: str) -> list:
	if version_idx == 0:
		review_texts = []
		with open(os.path.join(DATA_DIR[version_idx], "book-review-map.json"), "r") as fin1:
			book_review_map = json.load(fin1)
		review_ids = book_review_map[book_id][:MAX_REVIEWS]
		with open(os.path.join(DATA_DIR[version_idx], "reviews.json"), "r") as fin2:
			reviews = json.load(fin2)
		for review_id in review_ids:
			review_texts.append(reviews[str(review_id)]["body"])
		return review_texts[:MAX_RECOMMEND]


def _recalc_jaccard_sim_tags(version_idx: int, recommended_book: Book, request_books: list) -> float:
	if version_idx > 1:
		score = 0.0
		recommended_book_tags = json.loads(recommended_book.tags)
		assert type(recommended_book_tags) == list
		for request_book in request_books:
			request_book_tags = json.loads(request_book.tags)
			assert type(request_book_tags) == list
			score += len(set(recommended_book_tags).intersection(request_book_tags)) / len(set(recommended_book_tags).union(request_book_tags))
		return score / len(request_books)


def _get_recommended_books_detail(version_idx: int, recommended_book_ids: list, request_book_ids: list, recommended_book_scores: dict, preferred_genres=[]):
	if version_idx == 0:
		assert request_book_ids is not None
		assert recommended_book_scores is None
		recommended_books = []
		with open(os.path.join(DATA_DIR[version_idx], "books.json"), "r") as fin:
			books = json.load(fin)
		titles = [books[book_id]["title"] for book_id in request_book_ids]
		for book_id in recommended_book_ids:
			if books[book_id]["title"] not in titles:
				book = {
					"id": "id" + book_id,
					"title": books[book_id]["title"],
					"average_rating": books[book_id]["average_rating"],
					"image_url": books[book_id]["image_url"],
				}
				authors = []
				for author in books[book_id]["authors"]["author"]:
					if type(author) == dict and author.get("name"):
						authors.append(author["name"])
				book["authors"] = ", ".join(authors)
				book["reviews"] = _get_book_reviews(version_idx, book_id)
				recommended_books.append(book)
				titles.append(books[book_id]["title"])
		return recommended_books

	else:
		assert type(preferred_genres) == list
		do_boolean_search = not (version_idx == 1 or not preferred_genres or (len(preferred_genres) == 1 and not preferred_genres[0].strip()))
		assert recommended_book_scores is not None
		recommended_books_object = [Book.query.filter_by(id=recommended_book_id).one() for recommended_book_id in recommended_book_ids]
		recommended_books = []
		recommended_books2 = []
		request_books_object = Book.query.filter(Book.id.in_(request_book_ids)).all()

		for book in recommended_books_object:
			if version_idx == 1:
				reviews = json.loads(book.reviews)
				review_texts = [review["body"] for review in reviews]
			else:
				review_texts = sorted(json.loads(book.reviews), key=lambda k: (-k["votes"], -k["rating"], -len(k["body"])))
			return_book = {
				"id": "id" + str(book.id),
				"title": book.title,
				"isbn13": book.isbn13,
				"description": book.description,
				"image_url": book.image_url,
				"average_rating": str(book.average_rating),
				"url": book.url,
				"authors": ", ".join(json.loads(book.authors)),
				"tags": ", ".join(json.loads(book.tags)),
				"buy_link": book.buy_link,
				"reviews": review_texts,
				"cos_sim_desc": recommended_book_scores[str(book.id)][0],
				"cos_sim_tm_reviews": recommended_book_scores[str(book.id)][1],
				"cos_sim_tm_books": recommended_book_scores[str(book.id)][2],
				"jaccard_sim_tags": _recalc_jaccard_sim_tags(version_idx, book, request_books_object),
			}
			
			# No genres preferred
			if not do_boolean_search:
				recommended_books.append(return_book)
			else:
				book_tags = json.loads(book.tags)
				assert type(book_tags) == list
				boolean_search_found = False
				for preferred_genre in preferred_genres:
					if preferred_genre in book_tags:
						boolean_search_found = True
						recommended_books.append(return_book)
						break
				if not boolean_search_found:
					recommended_books2.append(return_book)

		if version_idx == 1:
			return recommended_books
		else:
			return recommended_books, recommended_books2


@irsystem.route("/", methods=["GET", "POST"])
def search():
	data = []
	data2 = []
	version_idx = _set_version(request)

	if request.method == "POST":
		request_book_ids = request.form.get("book_ids", "").split()
		if len(request_book_ids) >= 1 and request_book_ids[0] != "":
			if version_idx == 0:
				recommended_book_ids = _get_recommendation(version_idx, request_book_ids)
				data = _get_recommended_books_detail(version_idx, recommended_book_ids, request_book_ids, None)
			else:
				recommended_book_ids, recommended_book_scores = _get_recommendation(version_idx, request_book_ids)
				if version_idx == 1:
					data = _get_recommended_books_detail(version_idx, recommended_book_ids, None, recommended_book_scores)
				else:
					preferred_genres = request.form.get("tags_inputed", "").split()
					data, data2 = _get_recommended_books_detail(version_idx, recommended_book_ids, request_book_ids, recommended_book_scores, preferred_genres=preferred_genres)

	if version_idx == 0:
		return render_template('search_v1.html', name=project_name, netid=net_id, data=data, data2=None)
	elif version_idx == 1:
		return render_template('search_v2.html', name=project_name, netid=net_id, data=data, data2=None)
	else:
		return render_template('search_v3.html', name=project_name, netid=net_id, data=data, data2=data2)
