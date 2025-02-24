from pydantic import BaseModel
from typing import List, Dict
from enum import Enum


class OrderStatusEnum(str, Enum):
    received = 'Recebido'
    preparing = 'Em preparação'
    done = 'Pronto'
    finished = 'Finalizado'


class OrderReceived(BaseModel):
    external_id: str
    status: OrderStatusEnum
    items: List[Dict]


class OrderReceivedResponse(OrderReceived):
    id: int


class OrderStatusUpdate(BaseModel):
    id: int
    status: OrderStatusEnum
