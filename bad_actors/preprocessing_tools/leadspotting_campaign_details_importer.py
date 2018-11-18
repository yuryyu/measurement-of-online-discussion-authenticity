from preprocessing_tools.fake_news_snopes_importer.fake_news_snopes_importer import FakeNewsSnopesImporter
from DB.schema_definition import Post, date, Claim
from configuration.config_class import getConfig
from commons.commons import compute_post_guid, compute_author_guid_by_author_name
import datetime


class CampaignDetailsImporter(FakeNewsSnopesImporter):
    def __init__(self, db):
        FakeNewsSnopesImporter.__init__(self, db)

    def _convert_row_to_claim(self, row):
        claim = Claim()
        claim_id = unicode(row['campaign_id'])
        title = unicode(row['title'], errors='replace')
        claim.title = title
        try:
            verdict_date = datetime.datetime.strftime(datetime.datetime.strptime(row['date'], '%d-%m-%y'), '%Y-%m-%d %H:%M:%S')
        except:
            verdict_date = getConfig().eval(self.__class__.__name__, 'default_date')
        claim.verdict_date = date(verdict_date)
        post_guid = compute_post_guid(self._social_network_url, claim_id, verdict_date)
        claim.claim_id = post_guid
        claim.domain = self._domain
        keywords = unicode(row['category'])
        claim.keywords = keywords
        verdict = unicode(row['campaign_class'])
        claim.verdict = verdict
        #claim.claim_topic = unicode(row['category'])
        return claim
