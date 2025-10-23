"""
Knowledge point database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class KnowledgePoint(Base):
    """
    Knowledge point model for structuring course content
    """
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    difficulty = Column(String, default="medium")  # easy, medium, hard
    module_name = Column(String, nullable=True)   # Which module this belongs to
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    # Source document reference
    source_document = Column(String, nullable=True)
    source_content = Column(Text, nullable=True)  # Original document content

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="knowledge_points")