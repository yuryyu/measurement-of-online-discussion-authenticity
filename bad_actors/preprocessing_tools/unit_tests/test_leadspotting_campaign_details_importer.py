import sys
from unittest import TestCase
sys.argv.append('configuration\config.ini')
from preprocessing_tools.leadspotting_camoaign_details_importer import CampaignDetailsImporter
from DB.schema_definition import DB, Post

class TestCampaignDetailsImporter(TestCase):
    def setUp(self):
        self._db = DB()
        self._db.setUp()
        self.importer = CampaignDetailsImporter(self._db)

#    def test

