import scrapy
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor
import csv
filename='D:\\chequeado_com-ultimas-noticias.csv'
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

class ChequeadoSpider(scrapy.Spider):
        name = 'chequeado_spider'
        cnt=1        
        start_urls = [
            "https://chequeado.com/ultimas-noticias/",
            "https://cotejo.info/",
        ]
 
        def parse(self, response):      

            csvfile=open(filename, 'ab+')
                     
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)       
            print(self.cnt)
            #for quote in response.css('div.post-inner'):
            for quote in response.css('article'):   
                try:
                    print({
                        'author': quote.css('h2.post-title  a::text').get().split(':')[0], 
                        'claim_id': quote.css('article').get().split(' ')[1].replace('id=',''),
                        'title': quote.css('h2.post-title  a::text').get(),
                        'description': quote.css('div.four-fifth::text').get(),                    
                        'url': quote.css('h2.post-title  a').get().split(' ')[1].replace('href=',''),
                        'publication_date': quote.css('div.four-fifth').get().split('(')[1].split(')')[0],
                        'main_category': quote.css('article').get().split('category-')[1].split(' ')[0],
                        'verdict': quote.css('article').get().split('calificaciones-')[1].split(' ')[0], 
                        'secondary_category': quote.css('article').get().split('tag-')[1].split(' ')[0],                 
                    })                
                   
                    writer.writerow({                   
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

def f(q,spider):
        try:
            runner = crawler.CrawlerRunner()
            deferred = runner.crawl(spider)
            deferred.addBoth(lambda _: reactor.stop())
            print('reactor, stop-start')
            reactor.run()
            q.put(None)
        except Exception as e:
            print('run reactor exception occured!')
            q.put(e)
# the wrapper to make it run more times
def run_spider(spider):
    
    q = Queue()
    p = Process(target=f, args=(q,spider))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
    
    
if __name__ == '__main__':  
    
    csvfile=open(filename, 'wb')   
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.close()
    
    CS=ChequeadoSpider
    run_spider(CS)
      
    




