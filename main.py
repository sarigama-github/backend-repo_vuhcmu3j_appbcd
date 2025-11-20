import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Course, PortfolioItem, Inquiry, Lead

app = FastAPI(title="Ben Venturing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Ben Venturing API is running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# -------------------------
# Schemas Introspection
# -------------------------
@app.get("/api/schema")
def get_schema():
    return {
        "course": Course.model_json_schema(),
        "portfolioitem": PortfolioItem.model_json_schema(),
        "inquiry": Inquiry.model_json_schema(),
        "lead": Lead.model_json_schema(),
    }


# -------------------------
# Seed helpers
# -------------------------
SAMPLE_COURSES: List[Course] = [
    Course(
        id="launch-your-life",
        title="Launch Your Life — AI & Freelance Foundations",
        description="Kickstart a freedom-first career with AI, content, and client work.",
        price="USD 199",
        slug="launch-your-life",
        modules=[
            {"id": "m1", "title": "Mindset & Faith", "lessons": [{"id": "intro", "title": "Intro", "type": "video"}, {"id": "faith-in-business", "title": "Faith in Business", "type": "article"}]},
            {"id": "m2", "title": "AI Tools & Workflow", "lessons": [{"id": "ai-basics", "title": "AI Basics", "type": "video"}, {"id": "automation-playbook", "title": "Automation Playbook", "type": "article"}]},
            {"id": "m3", "title": "Content & Monetization", "lessons": [{"id": "ugc-strategy", "title": "UGC Strategy", "type": "video"}, {"id": "pricing-services", "title": "Pricing Services", "type": "article"}]},
        ],
        instructor="Ben",
        thumbnail=None,
    )
]

SAMPLE_PORTFOLIO: List[PortfolioItem] = [
    PortfolioItem(
        id="p1",
        title="Resort Investment Campaign",
        category="Photography",
        client=None,
        date=None,
        media=[],
        caseStudyText="Campaign increased bookings by 18%",
        metrics={"engagement": "+37% CTR"},
        slug="resort-investment-campaign",
    ),
    PortfolioItem(
        id="p2",
        title="Aetherflo Demo Site",
        category="Web",
        client=None,
        date=None,
        media=[],
        caseStudyText="Demo bookings via website",
        metrics={"conversion": "demo bookings"},
        slug="aetherflo-demo-site",
    ),
]


def seed_if_empty(collection: str, documents: List[BaseModel]):
    existing = get_documents(collection, {}, limit=1)
    if not existing:
        for doc in documents:
            create_document(collection, doc)


# -------------------------
# Courses
# -------------------------
@app.get("/api/courses")
def list_courses():
    try:
        seed_if_empty("course", SAMPLE_COURSES)
        docs = get_documents("course")
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Portfolio
# -------------------------
@app.get("/api/portfolio")
def list_portfolio():
    try:
        seed_if_empty("portfolioitem", SAMPLE_PORTFOLIO)
        docs = get_documents("portfolioitem")
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Inquiries & Leads
# -------------------------
@app.post("/api/inquiries")
def create_inquiry(payload: Inquiry):
    try:
        new_id = create_document("inquiry", payload)
        return {"status": "ok", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leads")
def capture_lead(payload: Lead):
    try:
        new_id = create_document("lead", payload)
        return {"status": "ok", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
