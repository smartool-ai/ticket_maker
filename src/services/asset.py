from typing import List

from src.lib.loggers import get_module_logger
from src.models.dynamo.asset import AssetModel

logger = get_module_logger()


def get_asset(asset_id: str) -> AssetModel:
    """
    Get an asset by id
    """
    return next(AssetModel.asset_id_index.query(asset_id))


def list_assets() -> List[AssetModel]:
    """
    List all assets
    """
    return list(AssetModel.scan())
