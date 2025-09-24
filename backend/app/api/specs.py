from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from core import db, models, test_generator
import json
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploaded_specs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_spec(file: UploadFile = File(...), session: Session = Depends(db.get_session)):
    # 1️⃣ Save the uploaded file locally
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2️⃣ Parse JSON
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            spec_json = json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")

    # 3️⃣ Store spec in DB
    try:
        new_spec = models.APISpec(filename=file.filename, content=json.dumps(spec_json))
        session.add(new_spec)
        session.commit()
        session.refresh(new_spec)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    # 4️⃣ Generate AI tests
    try:
        ai_tests = test_generator.generate_ai_tests(json.dumps(spec_json))
    except Exception as e:
        ai_tests = []
        print(f"AI test generation failed: {e}")

    # 5️⃣ Save generated tests to DB
    test_count = 0
    for t in ai_tests:
        try:
            tc = models.TestCase(
                spec_id=new_spec.id,
                endpoint=t["endpoint"],
                method=t["method"].upper(),
                payload=json.dumps(t.get("payload", {}))
            )
            session.add(tc)
            test_count += 1
        except Exception as e:
            print(f"Failed to save test case: {e}")
    session.commit()

    return {
        "spec_id": new_spec.id,
        "filename": file.filename,
        "generated_tests": test_count
    }
