from fastapi import APIRouter, HTTPException
from app.database.crud import get_all_commit_analyses

router = APIRouter()

def serialize_model(model):
    if not model: 
        return None
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

@router.get("/data")
async def fetch_all_data():
    try:
        records = await get_all_commit_analyses()
        results = []
        for r in records:
            data = serialize_model(r)
            data["developer_analysis"] = serialize_model(r.developer_analysis)
            data["orchestrator_decision"] = serialize_model(r.orchestrator_decision)
            data["security_review"] = serialize_model(r.security_review)
            data["architecture_review"] = serialize_model(r.architecture_review)
            data["better_approach_review"] = serialize_model(r.better_approach_review)
            data["principal_review"] = serialize_model(r.principal_review)
            data["detected_vulnerabilities"] = [serialize_model(v) for v in r.detected_vulnerabilities]
            data["priority_fixes"] = [serialize_model(f) for f in r.priority_fixes]
            data["llm_usage_logs"] = [serialize_model(l) for l in r.llm_usage_logs]
            results.append(data)
        return {"status": "success", "data": results}
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
