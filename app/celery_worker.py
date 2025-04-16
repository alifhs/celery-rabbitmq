from celery import Celery, Task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Order


celery_app = Celery(
    "worker",
    broker="pyamqp://guest:guest@rabbitmq//",  # Ensure correct RabbitMQ URL
    backend="redis://redis:6379/0",  # Storing task results (optional)
)

class BaseTaskWithAck(Task):
    def on_success(self, retval, task_id, args, kwargs):
        """Acknowledge manually after successful execution"""
        self.request.chain = None  # Prevent auto acknowledgment
        print(f"Task {task_id} completed. Acknowledging message.")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Don't acknowledge on failure to allow retrying"""
        print(f"Task {task_id} failed. Not acknowledging message.")

@celery_app.task(base=BaseTaskWithAck, acks_late=True)
def process_order(order_id: int, user_id: int):
    db: Session = SessionLocal()
    import time
    time.sleep(50)
    order = db.query(Order).filter(Order.id == order_id).first()
    print("Hello")

    if order:
        order.status = "completed"
        db.commit()

    db.close()
    return {"status": "Order processed", "order_id": order_id}
