from __future__ import print_function
from preprocessing_tools.abstract_controller import AbstractController
from DB.schema_definition import *
from BeautifulSoup import BeautifulSoup, SoupStrainer
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)


class CategoryFillerForClaims(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)
        self.necessary_columns = self._config_parser.eval(self.__class__.__name__, 'columns')
        self._snopes_strainer = SoupStrainer("li", {"class": "breadcrumb-item"})
        self._header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

    def execute(self, window_start):
        self.add_missing_columns()
        claims = self._db.get_claims_missing_category()
        claims_with_cats = self.add_categories_to_claims(claims)
        self._db.add_claims(claims_with_cats)

    def add_missing_columns(self):
        cols = self._db.get_claims_columns()
        cols_to_add = []
        for col_name in self.necessary_columns:
            if unicode(col_name) not in cols:
                cols_to_add.append({'name': col_name, 'type': 'Unicode'})
        self._db.add_columns('claims', cols_to_add)

    def add_categories_to_claims(self, claims):
        claims_with_cats = []
        failed_count = 0
        total = len(claims)
        for cnt, claim in enumerate(claims):
            msg = '\rAdding category to claim [{} / {}]'.format(cnt, total)
            print(msg, end="")
            url = claim.url
            try:
                if url[:18] == 'https://www.snopes':
                    cats = self.get_categories_snopes(url)
                elif url[:26] == 'http://www.politifact.com/':
                    cats = self.get_categories_politifact(url)
            except:
                failed_count += 1
            claim.main_category = cats[0]
            claim.secondary_category = cats[1]
            claims_with_cats.append(claim)
        if failed_count > 0:
            print('Failed to find categories for {} claims'.format(failed_count))
        return claims_with_cats

    def get_categories_snopes(self, url):
        response = urllib2.urlopen(url).read()
        soup = BeautifulSoup(response, parseOnlyThese=self._snopes_strainer)
        cats = []
        for li in soup.findAll('li'):
            if BeautifulSoup(str(li)).find('a').contents:
                cats.append(BeautifulSoup(str(li)).find('a').contents[0])
            else:
                cats.append(None)
        return cats

    def get_categories_politifact(self, url):
        hdr = self._header
        response = urllib2.Request(url, headers=hdr)
        page = urllib2.urlopen(response).read()
        soup = BeautifulSoup(page, parseOnlyThese=SoupStrainer('p'))
        tag = soup.find(text='Subjects: ')
        return [u'Politics', tag.next.contents[0]]
