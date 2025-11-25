from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from datetime import datetime
import uuid
from contextlib import contextmanager

app = FastAPI(title="Shared Memory API with SQLite")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path - will be in persistent disk on Render
DB_PATH = os.getenv('DATABASE_PATH', '/data/memories.db')
# For local testing, use current directory
if not os.path.exists(os.path.dirname(DB_PATH) or '.'):
    DB_PATH = './memories.db'

# Database connection manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                project TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        # Create indexes for faster queries
        conn.execute('CREATE INDEX IF NOT EXISTS idx_project ON memories(project)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at)')
        print(f"✅ Database initialized at {DB_PATH}")

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    init_db()

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

# Helper function to convert Row to dict
def row_to_dict(row):
    d = dict(row)
    # Convert tags from JSON string to list
    if d.get('tags'):
        import json
        d['tags'] = json.loads(d['tags'])
    else:
        d['tags'] = []
    return d

# CREATE
@app.post("/memory/add")
async def add_memory(memory: Memory):
    import json
    
    memory_id = f"mem_{uuid.uuid4().hex[:16]}"
    now = datetime.utcnow().isoformat()
    
    with get_db() as conn:
        conn.execute(
            '''INSERT INTO memories (id, project, content, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (memory_id, memory.project, memory.content, 
             json.dumps(memory.tags), now, now)
        )
    
    return {
        "success": True,
        "memory": {
            "id": memory_id,
            "project": memory.project,
            "content": memory.content,
            "tags": memory.tags,
            "created_at": now,
            "updated_at": now
        }
    }

# READ/SEARCH
@app.get("/memory/search")
async def search_memory(query: str, limit: int = 10):
    query_lower = f"%{query.lower()}%"
    
    with get_db() as conn:
        cursor = conn.execute(
            '''SELECT * FROM memories 
               WHERE LOWER(content) LIKE ? 
                  OR LOWER(project) LIKE ? 
                  OR LOWER(tags) LIKE ?
               ORDER BY created_at DESC
               LIMIT ?''',
            (query_lower, query_lower, query_lower, limit)
        )
        rows = cursor.fetchall()
    
    memories = [row_to_dict(row) for row in rows]
    
    return {
        "success": True,
        "count": len(memories),
        "memories": memories
    }

# LIST
@app.get("/memory/list")
async def list_memories(project: Optional[str] = None, limit: int = 50):
    with get_db() as conn:
        if project:
            cursor = conn.execute(
                '''SELECT * FROM memories 
                   WHERE LOWER(project) = LOWER(?)
                   ORDER BY created_at DESC
                   LIMIT ?''',
                (project, limit)
            )
        else:
            cursor = conn.execute(
                '''SELECT * FROM memories 
                   ORDER BY created_at DESC
                   LIMIT ?''',
                (limit,)
            )
        rows = cursor.fetchall()
    
    memories = [row_to_dict(row) for row in rows]
    
    return {
        "success": True,
        "count": len(memories),
        "memories": memories
    }

# UPDATE
@app.put("/memory/update/{memory_id}")
async def update_memory(memory_id: str, update: UpdateMemory):
    import json
    
    with get_db() as conn:
        # Check if memory exists
        cursor = conn.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Build update query
        updates = []
        params = []
        
        if update.content is not None:
            updates.append("content = ?")
            params.append(update.content)
        
        if update.tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(update.tags))
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(memory_id)
            
            query = f"UPDATE memories SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, params)
        
        # Fetch updated memory
        cursor = conn.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        memory = row_to_dict(row)
    
    return {"success": True, "memory": memory}

# DELETE
@app.delete("/memory/delete/{memory_id}")
async def delete_memory(memory_id: str):
    with get_db() as conn:
        # Check if memory exists
        cursor = conn.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        deleted = row_to_dict(row)
        
        # Delete memory
        conn.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
    
    return {"success": True, "deleted": deleted}

# STATS (bonus endpoint)
@app.get("/memory/stats")
async def get_stats():
    with get_db() as conn:
        # Total memories
        total = conn.execute('SELECT COUNT(*) as count FROM memories').fetchone()['count']
        
        # Memories by project
        cursor = conn.execute(
            'SELECT project, COUNT(*) as count FROM memories GROUP BY project'
        )
        by_project = {row['project']: row['count'] for row in cursor}
        
        # Recent activity (last 7 days)
        cursor = conn.execute(
            '''SELECT DATE(created_at) as date, COUNT(*) as count 
               FROM memories 
               WHERE created_at >= datetime('now', '-7 days')
               GROUP BY DATE(created_at)
               ORDER BY date DESC'''
        )
        recent_activity = [dict(row) for row in cursor]
    
    return {
        "total_memories": total,
        "by_project": by_project,
        "recent_activity": recent_activity
    }

# Health check
@app.get("/")
@app.head("/")
async def root():
    return {
        "status": "running",
        "service": "Shared Memory API",
        "database": "SQLite",
        "db_path": DB_PATH
    }

# Export/Import for migration
@app.get("/memory/export")
async def export_memories():
    """Export all memories as JSON (for backup/migration)"""
    with get_db() as conn:
        cursor = conn.execute('SELECT * FROM memories ORDER BY created_at')
        rows = cursor.fetchall()
    
    memories = [row_to_dict(row) for row in rows]
    
    return {
        "success": True,
        "count": len(memories),
        "memories": memories
    }

@app.post("/memory/import")
async def import_memories(data: dict):
    """Import memories from JSON (for migration from old system)"""
    import json
    
    memories = data.get('memories', [])
    imported = 0
    
    with get_db() as conn:
        for mem in memories:
            try:
                conn.execute(
                    '''INSERT OR REPLACE INTO memories 
                       (id, project, content, tags, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        mem.get('id', f"mem_{uuid.uuid4().hex[:16]}"),
                        mem['project'],
                        mem['content'],
                        json.dumps(mem.get('tags', [])),
                        mem.get('created_at', datetime.utcnow().isoformat()),
                        mem.get('updated_at', datetime.utcnow().isoformat())
                    )
                )
                imported += 1
            except Exception as e:
                print(f"Failed to import memory: {e}")
                continue
    
    return {
        "success": True,
        "imported": imported,
        "total": len(memories)
    }

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)