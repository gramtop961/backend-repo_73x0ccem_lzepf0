import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Blog, BlogUpdate

app = FastAPI(title="Fitness Affiliate Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON serializable dict"""
    if not doc:
        return doc
    d = {**doc}
    _id = d.pop("_id", None)
    if _id is not None:
        d["id"] = str(_id)
    # Convert datetime fields to isoformat if present
    for k in ("created_at", "updated_at"):
        if k in d and hasattr(d[k], "isoformat"):
            d[k] = d[k].isoformat()
    return d


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
            response["database"] = "✅ Connected & Working"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# ---------- Blog Endpoints ----------

@app.get("/blogs", response_model=List[dict])
def list_blogs(limit: int | None = 50):
    docs = get_documents("blog", {}, limit)
    return [serialize_doc(d) for d in docs]


@app.post("/blogs", status_code=201)
def create_blog(blog: Blog):
    inserted_id = create_document("blog", blog)
    doc = db["blog"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)


@app.get("/blogs/{blog_id}")
def get_blog(blog_id: str):
    try:
        oid = ObjectId(blog_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid blog id")
    doc = db["blog"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Blog not found")
    return serialize_doc(doc)


@app.put("/blogs/{blog_id}")
def update_blog(blog_id: str, payload: BlogUpdate):
    try:
        oid = ObjectId(blog_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid blog id")
    data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    data["updated_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    result = db["blog"].update_one({"_id": oid}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
    doc = db["blog"].find_one({"_id": oid})
    return serialize_doc(doc)


@app.delete("/blogs/{blog_id}", status_code=204)
def delete_blog(blog_id: str):
    try:
        oid = ObjectId(blog_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid blog id")
    result = db["blog"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"status": "deleted"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
