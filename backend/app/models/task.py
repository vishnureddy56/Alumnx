from sqlalchemy import Column, String, Integer, BigInteger, Float, Text, UniqueConstraint
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, index=True, nullable=False)
    source_email_id = Column(String, index=True, nullable=False)
    thread_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    priority = Column(String, nullable=False, index=True)
    due_date = Column(String, nullable=True)  # YYYY-MM-DD
    deal_value_inr = Column(BigInteger, nullable=True)
    company_name = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("candidate_id", "source_email_id", name="uq_candidate_source_email"),
    )
