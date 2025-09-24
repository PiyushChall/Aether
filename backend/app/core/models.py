from sqlalchemy import Column, Integer, String, Text
from .db import Base

class APISpec(Base):
    __tablename__ = "api_specs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    spec_json = Column(Text)

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True, index=True)
    spec_id = Column(Integer)
    endpoint = Column(String)
    method = Column(String)
    payload = Column(Text)
