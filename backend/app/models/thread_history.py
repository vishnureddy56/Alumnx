from sqlalchemy import Column, String, Integer, Text
from app.database import Base


class ThreadHistory(Base):
    __tablename__ = "thread_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String, index=True, nullable=False)
    thread_id = Column(String, index=True, nullable=False)
    task_id = Column(String, index=True, nullable=False)
    email_id = Column(String, nullable=False)
    update_type = Column(String, nullable=False)  # "create" | "update"
    update_count = Column(Integer, default=0)
    changed_fields = Column(Text, nullable=True)  # JSON string of updated fields
    summary = Column(Text, nullable=True)
    created_at = Column(String, nullable=False)
