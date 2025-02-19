from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.models.order import Order as OrderModel
from app.schemas.order import OrderStatusUpdate
from .. import database


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

    return OrderStatusUpdate(
        id=db_order.id,
        external_id=db_order.external_id,
        status=db_order.status
    )
