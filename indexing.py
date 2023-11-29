from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

class Indexer:
    
    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.schema = Schema(url=ID(stored=True, unique=True), title=TEXT(stored=True), teaser=TEXT(stored=True), content=TEXT)
        self.index = create_in(index_dir, self.schema)

    def add_document(self, url, title, content, teaser):
        with self.index.writer() as writer:
            writer.add_document(url=url, title=title, content=content, teaser=teaser)

    def commit(self):
        # Commit changes to the index
        pass  # This method is not necessary for Whoosh, as it automatically commits when the writer context is exited.

    def search(self, query):
        with self.index.searcher() as searcher:
            parser = QueryParser("content", schema=self.index.schema)
            query = parser.parse(" ".join(query))
            results = searcher.search(query)
            
            return list({'url': result['url'], 'title': result['title'], 'teaser': result['teaser']} for result in results)

if __name__ == "__main__":

    # Example usage:
    indexer = Indexer("indexdir")

    # now let's add some texts (=documents)
    indexer.add_document(url=u"URL1", title=u"First document", content=u"This is the first document we've added!")
    indexer.add_document(url=u"URL2", title=u"Second document", content=u"The second one is even more interesting!")
    indexer.add_document(url=u"URL3", title=u"Songtext", content=u"Music was my first love and it will be the last")

    # Commit the changes to the index (not necessary for Whoosh, as it automatically commits)

    # Retrieving data
    with indexer.index.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", indexer.index.schema).parse("first last")
        results = searcher.search(query)

        # print all results
        for r in results:
            print(r)

    # Initialize the indexer
    index_dir = "indexdir"
    indexer = Indexer(index_dir)