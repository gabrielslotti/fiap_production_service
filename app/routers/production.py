from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from functools import lru_cache
import httpx

from app.models.order import Order as OrderModel
from app.schemas.order import OrderStatusUpdate
from .. import database, config


@lru_cache()
def get_settings():
    """
    Config settings function.
    """
    return config.Settings()


conf_settings = get_settings()

router = APIRouter()


@router.post(
    "/update",
    response_model=OrderStatusUpdate,
    status_code=status.HTTP_200_OK
)
def update_order(
    order: OrderStatusUpdate,
    db_session: Session = Depends(database.get_db)
):
    db_order = (
        db_session.query(OrderModel)
                  .filter(OrderModel.id == order.id)
                  .one_or_none()
    )

    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    db_order.status = order.status

    db_session.add(db_order)
    db_session.commit()
    db_session.refresh(db_order)

    # Callback Orders Service to create the order
    req = httpx.post(
        f"{conf_settings.order_service_url}/order/update",
        json={
            "external_id": db_order.external_id,
            "status": db_order.status
        }
    )

    if req.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Error calling back order service"
        )

    return OrderStatusUpdate(
        id=db_order.id,
        status=db_order.status
    )
