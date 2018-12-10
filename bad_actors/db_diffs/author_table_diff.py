from __future__ import print_function
#import csv
#from configuration.config_class import getConfig
from DB.schema_definition import *
from db_diffs.Secondary_DB import SecondaryDB


class AuthorTableDiff(object):
    def __init__(self, db):
        self._config_parser = getConfig()
        self._db = db
        self._second_db = SecondaryDB()
        self._second_db.setUp(self._config_parser.eval(self.__class__.__name__, 'second_db_path'))
        self._new_db = SecondaryDB()
        self._new_db.setUp(self._config_parser.eval(self.__class__.__name__, 'new_db_path'))

    def setUp(self):
        pass

    def is_well_defined(self):
        return True

    def make_list_from_db(self, db_instance, db_name):
        print('Reading Author table from {} db'.format(db_name))
        authors = db_instance.get_authors()
        print('Finish reading {} lines to csv'.format(len(authors)))
        return authors

    def get_diff(self, old, second):
        print('Getting diff between tables...')
        new = []
        total = sum(1 for row in second)
        old_names = [i.name for i in old]
        i = 1
        j = 0
        for author in second:
            msg = '\r author [{}/{}]'.format(i, total)
            print(msg, end="")
            i += 1
            if author.name in old_names:
                old_names.remove(author.name)
                j += 1
            else:
                new.append(author)
        print('\rOld authors: {}'.format(j))
        print('\rNew authors: {}'.format(len(new)))
        return new

    def execute(self, window_start):
        old_authors = self.make_list_from_db(self._db, 'old')
        second_authors = self.make_list_from_db(self._second_db, 'second')
        new_authors = self.get_diff(old_authors, second_authors)
        self._new_db.add_authors(new_authors)

