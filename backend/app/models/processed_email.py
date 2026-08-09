from sqlalchemy import Column, String, Integer, BigInteger, Float, Text, Boolean, UniqueConstraint
from app.database import Base


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, index=True, nullable=False)
    candidate_id = Column(String, index=True, nullable=False)
    thread_id = Column(String, index=True, nullable=False)
    message_index = Column(Integer, default=0)
    from_name = Column(String, nullable=True)
    from_email = Column(String, nullable=False, index=True)
    to_email = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(String, nullable=False)
    is_reply = Column(Boolean, default=False)
    attachments = Column(Text, nullable=True)  # JSON string

    # Routing & Processing outcomes
    decision = Column(String, nullable=False)  # created, updated, skipped
    skip_reason = Column(String, nullable=True)  # out_of_office, newsletter, vendor_spam, duplicate
    category = Column(String, nullable=True)
    assignee_id = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    deal_value_inr = Column(BigInteger, nullable=True)
    company_name = Column(String, nullable=True)
    due_date = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    routing_reason = Column(Text, nullable=True)
    task_id = Column(String, nullable=True, index=True)
    is_spurious_candidate = Column(Boolean, default=False)
    raw_llm_output = Column(Text, nullable=True)
    created_at = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("candidate_id", "email_id", name="uq_candidate_email_id"),
    )
