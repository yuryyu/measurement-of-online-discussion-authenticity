from unittest import TestCase
import datetime
from DB.schema_definition import *
from configuration.config_class import getConfig
from missing_data_complementor.add_author_connection_claim_id import AddAuthorConnectionClaimId

class AddAuthorConnectionClaimIdTests(TestCase):
    def setUp(self):
        self.config = getConfig()
        self._db = DB()
        self._db.setUp()
        self._author_claim_complementor = AddAuthorConnectionClaimId(self._db)
        self.make_authors_posts_and_connections()

    def tearDown(self):
        self._db.session.close_all()
        self._db.deleteDB()
        self._db.session.close()

    def test_add_author_connection(self):
        connections = self._db.get_author_connections_by_author_guid(self._author_guid1)
        for c in connections:
            self.assertIsNone(c.claim_id)
        self._author_claim_complementor.execute(0)
        connections = self._db.get_author_connections_by_type(u'friend')
        for c in connections:
            self.assertIsNotNone(c[4])
            assert c[0] == u'64205a81-7045-3edc-8cf5-a9f316116573' or c[1]== u'3ac92c5a-478b-3bf7-9a6f-72b947aacbee'
        connections = self._db.get_author_connections_by_type(u'follower')
        for c in connections:
            self.assertIsNotNone(c[4])
            assert c[0] == u'64205a81-7045-3edc-8cf5-a9f316116573' or c[1] == u'3ac92c5a-478b-3bf7-9a6f-72b947aacbee'
            #self.assertIsNotNone(c.claim_id)


    def make_authors_posts_and_connections(self):
        self._author_guid1 = compute_author_guid_by_author_name(u'BillGates')
        author = Author()
        author.name = u'BillGates'
        author.domain = u'Microblog'
        author.protected = 0
        author.author_guid = self._author_guid1
        author.author_screen_name = u'BillGates'
        author.author_full_name = u'Bill Gates'
        author.statuses_count = 10
        author.author_osn_id = 149159975
        author.followers_count = 12
        author.created_at = datetime.datetime.strptime('2016-04-02 00:00:00', '%Y-%m-%d %H:%M:%S')
        author.missing_data_complementor_insertion_date = datetime.datetime.now()
        author.xml_importer_insertion_date = datetime.datetime.now()
        self._db.add_author(author)

        for i in range(10):
            post = Post()
            post.post_id = u'TestPost' + str(i)
            post.author = u'BillGates'
            post.guid = u'TestPost' + str(i)
            post.url = u'TestPost' + str(i)
            tempDate = u'2016-05-05 00:00:00'
            day = datetime.timedelta(1)
            post.date = datetime.datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S') + day * i
            post.domain = u'Microblog'
            post.author_guid = self._author_guid1
            post.content = u"InternetTV love it #wow"
            post.xml_importer_insertion_date = datetime.datetime.now()
            self._db.addPost(post)
            claim_tweet_conn = Claim_Tweet_Connection()
            claim_tweet_conn.claim_id = 'test_claim_' + str(i % 2 + 1)
            claim_tweet_conn.post_id = post.post_id
            self._db.session.merge(claim_tweet_conn)
            self._db.commit()

        self._author_guid2 = compute_author_guid_by_author_name(u'ZachServideo')
        author = Author()
        author.name = u'ZachServideo'
        author.domain = u'Microblog'
        author.protected = 0
        author.author_guid = self._author_guid2
        author.author_screen_name = u'ZachServideo'
        author.author_full_name = u'Zach Servideo'
        author.statuses_count = 110
        author.author_osn_id = 40291482
        author.created_at = datetime.datetime.strptime('2016-04-05 00:00:00', '%Y-%m-%d %H:%M:%S')
        author.missing_data_complementor_insertion_date = datetime.datetime.now()
        author.xml_importer_insertion_date = datetime.datetime.now()
        author.friends_count = 12
        self._db.add_author(author)

        for i in range(10, 120):
            post = Post()
            post.post_id = u'TestPost' + str(i)
            post.author = u'ZachServideo'
            post.guid = u'TestPost' + str(i)
            post.url = u'TestPost' + str(i)
            tempDate = u'2016-05-05 00:00:00'
            day = datetime.timedelta(1)
            post.date = datetime.datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S') + day * i
            post.domain = u'Microblog'
            post.author_guid = self._author_guid2
            post.content = u'OnlineTV love it http://google.com'
            post.xml_importer_insertion_date = datetime.datetime.now()
            self._db.addPost(post)
            claim_tweet_conn = Claim_Tweet_Connection()
            claim_tweet_conn.claim_id = 'test_claim_2'
            claim_tweet_conn.post_id = post.post_id
            self._db.session.merge(claim_tweet_conn)
            self._db.commit()

        self._author_guid3 = compute_author_guid_by_author_name(u'AyexBee')
        author = Author()
        self._author_3_name = u'AyexBee'
        author.name = self._author_3_name
        author.domain = u'Microblog'
        author.protected = 0
        author.author_guid = self._author_guid3
        author.author_screen_name = u'AyexBee'
        author.author_full_name = u'AxB'
        author.statuses_count = 100
        author.author_osn_id = 100271909
        author.created_at = datetime.datetime.strptime('2016-04-05 00:00:00', '%Y-%m-%d %H:%M:%S')
        author.missing_data_complementor_insertion_date = datetime.datetime.now()
        author.xml_importer_insertion_date = datetime.datetime.now()
        author.followers_count = 12
        self._db.add_author(author)

        for i in range(120, 220):
            post = Post()
            post.post_id = u'TestPost' + str(i)
            post.author = u'AyexBee'
            post.guid = u'TestPost' + str(i)
            post.url = u'TestPost' + str(i)
            tempDate = u'2016-05-05 00:00:00'
            day = datetime.timedelta(1)
            post.date = datetime.datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S') + day * i
            post.domain = u'Microblog'
            post.author_guid = self._author_guid3
            post.content = u'Security love it http://google.com'
            post.xml_importer_insertion_date = datetime.datetime.now()
            self._db.addPost(post)
            claim_tweet_conn = Claim_Tweet_Connection()
            claim_tweet_conn.claim_id = 'test_claim_3'
            claim_tweet_conn.post_id = post.post_id
            self._db.session.merge(claim_tweet_conn)
            self._db.commit()

        author_connections = []

        author_connection_1_2 = AuthorConnection()
        author_connection_1_2.source_author_guid = self._author_guid1
        author_connection_1_2.destination_author_guid = self._author_guid2
        author_connection_1_2.connection_type = u"friend"
        author_connection_1_2.weight = 1.0
        author_connection_1_2.insertion_date = datetime.datetime.now()
        author_connections.append(author_connection_1_2)

        author_connection_1_3 = AuthorConnection()
        author_connection_1_3.source_author_guid = self._author_guid1
        author_connection_1_3.destination_author_guid = self._author_guid3
        author_connection_1_3.connection_type = u"follower"
        author_connection_1_3.weight = 1.0
        author_connection_1_3.insertion_date = datetime.datetime.now()
        author_connections.append(author_connection_1_3)

        self._db.add_author_connections(author_connections)

        self._db.commit()