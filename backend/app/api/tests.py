from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db import get_session
from core.models import TestCase
from workers.test_runner import run_test_case
import asyncio

router = APIRouter()

@router.post("/run/{spec_id}")
async def run_tests(spec_id: int, session: Session = Depends(get_session)):
    test_cases = session.query(TestCase).filter(TestCase.spec_id == spec_id).all()
    results = await asyncio.gather(*(run_test_case(tc) for tc in test_cases))
    return {"spec_id": spec_id, "total_tests": len(test_cases), "results": results}
