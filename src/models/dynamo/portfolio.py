import os

from src.lib.dynamo_utils import BaseModel

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, MapAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class AssetIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "asset-id-index"
        projection = AllProjection()

    asset_id = UnicodeAttribute(hash_key=True)


class PortfolioModel(BaseModel):
    """Model representing an asset in a portfolio.

    fields:
        email: str
        asset_id: str
        shares: int
        average_price_per_share: float
        asset_image: dict
        song_title: str
        total_value: float
    """

    class Meta:
        table_name = "PortfolioTable"
        region = os.getenv("AWS_REGION", "us-west-2")

    email = UnicodeAttribute(hash_key=True)
    asset_id = UnicodeAttribute(range_key=True)
    shares = NumberAttribute()
    average_price_per_share = NumberAttribute()
    asset_image = MapAttribute(default={}, null=True)
    song_title = UnicodeAttribute()
    total_value = NumberAttribute()
