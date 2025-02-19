from app.models.order import Order as OrderModel
from app.schemas.order import OrderReceived
from .. import database


def receive_order(order_message: dict):
    """
    Receive new order to produce.

    :param order_message: Order received as a message from rmq.
    """
    order_raw = OrderReceived(**order_message).model_dump()

    db_session = next(database.get_db())

    db_order = OrderModel(**order_raw)
    db_session.add(db_order)
    db_session.commit()
    db_session.refresh(db_order)
