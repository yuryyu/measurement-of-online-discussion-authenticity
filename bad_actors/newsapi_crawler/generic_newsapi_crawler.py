from __future__ import print_function
from configuration.config_class import getConfig
from newsapi_python_client.newsapi_exception import NewsAPIException
from newsapi_python_client.newsapi_client import NewsApiClient
from DB.schema_definition import Post, date, Claim, News_Article, News_Article_Item
from commons.commons import compute_post_guid, compute_author_guid_by_author_name
from commons import commons
import logging
import datetime
import ast

class Generic_NewsAPI_Crawler(object):
    def __init__(self, db, keys, query):
        # AbstractController.__init__(self, db)
        self._db = db
        self._keys = keys
        self._newsapi_client = NewsApiClient(self._keys)
        self._config_parser = getConfig()
        self._domain = unicode(self._config_parser.get("DEFAULT", "domain"))
        self._query = query

    def retrieve_and_save_data_from_newsapi_by_terms(self, terms):

        # todo: The class name for newsapi articles is NewsArticle (title, description, content, etc.) and additional
        # todo: article information is saved using NewsArticleItems object, with respective tables at the DB.

        posts_lst, claims_lst, articles_lst, article_items_lst = self.get_articles_by_terms(terms)
        self._db.addPosts(posts_lst)
        self._db.add_claims(claims_lst)
        self._db.addArticles(articles_lst)
        self._db.addArticleItems(article_items_lst)

    def get_articles_by_terms(self, terms):
        print("###### 'ENTERING: get_articles_by_terms'")
        all_articles = []
        # params = {'language': 'en', 'sort_by': 'relevancy', 'page_size': 100}  # Max page_size is 100.
        params = ast.literal_eval(self._query)

        print("###### 'NewsAPI_Crawler query: {}".format(params))

        for term in terms:
            i = 0
            while True:
                i += 1  # Page numbers begin at 1.
                try:
                    all_articles.append(self._newsapi_client.get_everything(q=term, page=i, **params))
                except NewsAPIException:
                    print("Reached the last page of term: {}".format(term))
                    break  # Stops loop and moves to the next term.

        print("##### All articles from newsAPI: {} ######".format(str(all_articles)))
        print("###### 'EXITING: get_articles_by_terms'")
        return self._parse_articles_lst_to_articles(all_articles)

    def _parse_news_article(self, news_articles):
        print("###### 'Entering _parse_news_article'")
        articles_lst_of_dic = []
        for article_dic in news_articles['articles']:
            print("##### Current article dictionary from newsAPI: {} ######".format(str(article_dic)))
            tmp_lst = {'author': str(article_dic['author']),
                       'content': str(article_dic['content']),  # todo: crawl full content for certain sites.
                       'description': str(article_dic['description']),
                       'publishedAt': str(article_dic['publishedAt']).replace('T', ' ').replace('Z', ''),
                       'source_id': str(article_dic['source']['id']),
                       'source_name': str(article_dic['source']['name']),
                       'title': str(article_dic['title']),
                       'url': str(article_dic['url']),
                       'urlToImage': str(article_dic['urlToImage'])}
            tmp_lst = {k: "" if (v is None or v == "null") else v for k, v in tmp_lst.items()}
            articles_lst_of_dic.append(tmp_lst)

        print("###### 'parse_news_article' return value is the dictionary 'articles_lst_of_dic': {}".format(articles_lst_of_dic))
        print("###### EXITING 'parse_news_article'")
        return articles_lst_of_dic

    def _parse_articles_lst_to_articles(self, all_articles_lst_of_dics):
        print("###### 'Entering _parse_articles_lst_to_articles'")
        parsed_articles_lst = []
        claims_lst = []
        posts_lst = []
        articles_lst = []
        article_items_lst = []

        # Parsing articles list of dictionaries data, received using the API.
        for news_articles_dic in all_articles_lst_of_dics:
            print("###### 'PARSING: {}'".format(str(news_articles_dic)))
            parsed_articles_lst += self._parse_news_article(news_articles_dic)

        # For each news article dictionary commit:
        for parsed_news_article in parsed_articles_lst:
            print("###### 'Iterating parsed_articles_lst single item: {}'".format(str(parsed_news_article)))
            # Building: claim & News_Article & News_Article_Item objects.
            claim = Claim()
            post = Post()
            article = News_Article()
            article_item = News_Article_Item()

            # Initializing Claim object with data:
            identifier = compute_post_guid(parsed_news_article['url'], parsed_news_article['author'], parsed_news_article['publishedAt'])
            claim.claim_id = post.post_id = post.guid = post.post_osn_guid = article.post_id = article_item.post_id = unicode(identifier)

            author_guid = compute_author_guid_by_author_name(parsed_news_article['author'])
            post.author_guid = article.author_guid = article_item.author_guid = unicode(author_guid)

            post.author = article.author = unicode(parsed_news_article['author'])

            post.title = claim.title = article.title = unicode(parsed_news_article['title'])

            post.content = article_item.content = unicode(parsed_news_article['content'])

            post.description = claim.description = article.description = unicode(parsed_news_article['description'])

            post.date = post.created_at = claim.verdict_date = article.published_date = datetime.datetime.strptime(parsed_news_article['publishedAt'], '%Y-%m-%d %H:%M:%S')

            article_item.source_newsapi_internal_id = unicode(parsed_news_article['source_id'])

            article_item.source_newsapi_internal_name = unicode(parsed_news_article['source_name'])

            post.url = claim.url = article.url = unicode(parsed_news_article['url'])

            article_item.img_url = unicode(parsed_news_article['urlToImage'])

            post.post_type = claim.verdict = unicode("TRUE")  # todo: Add constant. We assume all news articles are true.

            post.domain = claim.domain = unicode("NewsSite")  # todo: Add constant.

            # Update objects lists:
            posts_lst.append(post)
            claims_lst.append(claim)
            articles_lst.append(article)
            article_items_lst.append(article_item)
        print("###### 'EXITING _parse_articles_lst_to_articles'")
        return posts_lst, claims_lst, articles_lst, article_items_lst
