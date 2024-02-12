import os

from src.lib.dynamo_utils import BaseModel
from src.lib.enums import OrderStatus
from src.lib.loggers import get_module_logger

from pynamodb.attributes import (
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


logger = get_module_logger()


class CreatedDatetimeIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "created_datetime-index"
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)
    created_datetime = UTCDateTimeAttribute(range_key=True)


class OrderModel(BaseModel):
    """Model representing a Order.

    fields:
        email: str
        order_id: str
        order_type: str
        asset_id: str
        currency: str
        shares: int
        price: float
        order_status: str
    """

    class Meta:
        table_name = "OrdersTable"
        region = os.getenv("AWS_REGION", "us-west-2")

    email = UnicodeAttribute(hash_key=True)
    order_id = UnicodeAttribute(range_key=True)
    order_type = UnicodeAttribute()
    asset_id = UnicodeAttribute()
    shares = NumberAttribute()
    price = NumberAttribute(null=True)
    currency = UnicodeAttribute(default="USD")
    order_status = UnicodeAttribute(default=OrderStatus.SUBMITTED.value)
    meta = MapAttribute(default={})
    created_datetime = UTCDateTimeAttribute()

    created_datetime_index = CreatedDatetimeIndex()
