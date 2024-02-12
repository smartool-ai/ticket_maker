import re
from logging import getLogger
from typing import List, Dict
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.lib.token_authentication import TokenAuthentication

from src.services.brassica import brassica_client
from src.services.asset import get_asset

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:brassica_offerings")


class CreateBrassicaOffering(BaseModel):
    issuer_id: str
    agreement_template_id: str
    title: str
    description: str
    targetStartDate: date
    targetTerminationDate: date
    targetRaiseAmount: int
    offeringType: str


class UpdateBrassicaOffering(BaseModel):
    status: str


class BrassicaOfferingSeries(BaseModel):
    offering_id: str
    asset_id: str


@router.get("/brassica/issuers")
async def get_issuers(
    user: Dict = Depends(granted_user)
) -> List:
    return brassica_client.get_all_issuers()


@router.get("/brassica/offerings")
async def get_offerings(
        user: Dict = Depends(granted_user)
) -> List:
    return brassica_client.get_all_offerings()


@router.get("/brassica/agreement-templates")
async def get_agreement_templates(
    user: Dict = Depends(granted_user)
) -> List:
    return brassica_client.get_all_agreement_templates()


@router.get("/brassica/offering/{offering_id}")
async def get_offering(
    offering_id: str,
    user: Dict = Depends(granted_user)
) -> Dict:
    return brassica_client.get_offering(offering_id)


@router.post("/brassica/offerings")
async def create_offerings(
    offering: CreateBrassicaOffering,
    user: Dict = Depends(granted_user)
) -> None:
    slug = re.sub(r"\W+", "-", offering.title.lower())

    offering_id = brassica_client.create_offering({
        "data": {
            "attributes": {
                "description": offering.description,
                "targetStartDate": offering.targetStartDate.isoformat(),
                "targetTerminationDate": offering.targetTerminationDate.isoformat(),
                "targetRaiseAmount": offering.targetRaiseAmount,
                "title": offering.title,
                "offeringType": offering.offeringType,
                "requireAccreditedInvestors": False,
                "restrictPurchaserCountries": False,
                "restrictPurchaserOwnerTypes": False,
                "restrictPurchaserUsStates": False,
                "slug": slug
            }
        }
    }, offering.issuer_id)

    brassica_client.create_funding_config(offering_id)

    brassica_client.create_purchase_agreement_template(
        offering_id, offering.agreement_template_id
    )

    return None


@router.put("/brassica/offering/{offering_id}")
async def update_offerings(
    offering_id: str,
    offering: UpdateBrassicaOffering,
    user: Dict = Depends(granted_user)
) -> None:
    brassica_client.update_offering(offering_id, {
        "data": {
            "attributes": {
                "status": offering.status,
            }
        }
    })

    return None


@router.get("/brassica/offering/{offering_id}/series")
async def get_offering_series(
    offering_id: str,
    user: Dict = Depends(granted_user)
) -> List:
    return brassica_client.get_all_offering_series(offering_id)


@router.post("/brassica/offering-series")
async def create_offering_series(
    offering_series: BrassicaOfferingSeries,
    user: Dict = Depends(granted_user)
) -> None:
    offering = brassica_client.get_offering(offering_series.offering_id)
    asset = get_asset(offering_series.asset_id)

    # Create a security for the asset if it does not exist
    security = None

    if asset.brassica_security_id:
        security = brassica_client.get_security(asset.brassica_security_id)
    else:
        securities = brassica_client.get_all_securities()

        for existing_security in securities:
            security_name = existing_security.get("attributes", {}).get(
                "class").replace(" ", "_")
            if security_name == asset.asset_id:
                security = existing_security
                break

        if not security:
            security_id = brassica_client.create_security({
                'data': {
                    'attributes': {
                        'class': asset.asset_id.replace("_", " "),
                        'cusip': None,
                        'debtCurrencyCode': None,
                        'description': asset.song_title,
                        'expiresInDays': None,
                        'isDtcEligible': False,
                        'isNmsListed': False,
                        'isin': None,
                        'securityType': 'equity',
                        'tradingSymbol': None,
                        'tradingVenue': None,
                        'unitNamePlural': 'shares',
                        'unitNameSingular': 'share',
                        'unitPrecision': 0
                    },
                },
            }, offering["relationships"]["issuer"]["data"]["id"])

            security = brassica_client.get_security(security_id)

    # Associate the offering and the asset
    offering_series_id: str = brassica_client.create_offering_series(
        security,
        asset.to_dict(),
        offering_series.offering_id,
    )

    offering_series_asset_id: str = (
        brassica_client.create_offering_series_asset(
            security,
            offering_series_id=offering_series_id,
        )
    )

    # Update the assets brassica references in dynamo
    asset.brassica_security_id = security.get("id")
    asset.offering_series_id = offering_series_id
    asset.offering_series_asset_id = offering_series_asset_id
    asset.offering_id = offering_series.offering_id

    asset.save()

    return None


@router.delete("/brassica/offering/{offering_id}/series/{offering_series_id}")
async def delete_offering_series(
    offering_id: str,
    offering_series_id: str,
    user: Dict = Depends(granted_user)
) -> List:
    brassica_client.delete_offering_series(offering_series_id)
    return brassica_client.get_all_offering_series(offering_id)
