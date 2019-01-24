from __future__ import print_function
from DB.schema_definition import *
from configuration.config_class import getConfig
import csv
import datetime

class RankedAuthorsExporter(object):
    def __init__(self, db):
        self._db = db
        self._config_parser = getConfig()
        self.threshold = self._config_parser.eval(self.__class__.__name__, "threshold")
        self.output_file_path = self._config_parser.eval(self.__class__.__name__, "output_file_path")
<<<<<<< HEAD
        self.output_file_path = self.output_file_path.format(
            datetime.datetime.today().strftime('%d/%m/%Y'), self.threshold)
=======
        self.output_file_path = self.output_file_path.format(datetime.datetime.today().strftime('%d/%m/%Y'), self.threshold)
>>>>>>> ee8c5c26e20692ffeda312466aa46d5c3fe387f1

    def setUp(self):
        pass

    def execute(self, window_start):
        ranked_authors = self.get_ranked_authors()
        self.write_to_csv(ranked_authors)

    def get_ranked_authors(self):
        print('Getting authors from databse sorted by post speed...')
        all_authors = self._db.get_sorted_authors()
        claims_authors_dict = self.make_threshold_dic(all_authors)
        total_authors = len(all_authors)
        authors_above_threshold = []
        authors_below_threshold = []
        i = 1
        for claim in claims_authors_dict:
            for author in claims_authors_dict[claim][:self.threshold]:
                msg = '\rRanking author [{}/{}]'.format(i, total_authors)
                print(msg, end='')
                i += 1
                #print(author)
                authors_above_threshold.append(author + [1])
            for author in claims_authors_dict[claim][self.threshold:]:
                msg = '\rRanking author [{}/{}]'.format(i, total_authors)
                print(msg, end='')
                i += 1
                authors_below_threshold.append(author + [0])
        print('\r')
        authors_above_threshold.sort(key=lambda x: x[4], reverse=True)
        authors_below_threshold.sort(key=lambda  x: x[4], reverse=True)
        return authors_above_threshold + authors_below_threshold

    def make_threshold_dic(self, sorted_authors):
        print('Making dictionary of authors in claims...')
        authors_for_claims_dict = {}
        for author in sorted_authors:
            #print(author)
            try:
                authors_for_claims_dict[author[2]].append(author)
            except KeyError:
                authors_for_claims_dict[author[2]] = [author]
        #print(authors_for_claims_dict)
        return authors_for_claims_dict

    def write_to_csv(self, ranked_authors):
        with open(self.output_file_path, 'wb') as f:
            print('Writing {} ranked authors to csv'.format(len(ranked_authors)))
            writer = csv.writer(f)
            writer.writerow(['author_guid', 'author_screen_name', 'claim_id', 'post_id', 'post_speed', 'first_{}'.format(self.threshold)])
            writer.writerows(ranked_authors)

    def is_well_defined(self):
        return True