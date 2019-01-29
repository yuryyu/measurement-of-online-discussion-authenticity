from preprocessing_tools.abstract_controller import AbstractController
from DB.schema_definition import *


class AddAuthorConnectionClaimId(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)

    def execute(self, window_start):
        self._db.add_claim_id_to_author_connections()

