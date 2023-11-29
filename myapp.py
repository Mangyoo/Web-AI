from flask import Flask, render_template, url_for, request
from crawler import WebCrawler
from indexing import Indexer

app = Flask(__name__)
index_dir = "index_dir"
indexer = Indexer(index_dir)
web_crawler = WebCrawler("https://vm009.rz.uos.de/crawl/index.html", "vm009.rz.uos.de", indexer)

@app.route('/')
def home():
    return """
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
        result_html = "<ul>"
        for result in search_results:  #search results in jinja template
            result_html += f"<li><a href='{result['url']}'>{result['title']}</a><br>{result['teaser']}</li>"
        result_html += "</ul>"
        return result_html
    else:
        return "Please enter a search query."
    
if __name__ == '__main__':
    app.run(debug=True)