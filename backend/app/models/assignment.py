"""
Assignment database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Assignment(Base):
    """
    Assignment model for student submissions
    """
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    # File information
    original_filename = Column(String, nullable=True)
    corrected_filename = Column(String, nullable=True)

    # Analysis results
    analysis_results = Column(Text, nullable=True)  # JSON string of analysis
    error_points = Column(Text, nullable=True)     # JSON string of error points
    knowledge_gaps = Column(Text, nullable=True)   # JSON string of knowledge gaps

    status = Column(String, default="pending")  # pending, processing, completed, failed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("User", back_populates="assignments")