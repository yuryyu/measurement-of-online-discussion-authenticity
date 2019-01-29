from __future__ import print_function
from preprocessing_tools.abstract_controller import AbstractController
import pandas as pd
from DB.schema_definition import *


class AuthorConnectionsImporter(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)
        self._input_path = self._config_parser.eval(self.__class__.__name__, 'input_path')
        self._connection_type = self._config_parser.eval(self.__class__.__name__, 'type')
        self._chunksize = self._config_parser.eval(self.__class__.__name__, 'chunksize')

    def execute(self, window_start):
        df = self.extract_connections_from_csv_in_chunks()
        if self._connection_type == 'author_connection':
            self.make_author_connections(df)

    def extract_connections_from_csv_in_chunks(self):
        #chunks = pd.DataFrame()
        print('Reading connections from csv in chunks...')
        return pd.read_csv(self._input_path, encoding="windows-1252", quotechar='"', delimiter=',')
        #for chunk in pd.read_csv(self._input_path, encoding="windows-1252", quotechar='"', delimiter=',',
        #                         chunksize=self._chunksize):
        #    chunks.append(chunk)
        #return chunks

    def make_author_connections(self, df):
        author_connections = []
        for row in df.itertuples():
            author_connection = AuthorConnection()
            author_connection.source_author_guid = row.source_author_guid
            author_connection.destination_author_guid = row.destination_author_guid
            author_connection.connection_type = row.connection_type
            author_connection.weight = row.weight
            author_connection.claim_id = row.claim_id
            author_connection.insertion_date = row.insertion_date
            author_connections.append(author_connection)
        self._db.save_author_connections(author_connections)
