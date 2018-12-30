#  Created by YY at 29.11.18
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
#import pandas as pd
import numpy as np
import networkx as nx
import sys

'''
This class is responsible for generating features based on authors properties
Each author-feature pair will be written in the AuthorFeature table
'''

class NetworkxFeatureGenerator(AbstractController):

    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")
        self._table_names = self._config_parser.eval(self.__class__.__name__, "table_names")
        self._group_by = self._config_parser.eval(self.__class__.__name__, "group_by")
        self._source = self._config_parser.eval(self.__class__.__name__, "source")
        self._target = self._config_parser.eval(self.__class__.__name__, "target")                
        self._prefix = self.__class__.__name__

    def execute(self, window_start=None):                
        function_name = 'extract_features_from_graph'
        try:
            claim_features = []
            for table_name in self._table_names:
                df=self._db.df_from_table(table_name)                
                grps = df.groupby(self._group_by)               
                for grp in grps:
                    G = nx.from_pandas_dataframe(grp[1], self._source, self._target)
                    claim_ext_id = grp[0]
                    claim_id = self._db.claim_ext_id_to_claim_id(claim_ext_id)[0]                   
                    for feature_name in self._features_list:
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
    