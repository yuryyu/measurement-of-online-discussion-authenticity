from DB.schema_definition import DB
from configuration.config_class import getConfig
from datetime import datetime
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base


class SecondaryDB(DB):
    def __init__(self):
        pass

    def setUp(self, path_to_db):
        configInst = getConfig()
        #self._date = getConfig().eval(self.__class__.__name__, "start_date")
        self._pathToEngine = path_to_db
        start_date = configInst.get("DEFAULT", "start_date").strip("date('')")
        self._window_start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        self._window_size = datetime.timedelta(
            seconds=int(configInst.get("DEFAULT", "window_analyze_size_in_sec")))
        self._window_end = self._window_start + self._window_size

        #if configInst.eval(self.__class__.__name__, "remove_on_setup"):
        #    self.deleteDB()

        self.engine = create_engine("sqlite:///" + self._pathToEngine, echo=False)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

        self.session = self.Session()

        self.posts = "posts"
        self.authors = "authors"
        self.author_features = "author_features"
        self.claim_features = "claim_features"

        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_rec):
            dbapi_connection.enable_load_extension(True)
            if (getConfig().eval("OperatingSystem", "windows")):
                dbapi_connection.execute(
                    'SELECT load_extension("%s%s")' % (configInst.get("DB", "DB_path_to_extension"), '.dll'))
            if (getConfig().eval("OperatingSystem", "linux")):
                dbapi_connection.execute(
                    'SELECT load_extension("%s%s")' % (configInst.get("DB", "DB_path_to_extension"), '.so'))

            dbapi_connection.enable_load_extension(False)

       # if getConfig().eval(self.__class__.__name__, "dropall_on_setup"):
        #    Base.metadata.drop_all(self.engine)
        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        pass