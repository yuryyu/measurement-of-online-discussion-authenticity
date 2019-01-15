from unittest import TestCase
from DB.schema_definition import *
from configuration.config_class import getConfig
from data_exporter.ranked_authors_exporter import RankedAuthorsExporter
import csv
import os

class TestRankedAuthorsExporter(TestCase):
    def setUp(self):
        self.config = getConfig()
        self._db = DB()
        self._db.setUp()
        self._ranked_authors_exporter = RankedAuthorsExporter(self._db)
        self._author_guid_dict = {}
        self.make_authors_posts_and_connections()
        self.csv_location = self.config.eval('RankedAuthorsExporter', 'output_file_path')
        self._threshold = self.config.eval('RankedAuthorsExporter', 'threshold')

    def tearDown(self):
        self._db.session.close_all()
        self._db.deleteDB()
        self._db.session.close()
        os.remove(self.csv_location)

    def test_ranked_authors_exporter(self):
        self.make_authors_posts_and_connections()
        self._ranked_authors_exporter.execute(window_start=1)
        with open(self.csv_location, 'rb') as f:
            reader = csv.reader(f)
            rows = list(reader)
            rows.pop(0)
            self.assertEqual(rows[0][4], '0.0')
            speed_list = [a[4] for a in rows]
            a = 0
            i = 0
            before_threshold = []
            for sp in speed_list:
                if sp > a:
                    a = sp
                    before_threshold.append(sp)
                    i += 1
                else:
                    after_threshold = speed_list[i:len(speed_list)]
                    break
            assert before_threshold == sorted(before_threshold)
            assert after_threshold == sorted(after_threshold)
            claim_ids_before_threshold = [row[2] for row in rows[:i-1]]
            claims_count_dict = dict((x, claim_ids_before_threshold.count(x)) for x in set(claim_ids_before_threshold))
            for v in claims_count_dict.values():
                assert v <= self._threshold

    def make_authors_posts_and_connections(self):
        for j in range(30):
            self._author_guid_dict['author_guid_' + str(j)] = compute_author_guid_by_author_name(unicode(j**2))
            author = Author()
            author.name = unicode(j**2)
            author.domain = u'Microblog'
            author.protected = 0
            author.author_guid = self._author_guid_dict['author_guid_' + str(j)]
            author.author_screen_name = unicode(j**2)
            author.author_full_name = unicode(j**2)
            author.statuses_count = 10
            author.author_osn_id = 149159975
            author.followers_count = 12
            author.created_at = datetime.datetime.strptime('2016-04-02 00:00:00', '%Y-%m-%d %H:%M:%S')
            author.missing_data_complementor_insertion_date = datetime.datetime.now()
            author.xml_importer_insertion_date = datetime.datetime.now()
            self._db.add_author(author)

            for i in range(10):
                post = Post()
                post.post_id = u'TestPost' + unicode(j) + u'_' + unicode(i)
                post.author = author.name
                post.guid = u'TestPost' + unicode(j) + u'_' + unicode(i)
                post.url = u'TestURL' + unicode(j) + u'_' + unicode(i)
                tempDate = u'2016-05-05 00:00:00'
                day = datetime.timedelta(1)
                post.date = datetime.datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S') + day * i
                post.domain = u'Microblog'
                post.author_guid = self._author_guid_dict['author_guid_' + str(j)]
                post.content = u"InternetTV love it #wow"
                post.xml_importer_insertion_date = datetime.datetime.now()
                self._db.addPost(post)
                claim_tweet_conn = Claim_Tweet_Connection()
                claim_tweet_conn.claim_id = u'test_claim_' + unicode(i)
                claim_tweet_conn.post_id = post.post_id
                self._db.session.merge(claim_tweet_conn)
                self._db.commit()
