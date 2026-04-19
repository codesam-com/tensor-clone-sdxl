import os
import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from services.auth import get_api_key
from services.db import SessionLocal, User

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

PRICE_MAP = {
    "starter": {"credits": 100, "amount": 900, "name": "100 credits"},
    "pro": {"credits": 500, "amount": 3900, "name": "500 credits"},
    "max": {"credits": 1500, "amount": 9900, "name": "1500 credits"},
}

class CheckoutRequest(BaseModel):
    package: str

@router.post("/checkout")
def create_checkout_session(req: CheckoutRequest, user: User = Depends(get_api_key)):
    package = PRICE_MAP.get(req.package)
    if not package:
        raise HTTPException(status_code=400, detail="Invalid package")

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": package["name"],
                    "description": "Tensor Clone credit pack"
                },
                "unit_amount": package["amount"]
            },
            "quantity": 1
        }],
        success_url=f"{FRONTEND_URL}?checkout=success",
        cancel_url=f"{FRONTEND_URL}?checkout=cancel",
        metadata={
            "user_id": str(user.id),
            "credits": str(package["credits"]),
            "package": req.package
        }
    )

    return {"checkout_url": session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(default="")):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Webhook error: {exc}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        credits = int(session.get("metadata", {}).get("credits", "0"))

        if user_id and credits > 0:
            db = SessionLocal()
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.credits += credits
                db.commit()

    return {"received": True}
