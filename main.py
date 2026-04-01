from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import hashlib
from dotenv import load_dotenv

# Load variables
load_dotenv()

app = FastAPI(title="Novanews API")

# Enable CORS for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    password = os.getenv("SupaBase_Password")
    conn = psycopg2.connect(
        host="db.imldatxbnfvktxemwdis.supabase.co",
        database="postgres",
        user="postgres",
        password=password,
        port="5432"
    )
    return conn

def hash_password(password: str) -> str:
    # Basic hashing so we don't store plaintext passwords (using built-in hashlib)
    return hashlib.sha256(password.encode()).hexdigest()

# --- Data Models (For Swagger UI and Flutter) ---
class UserAuth(BaseModel):
    email: str
    password: str

class BookmarkCreate(BaseModel):
    user_id: int
    title: str
    url: str
    image_url: str | None = None

# --- Setup Endpoint ---
@app.post("/setup-db", tags=["Setup"])
def setup_database():
    """Run this ONCE to create your tables in Supabase"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create Users Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create Bookmarks Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Tables created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Auth Endpoints ---
@app.post("/signup", tags=["Auth"])
def signup(user: UserAuth):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        hashed_pw = hash_password(user.password)
        
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email",
            (user.email, hashed_pw)
        )
        new_user = cur.fetchone()
        conn.commit()
        
        cur.close()
        conn.close()
        return {"status": "success", "user": new_user}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", tags=["Auth"])
def login(user: UserAuth):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        hashed_pw = hash_password(user.password)
        
        cur.execute(
            "SELECT id, email FROM users WHERE email = %s AND password_hash = %s",
            (user.email, hashed_pw)
        )
        existing_user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not existing_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        return {"status": "success", "user": existing_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Bookmark Endpoints ---
@app.post("/bookmarks", tags=["Bookmarks"])
def add_bookmark(bookmark: BookmarkCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            """INSERT INTO bookmarks (user_id, title, url, image_url) 
               VALUES (%s, %s, %s, %s) RETURNING *""",
            (bookmark.user_id, bookmark.title, bookmark.url, bookmark.image_url)
        )
        new_bookmark = cur.fetchone()
        conn.commit()
        
        cur.close()
        conn.close()
        return {"status": "success", "bookmark": new_bookmark}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookmarks/{user_id}", tags=["Bookmarks"])
def get_bookmarks(user_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT * FROM bookmarks WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        bookmarks = cur.fetchall()
        
        cur.close()
        conn.close()
        return {"status": "success", "bookmarks": bookmarks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Novanews API is running"}