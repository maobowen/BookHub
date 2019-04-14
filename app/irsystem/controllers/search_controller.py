from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "BookHub"
net_id = "Minghao Li: ml922; Bowen Mao: bm644; Lauren Wong: lqw5; Lu Yang: ly298"

DATA_DIR = os.path.abspath(os.path.join(__file__, "..", "..", "..", "data", "merged"))


@irsystem.route("/ajax/books/id-title", methods=["GET"])
def get_books_id_title():
	try:
		return send_file(os.path.join(DATA_DIR, "book-id-title-map.json"))
	except Exception as e:
		return str(e)


@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



