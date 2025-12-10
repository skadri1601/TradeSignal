from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
    func,
    JSON,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Notification(Base):
    """
    Represents an in-app notification for a user.
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_id = Column(
        Integer, ForeignKey("alerts.id"), nullable=True
    )  # Optional: if notification is from an alert
    type = Column(String, index=True)  # e.g., 'alert', 'system', 'promotion'
    title = Column(String, index=True, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(
        JSON, nullable=True
    )  # Arbitrary JSON data, e.g., trade details, link targets
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
    alert = relationship("Alert", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', title='{self.title[:30]}...')>"
