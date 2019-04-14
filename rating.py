import matplotlib.pyplot as plt
import json
import os
import re

DATA_DIR = os.path.abspath(os.path.join(__file__, ".."))

def rating_plot():
    book_names = set()
    #for filename in os.listdir(DATA_DIR):
        #if re.match("clean_book-\d+.json", filename):
            #print("here")
    with open(os.path.join(DATA_DIR, 'clean_book_data.json'), 'r') as fin:
        books = json.load(fin)
        for book_id in books:
            book_names.add(books[book_id]["title"])
    #print(ratings)
    with open('clean_title_data.json', 'w') as outfile:  
        json.dump(list(book_names), outfile)
    

rating_plot()