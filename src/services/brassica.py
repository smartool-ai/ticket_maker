import re
import os
from logging import getLogger
from typing import List, Optional


import requests


logger = getLogger(__name__)


class BrassicaClient:
    platform_slug = os.getenv("BRASSICA_PLATFORM_SLUG")
    url: str = os.getenv("BRASSICA_SERVER")
    headers: dict = {
        "accept": "application/vnd.api+json",
        "content-type": "application/vnd.api+json",
        "Authorization": f"Bearer {os.getenv('BRASSICA_TOKEN')}",
    }

    def _url(self, path):
        if re.match(r"^https?://", path):
            return path
        logger.info(f"URL path: {self.url}{path}")
        return f"{self.url}{path}"

    def _brassica_request(self, method, path, body):
        logger.info(f"[brassica] request path: {path}")
        logger.info(f"[brassica] request body: {body}")

        response = requests.request(
            method, self._url(path), headers=self.headers, json=body
        )

        logger.info(f"[brassica] response status: {response.status_code}")
        logger.info(f"[brassica] response body: {response.content}")

        response.raise_for_status()

        return response

    def _brassica_scroll(self, method, path, body):
        response = self._brassica_request(method, path, body).json()

        if not isinstance(response["data"], list):
            raise Exception(
                f"Expected response to be a list, received: {response['data']}"
            )

        data = response["data"]

        while "next" in response["links"]:
            response = self._brassica_request(
                method, response["links"]["next"], body
            ).json()

            data.extend(response["data"])

        return data

    def get_all_securities(self) -> Optional[List[dict]]:
        """
        Gets all securities from Brassica

        Returns:
            List[dict]: A list of securities
        """
        endpoint: str = f"/api/platforms/{self.platform_slug}/securities?page_size=100"
        return self._brassica_scroll("GET", endpoint, None)

    def get_all_issuers(self) -> Optional[List[dict]]:
        """
        Gets all issuers from Brassica

        Returns:
            List[dict]: A list of issuers
        """
        endpoint: str = f"/api/platforms/{self.platform_slug}/issuers?page_size=100"
        return self._brassica_scroll("GET", endpoint, None)

    def get_offering(self, offering_id: str) -> Optional[dict]:
        """
        Gets a offering from Brassica

        Args:
            offering_id (str): The offering id
        """
        endpoint: str = f"/api/offerings/{offering_id}"
        offering_resp = self._brassica_request("GET", endpoint, None)

        offering_dict: dict = offering_resp.json()

        return offering_dict.get("data")

    def get_all_offerings(self) -> Optional[List[dict]]:
        """
        Gets all offerings from Brassica

        Returns:
            List[dict]: A list of offerings
        """
        endpoint: str = f"/api/platforms/{self.platform_slug}/offerings?page_size=100"
        return self._brassica_scroll("GET", endpoint, None)

    def get_security(self, security_id: str) -> Optional[dict]:
        """
        Gets a security from Brassica

        Args:
            security_id (str): The security id
        """
        endpoint: str = f"/api/securities/{security_id}"
        security_resp = self._brassica_request("GET", endpoint, None)

        security_dict: dict = security_resp.json()

        return security_dict.get("data")

    def create_security(self, security_data: dict, issuer_id: str) -> str:
        """
        Creates an security in brassica

        Args:
            security_data (dict)

        Returns:
            str
        """
        security_resp = self._brassica_request(
            "POST", f"/api/issuers/{issuer_id}/securities", security_data
        )

        return security_resp.json().get("data", {}).get("id")

    def create_offering(self, offering_data: dict, issuer_id: str) -> str:
        """
        Creates an offering in brassica

        Args:
            offering_data (dict)

        Returns:
            str
        """
        offering_resp = self._brassica_request(
            "POST", f"/api/issuers/{issuer_id}/offerings", offering_data
        )

        return offering_resp.json().get("data", {}).get("id")

    def update_offering(self, offering_id: str, offering_data: dict) -> None:
        """
        Updates an offering in brassica

        Args:
            offering_id (str)
            offering_data (dict)

        Returns:
            None
        """
        self._brassica_request(
            "PATCH", f"/api/sandbox/offerings/{offering_id}", offering_data
        )

        return None

    def get_all_offering_series(self, offering_id: str) -> List[dict]:
        """
        Get all offering series for a given offering

        Args:
            offering_id (str): brassica offering id

        Returns:
            List[dict]: A list of offering series
        """
        return self._brassica_scroll(
            "GET", f"/api/offerings/{offering_id}/offering-series?page_size=100", None
        )

    def get_all_agreement_templates(self) -> List[dict]:
        """
        Get all agreement templates

        Returns:
            List[dict]: A list of agreement templates
        """
        return self._brassica_scroll(
            "GET",
            f"/api/platforms/{self.platform_slug}/agreement-templates?page_size=100",
            None,
        )

    def get_agreement_content(self, agreement_id: str) -> str:
        """
        Get the draft content of an agreement in Brassica
        Args:
            agreement_id (str): _description_
        Returns:
            dict: _description_
        """
        response = self._brassica_request(
            "GET", f"/api/agreement-templates/{agreement_id}", None
        )
        return response.json().get("data", {}).get("attributes", {}).get("draftContent")

    def get_all_offering_series_assets(self, offering_series_id: str) -> List[dict]:
        """
        Get all offering series assets

        Args:
            offering_id (str): brassica offering id

        Returns:
            List[dict]: A list of offering series assets
        """
        return self._brassica_scroll(
            "GET",
            f"/api/offering-series/{offering_series_id}/offering-series-assets?page_size=100",
            None,
        )

    def create_offering_series(
        self, security: dict, asset: dict, offering_id: str
    ) -> str:
        """
        Create an offering series describing securities in this offering

        Args:
            security (dict): brassica security object
            asset (dict): jkbx asset object
            offering_id (str)

        Returns:
            str: the id of the offering series
        """
        available_shares = 0
        float_shares = int(asset.get("float_shares"))
        # Total float above 70K, 15% of shares for GTS with a max of 20K shares
        # Total float between 60,000 - 69,999, 9% shares for GTS
        # Total float between 50,000 - 59,999, 5.5% shares for GTS
        # Total float between 40,000 - 49,999, 4.5% shares for GTS
        # Total float less than 40K, 0 shares for GTS
        if float_shares > 70000:
            available_shares = int(float_shares * 0.85)
            if available_shares > 20000:
                available_shares = 20000
        elif float_shares >= 60000 and float_shares < 70000:
            available_shares = int(float_shares * 0.91)
        elif float_shares >= 50000 and float_shares < 60000:
            available_shares = int(float_shares * 0.945)
        elif float_shares >= 40000 and float_shares < 50000:
            available_shares = int(float_shares * 0.955)
        else:
            available_shares = float_shares

        body = {
            "data": {
                "attributes": {
                    "minimumUnitPurchaseQuantity": 1,
                    "purchasePricePerUnit": float(asset.get("current_share_price")),
                    "maximumUnitPurchaseQuantity": available_shares,
                    "title": security.get("attributes", {}).get("class"),
                    "totalUnitsPurchased": 0,
                    "totalUnitsForSale": available_shares,
                }
            }
        }
        response = self._brassica_request(
            "POST", f"/api/offerings/{offering_id}/offering-series", body
        )

        return response.json().get("data", {}).get("id")

    def create_offering_series_asset(
        self, security: dict, offering_series_id: str
    ) -> str:
        """
        Create an offering series asset describing securities in this offering

        Args:
            asset (dict): jkbx asset object
            offering_series_id (str): brassica offering series id

        Returns:
            str: the id of the offering series asset
        """
        body: dict = {
            "data": {
                "attributes": {"quantityPerUnit": 1},
                "relationships": {
                    "security": {"id": security.get("id"), "type": "securities"}
                },
            }
        }

        response = self._brassica_request(
            "POST",
            f"/api/offering-series/{offering_series_id}/offering-series-assets",
            body,
        )

        return response.json().get("data", {}).get("id")

    def delete_offering_series(self, offering_series_id: str) -> None:
        """
        Delete an offering series

        Args:
            offering_series_id (str): brassica offering series id

        Returns:
            None
        """
        self._brassica_request(
            "DELETE", f"/api/offering-series/{offering_series_id}", None
        )

        return None

    def delete_offering_series_asset(self, offering_series_asset_id: str) -> None:
        """
        Delete an offering series asset

        Args:
            offering_series_asset_id (str): brassica offering series asset id

        Returns:
            None
        """
        self._brassica_request(
            "DELETE", f"/api/offering-series-assets/{offering_series_asset_id}", None
        )

        return None

    def create_funding_config(self, offering_id: str) -> str:
        """
        Creates a funding config in brassica

        Args:
            offering_id (str): _description_

        Returns:
            str: _description_
        """
        data = {
            "data": {
                "attributes": {
                    "allowTransferTypes": ["ach-us", "wire-domestic", "wire-swift"],
                    "requireEscrow": False,
                    "status": "open",
                }
            }
        }
        funding_config_resp = self._brassica_request(
            "POST", f"/api/offerings/{offering_id}/funding-config", data
        )

        return funding_config_resp.json().get("data", {}).get("id")

    def publish_agreement_template(self, agreement_template_id: str) -> dict:
        """
        Publishes a purchase agreement template in brassica

        Args:
            agreement_template_id (str): _description_

        Returns:
            str: _description_
        """
        # No attributes are sent but... you have to send an empty JSON:API document presently.
        body = {"data": {}}
        agreement_template_resp = self._brassica_request(
            "POST",
            f"/api/agreement-templates/{agreement_template_id}/agreement-template-versions",
            body,
        )

        return agreement_template_resp.json()

    def create_purchase_agreement_template(
        self, offering_id: str, purchase_agreement_id: str
    ) -> str:
        """
        create purchase agreement template to be added to an offering

        Args:
            offering_id (str): id of the offering

        Returns:
            str: id of the purchase agreement template
        """
        draft_content = self.get_agreement_content(purchase_agreement_id)

        body = {
            "data": {
                "attributes": {"markupType": "html", "draftContent": draft_content}
            }
        }
        agreement_template_resp = self._brassica_request(
            "POST", f"/api/offerings/{offering_id}/purchase-agreement-template", body
        )

        purchase_agreement_template_id = (
            agreement_template_resp.json().get("data", {}).get("id")
        )

        self.publish_agreement_template(purchase_agreement_template_id)

        return purchase_agreement_template_id


brassica_client = BrassicaClient()
