from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from core import db
import requests
import json

router = APIRouter()

# Run a single test case
def run_test_case(test_case, session: Session):
    try:
        method = test_case.method.upper()
        url = test_case.endpoint
        payload = json.loads(test_case.payload or "{}")
        response = requests.request(method, url, json=payload, timeout=10)

        test_result = db.models.TestResult(
            test_case_id=test_case.id,
            success=response.status_code >= 200 and response.status_code < 300,
            status=response.status_code
        )
        session.add(test_result)
        session.commit()
    except Exception as e:
        print(f"Error running test {test_case.id}: {e}")
        test_result = db.models.TestResult(
            test_case_id=test_case.id,
            success=False,
            status=0
        )
        session.add(test_result)
        session.commit()


def run_tests_background(spec_id: int):
    session: Session = db.get_session()
    test_cases = session.query(db.models.TestCase).filter(db.models.TestCase.spec_id == spec_id).all()
    for tc in test_cases:
        run_test_case(tc, session)


@router.post("/run/{spec_id}")
async def run_tests(spec_id: int, background_tasks: BackgroundTasks):
    session: Session = db.get_session()
    spec = session.query(db.models.APISpec).filter(db.models.APISpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    # Clear previous results for fresh run
    session.query(db.models.TestResult).filter(db.models.TestResult.test_case.has(spec_id=spec_id)).delete()
    session.commit()

    # Run tests in background
    background_tasks.add_task(run_tests_background, spec_id)

    return {"spec_id": spec_id, "message": "Tests started in background"}


@router.get("/status/{spec_id}")
async def get_test_status(spec_id: int):
    session: Session = db.get_session()
    test_cases = session.query(db.models.TestCase).filter(db.models.TestCase.spec_id == spec_id).all()
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found for this spec")

    results = []
    for tc in test_cases:
        last_result = session.query(db.models.TestResult).filter(db.models.TestResult.test_case_id == tc.id)\
                        .order_by(db.models.TestResult.id.desc()).first()
        if last_result:
            results.append({
                "test_case_id": tc.id,
                "endpoint": tc.endpoint,
                "method": tc.method,
                "success": last_result.success,
                "status": last_result.status
            })
        else:
            results.append({
                "test_case_id": tc.id,
                "endpoint": tc.endpoint,
                "method": tc.method,
                "success": None,
                "status": None
            })

    return {"spec_id": spec_id, "total_tests": len(test_cases), "results": results}
