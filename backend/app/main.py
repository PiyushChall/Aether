from fastapi import FastAPI
from core.db import Base, engine
from api import specs, tests

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AETHER - AI API Tester")

app.include_router(specs.router, prefix="/api/specs", tags=["Specs"])
app.include_router(tests.router, prefix="/api/tests", tags=["Tests"])
