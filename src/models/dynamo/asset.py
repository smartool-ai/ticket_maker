import os
from typing import Dict

from src.lib.dynamo_utils import BaseModel
from src.lib.loggers import get_module_logger

from pynamodb.attributes import (
    BooleanAttribute,
    ListAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UnicodeSetAttribute,
    MapAttribute,
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


logger = get_module_logger()


class AssetIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "asset-id-index"
        projection = AllProjection()

    asset_id = UnicodeAttribute(hash_key=True)


class AssetModel(BaseModel):
    """Model representing an asset.

    fields:
        asset_id: str = HASH
        series: str
        song_id: str
        rights_type: str
        approved_for_track_image: str
        isrc: str
        iswc: str
        song_title: str
        current_share_price: float
        three_years_avg: float
        last_twelve_months: float
        shares_offered: int
        outstanding_shares: int
        float_shares: int
        testing_the_waters: str
        primary_launch_date: str
        secondary_launch_date: str
        payment: str
        term: str
        spv_name: str
        date_of_last_reported_earnings: str
        market_cap: float
        estimated_dividend_yield: float
        recording_artists: str
        songwriters: str
        iio: str

        streaming_count: int
        meta: dict
        image: dict
        genre: str
        album_name: str
    """

    class Meta:
        table_name = "AssetTable"
        region = os.getenv("AWS_REGION", "us-west-2")

    asset_id = UnicodeAttribute(range_key=True)
    series = UnicodeAttribute(null=True)
    song_id = UnicodeAttribute(hash_key=True)
    album_name = UnicodeAttribute(null=True)
    rights_types = UnicodeSetAttribute(null=True)
    approved_for_track_image = BooleanAttribute(null=True)
    isrc = UnicodeAttribute(null=True)
    iswc = UnicodeAttribute(null=True)
    included_income_sources = UnicodeSetAttribute(null=True)
    song_title = UnicodeAttribute(null=True)
    current_share_price = NumberAttribute(null=True)
    three_years_avg = NumberAttribute(null=True)
    outstanding_shares = NumberAttribute(null=True)
    float_shares = NumberAttribute(null=True)
    testing_the_waters = UnicodeAttribute(null=True)
    primary_launch_date = UnicodeAttribute(null=True)
    secondary_launch_date = UnicodeAttribute(null=True)
    payment = UnicodeAttribute(null=True)
    term = UnicodeAttribute(null=True)
    spv_name = UnicodeAttribute(null=True)
    date_of_last_reported_earnings = UnicodeAttribute(null=True)
    market_cap = NumberAttribute(null=True)
    estimated_dividend_yield = NumberAttribute(null=True)
    recording_artists = UnicodeSetAttribute(null=True)
    songwriters = UnicodeSetAttribute(null=True)
    iio = UnicodeSetAttribute(null=True)
    quarterly_revenue = ListAttribute(null=True, of=MapAttribute)
    yearly_revenues = MapAttribute(null=True)
    yearly_distribution = MapAttribute(null=True)
    original_assignor_title = UnicodeAttribute(null=True)
    original_assignor_name = UnicodeAttribute(null=True)
    historic_data_age = UnicodeAttribute(null=True)
    description = UnicodeAttribute(null=True)
    issuance_type = UnicodeAttribute(null=True)

    # Created by brassica
    brassica_security_id = UnicodeAttribute(null=True)
    offering_id = UnicodeAttribute(null=True)
    offering_series_id = UnicodeAttribute(null=True)
    offering_series_asset_id = UnicodeAttribute(null=True)

    # Next fields from chartmetric
    streaming_count = NumberAttribute(null=True)
    meta = MapAttribute(default={})
    image = MapAttribute(default={}, null=True)
    genre = UnicodeSetAttribute(null=True)

    asset_id_index = AssetIdIndex()

    def to_dict(self) -> Dict:
        return {
            "asset_id": self.asset_id,
            "series": self.series,
            "song_id": self.song_id,
            "album_name": self.album_name,
            "rights_types": self.rights_types,
            "approved_for_track_image": self.approved_for_track_image,
            "isrc": self.isrc,
            "iswc": self.iswc,
            "included_income_sources": self.included_income_sources,
            "song_title": self.song_title,
            "current_share_price": self.current_share_price,
            "three_years_avg": self.three_years_avg,
            "outstanding_shares": self.outstanding_shares,
            "float_shares": self.float_shares,
            "testing_the_waters": self.testing_the_waters,
            "primary_launch_date": self.primary_launch_date,
            "secondary_launch_date": self.secondary_launch_date,
            "payment": self.payment,
            "term": self.term,
            "spv_name": self.spv_name,
            "date_of_last_reported_earnings": self.date_of_last_reported_earnings,
            "market_cap": self.market_cap,
            "estimated_dividend_yield": self.estimated_dividend_yield,
            "recording_artists": self.recording_artists,
            "songwriters": self.songwriters,
            "iio": self.iio,
            "quarterly_revenue": self.quarterly_revenue,
            "yearly_revenues": self.yearly_revenues,
            "yearly_distribution": self.yearly_distribution,
            "original_assignor_title": self.original_assignor_title,
            "original_assignor_name": self.original_assignor_name,
            "historic_data_age": self.historic_data_age,
            "description": self.description,
            "issuance_type": self.issuance_type,
            "offering_id": self.offering_id,
            "offering_series_id": self.offering_series_id,
            "offering_series_asset_id": self.offering_series_asset_id,
        }
