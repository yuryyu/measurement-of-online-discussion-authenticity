# -*- coding: utf-8 -*-
import scrapy
import const
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor
import csv
import datetime
import locale
locale.setlocale(locale.LC_ALL, 'esp_esp')
cheq_filename = 'C:\\users\\admin\\Documents\\chequeado_com-ultimas-noticias.csv'
cotejo_filename = 'C:\\users\\admin\\Documents\\cotejo_info-cotejado-a-fondo.csv'
import uuid
import unicodedata
import datetime
import re
import urllib2
import urlparse
import sys
from bs4 import BeautifulSoup
fieldnames = ['author',
                'claim_id',
                'title',
                'description',                    
                'url',
                'publication_date',
                'keywords',
                'domain',
                'main_category',
                'secondary_category',
                'verdict']

encode_scm = 'ascii' #'utf8'  'ascii'
errors = 'ignore'  #'strict' 'ignore' 'xmlcharrefreplace'


def createunicodedata(data):   
    return unicodedata.normalize('NFKD', unicode(data)).encode('ascii', 'ignore')


def generate_random_guid(ocn_id):
    class NULL_NAMESPACE:
        bytes = b''
    post_guid = uuid.uuid3(NULL_NAMESPACE, ocn_id.encode('utf-8'))
    str_author_guid = unicode(str(post_guid))
    return str_author_guid


def str_to_date(dd, d_format='%d de %B de %Y'):
    try:
        return datetime.datetime.strptime(dd, d_format).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return '2019-02-13 01:02:03'
        
def verdict_en(verdict):
    dict_v={'verdadero':'True',
            'verdad': 'True',
            'falso':'False',
            'enganoso':'Deceitful',
            'apresurado':'Hasty',
            'exagerado':'Exaggerated',
            'incumplida':'Unfulfilled',
            'verdadero-pero':'True-but',
            'cumplida':'Fulfilled',
            'en-progreso-adelantada':'In-progress-ahead',
            'en-progreso-demorada':'In-progress-delayed',
            'discutible':'Arguable',
            'insostenible':'Untenable',
            'inchequeable':'Unbreakable',
            'mentira': 'lie',
            'contejado a fondo': 'thoroughly discussed',
            'media-verdad': 'half-true'
            }
    try:        
        verd=dict_v[verdict.lower().split('"')[0]]
    except:
        print(verdict)
        verd=verdict            
    return verd


def catclean(catteg):
    dda=['c34-','c41-','c49-','c60-','">','<div','"']
    for dd in dda:
        catteg=catteg.replace(dd,'')    
    return catteg


class ChequeadoSpider(scrapy.Spider):
        name = 'chequeado_spider'
        cnt = 293
        start_urls = [
            "https://chequeado.com/ultimas-noticias/"
        ]
        csvfile = open(cheq_filename, 'ab+')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #writer.writeheader()

        def parse(self, response):
            print(self.cnt)
            #for quote in response.css('div.post-inner'):
            for quote in response.css('article'):   
                try:
                    print({
                        'publication_date': str_to_date(quote.css('div.four-fifth').get().split('(')[1].split(')')[0],
                                                        '%d de %B de %Y'),
                        'verdict': verdict_en(quote.css('article').get().split('calificaciones-')[1].split(' ')[0]),
                    })
                    self.writer.writerow({
                        'author': createunicodedata(quote.css('h2.post-title  a::text').get().split(':')[0]),
                        'claim_id': createunicodedata(generate_random_guid(quote.css('article').get().split(' ')[1].replace('id=',''))),
                        'title': createunicodedata(quote.css('h2.post-title  a::text').get()),
                        'description': createunicodedata(quote.css('div.four-fifth::text').get().lstrip()),
                        'url': createunicodedata(quote.css('h2.post-title  a').get().split(' ')[1].replace('href=','').replace('"','')),
                        'publication_date': createunicodedata(str_to_date(quote.css('div.four-fifth').get().split('(')[1]
                                                                          .split(')')[0], '%d de %B de %Y')),
                        'keywords': ' ',
                        'domain': createunicodedata('Claim'),
                        'main_category': createunicodedata(catclean(quote.css('article').get().split('category-')[1].split(' ')[0])),
                        'secondary_category': createunicodedata(catclean(quote.css('article').get().split('tag-')[1].split(' ')[0])),
                        'verdict': createunicodedata(verdict_en(quote.css('article').get().split('calificaciones-')[1].split(' ')[0])),                    
                })
                except:
                    pass
            pages = response.css('div.wp-pagenavi a::attr(href)').getall()
            if self.cnt == 2400:
                return
            next_page_link = response.css('a.nextpostslink').get()
            if next_page_link is None:
                #self.csvfile.close()
                #print 'finished Chequedo.com spider'
                return

            if pages is not None:
                self.cnt += 1
                next_page = response.urljoin('/ultimas-noticias/page/'+str(self.cnt)+'/')                               
                yield scrapy.Request(next_page, callback=self.parse)



class CotejoSpider(scrapy.Spider):
    name = 'cotejo_spider'
    cnt = {"https://cotejo.info/category/cotejado-a-fondo/": 1,
           "https://cotejo.info/category/regionales/": 1,
           "https://cotejo.info/category/cotejos-breves/": 1}
    start_urls = [
        "https://cotejo.info/category/cotejado-a-fondo/",
        "https://cotejo.info/category/regionales/",
        "https://cotejo.info/category/cotejos-breves/"
    ]
    csvfile = open(cotejo_filename, 'ab+')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #writer.writeheader()

    def get_author(self, article_url):
        html = urllib2.urlopen(article_url).read()
        soup = BeautifulSoup(html, features="lxml")
        author_div = soup.find_all('div', {'class': 'entry-content'})[0]
        p_tags = author_div.find_all('p')
        author_string = p_tags[len(p_tags) - 1].get_text()
        try:
            if author_string.strip() == '':
                author_string = p_tags[len(p_tags) - 2].find('span').get_text()
        except:
            try:
                author_string = p_tags[len(p_tags) - 1].find('span').get_text()
            except:
                author_string = ''
        try:
            author = re.search('Por (.*) para', author_string).group(1)
        except:
            try:
                author = re.search('(.*) para', author_string).group(1)
            except:
                author = 'Unknown'
        if len(author) > 40:
            author = 'Unknown'
        return author

    def parse(self, response):
        print response.request.url.split('page')[0] + ' page ' + str(self.cnt[response.request.url.split('page')[0]])
        for quote in response.css('div[class*=blog-post]'):
            try:
                url = quote.css('div.bp-details a::attr(href)').get()
                classes = quote.xpath('@class').get().split(' ')
                if 'category-mentira' in classes:
                    verdict = verdict_en('mentira')
                elif 'category-verdad' in classes:
                    verdict = verdict_en('verdad')
                elif 'category-media-verdad' in classes:
                    verdict =verdict_en('media-verdad')
                else:
                    verdict = 'Unknown'
                for cls in classes:
                    match = re.search('^post-(\d*)', cls)
                    if match:
                        post_id = match.group(1)
                        continue
                author = createunicodedata(quote.css('span[itemprop=author] a::text').get())
                if author == 'prensa':
                    author = self.get_author(url)
                print({
                    'publication_date': str_to_date(quote.css('div.mom-post-meta')
                                        .xpath('./span[2]/time/@datetime').get().split('+')[0], '%Y-%m-%dT%H:%M:%S'),
                    'verdict': verdict,
                })
                self.writer.writerow({
                    'author': createunicodedata(author),
                    'claim_id': createunicodedata(
                        generate_random_guid(post_id)),
                    'title': createunicodedata(quote.css('a::text').get()),
                    'description': createunicodedata(quote.css('div.bp-details p::text').get().lstrip()),
                    'url': createunicodedata(url),
                    'publication_date': createunicodedata(str_to_date(quote.css('div.mom-post-meta')
                                         .xpath('./span[2]/time/@datetime').get().split('+')[0], '%Y-%m-%dT%H:%M:%S')),
                    'keywords': ' ',
                    'domain': createunicodedata('Claim'),
                    'main_category': 'Politics',
                    'secondary_category': 'Venezuela',
                    'verdict': createunicodedata(verdict),
                })
            except:
                pass
        num_pages = len(response.css('div.pagination a::attr(href)').getall()) + 1
        self.cnt[response.url.split('page')[0]] += 1
        if self.cnt[response.url.split('page')[0]] > num_pages:
            #self.cnt[response.url.split('page')[0]] = 1
            return
        page_str = 'page/' + str(self.cnt[response.url.split('page')[0]]) + '/'
        if 'page' in response.request.url:
            next_page = response.request.url[:-7] + page_str
        else:
            next_page = response.request.url + page_str
        yield scrapy.Request(next_page, callback=self.parse)


def f(q, spiders):
        try:
            runner = crawler.CrawlerRunner({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
            for spider in spiders:
                deferred = runner.crawl(spider)
            #reactor.run()
            deferred.addBoth(lambda _: reactor.stop())
            print('reactor, stop-start')
            reactor.run()
            q.put(None)
        except Exception as e:
            print('run reactor exception occured!')
            q.put(e)


# the wrapper to make it run more times
def run_spiders(spiders):
    
    q = Queue()
    p = Process(target=f, args=(q,spiders))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
    
    
if __name__ == '__main__':
    for file in [cheq_filename, cotejo_filename]:
        csvfile = open(file, 'wb')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        csvfile.close()
    ChS = ChequeadoSpider
    CoS = CotejoSpider
    #run_spiders([ChS, CoS])
    run_spiders([CoS])

