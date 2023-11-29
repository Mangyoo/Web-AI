from flask import Flask, render_template, request, jsonify
from crawler import WebCrawler
from indexing import Indexer
from whoosh.spelling import ListCorrector, MultiCorrector

app = Flask(__name__, template_folder="templates")
index_dir = "index_dir"
indexer = Indexer(index_dir)
web_crawler = WebCrawler("https://vm009.rz.uos.de/crawl/index.html", "vm009.rz.uos.de", indexer)
word_list = []

@app.route('/')
def home():
    return render_template('index.html')

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
    #corrector = ListCorrector(word_list)
    #c1 = searcher.corrector("content")
    #c2 = spelling.ListCorrector(word_list)
    #corrector = MultiCorrector([c1, c2])
    if query:
        web_crawler.run_crawler()
        search_results = indexer.search(query)
        result_html = render_template('search_results.html', search_results=search_results)
        return jsonify({'result_html': result_html})
    else:
        return jsonify({'result_html': 'Please enter a search query.'})
    

if __name__ == '__main__':
    app.run(debug=True)