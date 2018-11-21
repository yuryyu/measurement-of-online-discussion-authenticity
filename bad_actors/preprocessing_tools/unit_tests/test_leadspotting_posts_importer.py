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
        valid_post_id = '783dcc3b-1ec0-38a5-a760-912e6be134b7'
        invalid_post_id = '2236cca9-bcc7-39d5-b702-6d5463d42fae'
        self.assertTrue(self._db.get_post_by_id(valid_post_id))
        self.assertFalse(self._db.get_post_by_id(invalid_post_id))


    def test_incorrect_fieds(self):
        #tests that importer doesn't insert to db posts from csv missing essential fields
        print 'test incorrect fields'
        self.importer.setUp()
        all_posts_in_db = self._db.get_all_posts()
        self.assertEqual(len(all_posts_in_db), 0)
        self.importer._data_folder = 'data/input/datasets/unittests/incorrect_fields/'
        self.importer.execute()
        all_posts_in_db = self._db.get_all_posts()
        self.assertEqual(len(all_posts_in_db), 0)


    def tearDown(self):
        self._db.session.close()
        self._db.deleteDB()
        self._db.session.close()


