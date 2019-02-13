# -*- coding: utf-8 -*-
import scrapy
import const
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor
import csv
#import unicodecsv as csv
import datetime
import locale
locale.setlocale(locale.LC_ALL, 'esp_esp')
cheq_filename = 'C:\\users\\admin\\Documents\\chequeado_com-ultimas-noticias.csv'
cotejo_filename = 'C:\\users\\admin\\Documents\\cotejo.csv'
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


class ChequeadoSpider(scrapy.Spider):
        name = 'chequeado_spider'
        cnt = 10
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
                    p_date = quote.css('div.four-fifth').get().split('(')[1].split(')')[0]
                    publication_date = datetime.datetime.strptime(p_date, '%d de %B de %Y').strftime('%Y-%m-%d %H:%M:%S')
                    verdict = translate_verdict(quote.css('article').get().split('calificaciones-')[1].split(' ')[0])
                    title = quote.css('h2.post-title  a::text').get().split(':')[1].replace(u'“', '')
                    author = quote.css('h2.post-title  a::text').get().split(':')[0]
                    description = quote.css('div.four-fifth::text').get()
                    url = quote.css('h2.post-title  a').get().split(' ')[1].replace('href=', '').replace('"', '')
                    main_category = quote.css('article').get().split('category-')[1].split(' ')[0]
                    secondary_category = quote.css('article').get().split('tag-')[1].split(' ')[0]
                    raw_claim_id = quote.css('article').get().split(' ')[1].replace('id=','')
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
            if self.cnt==2000:
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

    




