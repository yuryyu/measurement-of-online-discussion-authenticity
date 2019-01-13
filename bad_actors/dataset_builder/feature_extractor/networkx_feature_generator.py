#  Created by YY at 29.11.18
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
import pandas as pd
import numpy as np
import networkx as nx
import sys
import logging
import time

'''
This class is responsible for generating features based on authors properties
Each author-feature pair will be written in the AuthorFeature table
'''

class NetworkxFeatureGenerator(AbstractController):

    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")
        self._table_names = self._config_parser.eval(self.__class__.__name__, "table_names")
        self._csv_file = self._config_parser.eval(self.__class__.__name__, "csv_file")
        self._group_by = self._config_parser.eval(self.__class__.__name__, "group_by")
        self._source = self._config_parser.eval(self.__class__.__name__, "source")
        self._target = self._config_parser.eval(self.__class__.__name__, "target")                
        self._prefix = self.__class__.__name__

    def execute(self, window_start=None):                
        function_name = 'extract_features_from_graph'
        start_time = time.time()
        info_msg = "execute started for " + function_name + " started at " + str(start_time)        
        print (info_msg)
        logging.info(info_msg)
        
        try:
            claim_features = []
            for table_name in self._table_names:
                #df=self._db.df_from_table(table_name)
                #df = pd.read_csv(self._csv_file, names=['source_author_guid','destination_author_guid',
                #                                        'connection_type','weight','claim_id','insertion_date'], low_memory=False)
                print('Getting existing author connections with claim_id...')
                author_connections_with_claim_id = self._db.get_author_connections_with_claim_id()
                print('Checking author connections for claim id...')
                author_connections_with_claim_id.extend(self._db.make_connections_with_claim_id()[0])
                print(author_connections_with_claim_id[0])
                list_of_con_dicts = []
                for author_con in author_connections_with_claim_id:
                    connections_dict = {'source_author_guid': author_con.source_author_guid,
                                        'destination_author_guid': author_con.destination_author_guid,
                                        'connection_type': author_con.connection_type,
                                        'weight': author_con.weight,
                                        'claim_id': author_con.claim_id,
                                        'insertion_date': author_con.insertion_date}
                    list_of_con_dicts.append(connections_dict)
                df = pd.DataFrame(list_of_con_dicts)

                #df = pd.read_csv(self._csv_file, names=['source_author_guid','destination_author_guid','claim_id'], low_memory=False)
               
                grps = df.groupby(self._group_by)              
                if len(grps)==1:
                    self._db.update_table_group_by(table_name,self._group_by) # create in scheme
                cnt=1
                for grp in grps:
                    logging.info('Started ' +str(cnt)+ ' group from ' +str(len(grps)) +' groups')
                    print('Started ' +str(cnt)+ ' group from ' +str(len(grps)) +' groups')
                    cnt+=1
                    G = nx.from_pandas_dataframe(grp[1], self._source[0], self._target[0])
                    claim_ext_id = grp[0]
                    #claim_id = self._db.claim_ext_id_to_claim_id(claim_ext_id)[0]
                    claim_id =claim_ext_id
                    ftr=1                    
                    for feature_name in self._features_list:
                        logging.info('Started ' +str(ftr)+ ' feature from ' +str(len(self._features_list)) +' features')
                        print('Started ' +str(ftr)+ ' feature from ' +str(len(self._features_list)) +' features')
                        ftr+=1
                        attributes_dict = getattr(self, function_name)(G=G,ff=feature_name)
                        if len(attributes_dict)==1 and attributes_dict[feature_name] is not None:
                            attribute_name = "{0}_{1}".format(self._prefix, feature_name)
                            # next line add envelope for feature
                            claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attributes_dict[feature_name],
                                                                                    self._window_start, self._window_end)
                            claim_features.append(claim_feature)
                            continue                        
                        
                        for sub_feature_name in ('min_','max_','median_','std_'):
                            attribute_value = attributes_dict[sub_feature_name+feature_name]                            
                            if attribute_value is not None:
                                attribute_name = "{0}_{1}".format(self._prefix, sub_feature_name+feature_name)
                                # next line add envelope for feature
                                claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attribute_value,
                                                                                        self._window_start, self._window_end)
                                claim_features.append(claim_feature)
        except:
            print('Fail')
            print(sys.exc_info())
        stop_time = time.time()
        info_msg = "execute ended at " + str(stop_time)        
        print (info_msg)
        logging.info(info_msg)    
        # used author_feature table - due to next use
        self._db.add_author_features(claim_features)
        # regular use:   
        #self._db.add_claim_features(claim_features)
        
    def cleanUp(self):
        pass
    
    def extract_features_from_graph(self,G,ff):    
        ret={}
        try:
            if 'degree'==ff:                
                res =G.degree().values()
            elif ff in ['density', 'average_clustering']:
                res = eval('nx.'+ff+'(G)')
                return {ff:res}
            else:
                res = eval('nx.'+ff+'(G).values()')            
        except:
            res = [-1]    
        ret.update({'min_'+ff:min(res)})
        ret.update({'max_'+ff:max(res)})
        ret.update({'median_'+ff:np.median(res)})
        ret.update({'std_'+ff:np.std(res)})    
        return ret
    