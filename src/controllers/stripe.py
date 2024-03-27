import os
from datetime import datetime
from logging import getLogger
from typing import Dict

import stripe
from fastapi import APIRouter, Depends
from pixelum_core.api.authorized_api_handler import authorized_api_handler

from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.transaction import Transaction
from src.models.dynamo.user_metadata import UserMetadataModel

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "allow:make_payment"
)
safe_endpoints = True if os.getenv("STAGE_NAME") != "prod" else False


@router.post("/process-payment", tags=["Stripe"])
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def process_payment(
    amount: int,
    currency: str,
    token: str,
    user: UserMetadataModel = Depends(granted_user)
) -> Dict:
    try:
        # Create a charge using the Stripe API
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=token,  # Stripe token obtained from the client-side (e.g., Stripe.js)
            description=f"Payment for Transcriber by user: {user.user_id} at {datetime.now().isoformat()}",  # Add a description for the payment
        )

        transaction: Transaction = await Transaction.initialize(
            user_id=user.user_id,
            transaction_id=charge.id,
            amount=amount,
            currency=currency,
            token=token,
        )
        await transaction.save()

        # Return a success response
        return {"status": "success", "charge_id": charge.id}

    except stripe.error.CardError as e:
        # Handle specific Stripe errors
        logger.info(f"Stripe Card error: {e}")
        return {"status": "error", "message": str(e)}
    except stripe.error.StripeError as e:
        # Handle generic Stripe errors
        logger.info(f"Stripe error: {e}")
        return {"status": "error", "message": "Something went wrong. Please try again later."}
