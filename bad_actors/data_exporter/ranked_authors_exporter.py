from __future__ import print_function
from DB.schema_definition import *
from configuration.config_class import getConfig
import csv

class RankedAuthorsExporter(object):
    def __init__(self, db):
        self._db = db
        self._config_parser = getConfig()
        self.threshold = self._config_parser.eval(self.__class__.__name__, "threshold")
        self.output_file_path = self._config_parser.eval(self.__class__.__name__, "output_file_path")

    def setUp(self):
        pass

    def execute(self, window_start):
        ranked_authors = self.get_ranked_authors()
        self._db.delete_sorted_authors_table()
        self.write_to_csv(ranked_authors)

    def get_ranked_authors(self):
        self._db.make_sorted_authors_table()
        all_authors = self._db.get_all_sorted_authors()
        total_authors = len(all_authors)
        authors_above_threshold = []
        authors_below_threshold = []
        i = 0
        for author in all_authors:
            msg = '\rRanking author [{}/{}]'.format(i, total_authors)
            print(msg, end='')
            i += 1
            #print(author)
            if self._db.is_within_threshold(author[0], author[2], self.threshold):
                authors_above_threshold.append(author + (1,))
            else:
                authors_below_threshold.append(author + (0,))
        print('\r')
        #print(authors_above_threshold)
        #print(authors_below_threshold)
        return authors_above_threshold + authors_below_threshold

    def write_to_csv(self, ranked_authors):
        with open(self.output_file_path, 'wb') as f:
            print('Writing {} ranked authors to csv'.format(len(ranked_authors)))
            writer = csv.writer(f)
            writer.writerow(['author_guid', 'author_screen_name', 'claim_id', 'post_id', 'post_speed', 'first_{}'.format(self.threshold)])
            writer.writerows(ranked_authors)

    def is_well_defined(self):
        return True