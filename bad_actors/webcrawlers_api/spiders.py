# -*- coding: utf-8 -*-
import scrapy
import const
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor
#from bad_actors.commons.commons import *
import csv

#import unicodecsv as csv
import datetime
import locale
locale.setlocale(locale.LC_ALL, 'esp_esp')
cheq_filename = 'C:\\users\\admin\\Documents\\chequeado_com-ultimas-noticias.csv'
cotejo_filename = 'C:\\users\\admin\\Documents\\cotejo.csv'
import uuid
import unicodedata
import datetime
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


def translate_verdict(sp_verdict, split=False):
    en_sp_dict = const.EN_SP_VERDICTS
    for en_ver, sp_vers in en_sp_dict.items():
        if sp_verdict in sp_vers:
            return en_ver
    split_verdict = sp_verdict.split('"')
    if not split:
        if translate_verdict(split_verdict[0], split=True) != 'Unknown':
            return translate_verdict(split_verdict[0], split=True)
        return translate_verdict(split_verdict[1], split=True)
    return 'Unknown'


encode_scm='ascii' #'utf8'  'ascii'
errors='ignore'  #'strict' 'ignore' 'xmlcharrefreplace'

def createunicodedata(data):   
    return unicodedata.normalize('NFKD', unicode(data)).encode('ascii', 'ignore')

def generate_random_guid(ocn_id):
    class NULL_NAMESPACE:
        bytes = b''
    post_guid = uuid.uuid3(NULL_NAMESPACE, ocn_id.encode('utf-8'))
    str_author_guid = unicode(str(post_guid))
    return str_author_guid

def str_to_date(dd, formate="%Y-%m-%d %H:%M:%S"):    
    #dd='17 de Diciembre de 2018'
        
    mnth={'Enero':'01',
          'Febrero':'02',
          'Marzo':'03',
          'Abril':'04',
          'Mayo':'05',
          'Junio':'06',
          'Julio':'07',
          'Agosto':'08',
          'Septiembre':'09',
          'Octubre':'10',
          'Noviembre':'11',
          'Diciembre':'12',
          }
    try:
        de=dd.split(' de ')
        datestring=de[-1]+'-'+mnth[de[1]]+'-'+de[0]+' 12:00:00'   
        return datetime.datetime.strptime(datestring, formate)
    except:
        return '2019-02-13 01:02:03'
        
def verdict_en(verdict):
    dict_v={'verdadero':'True',
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
          'inchequeable':'Unbreakable'
    
          }
    try:        
        verd=dict_v[verdict.split('"')[0]]
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

        cnt=293        
        start_urls = [
            "https://chequeado.com/ultimas-noticias/"
        ]

        def parse(self, response):
            csvfile = open(cheq_filename, 'ab+')
            #writer = csv.DictWriter(csvfile, fieldnames=fieldnames, encoding='utf-8')
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            print(self.cnt)
            #for quote in response.css('div.post-inner'):
            for quote in response.css('article'):   
                try:

                    print({                         
                        
                        'publication_date': str_to_date(quote.css('div.four-fifth').get().split('(')[1].split(')')[0]),
                        
                        'verdict': verdict_en(quote.css('article').get().split('calificaciones-')[1].split(' ')[0]), 
                                        
                    })                
                   
                    writer.writerow({
                        'author': createunicodedata(quote.css('h2.post-title  a::text').get().split(':')[0]),
                        'claim_id': createunicodedata(generate_random_guid(quote.css('article').get().split(' ')[1].replace('id=',''))),
                        'title': createunicodedata(quote.css('h2.post-title  a::text').get()),
                        'description': createunicodedata(quote.css('div.four-fifth::text').get()),                    
                        'url': createunicodedata(quote.css('h2.post-title  a').get().split(' ')[1].replace('href=','').replace('"','')),
                        'publication_date': createunicodedata(str_to_date(quote.css('div.four-fifth').get().split('(')[1].split(')')[0])),
                        'keywords': ' ',
                        'domain': createunicodedata('Claim'),
                        'main_category': createunicodedata(catclean(quote.css('article').get().split('category-')[1].split(' ')[0])),
                        'secondary_category': createunicodedata(catclean(quote.css('article').get().split('tag-')[1].split(' ')[0])),
                        'verdict': createunicodedata(verdict_en(quote.css('article').get().split('calificaciones-')[1].split(' ')[0])),                    
                })

                except:
                    pass
            csvfile.close()              
            
            pages = response.css('div.wp-pagenavi a::attr(href)').getall()
#             if self.cnt==0:
#                 next_page=pages[0]
#             else:
#                 next_page=pages[2]
            if self.cnt==2400:
                return                           
            
            if pages is not None:
                self.cnt+=1                
                next_page = response.urljoin('/ultimas-noticias/page/'+str(self.cnt)+'/')                               
                yield scrapy.Request(next_page, callback=self.parse)


class CotejoSpider(scrapy.Spider):
    name = 'cotejo_spider'
    cnt = 10
    start_urls = ["https://cotejo.info/"]

    def parse(self, response):
        csvfile = open(cotejo_filename, 'ab+')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        print(self.cnt)
        # for quote in response.css('div.post-inner'):
        for quote in response.css('article'):
            try:
                p_date = quote.css('div.four-fifth').get().split('(')[1].split(')')[0]
                publication_date = datetime.datetime.strptime(p_date, '%d de %B de %Y').strftime('%Y-%m-%d %H:%M:%S')
                verdict = self.translate_verdict(quote.css('article').get().split('calificaciones-')[1].split(' ')[0])
                title = quote.css('h2.post-title  a::text').get().split(':')[1].replace(u'“', '')
                author = quote.css('h2.post-title  a::text').get().split(':')[0]
                description = quote.css('div.four-fifth::text').get()
                url = quote.css('h2.post-title  a').get().split(' ')[1].replace('href=', '').replace('"', '')
                main_category = quote.css('article').get().split('category-')[1].split(' ')[0]
                secondary_category = quote.css('article').get().split('tag-')[1].split(' ')[0]
                raw_claim_id = quote.css('article').get().split(' ')[1].replace('id=', '')
                domain = 'Claim'
                print({
                    'author': author,
                    'claim_id': raw_claim_id,
                    'title': title,
                    'description': description,
                    'url': url,
                    'publication_date': publication_date,
                    'main_category': main_category,
                    'verdict': verdict,
                    'secondary_category': secondary_category,
                })

                writer.writerow({
                    'author': author.encode('utf8'),
                    'claim_id': raw_claim_id.encode('utf8'),
                    'title': title.encode('utf-8'),
                    'description': description.encode('utf8'),
                    'url': url.encode('utf8'),
                    'publication_date': publication_date,
                    'keywords': ' ',
                    'domain': domain,
                    'main_category': main_category.encode('utf8'),
                    'secondary_category': main_category.encode('utf8'),
                    'verdict': verdict,
                })
            except:
                pass
        csvfile.close()

        pages = response.css('div.wp-pagenavi a::attr(href)').getall()
        #             if self.cnt==0:
        #                 next_page=pages[0]
        #             else:
        #                 next_page=pages[2]
        if self.cnt == 2000:
            return

        if pages is not None:
            self.cnt += 1
            next_page = response.urljoin('/ultimas-noticias/page/' + str(self.cnt) + '/')
            yield scrapy.Request(next_page, callback=self.parse)

    def parse(self):
        pass


def f(q, spiders):
        try:
            runner = crawler.CrawlerRunner()
            for spider in spiders:
                deferred = runner.crawl(spider)
            reactor.run()
            deferred.addBoth(lambda _: reactor.stop())
            print('reactor, stop-start')
            reactor.run()
            q.put(None)
        except Exception as e:
            print('run reactor exception occured!')
            q.put(e)


# the wrapper to make it run more times
def run_spider(spiders):
    
    q = Queue()
    p = Process(target=f, args=(q,spiders))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
    
    
if __name__ == '__main__':
    ChS = ChequeadoSpider
    CoS = CotejoSpider
    #run_spider([ChS, Cos])
    run_spider([ChS])

    

   
"""writer.writerow({                   
                        'author': quote.css('h2.post-title  a::text').get().split(':')[0].encode('utf8'),                     
                        'claim_id': quote.css('article').get().split(' ')[1].replace('id=','').encode('utf8'),
                        'title': quote.css('h2.post-title  a::text').get().split(':')[1].encode('utf8'),
                        'description': quote.css('div.four-fifth::text').get().encode('utf8'),                    
                        'url': quote.css('h2.post-title  a').get().split(' ')[1].replace('href=','').encode('utf8'),
                        'publication_date': quote.css('div.four-fifth').get().split('(')[1].split(')')[0].encode('utf8'),
                        'keywords': ' ',
                        'domain': 'Claim',
                        'main_category': quote.css('article').get().split('category-')[1].split(' ')[0].encode('utf8'),
                        'secondary_category': quote.css('article').get().split('tag-')[1].split(' ')[0].encode('utf8'),
                        'verdict': quote.css('article').get().split('calificaciones-')[1].split(' ')[0].encode('utf8'),                    
                })
               """



