from preprocessing_tools.abstract_controller import AbstractController
from DB.schema_definition import *


class CategoryFillerForClaims(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)

    def execute(self):
        claims = self.db.get_claims_missing_category()
        print(len(claims))
        print(claims[0])
