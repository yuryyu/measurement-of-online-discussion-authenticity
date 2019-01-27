from preprocessing_tools.abstract_controller import AbstractController
from DB.schema_definition import *


class CategoryFillerForClaims(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)

    def execute(self, window_start):
        cols = self._db.get_claims_columns()
        cols_to_add = []
        for col_name in ['main_category', 'secondary_category', 'claim_topic', 'claim_post_id', 'claim_ext_id']:
            if unicode(col_name) not in cols:
                cols_to_add.append({'name': col_name, 'type': 'Unicode'})
        self._db.add_columns('claims', cols_to_add)
        claims = self._db.get_claims_missing_category()
        for claim in claims:
            url = claim.url
            print(url)
