'''
@author: Jorge Bendahan jorgeaug@post.bgu.ac.il
'''
import time
import logging
import pandas as pd
from pandas import DataFrame


from Twitter_API.twitter_api_requester import TwitterApiRequester
from dataset_builder.graph_builder import GraphBuilder


from commons.consts import Graph_Type
import datetime
import networkx as nx

class FriendsLookup(object):
    def __init__(self, api):
        self.request_counter = []
        self.cache = {}
        self.complete_connection_graph = nx.DiGraph()  # edge = (u, v) means that u is following v in twitter this does not mean that (v, u) exists in E
        self.api = api

    def start_counter(self):
        self.request_counter.append(0)

    def increase_counter(self):
        try:
            self.request_counter[-1] += 1
        except:
            pass

    def get_latest_counter_count(self):
        return self.request_counter[-1]

    def is_following(self, source, target):
        try:
            return self.cache[source][target]
        except KeyError:
            try:
                friendship = self.api.show_friendship(source, target)['relationship']
            except Exception as ex:
                print "[X] Performed too many requests... sleeping 16 for min "
                time.sleep(15 * 60)
                print "[X] Trying again..."
                try:
                    friendship = self.api.show_friendship(source, target)['relationship']
                except Exception as ex_2:
                    print ex_2
                    return False
            self.increase_counter()  # monitoring number of requests
            print "[X] API friendship query: {0} , {1}".format(source, target)
            self.cache[source] = self.cache.get(source, dict())
            self.cache[source][target] = friendship['source']['following']
            self.cache[target] = self.cache.get(target, dict())
            self.cache[target][source] = friendship['target']['following']
            if self.cache[source][target]:
                print "edge: {0} --> {1}".format(source, target)
                self.complete_connection_graph.add_edge(source, target)
            if self.cache[target][source]:
                print "edge: {1} --> {0}".format(source, target)
                self.complete_connection_graph.add_edge(target, source)
        return self.cache[source][target]

    def expand_followers(self, source, open_nodes):
        usrs_set = set(map(lambda x: long(x), open_nodes))
        all_followers = set(map(lambda x: long(x), self.api.get_follower_ids_by_user_id(source)))
        ret = []
        discovered_nodes = all_followers.intersection(usrs_set)
        print("[X] Number of nodes discovered : {0}".format(discovered_nodes))
        for follower in discovered_nodes:
            self.cache[follower] = self.cache.get(follower, dict())
            self.cache[follower][source] = True
            self.complete_connection_graph.add_edge(follower,source)
            usrs_set.remove(follower)
            ret.append(follower)
        for not_follower in usrs_set:
            self.cache[not_follower] = self.cache.get(not_follower, dict())
            self.cache[not_follower][source] = False
        return ret


class GraphBuilder_RetweetCascade(GraphBuilder):
    """Generate graphs where nodes represent authors.
    if author B retweeted a post following author A """

    def __init__(self, db):
        GraphBuilder.__init__(self, db)
        # self._min_number_of_cocited_posts = int(self._config_parser.get(self.__class__.__name__,
        #                                                             "min_number_of_cocited_posts"))

    def sample_by_top_followers(self, df, n_samples):
        #TODO: Change to sql query?
        if n_samples > len(df):
            return df
        else:
            dt = df.sort_values(by='followers', ascending=False)
            return dt[:n_samples]

    def setUp(self):
        self.api = TwitterApiRequester(sleep_on_rate_limit=False)
        self._lookup = FriendsLookup(self.api)
        self._sample_top_followers_users = int(self._config_parser.get(self.__class__.__name__,
                                                                    "sample_top_followers_users"))

    def get_followers_count(self, usr_id, df):
        return int(df.loc[df['author_id'] == unicode(usr_id)].iloc[0]['followers'])

    def create_cascade_graph(self, users_list, df):
        print "[X] Creating graph for users: {0}".format(users_list)
        self._lookup.start_counter()
        undiscovered_nodes = list(users_list)
        discovered_nodes = [undiscovered_nodes.pop(0)]
        q = [discovered_nodes[0]]
        discovery_map = {}  # maintains a list of the author each other author retweeted. Inializing with the original poster
        while q and undiscovered_nodes:
            u = q.pop(0)
            if self.get_followers_count(u, df) < 5000:
                try:
                    discovered_followers = self._lookup.expand_followers(u, undiscovered_nodes)
                    for v in discovered_followers:
                        self.handle_discoverd_node(discovered_nodes, discovery_map, q, u, undiscovered_nodes, v)
                except:
                    print "[X] Finished followers quota, switching to friendship lookup"
                    self.expand_using_friendship_lookup(discovered_nodes, discovery_map, q, u, undiscovered_nodes)
            else:
                self.expand_using_friendship_lookup(discovered_nodes, discovery_map, q, u, undiscovered_nodes)

        print "Total requests = {0} vs {1} all possible edges ".format(self._lookup.get_latest_counter_count(),
                                                                       (len(users_list) * (len(users_list) - 1)) / 2)
        # nx.write_gexf(fs.complete_connection_graph, users_list[0] + "_graph_3.gexf")
        return self._lookup.complete_connection_graph, discovery_map

    def expand_using_friendship_lookup(self, discovered_nodes, discovery_map, q, u, undiscovered_nodes):
        for v in set(undiscovered_nodes) - set(discovered_nodes):
            if self._lookup.is_following(v, u):
                self.handle_discoverd_node(discovered_nodes, discovery_map, q, u, undiscovered_nodes, v)

    def handle_discoverd_node(self, discovered_nodes, discovery_map, q, u, undiscovered_nodes, v):
        q.append(v)
        discovered_nodes.append(v)
        undiscovered_nodes.remove(v)
        discovery_map[v] = u

    def get_orig_poster_id(self, df, retweet_post):
        return df.loc[df['post_id'] == retweet_post].iloc[0]['author_id']

    def generate_graph_for_retweet_cascade(self, cascade_df, df):
        cascade_df = self.sample_by_top_followers(cascade_df,self._sample_top_followers_users) # use only top X users
        orig_post =  cascade_df.iloc[0]['parent_id']
        orig_author = self.get_orig_poster_id(df, orig_post) # add post author
        retweeters_list = list(cascade_df.author_id)
        G, discovery_map = self.create_cascade_graph(map(lambda x: long(x), [orig_author] + retweeters_list), df)
        return discovery_map

    # add_author_connections
    def get_guid_from_id(self, id, df):
        if type(id) in [int, long]:
            id = str(id)
        return df.loc[df['author_id']==id].iloc[0]['author_guid']

    def save_cascade_graph_for_claim(self, retweet_discovery_map, df, claim_id):
        for author, discovered_from in retweet_discovery_map.items():
            # def create_and_save_author_connections(self, source_author_id, follower_ids, weight, connection_type):
            self._db.create_and_save_author_connections(self.get_guid_from_id(author, df),
                                                        map(lambda x: self.get_guid_from_id(x, df), discovered_from),
                                                        -1,
                                                        "claim_cascade_graph", claim_id)

    def generate_graph_for_claim(self, claim_id):
        claim_posts = self._db.get_posts_in_claim(claim_id)
        claim_df = pd.DataFrame(claim_posts, columns=['post_id', 'parent_id', 'author_screen_name', 'author_id', 'author_guid', 'followers'])
        grps = claim_df.groupby(['parent_id'])
        aggregated_dict = {}
        for grp in grps:
            if grp[0] == 0:
                continue
            discovery_map = self.generate_graph_for_retweet_cascade(grp[1], claim_df)
            for key, value in discovery_map.items():
                aggregated_dict[key] = aggregated_dict.get(key, set()).union([value])
        self.save_cascade_graph_for_claim(aggregated_dict, claim_df, claim_id)

    def execute(self, window_start):
        claims = self._db.get_claims()
        for i,claim in enumerate(claims):
            print "[X] Claim {0} / {1}".format(i, len(claims))
            try:
                self.generate_graph_for_claim(claim[0])
            except Exception as e:
                print("Failed for claim_id : {0}".format(claim))
'''
    def test_quota_times(users):
        st = datetime.datetime.now()
        print "Testing friendship lookup: time : {0}".format(st)
        try:
            for i, comb in enumerate(itertools.combinations(users, 2)):
                print "req #n : {}".format(i)
                api.show_friendship(source_id=comb[0], target_id=comb[1])
        except Exception as e:
            print e
            dt1 = datetime.datetime.now()
            print "Timed out for friendship. Total time: \n Starting followers req".format({dt1 - st})
            try:
                for i, usr in enumerate(users):
                    print "req #n : {}".format(i)
                    api.followers(usr)
            except:
                print "Finished followers reqs : {0}".format(dt1 - datetime.datetime.now())

    if __name__ == "__main__":

        # Load data and parse
        print "[X] Loading data..."

        df = DataFrame.from_csv(input_path)
        df['parentTweet'] = df.parentTweet.apply(lambda x: x.replace("\"", ""))
        df['tweetId'] = df.tweetId.apply(lambda x: x.replace("\"", ""))
        df['userId'] = df.userId.apply(lambda x: x.replace("\"", ""))
        df['date'] = df['DATE'].apply(lambda x: x.replace("\"", ""))
        df['retweet_from'] = pd.Series([-1] * len(df))
        df.sort_values(by='date')
        print "[X] Data loaded."

        # initialize query module
        fs = FriendsLookup()

        test_quota_times(list(df['userId']))

        # Split to retweets groups    df_ret.to_csv("output.csv")
        grps = df.groupby(['parentTweet'])
        ret = {}
        for retweet_chain in grps:
            if retweet_chain[0] == '0':
                continue

            users_in_cascade = sample_by_top_followers(retweet_chain[1], n_samples)

            retweeters_list = list(users_in_cascade.userId)
            orig_poster = get_orig_poster_id(df, retweet_chain[0])
            G, discovery_map = create_cascade_graph([orig_poster] + retweeters_list)
            tmp_dict = retweet_chain[1].set_index('tweetId').T.to_dict()
            for k in tmp_dict:
                tmp_dict[k]['retweet_from'] = discovery_map.get(tmp_dict[k]['userId'], -1)
            ret.update(tmp_dict)
        df_ret = pd.DataFrame.from_dict(tmp_dict).T
        df_ret.index.name = 'tweetId'
        df_ret.to_csv('output.csv')
        # Adding retweet_from value to rows.

        exit()
'''