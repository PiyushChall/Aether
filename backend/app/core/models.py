from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class APISpec(Base):
    __tablename__ = "api_specs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # Added filename
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_cases = relationship("TestCase", back_populates="spec", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True, index=True)
    spec_id = Column(Integer, ForeignKey("api_specs.id"))
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    payload = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    spec = relationship("APISpec", back_populates="test_cases")
    results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")


class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    success = Column(Boolean, nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_case = relationship("TestCase", back_populates="results")
