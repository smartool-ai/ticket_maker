from typing import List, Optional

from src.lib.enums import AWSService
from src.lib.utilities import BotoConnector, only_run_in_lambda_env


@only_run_in_lambda_env
def initialize_boto_connections(
    boto_clients_to_initialize: Optional[List[AWSService]],
) -> None:
    """Initialize the requested boto connections if running in lambda.

    This function gets used to initialize connections during lambda initialization to assure
    that they're ready during invocation.
    """
    if boto_clients_to_initialize:
        boto_connector = BotoConnector()
        for boto_client in boto_clients_to_initialize:
            boto_connector.initialize_client(service=boto_client)
