from flask import Flask, render_template, url_for, request, jsonify
from crawler import WebCrawler
from indexing import Indexer

app = Flask(__name__, template_folder="templates")
index_dir = "index_dir"
indexer = Indexer(index_dir)
web_crawler = WebCrawler("https://vm009.rz.uos.de/crawl/index.html", "vm009.rz.uos.de", indexer)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').split()
    if query:
        web_crawler.run_crawler()
        search_results = indexer.search(query)
        return jsonify(search_results)
    else:
        return jsonify(message="Please enter a search query.")

if __name__ == '__main__':
    app.run(debug=True)