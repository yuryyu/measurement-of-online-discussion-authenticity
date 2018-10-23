from csv_importer import CsvImporter
from commons.commons import *
from configuration.config_class import getConfig
encoding = 'utf-8'

class LeadspottingPostsImporter(CsvImporter):
    def __init__(self, db):
        CsvImporter.__init__(self, db)
        config_parser = getConfig()
        self.start_date = config_parser.eval("DEFAULT", "start_date")
        self.end_date = config_parser.eval("DEFAULT", "end_date")

    def create_post_dict_from_row(self, row):
        guid = unicode(generate_random_guid())
        post_dict = {}
        post_dict["content"] = unicode(row["title"])
        post_dict["date"] = unicode(row["DATE"])
       # post_dict["guid"] = guid.replace('-', '')
        post_dict["guid"] = unicode(row["tweetId"])
        post_dict["author"] = row["name"].decode('utf-8')
      #  author_guid = compute_author_guid_by_author_name(unicode(row["name"]).replace('-', ''))
      #  post_dict["author_guid"] = author_guid
        post_dict["author_guid"] = unicode(row["userId"])
        post_dict["references"] = u""
        post_dict["domain"] = self._domain
        post_dict["author_osn_id"] = unicode(row["userId"])
        post_dict["url"] = unicode("https://twitter.com/{0}/status/{1}".format(post_dict["author"], row["tweetId"]).decode('utf-8'))
        return post_dict