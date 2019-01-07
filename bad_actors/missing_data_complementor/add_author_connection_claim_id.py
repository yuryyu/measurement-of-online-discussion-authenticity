from preprocessing_tools.abstract_controller import AbstractController
from DB.schema_definition import *


class AddAuthorConnectionClaimId(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)

    def execute(self, window_start):
        self._db.add_claim_id_to_author_connections()
        #print('number of new connections to save: ' + str(len(connections_to_save)))
        #print(connections_to_save[0])

    #def



            #print("User : {0} seems to not have posts".format(source_author))

    # friends_connections = {}
    # followers_connections = {}
    #
    #
    #     if c_type=="friend":
    #         t = friends_connections.get(source_author, set())
    #         t.add(dest_author)
    #         friends_connections[source_author] = t
    #     elif c_type=="follower":
    #         t = followers_connections.get(source_author, set())
    #         t.add(dest_author)
    #         followers_connections[source_author] = t
    #
    # for claim, authors_list in claims_per_author:
    #
#
#
