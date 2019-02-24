from DB.schema_definition import PostConnection, Author
from csv_importer import CsvImporter, Claim_Tweet_Connection
from commons.commons import *
from configuration.config_class import getConfig
import logging
import csv
import re

encoding = 'utf-8'


class LeadspottingPostsImporter(CsvImporter):
    def __init__(self, db):
        CsvImporter.__init__(self, db)
        config_parser = getConfig()
        self._author_prop_dict = []
        #self.start_date = config_parser.eval("DEFAULT", "start_date")
        #self.end_date = config_parser.eval("DEFAULT", "end_date")

    def updateClaims(self):
        claims_list = [unicode(x['claim_id']) for x in self._listdic]
        self._db.insert_or_update_claims(list(set(claims_list)))

    def updatePostClaimsConnections(self):
        list_to_add = []
        for dic in self._listdic:
            claim_tweet = Claim_Tweet_Connection()
            claim_tweet.claim_id = unicode(dic['claim_id'])
            claim_tweet.post_id = unicode(dic['post_id'])
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
        for dic in self._author_prop_dict:
            try:
                author = Author()
                author.name = dic['author']
                author.domain = unicode('Microblog')
                author.author_osn_id = dic['author_osn_id']
                author.author_guid = dic['author_guid']
                author.followers_count = dic['followers_count']
                author.location = dic['location']
                author.favourites_count = dic['favorite']
                author.description = dic['description']
                author.url = dic['url']
                list_to_add.append(author)
            except (ValueError, TypeError, KeyError) as e:
                logging.warn("Failed to add author: {0} - {1}".format(author.name, e))
        self._db.update_authors(list_to_add)

    def execute(self, window_start=None):
        self.readFromFolders()
        self._db.insert_or_update_authors_from_posts(self._domain, self._author_classify_dict, self._author_prop_dict)
        self.updateClaims()
        self.updatePostClaimsConnections()  # TODO: Yuri, this might have to change to topics based on mapping that will be from claims (claims) to topic
        self.updateOriginalPostsConnections()
        self.updateAuthorsData()

    def create_post(self, dictItem):
        try:
            pre_post, date = super(LeadspottingPostsImporter, self).create_post(dictItem)
            pre_post.post_osn_id = int(dictItem["post_osn_id"])
        except:
            print "[X] Failed to create post"
        return pre_post, date

    def parse_csv(self, csv_file, f):
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            try:
                post_dict = self.create_post_dict_from_row(row)
                self._listdic.append(post_dict.copy())
                try:
                    author_dic = self.create_author_dict_from_row(row, post_dict)
                    self._author_prop_dict.append(author_dic.copy())
                except KeyError as e:
                    logging.warn("[-] Failed to parse author details from row: {0}".format(e))
            except (KeyError, ValueError) as e:
                logging.warn("[-] Failed to parse row : {0}".format(e))

    def create_post_dict_from_row(self, row):
        post_dict = {}
        try:
            post_dict["content"] = unicode(row["title"])
        except:
            post_dict["content"] = row["title"]
        post_dict["date"] = parse_date(row)
        # post_dict["guid"] = unicode(row["tweetId"])
        parsed_author_name = row["userUrl"][row["userUrl"].rfind('/') + 1:]
        post_dict["author"] = unicode(parsed_author_name)
        author_guid = compute_author_guid_by_author_name(parsed_author_name)
        author_guid = cleanForAuthor(author_guid)
        post_dict["author_guid"] = author_guid
        post_dict["content"] = unicode(row["title"])
        post_dict["post_osn_id"] = row["tweetId"].replace("\"", "")
        #  post_dict["author_guid"] = unicode(row["userId"])
        post_dict["references"] = u""
        post_dict["domain"] = self._domain
        post_dict["author_osn_id"] = unicode(row["userId"]).replace("\"", "")
        post_dict["url"] = unicode(
            "https://twitter.com/{0}/status/{1}".format(post_dict["author"], post_dict["post_osn_id"]).decode('utf-8'))
        post_dict["guid"] = compute_post_guid(post_dict["url"], post_dict["author"], post_dict["date"])
        post_dict["post_id"] = post_dict["guid"]
        post_dict["followers"] = int(row['followers']) if row['followers'] is not None else -1
        post_dict["claim_id"] = int(row["campaign_id"])
        post_dict["parent_osn_id"] = row["parentTweet"].replace("\"", "")
        #print post_dict["claim_id"]
        return post_dict

    def create_author_dict_from_row(self, row, post_dict):
        author_dict = {}
        try:
            author_dict['author'] = post_dict['author']
            author_dict['domain'] = post_dict['domain']
            author_dict['author_osn_id'] = post_dict['author_osn_id']
            author_dict['author_guid'] = post_dict['author_guid']
            author_dict['followers_count'] = post_dict['followers']
            #try:
            author_dict['location'] = unicode(row['location'])
            #except:
            #    author_dict['location'] = row['location']
            author_dict['favorite'] = unicode(row['favorite'])
            #try:
            author_dict['description'] = unicode(row['description'])
            #except:
            #    author_dict['description'] = row['description']
            author_dict['url'] = unicode(row['userUrl'])
        except:
            logging.warn('Failed to parse author details from row : {}'.format(post_dict['author']))
        return author_dict


def parse_date(row):
    try:
        dt = unicode(row["DATE"])
    except:
        dt = unicode(row["date"])
    pattern1 = '\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\"'
    if len(re.findall(pattern1, dt)) > 0:
        parsed_date = dt[1:len(dt) - 1]
    else:
        try:
            # parsed_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dt, '%d/%m/%Y %H:%M'))
            parsed_date = unicode(time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dt, '%d/%m/%Y %H:%M')))
        except:
            # parsed_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dt, '%d-%m-%y %H:%M'))
            parsed_date = unicode(time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dt, '%d-%m-%y %H:%M')))
    return parsed_date
