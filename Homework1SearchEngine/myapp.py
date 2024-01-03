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

    """
    <form action="/search" method="get" style="margin-top: 20px; text-align: center;">
    <label for="q" style="font-size: 18px; margin-right: 10px;">Search:</label>
    <input type="text" id="q" name="q" style="padding: 8px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px;">
    <input type="submit" value="Search" style="padding: 8px 16px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
    </form>
    """

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

import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"
    

if __name__ == '__main__':
    app.run(debug=True)
