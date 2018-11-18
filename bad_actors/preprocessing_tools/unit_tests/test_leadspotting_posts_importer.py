from StringIO import StringIO
from unittest import TestCase
import sys

from decorator import contextmanager

sys.argv.append('configuration/config_test.ini')
from preprocessing_tools.leadspotting_posts_importer import LeadspottingPostsImporter
from DB.schema_definition import DB, Post
from configuration.config_class import getConfig
import csv


#used to check print outputs
@contextmanager
def captured_output(self):
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestLeadspottingPostsImporter(TestCase):
    def setUp(self):
        self._db = DB()
        self._db.setUp()
        self.importer = LeadspottingPostsImporter(self._db)

    def test_skips_one_file_in_folder(self):
        print '\ntest skips one file in folder:'
        self.assertEqual(len(self._db.get_all_posts()), 0)
        self.importer.setUp()
        self.importer._data_folder = 'data/input/datasets/unittests/folder1/'
        self.importer.execute()
        self.assertEqual(len(self._db.get_all_posts()), 3)

    def test_incorrect_fieds(self):
        #tests that importer doesn't insert to db posts from csv missing essential fields
        print 'test incorrect fields'
        self.importer.setUp()
        self.importer._data_folder = 'data/input/datasets/unittests/incorrect_fields/'
        csv_file = 'data/input/datasets/unittests/incorrect_fields/incorrect_fields.csv'
        with captured_output(self) as (out, err):
            with open(csv_file, 'r') as f:
                self.importer.parse_csv(csv_file, f)
        output = out.getvalue().strip()
        expected_output = '[-] Failed to parse row\n[-] Failed to parse row\n[-] Failed to parse row'
        self.assertEqual(output, expected_output)
        all_posts_in_db = self._db.get_all_posts()
        self.importer.execute()
        self.assertEqual(len(all_posts_in_db), 0)


    def test_skips_lines(self):
        print '\ntest skips lines   '
        self.importer.setUp()
        csv_file = 'data/input/datasets/unittests/folder1/leadspotting_posts_incorrect_lines.csv'
        with captured_output(self) as (out, err):
            with open(csv_file, 'r') as f:
                self.importer.parse_csv(csv_file, f)
        output = out.getvalue().strip()
        expected_output = '[-] Failed to parse row'
        print 'output: {}'.format(output)
        self.assertEqual(output, expected_output)


    def tearDown(self):
        self._db.session.close()
        self._db.deleteDB()
        self._db.session.close()


