import sys
from unittest import TestCase
sys.argv.append('configuration\config.ini')
from preprocessing_tools.leadspotting_claim_details_importer import  ClaimDetailsImporter
from DB.schema_definition import DB, Post

class TestClaimDetailsImporter(TestCase):
    def setUp(self):
        self._db = DB()
        self._db.setUp()
        self.importer = ClaimDetailsImporter(self._db)

    def test_missing_fields(self):
        self.importer._input_csv_file = "data/input/datasets/unittests/claims/incorrect_fields.csv"
        self.importer.execute()
        self.assertEqual(len(self._db.get_claims()), 0)

    def test_valid_csv(self):
        self.importer._input_csv_file = "data/input/datasets/unittests/claims/valid.csv"
        self.importer.execute()
        self.assertEqual(len(self._db.get_claims()), 6)

    def tearDown(self):
        self._db.session.close()
        self._db.deleteDB()

