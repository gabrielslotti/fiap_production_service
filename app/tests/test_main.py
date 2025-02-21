import json
import pytest
from fastapi.testclient import TestClient
# from unittest.mock import MagicMock, patch
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.dialects.sqlite import JSON
from app.database import Base, get_db
from app.tests.db import engine, override_get_db
from app import main


"""
with patch("pika.BlockingConnection") as mock_pika_conn:
    # Configura os mocks
    mock_pika_instance = MagicMock()
    mock_pika_conn.return_value = mock_pika_instance

    from app import main


@pytest.fixture(autouse=True)
def mock_dependencies():
    yield {
        "pika": mock_pika_instance,
    }
"""


class OrderTest(Base):
    __tablename__ = "order"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    external_id = Column(String(120))
    status = Column(String(60))
    items = Column(JSON, nullable=False)


main.app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def test_db():
    """
    Test database.
    """
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        items = json.dumps([
            {
                "category": "Bebida",
                "item": "Coca-Cola Lata 350ml",
                "obs": "copo gelo e limão",
                "amount": 1,
                "price": 6
            },
            {
                "category": "Lanche",
                "item": "X-Egg",
                "obs": "sem tomate",
                "amount": 1,
                "price": 32
            }
        ])
        conn.execute(text(
            "INSERT INTO \"order\"  (external_id, status, items) "
            f"VALUES ('abc-123', 'Recebido', '{items}')"
        ))
        conn.commit()

    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(main.app)


def test_health():
    """
    Test health route.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_order_production(test_db):
    response = client.post(
        "/update",
        json={
            "id": 1,
            "external_id": "abc-123",
            "status": "Em preparação"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "external_id": "abc-123",
        "status": "Em preparação"
    }
