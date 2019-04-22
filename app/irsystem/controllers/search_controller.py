from . import *
from app.irsystem.models import Book
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "BookHub"
net_id = "Minghao Li: ml922; Bowen Mao: bm644; Lauren Wong: lqw5; Lu Yang: ly298"

DATA_DIR = [
	os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "merged")),
	os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "v2")),
]
MAX_COMPARED = 20
MAX_RECOMMEND = 8
MAX_REVIEWS = 5
VERSIONS = [1, 2]


def _set_version(request) -> int:
	if not session.get("version") in VERSIONS:
		session["version"] = VERSIONS[-1]
	version_query_string = request.args.get("v", type=str)
	if version_query_string == "1":
		session["version"] = VERSIONS[0]
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


def _get_recommendation(version_idx: int, book_ids: list) -> list:
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
		cos_sim_sums = [defaultdict(float) for _ in range(3)]
		for book in request_books:
			top_k_cos_sim = [
				json.loads(book.cos_sim_desc),
				json.loads(book.cos_sim_tm_reviews),
				json.loads(book.cos_sim_tm_books),
			]
			for i in range(3):
				for similar_book_id in top_k_cos_sim[i]:
					cos_sim_sums[i][similar_book_id] += top_k_cos_sim[i][similar_book_id]

		cos_sim_avg = defaultdict(float)
		ratio = [0.7, 0.3, 0]
		for i in range(3):
			for similar_book_id in cos_sim_sums[i]:
				cos_sim_avg[similar_book_id] += ratio[i] * cos_sim_sums[i][similar_book_id]

		result = sorted(cos_sim_avg, key=cos_sim_avg.get, reverse=True)[:MAX_RECOMMEND]
		print(result)
		return result


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


def _get_recommended_books_detail(version_idx: int, recommended_book_ids: list, request_book_ids: list) -> list:
	if version_idx == 0:
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
		recommended_books_object = Book.query.filter(Book.id.in_(recommended_book_ids)).all()
		recommended_books = []
		for book in recommended_books_object:
			reviews = json.loads(book.reviews)
			review_texts = [review["body"] for review in reviews]
			recommended_books.append({
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
			})
		return recommended_books


@irsystem.route("/", methods=["GET", "POST"])
def search():
	data = []
	version_idx = _set_version(request)

	if request.method == "POST":
		request_book_ids = request.form.get("book_ids", "").split()
		if len(request_book_ids) >= 1 and request_book_ids[0] != "":
			recommended_book_ids = _get_recommendation(version_idx, request_book_ids)
			data = _get_recommended_books_detail(version_idx, recommended_book_ids, request_book_ids)
	else:
		data = []

	if version_idx == 0:
		return render_template('search_v1.html', name=project_name, netid=net_id, data=data)
	else:
		return render_template('search_v2.html', name=project_name, netid=net_id, data=data)
