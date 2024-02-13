from typing import List, Optional, Type

from src.lib.dynamo_utils import BaseModel

from src.lib.utilities import only_run_in_lambda_env


@only_run_in_lambda_env
def initialize_dynamo_tables(
    models_to_initialize: Optional[List[Type[BaseModel]]],
) -> None:
    """Initialize the requested dynamo tables from Pynamo models if running in lambda."""
    if models_to_initialize:
        for model in models_to_initialize:
            model.initialize_connection()
