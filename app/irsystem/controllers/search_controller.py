from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "BookHub"
net_id = "Minghao Li: ml922; Bowen Mao: bm644; Lauren Wong: lqw5; Lu Yang: ly298"

DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "merged"))
MAX_COMPARED = 20
MAX_RECOMMEND = 8
MAX_REVIEWS = 5


@irsystem.route("/ajax/books/id-title", methods=["GET"])
def get_books_id_title():
	try:
		return send_file(os.path.join(DATA_DIR, "book-id-title-map.json"))
	except Exception as e:
		return str(e)


def _get_cos_sim_desc(book_ids: list) -> list:
	with open(os.path.join(DATA_DIR, "cos-sim-desc.json"), "r") as fin:
		top_k_cos_sim = json.load(fin)
	cos_sim_sum = defaultdict(float)
	for book_id in book_ids:
		if book_id in top_k_cos_sim:
			for similar_book_id in top_k_cos_sim[book_id]:
				cos_sim_sum[similar_book_id] += top_k_cos_sim[book_id][similar_book_id]
	result = sorted(cos_sim_sum, key=cos_sim_sum.get, reverse=True)[:MAX_COMPARED]
	return result


def _get_book_reviews(book_id: str) -> list:
	review_texts = []
	with open(os.path.join(DATA_DIR, "book-review-map.json"), "r") as fin1:
		book_review_map = json.load(fin1)
	review_ids = book_review_map[book_id][:MAX_REVIEWS]
	with open(os.path.join(DATA_DIR, "reviews.json"), "r") as fin2:
		reviews = json.load(fin2)
	for review_id in review_ids:
		review_texts.append(reviews[str(review_id)]["body"])
	return review_texts[:MAX_RECOMMEND]


def _get_recommended_books_detail(recommended_book_ids: list, request_book_ids: list) -> list:
	recommended_books = []
	with open(os.path.join(DATA_DIR, "books.json"), "r") as fin:
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
			book["reviews"] = _get_book_reviews(book_id)
			recommended_books.append(book)
			titles.append(books[book_id]["title"])
	return recommended_books


@irsystem.route("/", methods=["GET", "POST"])
def search():
	data = []
	if request.method == "POST":
		request_book_ids = request.form.get("book_ids", "").split()
		if len(request_book_ids) >= 1 and request_book_ids[0] != "":
			recommended_book_ids = _get_cos_sim_desc(request_book_ids)
			data = _get_recommended_books_detail(recommended_book_ids, request_book_ids)
	else:
		data = []
	return render_template('search.html', name=project_name, netid=net_id, data=data)
