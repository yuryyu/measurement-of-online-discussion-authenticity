from unittest import TestCase
from preprocessing_tools.leadspotting_posts_importer import LeadspottingPostsImporter
from DB.schema_definition import DB, Post


class TestLeadspottinPostsImporter(TestCase):
    def SetUp(self):
        self._db = DB()
        self._db.setUp()

    def test_