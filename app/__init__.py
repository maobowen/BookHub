# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Configure app
socketio = SocketIO()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# DB
db = SQLAlchemy(app)

# Import + Register Blueprints
from app.accounts import accounts as accounts
app.register_blueprint(accounts)
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404


# Add command line interface
import click
from flask.cli import AppGroup

data_cli = AppGroup("data")


# Command line interface for downloader
@data_cli.command("download-reviews")
@click.option("--start-id", "-s", type=int, default=1, show_default=True, help='Start ID of Goodreads reviews.')
@click.option("--end-id", "-e", type=int, default=1000000, show_default=True, help='End ID of Goodreads reviews.')
@click.option("--start-counter", "-c", type=int, default=0, show_default=True, help='Start ID of review files.')
def download_reviews(start_id=1, end_id=1000000, start_counter=0):
    from app.data import downloader
    downloader.download_reviews(start_id, end_id, start_counter)


@data_cli.command("clean-reviews")
@click.option("--start-counter", "-c", type=int, default=0, show_default=True, help='Start ID of review files.')
def clean_reviews(start_counter=0):
    from app.data import downloader
    downloader.clean_reviews(start_counter)


@data_cli.command("download-books")
@click.option("--start-counter", "-c", type=int, default=0, show_default=True, help='Start ID of review files.')
def download_books(start_counter=0):
    from app.data import downloader
    downloader.download_books(start_counter)


@data_cli.command("clean-books")
@click.option("--start-counter", "-c", type=int, default=0, show_default=True, help='Start ID of book files.')
def clean_books(start_counter=0):
    from app.data import downloader
    downloader.clean_books(start_counter)


@data_cli.command("downloader-merge")
def downloader_merge():
    from app.data import downloader
    downloader.merge()


# Command line interface for cleaner
@data_cli.command("cleaner-prepare")
def cleaner_prepare():
    from app.data import cleaner
    cleaner.deduplicate_books_titles_by_edit_distance()
    cleaner.filter_book_ids_by_ratings(threshold=3.7)
    cleaner.filter_book_ids_by_most_reviews()
    cleaner.count_book_tags()
    cleaner.merge_book_ids()


@data_cli.command("cleaner-clean")
def cleaner_clean():
    from app.data import cleaner
    cleaner.clean_reviews()
    cleaner.clean_books()


# Command line interface for pre-processor
@data_cli.command("calc-cos-sim-desc")
def calc_cos_sim_desc():
    from app.data import preprocessor
    preprocessor.calc_cos_sim_desc()


@data_cli.command("calc-cos-sim-tm-reviews")
def calc_cos_sim_tm_reviews():
    from app.data import preprocessor
    preprocessor.calc_cos_sim_tm_reviews()


@data_cli.command("calc-cos-sim-tm-books")
def calc_cos_sim_tm_books():
    from app.data import preprocessor
    preprocessor.calc_cos_sim_tm_books()


app.cli.add_command(data_cli)
