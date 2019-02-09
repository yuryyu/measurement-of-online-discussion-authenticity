import scrapy
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor


class ChequeadoSpider(scrapy.Spider):
        name = 'chequeado_spider'
        cnt=1
        req_list=[]
        start_urls = [
            "https://chequeado.com/ultimas-noticias/",
        ]
 
        def parse(self, response):      

            for quote in response.css('div.post-inner'):
                print({
                    'claim': quote.css('h2.post-title  a::text').get().split(':')[1],
                    'author': quote.css('h2.post-title  a::text').get().split(':')[0],
                    'text': quote.css('div.four-fifth::text').get(),
                })
                self.req_list.append({
                    'claim': quote.css('h2.post-title  a::text').get().split(':')[1],
                    'author': quote.css('h2.post-title  a::text').get().split(':')[0],
                    'text': quote.css('div.four-fifth::text').get(),
                })
                
            print(len(self.req_list))
            pages = response.css('div.wp-pagenavi a::attr(href)').getall()
            if self.cnt==0:
                next_page=pages[0]
            else:
                next_page=pages[2]
            if self.cnt==2:
                return   
                           
            print(pages)
            if next_page is not None:
                self.cnt+=1                
                next_page = response.urljoin('/ultimas-noticias/page/'+str(self.cnt)+'/')
                #next_page = next_page.replace('/'+str(self.cnt)+'/','/'+str(self.cnt+1)+'/')
                print('next page is '+next_page)                
                yield scrapy.Request(next_page, callback=self.parse)
            
#             page = response.url.split("/")[-2]
#             filename = 'D:\\chequeado-%s.html' % page
#             with open(filename, 'wb') as f:
#                 f.write(response.body)



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
    
    CS=ChequeadoSpider
    run_spider(CS)
    rez=CS.req_list   
    




