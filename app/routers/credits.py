"""Credits router — Stripe Checkout, webhook, balance."""

import logging
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.routers.auth import require_current_user
from app.services.credit_service import add_credits, get_balance

logger = logging.getLogger("mapsearch.credits")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/api/credits", tags=["credits"])

CREDIT_PACKS = [
    {"id": "starter", "credits": 1000, "price_cents": 150, "label": "Starter"},
    {"id": "growth", "credits": 5000, "price_cents": 700, "label": "Growth"},
    {"id": "pro", "credits": 25000, "price_cents": 3200, "label": "Pro"},
    {"id": "agency", "credits": 100000, "price_cents": 12000, "label": "Agency"},
]


class CheckoutRequest(BaseModel):
    pack_id: str


@router.get("/packs")
async def list_packs():
    """Return available credit packs."""
    return {"packs": CREDIT_PACKS}


@router.post("/checkout")
async def create_checkout(request: Request, body: CheckoutRequest, user: dict = Depends(require_current_user)):
    pack = next((p for p in CREDIT_PACKS if p["id"] == body.pack_id), None)
    if not pack:
        raise HTTPException(status_code=400, detail="Invalid pack_id")

    base_url = f"https://{request.headers.get('host', 'mapsearch.app')}"
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": pack["price_cents"],
                "product_data": {"name": f"MapSearch {pack['label']} — {pack['credits']:,} credits"},
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{base_url}/?payment=success",
        cancel_url=f"{base_url}/?payment=cancelled",
        metadata={
            "user_id": str(user["id"]),
            "pack_id": pack["id"],
            "credits": str(pack["credits"]),
        },
    )
    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events. CRITICAL: Verify signature."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        meta = session.get("metadata", {})
        user_id = meta.get("user_id")
        credits = int(meta.get("credits", 0))
        payment_id = session.get("payment_intent")

        if user_id and credits > 0:
            from uuid import UUID
            await add_credits(UUID(user_id), credits, stripe_payment_id=payment_id)
            logger.info(f"Added {credits} credits to user {user_id} (payment: {payment_id})")

    return {"status": "ok"}


@router.get("/balance")
async def credit_balance(user: dict = Depends(require_current_user)):
    balance = await get_balance(user["id"])
    return {"credits": balance}


@router.get("/transactions")
async def credit_transactions(
    page: int = 1,
    user: dict = Depends(require_current_user),
):
    from app.database import queries as q
    limit = 50
    offset = (page - 1) * limit
    txns = await q.get_credit_transactions(user["id"], limit=limit, offset=offset)
    total = await q.count_credit_transactions(user["id"])
    return {
        "transactions": [
            {
                "id": str(t["id"]),
                "amount": t["amount"],
                "type": t["type"],
                "stripe_payment_id": t["stripe_payment_id"],
                "created_at": t["created_at"].isoformat() if t["created_at"] else None,
            }
            for t in txns
        ],
        "page": page,
        "total": total,
        "has_next": offset + limit < total,
    }
