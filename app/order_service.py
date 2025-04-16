from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app.models import Order
from app.celery_worker import process_order

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/order/")
def place_order(order_id: int, user_id: int, db: Session = Depends(get_db)):
    # Create new order entry
    new_order = Order(id=order_id, user_id=user_id, status="pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Trigger Celery task
    task = process_order.apply_async(args=[order_id, user_id])

    return {"message": "Order placed!", "task_id": task.id}
