from flask import Flask, render_template, request, jsonify, url_for
from crawler import WebCrawler
from indexing import Indexer

app = Flask(__name__, template_folder="templates")
index_dir = "index_dir"
indexer = Indexer(index_dir)
web_crawler = WebCrawler("https://vm009.rz.uos.de/crawl/index.html", "vm009.rz.uos.de", indexer)
word_list = []

@app.route('/')
def home():
    return render_template('index.html', search_url=url_for("search"))


@app.route('/search')
def search():
    query = request.args.get('q', '').split()
    if query:
        web_crawler.run_crawler()
        search_results = indexer.search(query)
        result_html = render_template('search_results.html', search_results=search_results)
        return jsonify({'result_html': result_html})
    else:
        return jsonify({'result_html': 'Please enter a search query.'})
    

if __name__ == '__main__':
    app.run(debug=True)