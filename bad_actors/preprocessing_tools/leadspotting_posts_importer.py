from DB.schema_definition import PostConnection, Author
from csv_importer import CsvImporter, Claim_Tweet_Connection
from commons.commons import *
from configuration.config_class import getConfig
encoding = 'utf-8'

class LeadspottingPostsImporter(CsvImporter):
    def __init__(self, db):
        CsvImporter.__init__(self, db)
        config_parser = getConfig()
        self.start_date = config_parser.eval("DEFAULT", "start_date")
        self.end_date = config_parser.eval("DEFAULT", "end_date")

    def updateClaims(self):
        claims_list = [unicode(x['campaign_id']) for x in self._listdic]
        self._db.insert_or_update_claims(list(set(claims_list)))

    def updatePostClaimsConnections(self):
        list_to_add = []
        for dic in self._listdic:
            claim_tweet = Claim_Tweet_Connection()
            claim_tweet.claim_id=unicode(dic['campaign_id'])
            claim_tweet.post_id=unicode(dic['post_id'])
            list_to_add.append(claim_tweet)
        self._db.add_claim_connections(list_to_add)

    def updateOriginalPostsConnections(self):
        list_to_add = []
        for dic in self._listdic:
            post_connection = PostConnection()
            post_connection.source_post_osn_id = int(dic["parent_osn_id"])
            post_connection.target_post_osn_id = dic["post_osn_id"]
            post_connection.connection_type = unicode('retweet')
            post_connection.insertion_date = dic["date"]
            list_to_add.append(post_connection)
        self._db.add_posts_connections(list_to_add)

    def updateAuthorsData(self):
        list_to_add = []
        for dic in self._listdic:
            author = Author()
            author.name = dic['author']
            author.domain = unicode('Microblog')
            author.author_osn_id = dic['author_osn_id']
            author.author_guid = dic['author_guid']
            author.followers_count = dic['followers']
            list_to_add.append(author)
        self._db.update_authors(list_to_add)


    def execute(self, window_start=None):
        self.readFromFolders()
        self._db.insert_or_update_authors_from_posts(self._domain, self._author_classify_dict, self._author_prop_dict)
        self.updateClaims()
        self.updatePostClaimsConnections() # TODO: Yuri, this might have to change to topics based on mapping that will be from claims (campaigns) to topic
        self.updateOriginalPostsConnections()
        self.updateAuthorsData()

    def create_post(self, dictItem):
        pre_post, date = super(LeadspottingPostsImporter, self).create_post(dictItem)
        try:
            pre_post.post_osn_id = int(dictItem["post_osn_id"])
        except:
            pass
        return  pre_post, date

    def create_post_dict_from_row(self, row):
        post_dict = {}
        try:
            post_dict["content"] = unicode(row["title"])
        except:
            post_dict["content"] = row["title"]
        try:
            post_dict["date"] = unicode(row["DATE"])
        except:
            post_dict["date"] = unicode(row["date"])
        post_dict["date"] = post_dict["date"].replace("\"","")

       # post_dict["guid"] = unicode(row["tweetId"])
        parsed_author_name = row["userUrl"][row["userUrl"].rfind('/')+1:]
        post_dict["author"] = unicode(parsed_author_name)
        author_guid = compute_author_guid_by_author_name(parsed_author_name)
        author_guid = cleanForAuthor(author_guid)
        post_dict["author_guid"] = author_guid
        post_dict["post_osn_id"] = row["tweetId"].replace("\"","")
        #  post_dict["author_guid"] = unicode(row["userId"])
        post_dict["references"] = u""
        post_dict["domain"] = self._domain
        post_dict["author_osn_id"] = unicode(row["userId"]).replace("\"","")
        post_dict["url"] = unicode("https://twitter.com/{0}/status/{1}".format(post_dict["author"], post_dict["post_osn_id"]).decode('utf-8'))
        post_dict["guid"] = compute_post_guid(post_dict["url"], post_dict["author"], post_dict["date"])
        post_dict["post_id"] = post_dict["guid"]
        post_dict["followers"] = int(row['followers'])
        post_dict["campaign_id"] = row["campaign_id"]
        post_dict["parent_osn_id"] = row["parentTweet"].replace("\"","")

        #TODO: Leah, please add the rest of the data from the csv (poster friends, likes etc) so we can add it later to the DB

        return post_dict
