from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from data.database.db import Base
import json


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # ----------------------------
    # Primary Key
    # ----------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ----------------------------
    # User Identity
    # ----------------------------
    user_id = Column(Integer, index=True, nullable=True)  # FK-style reference
    username = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)

    # ----------------------------
    # Action Details
    # ----------------------------
    action = Column(String, nullable=False)
    query = Column(Text, nullable=True)
    documents = Column(Text, nullable=True)

    # ----------------------------
    # Timestamp
    # ----------------------------
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ----------------------------
    # Helpers
    # ----------------------------
    def set_documents(self, docs: list):
        """
        Store documents safely as JSON string.
        Always stores a list.
        """
        try:
            self.documents = json.dumps(docs or [])
        except Exception:
            self.documents = "[]"

    def get_documents(self):
        """
        Return documents as Python list.
        Never raises exception (audit safety).
        """
        if not self.documents:
            return []

        try:
            return json.loads(self.documents)
        except Exception:
            return []
