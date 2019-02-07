import const
from webcrawlers_exception import WebCrawlersAPIException
import scrapy
from scrapy.crawler import CrawlerProcess

class WebCrawlersClient(object):

    def __init__(self):
        print("New web crawler initialized.")

    def get_top_headlines(self, q=None, site=None, category=None, from_date=None, to_date=None):
        """
        Returns live top and breaking headlines for a country, specific category in a country, single source, or
        multiple sources.

        Optional parameters:
        (str) q - return headlines w/ specific keyword or phrase. For example:
                    'bitcoin', 'trump', 'tesla', 'ethereum', etc.
        (str) site - Supported news site to get results from.
        (str) category - Choose certain section of atricles inside the website.
        (str) from_date - Including.
        (str) to_date - Including.
        """
        pass

    def get_everything(self, q=None, site=None, categories=None, from_date=None, to_date=None):
        """
        Search through articles of fact checking sites.

        Optional parameters:
        (str) q - return headlines w/ specific keyword or phrase. For example:
                    'bitcoin', 'trump', 'tesla', 'ethereum', etc.
        (str) site - Supported news site to get results from.
        (str) category - Choose certain section of atricles inside the website.
        (str) from_date - Including.
        (str) to_date - Including.
        """

        # Define Payload
        payload = {}

        # Keyword/Phrase
        if q is not None:
            if type(q) == str:
                payload['q'] = q
            else:
                raise TypeError('keyword/phrase q param should be of type str')

        # Sources
        if site is not None:
            if type(site) == str:
                payload['site'] = site
            else:
                raise TypeError('site param should be of type str')
        else:
            ValueError('Site name is a required field.')

        # Categories To Search
        if categories is not None:
            if type(categories) == str:
                payload['category'] = categories.split(',')
            else:
                raise TypeError('category param should be of type str')

        # Search From This Date ...
        if from_date is not None:
            if type(from_date) == str:
                if (len(from_date)) >= 10:
                    for i in range(len(from_date)):
                        if (i == 4 and from_date[i] != '-') or (i == 7 and from_date[i] != '-'):
                            raise ValueError('from_date should be in the format of YYYY-MM-DD')
                        else:
                            payload['from'] = from_date
                else:
                    raise ValueError('from_date should be in the format of YYYY-MM-DD')
            else:
                raise TypeError('from_date should be of type str')

        # ... To This Date
        if to_date is not None:
            if type(to_date) == str:
                if (len(to_date)) >= 10:
                    for i in range(len(to_date)):
                        if (i == 4 and to_date[i] != '-') or (i == 7 and to_date[i] != '-'):
                            raise ValueError('to_date should be in the format of YYYY-MM-DD')
                        else:
                            payload['to'] = to_date
                else:
                    raise ValueError('to_date param should be in the format of YYYY-MM-DD')
            else:
                raise TypeError('to_date param should be of type str')

        return self._get_everything(payload)  # Returns a dictionary. with 'articles', , , keys.

    def get_sources(self):
        """
        Returns a list of fact checking site names and URLs that are currently supported by the crawler.
        """
        return str(const.SUPPORTED_URLS)

    def _get_everything(self, payload):
        articles = {}
        if payload['site'] in const.SUPPORTED_SITES:
            articles = self._crawl_site(payload['site'])
            articles = self._filter_results(articles, payload)
        else:
            ValueError('This site is yet to be supported.')
        return articles

    def _crawl_site(self, site_name):
        if site_name == "chequeado":
            process = CrawlerProcess({
                'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
            })

            process.crawl(self.ChequeadoSpider)
            process.start()  # the script will block here until the crawling is finished

    def _filter_results(self, articles_dic, payload):
        """
        Used to filter scrapped data according to the flags given in the payload.
        :param articles_dic:
        :param payload:
        :return:
        """
        pass

    class ChequeadoSpider(scrapy.Spider):
        name = 'chequeado_spider'
        start_urls = [
            const.SUPPORTED_SITES["chequeado"],
        ]

        def parse(self, response):
            # todo: example for crawling using xpath.
            for quote in response.xpath('//div[@class="quote"]'):
                yield {
                    'text': quote.xpath('./span[@class="text"]/text()').extract_first(),
                    'author': quote.xpath('.//small[@class="author"]/text()').extract_first(),
                    'tags': quote.xpath('.//div[@class="tags"]/a[@class="tag"]/text()').extract()
                }

            next_page_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
            if next_page_url is not None:
                yield scrapy.Request(response.urljoin(next_page_url))
