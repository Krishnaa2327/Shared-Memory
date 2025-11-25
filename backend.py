from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
import uuid

app = FastAPI(title="Shared Memory API")

# Storage file
STORAGE_FILE = os.path.expanduser("~/.mcp-shared-memory.json")

# Models
class Memory(BaseModel):
    id: Optional[str] = None
    project: str
    content: str
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UpdateMemory(BaseModel):
    content: Optional[str] = None
    tags: Optional[List[str]] = None

# Load/Save functions
def load_memories():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {"memories": []}

def save_memories(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# CREATE
@app.post("/memory/add")
async def add_memory(memory: Memory):
    data = load_memories()
    
    memory.id = f"mem_{uuid.uuid4().hex[:16]}"
    memory.created_at = datetime.utcnow().isoformat()
    memory.updated_at = memory.created_at
    
    data["memories"].append(memory.dict())
    save_memories(data)
    
    return {"success": True, "memory": memory}

# READ/SEARCH
@app.get("/memory/search")
async def search_memory(query: str, limit: int = 10):
    data = load_memories()
    query_lower = query.lower()
    
    results = [
        m for m in data["memories"]
        if query_lower in m["content"].lower() or
           query_lower in m["project"].lower() or
           any(query_lower in tag.lower() for tag in m.get("tags", []))
    ]
    
    return {
        "success": True,
        "count": len(results[:limit]),
        "memories": results[:limit]
    }

# LIST
@app.get("/memory/list")
async def list_memories(project: Optional[str] = None, limit: int = 50):
    data = load_memories()
    memories = data["memories"]
    
    if project:
        memories = [m for m in memories if m["project"].lower() == project.lower()]
    
    return {
        "success": True,
        "count": len(memories[:limit]),
        "memories": memories[:limit]
    }

# UPDATE
@app.put("/memory/update/{memory_id}")
async def update_memory(memory_id: str, update: UpdateMemory):
    data = load_memories()
    
    for memory in data["memories"]:
        if memory["id"] == memory_id:
            if update.content is not None:
                memory["content"] = update.content
            if update.tags is not None:
                memory["tags"] = update.tags
            memory["updated_at"] = datetime.utcnow().isoformat()
            
            save_memories(data)
            return {"success": True, "memory": memory}
    
    raise HTTPException(status_code=404, detail="Memory not found")

# DELETE
@app.delete("/memory/delete/{memory_id}")
async def delete_memory(memory_id: str):
    data = load_memories()
    
    for i, memory in enumerate(data["memories"]):
        if memory["id"] == memory_id:
            deleted = data["memories"].pop(i)
            save_memories(data)
            return {"success": True, "deleted": deleted}
    
    raise HTTPException(status_code=404, detail="Memory not found")

# Health check
@app.get("/")
@app.head("/")
async def root():
    return {"status": "running", "service": "Shared Memory API"}


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
